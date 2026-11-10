"""Baut das BMW-Short aus 9 Standbildern: Kamerafahrten (Ken Burns), analoges Grading, Korn, Untertitel, Ton.
python tools/render.py  ->  bmw-short.mp4"""
import json, subprocess, math
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent.parent
W, H, FPS, DUR = 1080, 1920, 24, 30.0
N = int(DUR * FPS)
FONT_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT_T = "/usr/share/fonts/opentype/inter/Inter-Thin.otf"
CFG = json.load(open(HERE / "tools" / "edit.json"))

# ------------------------------------------------------------------ voice timeline -> shot windows
lead, gap = 0.30, 0.40
t = lead
LINES = []
for ln in CFG["lines"]:
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                       str(HERE / "voice" / f"{ln['id']}.wav")]).decode())
    LINES.append({**ln, "start": t, "dur": d})
    t += d + gap
# each shot runs from its line's start (shot 1 from 0) to the next line's start; the last to the end
SHOTS = []
for i, ln in enumerate(LINES):
    s = 0.0 if i == 0 else ln["start"] - 0.15
    e = DUR if i == len(LINES) - 1 else LINES[i + 1]["start"] - 0.15
    SHOTS.append({**CFG["shots"][i], "s": s, "e": e})
print("shots:", [(round(x["s"], 2), round(x["e"], 2)) for x in SHOTS])

# ------------------------------------------------------------------ images, upscaled once
def load(name):
    im = Image.open(HERE / "img" / name).convert("RGB")
    big = im.resize((int(W * 1.25), int(H * 1.25)), Image.LANCZOS)          # headroom for the moves
    big = big.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return np.asarray(big)[:, :, ::-1].copy()                              # BGR for OpenCV
IMGS = {s["img"]: load(s["img"]) for s in SHOTS}

def ease(x):  # smooth in and out
    return 0.5 - 0.5 * math.cos(math.pi * min(1, max(0, x)))

def camera(shot, u):
    """u in 0..1 over the shot -> crop of the 1.25x plate (zoom, pan)"""
    z0, z1 = shot["zoom"]
    (x0, y0), (x1, y1) = shot["pan"]          # centre offsets as fractions of the free margin, -1..1
    k = ease(u)
    z = z0 + (z1 - z0) * k
    cx, cy = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    img = IMGS[shot["img"]]
    ih, iw = img.shape[:2]
    vw, vh = iw / z, ih / z                   # visible window on the plate
    mx, my = (iw - vw) / 2, (ih - vh) / 2
    left = mx + cx * mx
    top = my + cy * my
    M = np.array([[W / vw, 0, -left * W / vw], [0, H / vh, -top * H / vh]], dtype=np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

# ------------------------------------------------------------------ the analog grade (built once)
x = np.arange(256) / 255.0
def curve(lift, gamma, gain):
    y = np.clip(lift + (gain - lift) * np.power(x, gamma), 0, 1)
    y = y - 0.05 * np.sin(2 * np.pi * y) * 0.5          # gentle S, soft shoulders
    return (np.clip(y, 0, 1) * 255).astype(np.uint8)
LUT = np.dstack([curve(0.045, 1.02, 0.97),             # B: shadows a touch petrol
                 curve(0.035, 1.00, 0.985),            # G
                 curve(0.025, 0.97, 1.0)]).reshape(1, 256, 3)   # R: warm highlights
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.32 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.46) / (H * 0.62)) ** 2, 0, 1)).astype(np.float32)[..., None]
RNG = np.random.default_rng(1916)
GRAIN = [RNG.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(12)]

