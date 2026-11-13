"""Animated silk background: flowing ribbons that sleep (dark, muted) until the ignition at 10 s,
then a light wave runs through them and they glow gold. Writes clips/silk.mp4 (1080x1920, 30 fps, 22 s)."""
import math, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent.parent
W, H, FPS, DUR = 360, 640, 30, 22.0
IGN = 10.0
N = int(DUR * FPS)

x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
y = np.linspace(0, H / W, H, dtype=np.float32)[:, None]
cx, cy = 0.5, (H / W) * 0.57          # where the spark sits
r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

def smooth(a, b, v):
    t = np.clip((v - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

# ribbons: (base height, amplitude, frequency, speed, phase, width, slope, weight)
RIB = [
    (0.35, 0.10, 2.2, 0.16, 0.0, 0.070, 0.30, 1.00),
    (0.62, 0.12, 1.7, -0.12, 1.7, 0.095, 0.22, 0.85),
    (0.90, 0.09, 2.6, 0.20, 3.1, 0.060, 0.34, 0.90),
    (1.18, 0.13, 1.5, -0.14, 4.4, 0.110, 0.26, 0.80),
    (1.42, 0.10, 2.0, 0.18, 5.6, 0.075, 0.30, 0.95),
    (1.68, 0.08, 2.9, -0.22, 2.3, 0.055, 0.20, 0.70),
]

def frame(t):
    sp = 1.0 + 0.6 * smooth(IGN - 0.2, IGN + 1.5, t)          # flow speeds up after the ignition
    tt = t * sp if t < IGN else IGN + (t - IGN) * 1.6
    yw = y + 0.045 * np.sin(3.1 * x + 0.35 * tt) + 0.03 * np.sin(5.7 * x - 0.22 * tt + 2.2 * y)
    body = np.zeros((H, W), np.float32)
    sheen = np.zeros((H, W), np.float32)
    for b, a, f, s, p, w, sl, wt in RIB:
        c = b + sl * (x - 0.5) + a * np.sin(f * 2 * math.pi * x * 0.5 + s * tt + p) + 0.02 * np.sin(7 * x + 0.5 * tt + p)
        ww = w * (1 + 0.55 * np.sin(1.3 * 2 * math.pi * x + 0.2 * tt + p * 1.7))
        d = (yw - c) / ww
        body += wt * np.exp(-d * d)
        e = (yw - c - 0.35 * ww) / (0.16 * ww)                    # thin bright edge = silk highlight
        sheen += wt * np.exp(-e * e)
    # state: 0 = dormant, 1 = ignited
    s = smooth(IGN - 0.05, IGN + 1.2, t)
    calm = smooth(16.6, 18.5, t)                                # settle under the logo
    wave = 0.0
    if t >= IGN:
        rad = (t - IGN) * 1.25
        wave = np.exp(-((r - rad) / 0.07) ** 2) * math.exp(-(t - IGN) * 0.9)
    lum_body = body * (0.10 + 0.19 * s - 0.05 * calm)
    lum_sheen = sheen * (0.10 + 0.30 * s - 0.08 * calm)
    glow = np.exp(-(r / (0.55 + 0.25 * s)) ** 2) * (0.05 + 0.18 * s)
    L = lum_body + lum_sheen + glow
    # keep the text band a little calmer so white type always reads
    band = 1 - 0.38 * np.exp(-((y - (H / W) * 0.5) / 0.32) ** 2)
    L = L * band
    # colour: dormant = smoky bronze, ignited = gold
    dorm = np.array([0.50, 0.45, 0.44], np.float32)           # BGR
    gold = np.array([0.30, 0.66, 1.00], np.float32)
    col = dorm * (1 - s) + gold * s
    base = np.array([0.020, 0.018, 0.022], np.float32) * (1 - s) + np.array([0.008, 0.014, 0.026], np.float32) * s
    img = base[None, None, :] + L[..., None] * col[None, None, :]
    if t >= IGN:
        img = img + (wave * 1.1)[..., None] * gold[None, None, :]
    hi = np.clip(L - 0.55, 0, None)[..., None]                  # hottest parts tend to white
    img = img + hi * np.array([0.6, 0.75, 0.85], np.float32)
    img = 1 - np.exp(-img * 1.6)                                # soft filmic roll-off
    return img

out = HERE / "clips" / "silk.mp4"
out.parent.mkdir(exist_ok=True)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr48le", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-vf", "scale=1080:1920:flags=bicubic,gblur=sigma=1.2,noise=alls=3:allf=t",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                       stdin=subprocess.PIPE)
rng = np.random.default_rng(3)
for i in range(N):
    f = frame(i / FPS)
    f = np.clip(f * 65535 + rng.normal(0, 90, f.shape), 0, 65535).astype("<u2")
    enc.stdin.write(f.tobytes())
enc.stdin.close(); enc.wait()
print("wrote", out)
