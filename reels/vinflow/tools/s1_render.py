"""Opening: the camera lands on the showroom with the first hit of the music, then whips into a lateral move
along the row of cars. Writes clips/s1.mp4 (4.0 s, 30 fps, no audio)."""
import math, subprocess
from pathlib import Path
import numpy as np, cv2

HERE = Path(__file__).resolve().parent.parent
W, H, FPS, DUR = 1080, 1920, 30, 4.0

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

def expo_out(x):
    x = min(1, max(0, x)); return 1 - pow(2, -10 * x) if x < 1 else 1.0

def motion_blur(f, length):
    if length < 2:
        return f
    L = int(length) | 1
    k = np.zeros((1, L), np.float32); k[0, :] = 1.0 / L
    return cv2.filter2D(f, -1, k)

CUT = 2.0
def opening(t):
    # the camera lands on the first hit of the music: a fast push that settles, then keeps drifting
    z = 1.0 + 0.16 * (1 - expo_out(t / 0.9)) + 0.03 * (t / CUT)
    f = view(A, z, 0.0, 0.05)
    # whip out to the right in the last frames before the cut
    if t > CUT - 0.13:
        k = (t - (CUT - 0.13)) / 0.13
        f = np.roll(f, int(-260 * k * k), axis=1)
        f = motion_blur(f, 160 * k)
    return f

def dolly(t):
    # whip in from the right, then a steady lateral move along the row
    u = (t - CUT) / (DUR - CUT)
    ox = 0.8 - 1.2 * u
    f = view(B, 1.32 + 0.04 * u, ox, 0.05)
    if t < CUT + 0.13:
        k = 1 - (t - CUT) / 0.13
        f = np.roll(f, int(260 * k * k), axis=1)
        f = motion_blur(f, 160 * k)
    return f

out = HERE / "clips" / "s1.mp4"
out.parent.mkdir(exist_ok=True)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                       stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    t = i / FPS
    f = opening(t) if t < CUT else dolly(t)
    enc.stdin.write(f.tobytes())
enc.stdin.close(); enc.wait()
print("wrote", out)
