"""BMW-Short v2: ohne Stimme, schnell, auf den Beat geschnitten, Morph-Übergänge per optischem Fluss.
python tools/render_v2.py  ->  bmw-short-v2.mp4"""
import json, math, subprocess
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = Path(__file__).resolve().parent.parent
W, H, FPS, DUR = 1080, 1920, 24, 30.0
N = int(DUR * FPS)
CFG = json.load(open(HERE / "tools" / "edit_v2.json"))
MORPH = 0.62                      # seconds, centred on each cut

# ------------------------------------------------------------------ cuts on the beat
beats = json.loads(subprocess.check_output(["npx", "hyperframes", "beats", str(HERE / "music" / CFG["music"]), "--json"],
                                           stderr=subprocess.DEVNULL))["beatTimes"]
cuts = [beats[i] for i in CFG["cut_beats"]]
bounds = [0.0] + cuts + [DUR]
SHOTS = [{**s, "s": bounds[i], "e": bounds[i + 1]} for i, s in enumerate(CFG["shots"])]
assert len(SHOTS) == len(bounds) - 1, (len(SHOTS), len(bounds))
print("cuts:", [round(c, 2) for c in cuts])
for item in CFG["text"]:                      # text spans whole shots: from shot a to shot b
    item["s"] = SHOTS[item["shots"][0]]["s"] + (0.0 if item["shots"][0] == 0 else 0.2)
    item["e"] = SHOTS[item["shots"][1]]["e"] - 0.15

# ------------------------------------------------------------------ plates
def load(name):
    im = Image.open(HERE / "img" / name).convert("RGB")
    big = im.resize((int(W * 1.3), int(H * 1.3)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=2))
    return np.asarray(big)[:, :, ::-1].copy()
PLATES = {s["img"]: load(s["img"]) for s in SHOTS}

