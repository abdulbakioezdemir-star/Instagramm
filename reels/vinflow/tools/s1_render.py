"""Opening shot: black -> the showroom's light strips switch on one after another -> the room comes up,
while the camera dollies in; then a cut on motion into a lateral move along the row of cars.
Writes clips/s1.mp4 (4.6 s, 30 fps, no audio)."""
import math, subprocess
from pathlib import Path
import numpy as np, cv2

HERE = Path(__file__).resolve().parent.parent
W, H, FPS, DUR = 1080, 1920, 30, 4.6
CUT = 2.95

def plate(name, scale=1.3):
    im = cv2.imread(str(HERE / "img" / name))
    return cv2.resize(im, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_LANCZOS4)

A, B = plate("shot1_1.png"), plate("shot2_1.png")

def view(img, z, ox=0.0, oy=0.0):
    ih, iw = img.shape[:2]
    vw, vh = iw / z, ih / z
    cx, cy = iw / 2 + ox * (iw - vw) / 2, ih / 2 + oy * (ih - vh) / 2
    s = W / vw
    M = np.array([[s, 0, W / 2 - cx * s], [0, s, H / 2 - cy * s]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def ease(x):
    x = min(1, max(0, x)); return x * x * (3 - 2 * x)

yy = np.mgrid[0:H, 0:W][0].astype(np.float32)

def lights_on(t):
    # one continuous dolly-in through the whole reveal
    u = ease((t - 0.0) / CUT)
    frame = view(A, 1.0 + 0.11 * u, 0.0, -0.05 + 0.08 * u).astype(np.float32)
    g = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    lamps = np.clip((g - 200) / 45, 0, 1)                                 # the light strips and their reflections
    # the strips switch on from the far ceiling to the camera
    p = (t - 1.15) / 0.75
    sweep = np.clip((p * (H + 500) - yy) / 500, 0, 1)
    # a fluorescent start: the first strips blink twice
    blink = 1.0
    if 1.15 < t < 1.42:
        blink = 0.25 if int((t - 1.15) * 30) % 3 == 1 else 1.0
    lamp_layer = frame * (lamps * sweep * blink)[..., None]
    glow = cv2.GaussianBlur(lamp_layer, (0, 0), 14) * 0.9
    ambient = 0.05 + 0.95 * ease((t - 1.75) / 1.0)                        # the room fills with light
    out = frame * ambient + (lamp_layer + glow) * (1 - ambient * 0.85)
    if t < 1.15:
        out *= 0.0                                                         # pure black before the lights
    return np.clip(out, 0, 255).astype(np.uint8)

def dolly(t):
    # lateral move along the row, already moving at the cut, still moving at the end
    u = (t - CUT) / (DUR - CUT)
    ox = 0.75 - 1.1 * u
    return view(B, 1.32 + 0.05 * u, ox, 0.05)

out = HERE / "clips" / "s1.mp4"
out.parent.mkdir(exist_ok=True)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                       stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    t = i / FPS
    f = lights_on(t) if t < CUT else dolly(t)
    enc.stdin.write(f.tobytes())
enc.stdin.close(); enc.wait()
print("wrote", out)
