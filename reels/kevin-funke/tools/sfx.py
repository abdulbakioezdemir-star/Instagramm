"""Sound design for 'Der Funke' – every effect sits on the frame of the motion it belongs to.
Writes audio/sfx.wav (48 kHz stereo, 18 s)."""
import subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent.parent
SR, DUR = 48000, 18.0
N = int(SR * DUR)
rng = np.random.default_rng(21)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR)
    if i >= N: return
    s = sig[: N - i] * g
    L[i:i + len(s)] += s * (1 - max(0, pan)); R[i:i + len(s)] += s * (1 + min(0, pan))

def lp(x, a):
    y = np.zeros_like(x); c = 0.0; a = np.broadcast_to(a, x.shape)
    for i in range(len(x)):
        c += a[i] * (x[i] - c); y[i] = c
    return y

def tt(d): return np.arange(int(d * SR)) / SR

def whoosh(d=0.6, up=True, g=1.0):
    t = tt(d); n = len(t)
    env = np.sin(np.pi * t / d) ** 2
    cut = np.linspace(0.02, 0.35, n) if up else np.linspace(0.35, 0.03, n)
    x = rng.normal(0, 1, n); y = lp(x, cut) - lp(x, cut * 0.25)
    return y * env * 0.9 * g

def shimmer(d=0.8, f0=2600, g=1.0):
    t = tt(d); x = np.zeros_like(t)
    for k, f in enumerate([f0, f0 * 1.26, f0 * 1.5, f0 * 2.0]):
        x += np.sin(2 * np.pi * f * t + k) * (0.6 + 0.4 * np.sin(2 * np.pi * (7 + k) * t))
    return x * np.exp(-t * 3.5) * np.minimum(1, t / 0.02) * 0.06 * g

def ping(f=1760, d=0.9, g=1.0):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 6) * np.minimum(1, t / 0.003) * 0.25 * g

def thud(g=1.0):
    t = tt(0.7)
    body = np.sin(2 * np.pi * np.cumsum(42 + 60 * np.exp(-t * 25)) / SR) * np.exp(-t * 6)
    hit = lp(rng.normal(0, 1, len(t)), 0.08) * np.exp(-t * 30)
    return (0.9 * body + 0.6 * hit) * g

def crackle(d=0.9, g=1.0):
    t = tt(d); x = np.zeros_like(t)
    for _ in range(70):
        p = rng.integers(0, len(t) - 200)
        x[p:p + 120] += rng.normal(0, 1, 120) * np.exp(-np.arange(120) / 18) * rng.uniform(.3, 1)
    x = x - lp(x, 0.2)
    return x * np.linspace(1, 0.3, len(t)) * 0.35 * g

def riser(d=1.3, g=1.0):
    t = tt(d); n = len(t)
    x = rng.normal(0, 1, n); y = lp(x, np.linspace(0.02, 0.5, n))
    tone = np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, n)) / SR) * 0.25
    return (y + tone) * (t / d) ** 2.2 * 0.5 * g

def impact(g=1.0):
    t = tt(2.2)
    boom = np.sin(2 * np.pi * np.cumsum(34 + 80 * np.exp(-t * 14)) / SR) * np.exp(-t * 1.8)
    noise = lp(rng.normal(0, 1, len(t)), 0.25) * np.exp(-t * 5)
    return (1.1 * boom + 0.5 * noise) * g

def shatter(g=1.0):
    t = tt(1.2); x = np.zeros_like(t)
    for _ in range(90):
        p = rng.integers(0, int(len(t) * 0.7)); f = rng.uniform(2500, 7000); m = rng.integers(400, 2500)
        seg = np.sin(2 * np.pi * f * np.arange(m) / SR) * np.exp(-np.arange(m) / (m / 5))
        x[p:p + m] += seg[: len(x) - p] * rng.uniform(.1, .5)
    return x * np.exp(-t * 2.5) * 0.35 * g

def pluck(f, g=1.0):
    t = tt(1.0)
    x = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (4 + 3 * k)) / k for k in (1, 2, 3, 4))
    return x * np.minimum(1, t / 0.004) * 0.32 * g

def chime(g=1.0):
    t = tt(2.2)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((880, 1.6), (1320, 2.0), (1760, 2.6), (2637, 3.4)))
    return x * np.minimum(1, t / 0.004) * 0.12 * g

# ---------------------------------------------------------------- events (seconds, matching tools/build.py)
add(whoosh(1.0, True, .5), 0.0, -0.4); add(shimmer(1.0, 3000, .7), 0.02, -0.3)       # spark writes line 1
add(whoosh(1.0, True, .5), 1.04, -0.2); add(shimmer(1.0, 3200, .7), 1.05, 0.2)       # line 2
add(whoosh(0.45, False, .6), 2.12, 0.3)                                               # spark flies to the full stop
add(ping(1760, .9, 1.0), 2.88, 0.3); add(ping(2637, .7, .4), 2.9, 0.3)                 # it becomes the full stop
add(whoosh(0.4, False, .5), 3.18)                                                      # drops down
for t in (3.52, 4.38, 5.40):                                                           # slabs fall
    add(whoosh(0.32, False, .55), t - 0.32)
    add(thud(1.0 if t < 5 else 1.25), t - 0.01)
add(crackle(0.9, 1.0), 6.28); add(shimmer(0.9, 2200, .8), 6.3)                          # cracks of light
add(ping(1320, .8, .5), 7.32)                                                          # "genügt"
add(riser(1.3, 1.0), 6.58)                                                             # tension ...
# ... silence 7.88 – 8.2 (nothing placed here)
add(impact(1.2), 8.19); add(shatter(1.0), 8.2); add(shimmer(1.6, 2400, 1.4), 8.22)       # IGNITION
add(whoosh(0.5, True, .45), 9.25)                                                      # Potenzial leaves
add(pluck(329.6), 9.74); add(pluck(392.0), 10.68); add(pluck(493.9, 1.1), 11.68)       # climbing notes E-G-B
for t in (9.56, 10.5, 11.5):
    add(whoosh(0.25, True, .3), t)
add(whoosh(0.4, True, .5), 12.3)                                                       # spark shoots up
add(shimmer(0.9, 2800, 1.0), 12.6)                                                     # draws the ring
add(chime(1.0), 13.0)                                                                  # logo
add(ping(2093, .6, .5), 13.74)                                                         # lands as the line
add(shimmer(0.8, 3000, .5), 15.3)
add(ping(1760, .8, .45), 17.62)                                                        # spark returns (loop)

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.0); mix /= np.max(np.abs(mix)) + 1e-9; mix *= 0.9
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", str(HERE / "audio" / "sfx.wav")],
               input=(mix * 32767).astype("<i2").tobytes(), check=True)
print("wrote audio/sfx.wav")