def grade(f, i):
    f = cv2.LUT(f, LUT)
    ff = f.astype(np.float32)
    # halation: highlights bleed a warm glow
    hi = np.clip((ff - 200) / 55, 0, 1)
    glow = cv2.GaussianBlur(hi, (0, 0), 18) * np.array([10, 28, 55], np.float32)
    ff = ff + glow
    ff *= VIG
    g = cv2.resize(GRAIN[i % 12], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    ff += g * 5.5
    return np.clip(ff, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ captions (pre-rendered RGBA layers)
fb = ImageFont.truetype(FONT_B, 62)
fy = ImageFont.truetype(FONT_T, 230)
ACC = (214, 168, 92)       # warm gold accent

def layout(words, maxw=900):
    rows, row = [], []
    for w in words:
        test = " ".join(x[0] for x in row + [w])
        if row and fb.getlength(test) > maxw:
            rows.append(row); row = []
        row.append(w)
    rows.append(row)
    return rows

def caption_layer(line, n_visible):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    words = [(w.strip("*"), w.startswith("*")) for w in line["text"].split()]
    rows = layout(words)
    y = 1330 - len(rows) * 78
    k = 0
    for row in rows:
        total = fb.getlength(" ".join(w for w, _ in row))
        xx0 = (W - total) / 2
        for w, hl in row:
            if k < n_visible:
                for dx, dy in ((0, 4), (0, 2)):
                    d.text((xx0 + dx, y + dy), w, font=fb, fill=(0, 0, 0, 150))
                d.text((xx0, y), w, font=fb, fill=ACC + (255,) if hl else (255, 255, 255, 255))
            xx0 += fb.getlength(w + " ")
            k += 1
        y += 78
    return np.asarray(im)

def year_layer(year, a):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tw = fy.getlength(year)
    d.text(((W - tw) / 2, 230), year, font=fy, fill=(255, 255, 255, int(235 * a)))
    return np.asarray(im)

def over(base, layer):
    a = layer[..., 3:4].astype(np.float32) / 255
    return (base * (1 - a) + layer[..., 2::-1] * a).astype(np.uint8)

# bottom gradient for legibility
GRAD = np.clip((yy - 1050) / 600, 0, 1).astype(np.float32)[..., None] * 0.55

cache = {}
def cap_at(tt):
    for ln in LINES:
        if ln["start"] <= tt < ln["start"] + ln["dur"] + 0.35:
            n = len(ln["text"].split())
            vis = min(n, int((tt - ln["start"]) / max(0.12, ln["dur"] * 0.9 / n)) + 1)
            key = (ln["id"], vis)
            if key not in cache:
                cache[key] = caption_layer(ln, vis)
            return cache[key]
    return None

# ------------------------------------------------------------------ render
ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                       str(HERE / "build" / "video.mp4")], stdin=subprocess.PIPE)
XF = 0.45   # crossfade length
for i in range(N):
    tt = i / FPS
    k = next(j for j, s in enumerate(SHOTS) if s["s"] <= tt < s["e"] + 1e-9 or j == len(SHOTS) - 1)
    sh = SHOTS[k]
    u = (tt - sh["s"]) / (sh["e"] - sh["s"])
    frame = camera(sh, u)
    # crossfade into the next shot during the last XF seconds (shot 3->4 is a hard match cut)
    if k + 1 < len(SHOTS) and tt > sh["e"] - XF and not sh.get("cut"):
        nx = SHOTS[k + 1]
        a = ease((tt - (sh["e"] - XF)) / XF)
        frame = cv2.addWeighted(frame, 1 - a, camera(nx, 0.0), a, 0)
    # the loop: the last second dissolves into shot 1's first frame
    if tt > DUR - 1.2:
        a = ease((tt - (DUR - 1.2)) / 1.0)
        frame = cv2.addWeighted(frame, 1 - a, camera(SHOTS[0], 0.0), a, 0)
    frame = grade(frame, i)
    frame = (frame * (1 - GRAD)).astype(np.uint8)
    if sh.get("year"):
        a = min(1, (tt - sh["s"]) / 0.4) * min(1, (sh["e"] - tt) / 0.3)
        frame = over(frame, year_layer(sh["year"], max(0, a)))
    c = cap_at(tt)
    if c is not None:
        frame = over(frame, c)
    ff.stdin.write(frame.tobytes())
    if i % 48 == 0:
        print(f"frame {i}/{N}", flush=True)
ff.stdin.close(); ff.wait()

# ------------------------------------------------------------------ audio: voice + ducked music + a few effects
inputs, filters, mix = [], [], []
for j, ln in enumerate(LINES):
    inputs += ["-i", str(HERE / "voice" / f"{ln['id']}.wav")]
    ms = int(ln["start"] * 1000)
    filters.append(f"[{j}:a]adelay={ms}|{ms},apad[v{j}]")
    mix.append(f"[v{j}]")
nv = len(LINES)
inputs += ["-i", str(HERE / "music" / CFG["music"])]
filters.append(f"{''.join(mix)}amix=inputs={nv}:normalize=0,atrim=0:{DUR},asplit=2[vo][sc]")
filters.append(f"[{nv}:a]atrim=0:{DUR},afade=t=in:d=0.8,afade=t=out:st={DUR - 2.0}:d=2.0,volume=0.55[mu]")
filters.append("[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=500[duck]")
sfx_lbl = []
for j, (f, at, vol) in enumerate(CFG["sfx"]):
    inputs += ["-i", str(HERE / "sfx" / f)]
    ms = int(at * 1000)
    filters.append(f"[{nv + 1 + j}:a]adelay={ms}|{ms},volume={vol},apad[s{j}]")
    sfx_lbl.append(f"[s{j}]")
filters.append(f"[vo][duck]{''.join(sfx_lbl)}amix=inputs={2 + len(sfx_lbl)}:normalize=0,atrim=0:{DUR},loudnorm=I=-15:TP=-2[out]")
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filters), "-map", "[out]",
                "-ar", "48000", str(HERE / "build" / "audio.wav")], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(HERE / "build" / "video.mp4"), "-i", str(HERE / "build" / "audio.wav"),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                str(HERE / "bmw-short.mp4")], check=True)
print("done", HERE / "bmw-short.mp4")
