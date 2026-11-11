"""BMW-Edit v3 im Stil der Referenz: dunkel, Licht-Akzente, harte kurze Übergänge auf den Beat.
Intro: Scheinwerfer-Kontur zeichnet sich als Lichtlinie, Auto flackert herein, Drop bei 4,0 s.
Übergänge (2-3 Frames): Whip mit Bewegungsunschärfe, Zoom-Blur, Rotations-Whip, Halbton-Blitz, Weißblitz.
python tools/render_v3.py -> bmw-edit-v3.mp4"""
import json, math, os, subprocess
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent.parent
V3 = HERE / "v3"
W, H, FPS, DUR = 1080, 1920, 24, 30.0
N = int(float(os.environ.get("V3_SECONDS", DUR)) * FPS)
CFG = json.load(open(os.environ.get("V3_EDL", HERE / "tools" / "edit_v3.json")))
MUSIC, MS = V3 / "music" / CFG["music"], CFG["music_start"]
DROP = CFG["drop"]

beats = json.loads(subprocess.check_output(["npx", "hyperframes", "beats", str(MUSIC), "--json"], stderr=subprocess.DEVNULL))["beatTimes"]
beats = [b - MS for b in beats if b - MS >= DROP - 0.05]
cuts = [beats[i] for i in range(0, len(beats), CFG["beats_per_shot"]) if beats[i] < DUR - 0.3]
print("drop", DROP, "cuts", len(cuts), [round(c, 2) for c in cuts[:6]], "…")

# ------------------------------------------------------------------ plates
def load(name):
    im = cv2.imread(str(V3 / "img" / name))
    return cv2.resize(im, (int(W * 1.25), int(H * 1.25)), interpolation=cv2.INTER_LANCZOS4)
PL = {}
def plate(name):
    if name not in PL:
        PL[name] = load(name)
    return PL[name]

def view(name, zoom, ox=0.0, oy=0.0, rot=0.0, dx=0.0, dy=0.0):
    """frame from the 1.25x plate: zoom 1 = whole plate; ox/oy pan in -1..1 of the free margin; rot degrees; dx/dy pixel shift"""
    img = plate(name)
    ih, iw = img.shape[:2]
    vw, vh = iw / zoom, ih / zoom
    cx = iw / 2 + ox * (iw - vw) / 2
    cy = ih / 2 + oy * (ih - vh) / 2
    s = W / vw
    M = cv2.getRotationMatrix2D((cx, cy), rot, s)
    M[0, 2] += W / 2 - cx + dx
    M[1, 2] += H / 2 - cy + dy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ------------------------------------------------------------------ effects