def ease(x):
    x = min(1, max(0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)

def camera(shot, tt):
    """continuous push-in through the whole shot, a little past both ends so the morph has motion on both sides"""
    span = shot["e"] - shot["s"] + MORPH
    u = (tt - (shot["s"] - MORPH / 2)) / span
    u = min(1.0, max(0.0, u))
    z = shot["zoom"][0] + (shot["zoom"][1] - shot["zoom"][0]) * u          # linear: the camera never stops
    (x0, y0), (x1, y1) = shot["pan"]
    cx, cy = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
    img = PLATES[shot["img"]]
    ih, iw = img.shape[:2]
    vw, vh = iw / z, ih / z
    mx, my = (iw - vw) / 2, (ih - vh) / 2
    left, top = mx + cx * mx, my + cy * my
    M = np.array([[W / vw, 0, -left * W / vw], [0, H / vh, -top * H / vh]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

# ------------------------------------------------------------------ morph: optical flow between the two frames at the cut
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
SMALL = (W // 4, H // 4)
gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)

def flow(a, b):
    ga = cv2.cvtColor(cv2.resize(a, SMALL, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, SMALL, interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    f = DIS.calc(ga, gb, None)
    f = cv2.GaussianBlur(f, (0, 0), 6)                                    # smooth, liquid motion, no tearing
    return cv2.resize(f, (W, H), interpolation=cv2.INTER_CUBIC) * 4.0

FLOWS = {}
for k in range(len(SHOTS) - 1):
    c = SHOTS[k]["e"]
    a, b = camera(SHOTS[k], c), camera(SHOTS[k + 1], c)
    FLOWS[k] = (flow(a, b), flow(b, a))
print("flows ready")

def morph(a, b, fab, fba, s):
    wa = cv2.remap(a, gx - s * fab[..., 0], gy - s * fab[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    wb = cv2.remap(b, gx - (1 - s) * fba[..., 0], gy - (1 - s) * fba[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.addWeighted(wa, 1 - s, wb, s, 0)

# ------------------------------------------------------------------ grade (same analog look as v1, a little cleaner)
x = np.arange(256) / 255.0
def curve(lift, gamma, gain):
    y = np.clip(lift + (gain - lift) * np.power(x, gamma), 0, 1)
    y = y - 0.025 * np.sin(2 * np.pi * y)
    return (np.clip(y, 0, 1) * 255).astype(np.uint8)
LUT = np.dstack([curve(0.04, 1.02, 0.97), curve(0.03, 1.0, 0.985), curve(0.02, 0.97, 1.0)]).reshape(1, 256, 3)
VIG = (1 - 0.26 * np.clip(((gx - W / 2) / (W * 0.62)) ** 2 + ((gy - H * 0.46) / (H * 0.62)) ** 2, 0, 1))[..., None]
RNG = np.random.default_rng(1916)
GRAIN = [RNG.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(12)]
def grade(f, i):
    ff = cv2.LUT(f, LUT).astype(np.float32)
    hi = np.clip((ff - 205) / 50, 0, 1)
    ff += cv2.GaussianBlur(hi, (0, 0), 16) * np.array([8, 22, 45], np.float32)
    ff *= VIG
    ff += cv2.resize(GRAIN[i % 12], (W, H))[..., None] * 3.5
    return np.clip(ff, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ clean type
F_LINE = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf", 58)
F_YEAR = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Thin.otf", 210)
LAYERS = {}
def text_layer(item):
    key = json.dumps(item, sort_keys=True)
    if key in LAYERS:
        return LAYERS[key]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for layer, fill in ((sh, (0, 0, 0, 215)), (im, (255, 255, 255, 255))):
        d = ImageDraw.Draw(layer)
        y = 1120
        if item.get("year"):
            tw = F_YEAR.getlength(item["year"])
            d.text(((W - tw) / 2, y - 250), item["year"], font=F_YEAR, fill=fill)
        for ln in item["text"].split("\n"):
            tw = F_LINE.getlength(ln)
            d.text(((W - tw) / 2, y), ln, font=F_LINE, fill=fill)
            y += 74
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    sh = Image.alpha_composite(sh, sh)
    out = np.asarray(Image.alpha_composite(sh, im)).astype(np.float32)
    LAYERS[key] = out
    return out

def over(frame, layer, a):
    al = layer[..., 3:4] / 255 * a
    return (frame * (1 - al) + layer[..., 2::-1] * al).astype(np.uint8)

GRAD = (np.clip((gy - 820) / 600, 0, 1) * 0.55)[..., None]

# ------------------------------------------------------------------ render
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", str(HERE / "build" / "v2.mp4")],
                       stdin=subprocess.PIPE)
for i in range(N):
    tt = i / FPS
    k = max(j for j, s in enumerate(SHOTS) if s["s"] <= tt)
    frame = camera(SHOTS[k], tt)
    # inside a morph window?  (before or after a cut)
    for c in (k - 1, k):
        if 0 <= c < len(SHOTS) - 1:
            cut = SHOTS[c]["e"]
            if abs(tt - cut) < MORPH / 2:
                s = ease((tt - (cut - MORPH / 2)) / MORPH)
                fab, fba = FLOWS[c]
                frame = morph(camera(SHOTS[c], tt), camera(SHOTS[c + 1], tt), fab, fba, s)
    frame = grade(frame, i)
    frame = (frame * (1 - GRAD)).astype(np.uint8)
    for item in CFG["text"]:
        if item["s"] <= tt < item["e"]:
            fade_in = 1 if item["s"] == 0 else min(1, (tt - item["s"]) / 0.35)   # the hook is there from frame 0
            a = fade_in * min(1, (item["e"] - tt) / 0.35)
            frame = over(frame, text_layer({"text": item["text"], "year": item.get("year")}), ease(a))
    enc.stdin.write(frame.tobytes())
    if i % 96 == 0:
        print(f"frame {i}/{N}", flush=True)
enc.stdin.close(); enc.wait()

# ------------------------------------------------------------------ audio: music only, a soft breath of air on a few morphs
inputs = ["-i", str(HERE / "music" / CFG["music"])]
flt = [f"[0:a]atrim=0:{DUR},afade=t=in:d=0.3,afade=t=out:st={DUR - 1.6}:d=1.6[m]"]
lbl = ["[m]"]
for j, c in enumerate(CFG["whoosh_on_cuts"]):
    inputs += ["-i", str(HERE / "sfx" / "whoosh-short.mp3")]
    ms = int((cuts[c] - 0.16) * 1000)
    flt.append(f"[{j + 1}:a]adelay={ms}|{ms},volume=0.28,apad[w{j}]"); lbl.append(f"[w{j}]")
flt.append(f"{''.join(lbl)}amix=inputs={len(lbl)}:normalize=0,atrim=0:{DUR},loudnorm=I=-14:TP=-1.5[out]")
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(flt), "-map", "[out]", "-ar", "48000",
                str(HERE / "build" / "v2.wav")], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(HERE / "build" / "v2.mp4"), "-i", str(HERE / "build" / "v2.wav"),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                str(HERE / "bmw-short-v2.mp4")], check=True)
print("done")
