"""Sound design for Kevin Neon (Stil-Referenz 3) – every effect sits on the frame of the motion it belongs to.
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
    return y * env * 0.9 * g * 0.316          # whooshes 10 dB down (customer request)

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


def tick(g=1.0):
    t = tt(0.03); x = rng.normal(0, 1, len(t)); x = x - lp(x, 0.5)
    return x * np.exp(-t * 300) * 0.25 * g

def buzz(d=0.35, g=1.0):
    """neon tube switching on: 100 Hz hum + crackle, flickering"""
    t = tt(d); hum = np.sign(np.sin(2 * np.pi * 100 * t)) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.5
    hum = lp(hum, 0.08); fl = (np.sin(2 * np.pi * 23 * t) > -0.3).astype(float)
    cr = rng.normal(0, 1, len(t)) * (rng.uniform(0, 1, len(t)) > 0.995) * 3
    return (hum * fl * 0.35 + cr * 0.2) * np.exp(-t * 4) * np.minimum(1, t / 0.005) * g

def clank(g=1.0):
    """metal bars landing"""
    t = tt(1.2); x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dd) for f, dd in ((310, 5), (742, 7), (1287, 9), (2210, 12), (3330, 16)))
    hit = rng.normal(0, 1, len(t)) * np.exp(-t * 60)
    return (x * 0.18 + hit * 0.3) * np.minimum(1, t / 0.001) * g

def boom(g=1.0):
    t = tt(1.6)
    return np.sin(2 * np.pi * np.cumsum(40 + 50 * np.exp(-t * 18)) / SR) * np.exp(-t * 2.5) * 0.8 * g

# ---------------------------------------------------------------- events (seconds, matching tools/build.py)
add(whoosh(0.6, True, .5), 0.0, -0.3)                                                  # phone flies in
add(whoosh(0.5, True, .45), 0.5, 0.3)                                                  # camera to the bio
add(whoosh(0.9, False, .35), 1.02, -0.2)                                               # pan over line 2
add(whoosh(0.35, True, .7), 2.05)                                                      # dive into the profile picture
add(shimmer(0.9, 2600, 1.0), 2.32); add(ping(1760, .7, .5), 2.34)                      # glowing icon + rings
for i in range(8): add(tick(0.6), 2.48 + i * 0.06, (-1) ** i * 0.5)                    # letters circling
add(ping(2093, .5, .4), 3.0)                                                           # they lock into "Ein Funke"
add(whoosh(0.25, False, .6), 3.22)                                                     # sucked to the centre
add(thud(0.6), 3.44)                                                                   # grey world
for i in range(6): add(tick(0.8), 3.42 + i * 0.035)                                    # D-r-u-c-k tumble in
add(thud(0.7), 3.52)
add(whoosh(0.3, True, .6), 4.26, 0.4); add(thud(0.8), 4.37)                             # Zweifel box
add(whoosh(0.3, True, .7), 5.14); add(whoosh(0.3, False, .6), 5.30, -0.4); add(thud(1.0), 5.40)   # Angst
add(thud(0.9), 5.78)                                                                   # spotlight clunk
add(whoosh(0.25, True, .5), 6.2, -0.4); add(whoosh(0.25, True, .5), 6.76, 0.4); add(thud(0.5), 7.27)
add(riser(1.2, 0.7), 6.68)                                                             # tension, then silence 7.88-8.2
add(impact(1.1), 8.19); add(buzz(0.5, 1.0), 8.2); add(shimmer(1.2, 2400, 1.0), 8.22)   # neon POTENZIAL
add(buzz(0.25, 0.6), 8.64)                                                             # flicker
add(whoosh(0.3, True, .4), 8.76); add(buzz(0.25, 0.6), 8.84)                            # entfachen
for t, f in ((9.76, 329.6), (10.70, 392.0), (11.70, 493.9)):
    add(whoosh(0.3, True, .35), t - 0.24); add(buzz(0.3, 0.6), t - 0.04); add(pluck(f, 0.9), t)
add(clank(1.0), 12.07)                                                                 # bars slam down
add(whoosh(0.4, True, .6), 12.2); add(shatter(0.6), 12.4)                              # bars break open
add(boom(1.0), 12.52); add(chime(0.9), 12.58)                                          # logo
for i in range(11): add(tick(0.35), 14.2 + i * 0.055)                                  # MENTAL COACH letters
add(shimmer(0.8, 3000, .5), 15.3)
add(whoosh(0.5, True, .4), 17.45)                                                      # back to blue (loop)

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.0); mix /= np.max(np.abs(mix)) + 1e-9; mix *= 0.9
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", str(HERE / "audio" / "sfx.wav")],
               input=(mix * 32767).astype("<i2").tobytes(), check=True)
print("wrote audio/sfx.wav")