def motion_blur(f, length, angle_deg):
    if length < 2:
        return f
    small = cv2.resize(f, (W // 2, H // 2))
    L = max(3, int(length / 2) | 1)
    k = np.zeros((L, L), np.float32); k[L // 2, :] = 1.0 / L
    R = cv2.getRotationMatrix2D((L / 2 - 0.5, L / 2 - 0.5), angle_deg, 1.0)
    k = cv2.warpAffine(k, R, (L, L)); k /= max(k.sum(), 1e-6)
    return cv2.resize(cv2.filter2D(small, -1, k), (W, H))

def zoom_blur(name, z, ox, oy, strength):
    acc = np.zeros((H, W, 3), np.float32)
    n = 6
    for i in range(n):
        acc += view(name, z * (1 + strength * i / n), ox, oy).astype(np.float32)
    return (acc / n).astype(np.uint8)

def spin_blur(name, z, ox, oy, rot, spread):
    acc = np.zeros((H, W, 3), np.float32)
    n = 6
    for i in range(n):
        acc += view(name, z, ox, oy, rot + spread * (i / (n - 1) - 0.5)).astype(np.float32)
    return (acc / n).astype(np.uint8)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
DOTS = (np.sin(xx * 2 * np.pi / 14) * np.sin(yy * 2 * np.pi / 14) + 1) / 2          # halftone screen
def halftone(f):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    g = cv2.equalizeHist((g * 255).astype(np.uint8)).astype(np.float32) / 255
    out = (g > DOTS).astype(np.float32) * 235 + 10
    return cv2.merge([out, out, out]).astype(np.uint8)

def interlace(f, amount):
    m = np.ones((H, 1, 1), np.float32); m[::3] = 1 - amount; m[1::3] = 1 - amount * 0.5
    return (f.astype(np.float32) * m).astype(np.uint8)

# ------------------------------------------------------------------ the look: near monochrome, colour only in the lights
x = np.arange(256) / 255.0
tone = np.clip((x - 0.06) / 0.9, 0, 1); tone = tone * tone * (3 - 2 * tone) * 0.55 + tone * 0.45     # crushed blacks, S-curve
TLUT = (np.clip(tone, 0, 1) * 255).astype(np.uint8)
VIG = (1 - 0.42 * np.clip(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H * 0.47) / (H * 0.6)) ** 2, 0, 1))[..., None]
RNG = np.random.default_rng(8)
GRAIN = [RNG.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(10)]

def look(f, i):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    red = ((h < 14) | (h > 165)).astype(np.float32)              # taillights keep their red
    hot = np.clip((v - 170) / 60, 0, 1)                          # highlights may stay a cool white-blue
    keep = np.clip(red * 1.15 + hot * 0.25, 0, 1.2)
    hsv[..., 1] = s * (0.12 + 0.95 * keep)
    f = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    f = cv2.LUT(f, TLUT)
    ff = f.astype(np.float32)
    ff[..., 0] *= 1.04                                            # a cold cast in the steel
    blur = cv2.GaussianBlur(ff, (0, 0), 2.0)
    ff = ff + 0.6 * (ff - blur)                                   # crisp
    ff *= VIG
    ff += cv2.resize(GRAIN[i % 10], (W, H))[..., None] * 3.0
    return np.clip(ff, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ intro: the headlight drawn as a line of light
INTRO = CFG["intro"]
INTRO_CACHE = {}
def intro_frame(t):
    name = INTRO["img"]
    base = view(name, INTRO["zoom"], INTRO["ox"], INTRO["oy"])
    g = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    LINE = INTRO_CACHE.get("line")
    if LINE is None:
        # only the outline of the brightest lights: a thin, clean line
        hot = (cv2.GaussianBlur(g, (7, 7), 0) > np.percentile(g, 98.2)).astype(np.uint8) * 255
        hot = cv2.morphologyEx(hot, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        cnts, _ = cv2.findContours(hot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:6]
        canvas = np.zeros((H, W), np.uint8)
        cv2.drawContours(canvas, cnts, -1, 255, 3, lineType=cv2.LINE_AA)
        LINE = INTRO_CACHE["line"] = canvas.astype(np.float32) / 255
    line = LINE
    out = np.zeros((H, W, 3), np.float32)
    if t < 0.5:
        return out.astype(np.uint8)
    # the trace sweeps left to right, with a glow
    p = min(1, (t - 0.5) / 1.6)
    sweep = np.clip((p * (W + 300) - xx) / 300, 0, 1)
    tr = line * sweep
    glow = cv2.GaussianBlur(tr, (0, 0), 7) * 1.6 + cv2.GaussianBlur(tr, (0, 0), 22) * 1.2 + tr
    out += np.dstack([glow * 255, glow * 245, glow * 230])
    # the car flickers in with interlace lines
    if t > 2.2:
        a = min(1, (t - 2.2) / 1.2)
        flick = 0.55 + 0.45 * (math.sin(t * 60) > 0)
        car = interlace(base, (1 - a) * 0.8).astype(np.float32) * a * (flick if a < 1 else 1)
        out = np.maximum(out * (1 - a * 0.6), car)
    return np.clip(out, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ the cut list
SHOTS = CFG["shots"]
assert len(SHOTS) >= len(cuts), (len(SHOTS), len(cuts))
bounds = cuts + [DUR]
def shot_at(t):
    k = max(j for j, c in enumerate(cuts) if c <= t)
    return k, SHOTS[k], t - cuts[k], bounds[k + 1] - t

TF = 3 / FPS          # transition half-length: 3 frames each side
def landing(sh, u):
    """the shot lands: a little zoom recoil and a decaying shake, then a slow drift"""
    z = sh["z"] * (1 + 0.07 * math.exp(-u / 0.09)) + 0.02 * u
    sx = 7 * math.exp(-u / 0.07) * math.sin(u * 90)
    sy = 5 * math.exp(-u / 0.07) * math.cos(u * 77)
    return z, sx, sy

def shot_frame(k_idx, sh, u, rem):
    z, sx, sy = landing(sh, u)
    ox, oy = sh.get("ox", 0), sh.get("oy", 0) + 0.15 * u * sh.get("drift", 0)
    tin = sh["tin"]
    # incoming effect (first frames)
    if u < TF:
        k = 1 - u / TF
        if tin == "whip":
            return motion_blur(view(sh["img"], z, ox, oy, dx=-260 * k), 180 * k, 0)
        if tin == "zoom":
            return zoom_blur(sh["img"], z * (1 + 0.25 * k), ox, oy, 0.18 * k)
        if tin == "spin":
            return spin_blur(sh["img"], z * (1 + 0.1 * k), ox, oy, -20 * k, 24 * k)
        if tin == "halftone" and u < 2 / FPS:
            return halftone(view(sh["img"], z, ox, oy))
        if tin == "flash" and u < 1 / FPS:
            return np.full((H, W, 3), 245, np.uint8)
        if tin == "glitch" and u < 2 / FPS:
            return interlace(view(sh["img"], z, ox, oy, dx=30), 0.7)
    # outgoing effect (last frames), matching the next shot's entry
    nxt = SHOTS[k_idx + 1]["tin"] if k_idx + 1 < len(cuts) else None
    if rem < TF and nxt:
        k = 1 - rem / TF
        if nxt == "whip":
            return motion_blur(view(sh["img"], z, ox, oy, dx=260 * k), 180 * k, 0)
        if nxt == "zoom":
            return zoom_blur(sh["img"], z * (1 + 0.3 * k), ox, oy, 0.2 * k)
        if nxt == "spin":
            return spin_blur(sh["img"], z, ox, oy, 20 * k, 24 * k)
    return view(sh["img"], z, ox, oy, dx=sx, dy=sy)

# ------------------------------------------------------------------ end card
FONT = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Thin.otf", 64)
def end_text(f, a):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    txt = CFG["end_text"]
    spaced = " ".join(txt)
    tw = FONT.getlength(spaced)
    d.text(((W - tw) / 2, 1180), spaced, font=FONT, fill=(255, 255, 255, int(230 * a)))
    l = np.asarray(im).astype(np.float32)
    al = l[..., 3:4] / 255
    return (f * (1 - al) + l[..., 2::-1] * al).astype(np.uint8)

# ------------------------------------------------------------------ render
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", str(HERE / "build" / "v3.mp4")],
                       stdin=subprocess.PIPE)
for i in range(N):
    t = i / FPS
    if t < DROP:
        f = intro_frame(t)
        if t > DROP - TF:                                   # into the drop: a white flash
            f = cv2.addWeighted(f, 0.3, np.full_like(f, 245), 0.7, 0)
    else:
        k, sh, u, rem = shot_at(t)
        f = shot_frame(k, sh, u, rem)
    f = look(f, i)
    if t > DUR - 2.2:
        f = end_text(f, min(1, (t - (DUR - 2.2)) / 0.5))
    if t > DUR - 0.6:
        f = (f.astype(np.float32) * max(0, (DUR - t) / 0.6)).astype(np.uint8)
    enc.stdin.write(f.tobytes())
    if i % 96 == 0:
        print(f"frame {i}/{N}", flush=True)
enc.stdin.close(); enc.wait()

# ------------------------------------------------------------------ audio
inputs = ["-ss", str(MS), "-i", str(MUSIC)]
flt = [f"[0:a]atrim=0:{DUR},afade=t=out:st={DUR - 1.0}:d=1.0[m]"]
lbl = ["[m]"]
for j, c in enumerate(cuts):
    if SHOTS[j]["tin"] in ("whip", "spin"):
        inputs += ["-i", str(HERE / "sfx" / "whoosh-short.mp3")]
        ms = int(max(0, c - 0.16) * 1000)
        flt.append(f"[{len(lbl)}:a]adelay={ms}|{ms},volume=0.35,apad[w{j}]"); lbl.append(f"[w{j}]")
flt.append(f"{''.join(lbl)}amix=inputs={len(lbl)}:normalize=0,atrim=0:{DUR},loudnorm=I=-13:TP=-1.5[out]")
subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(flt), "-map", "[out]", "-ar", "48000",
                str(HERE / "build" / "v3.wav")], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(HERE / "build" / "v3.mp4"), "-i", str(HERE / "build" / "v3.wav"),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                str(HERE / "bmw-edit-v3.mp4")], check=True)
print("done")
