"""Stadium background: dark until the ignition, then the floodlights come on bank by bank.
Writes clips/stadium.mp4 (1080x1920, 30 fps, 24.5 s)."""
import math, subprocess
from pathlib import Path
import numpy as np, cv2
HERE = Path(__file__).resolve().parent.parent
W, H, FPS, DUR, IGN = 1080, 1920, 30, 24.5, 13.12
src = cv2.imread(str(HERE / "img" / "stadium_a_42.png")).astype(np.float32) / 255
big = cv2.resize(src, (int(W * 1.18), int(H * 1.18)), interpolation=cv2.INTER_LANCZOS4)
big = cv2.GaussianBlur(big, (0, 0), 1.2)                       # soft depth, hides upscale artefacts
# grade: pull the green cast towards a warm night look
b, g, r = cv2.split(big)
g2 = g * 0.80 + r * 0.10 + b * 0.10
r2 = r * 0.95 + g * 0.12
b2 = b * 0.85 + g * 0.05
lit = cv2.merge([b2, g2, r2])
gry = lit.mean(axis=2, keepdims=True)
lit = np.clip((gry + (lit - gry) * 0.5) * np.array([0.82, 0.95, 1.12], np.float32), 0, 1)
lum = lit.max(axis=2)
lamps = np.clip((lum - 0.72) / 0.28, 0, 1)
lamps = cv2.GaussianBlur(lamps, (0, 0), 3)[..., None]
glow = cv2.GaussianBlur(lamps[..., 0], (0, 0), 40)[..., None] * 1.6
warm = np.array([0.55, 0.80, 1.0], np.float32)               # BGR warm light
grey = lit.mean(axis=2, keepdims=True)
dark = (grey * 0.5 + lit * 0.5) * 0.16 * np.array([1.05, 0.95, 0.9], np.float32)
lit_full = np.clip(lit * 0.9 + glow * warm * 0.35, 0, 1)
ih, iw = big.shape[:2]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = (1 - 0.55 * np.clip(((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .5) / (H * .7)) ** 2, 0, 1))[..., None]

def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)

def lights(t):
    """0 = off, 1 = on. three banks flicker on, like a real stadium"""
    if t < IGN: return 0.0, 0.0
    d = t - IGN
    steps = [(0.00, .45), (0.06, .15), (0.12, .6), (0.20, .35), (0.30, .8), (0.40, .65), (0.55, 1.0)]
    v = 0
    for s, val in steps:
        if d >= s: v = val
    flash = math.exp(-d * 3.5)
    return v, flash

def view(img, z, oy):
    vw, vh = iw / z, ih / z
    cx, cy = iw / 2, ih / 2 + oy
    s = W / vw
    M = np.array([[s, 0, W / 2 - cx * s], [0, s, H / 2 - cy * s]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

out = HERE / "clips" / "stadium.mp4"
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
rng = np.random.default_rng(1)
for i in range(int(DUR * FPS)):
    t = i / FPS
    z = 1.0 + 0.10 * (t / DUR) + 0.04 * ease((t - IGN) / 2.0)           # slow push, a small lift when the lights hit
    on, flash = lights(t)
    pre = 0.05 * ease(t / 1.5) + 0.04 * ease((t - 10) / 3) if t < IGN else 0
    base = dark * (1 + pre * 4) + (lit_full - dark) * on
    base = base + glow * warm * flash * 0.9
    f = view(base.astype(np.float32), z, -20 * (t / DUR))
    f = f * vig
    f = f + rng.normal(0, 0.008, (H // 4, W // 4, 1)).repeat(4, 0).repeat(4, 1).astype(np.float32)
    enc.stdin.write((np.clip(f, 0, 1) * 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print("wrote", out)
