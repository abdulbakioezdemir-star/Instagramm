"""Dark trap instrumental, ~136 BPM, F minor, for the Slate-style Kevin reel (no voice).
Beat grid b(n) = T0 + n*B: grey world b13 (5.85), neon b19 (8.5), bars b26 (11.59), logo b28 (12.475).
Writes audio/beat.wav (16.4 s). Kevin 3D: cube at b10.5, spark ending from b26."""
import subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent.parent
SR, DUR = 48000, 16.4
N = int(SR * DUR)
B = 2.65 / 6                       # one beat
T0 = 5.85 - 13 * B
def bt(n): return T0 + n * B
S = B / 4                          # 16th
rng = np.random.default_rng(5)
L = np.zeros(N); R = np.zeros(N)


def add(sig, t, pan=0.0, g=1.0):
    i = int(round(t * SR))
    if i >= N or i < 0: return
    s = sig[: N - i] * g
    L[i:i + len(s)] += s * (1 - max(0, pan)); R[i:i + len(s)] += s * (1 + min(0, pan))


def tt(d): return np.arange(int(d * SR)) / SR


def lp(x, a):
    y = np.zeros_like(x); c = 0.0; a = np.broadcast_to(a, x.shape)
    for i in range(len(x)):
        c += a[i] * (x[i] - c); y[i] = c
    return y


def b808(f, d=0.9, g=1.0):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(f * (1 + 1.2 * np.exp(-t * 40))) / SR
    x = np.tanh(2.2 * np.sin(ph)) * np.exp(-t * 2.2) * np.minimum(1, t / 0.003)
    return x * np.minimum(1, (d - t) / 0.03) * 0.55 * g


def kick(g=1.0):
    t = tt(0.25)
    return np.sin(2 * np.pi * np.cumsum(55 + 160 * np.exp(-t * 45)) / SR) * np.exp(-t * 14) * 0.7 * g


def clap(g=1.0):
    t = tt(0.35); n = len(t); x = rng.normal(0, 1, n)
    env = sum(np.exp(-np.maximum(t - o, 0) * 60) * (t >= o) for o in (0, 0.011, 0.022)) + 0.5 * np.exp(-t * 12)
    x = x - lp(x, 0.15)
    return x * env * 0.32 * g


def hat(g=1.0, d=0.04):
    t = tt(d); x = rng.normal(0, 1, len(t)); x = x - lp(x, 0.6)
    return x * np.exp(-t * 110) * 0.16 * g


def bell(f, g=1.0):
    t = tt(1.4)
    x = np.sin(2 * np.pi * f * t + 1.8 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t * 6)) * np.exp(-t * 3.2)
    return x * np.minimum(1, t / 0.002) * 0.16 * g


def pad(freqs, d, bright=0.04, g=1.0):
    t = tt(d); n = len(t)
    x = sum(sum(2 * ((t * f * (1 + dt)) % 1) - 1 for dt in (-.006, 0, .006)) for f in freqs) / (3 * len(freqs))
    x = lp(x, bright) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
    return x * 0.5 * g


F1, Db1, Eb1, C1 = 43.65, 34.65, 38.89, 32.70
CH = [(F1, (174.6, 207.7, 261.6)), (Db1, (138.6, 174.6, 207.7)), (Eb1, (155.6, 196.0, 233.1)), (C1, (130.8, 164.8, 196.0))]
MEL = [698.5, 830.6, 1046.5, 932.3, 830.6, 698.5, 622.3, 698.5]      # F minor bell line

bar = 4 * B
for k in range(-1, 10):
    t0 = T0 + k * bar
    root, chord = CH[k % 4]
    for st in range(16):
        n = k * 4 + st / 4                       # position in beats
        t = t0 + st * S
        if t < 0 or t >= DUR - 0.3: continue
        if st == 0:
            add(pad(chord, bar + 0.3, 0.025 if n < 13 else 0.05), t, 0, 0.8 if n < 26 else 0.55)
        if n < 13:                                   # world 1: floating intro
            if st == 0: add(b808(root * 2, 1.2, 0.55), t)
            if n >= 4 and st % 4 == 2: add(hat(0.45), t, 0.2)
            if n >= 9 and st % 2 == 0: add(hat(0.3), t, -0.2)
            if st % 8 == 0: add(bell(MEL[(k * 2 + st // 8) % 8], 0.55), t, 0.3)
        elif n < 26:                                 # worlds 2 and 3: full beat
            if 16.0 <= n < 16.5: continue            # drop-out for the oval spotlight
            drop = n >= 19
            if st in (0, 6, 10) or (drop and st == 14):
                add(kick(1.0), t); add(b808(root * 2 * (1.5 if st == 14 else 1), 0.6 if st else 0.9, 0.9), t)
            if st == 8: add(clap(1.0 if not drop else 1.15), t)
            if st % 2 == 0: add(hat(0.8 if st % 4 else 1.0), t, 0.25)
            if drop and st in (13, 15): add(hat(0.6), t, -0.2)
            if st == 12 and k % 2: [add(hat(0.45, 0.025), t + j * S / 3, -0.2) for j in range(6)]
            if st % 4 == 0: add(bell(MEL[(k * 4 + st // 4) % 8] * (2 if drop else 1), 1.0 if drop else 0.8), t, 0.3 if st % 8 else -0.3)
add(kick(1.2), bt(13)); add(b808(F1 * 2, 1.2, 1.0), bt(13))     # grey world hits
add(kick(1.3), bt(16)); add(b808(F1 * 2, 0.5, 1.0), bt(16.5))   # spotlight
add(kick(1.3), bt(19)); add(b808(F1 * 2, 1.4, 1.2), bt(19))     # neon drop
add(b808(Db1 * 2, 1.6, 1.0), bt(26))                              # bars: beat stops
add(b808(F1 * 2, 2.0, 0.9), bt(28));
for n, f in ((26, 1046.5), (28, 1396.9), (30, 1046.5), (31.5, 1244.5), (32.6, 1396.9)): add(bell(f, 0.7), bt(n), 0.2)
add(pad((174.6, 207.7, 261.6, 349.2), 1.9, 0.06, 1.0), bt(28))   # logo chord
mix = np.stack([L, R], 1)
d = int(B * 0.75 * SR); wet = np.zeros_like(mix); wet[d:] = mix[:-d] * 0.18; mix = mix + wet[:, ::-1]
tm = np.arange(N) / SR
mix = np.tanh(mix * 1.3); mix /= np.max(np.abs(mix)) + 1e-9; mix *= 0.9
mix *= np.minimum(1, (DUR - tm) / 1.2)[:, None]
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "highpass=f=28", str(HERE / "audio" / "beat.wav")], input=(mix * 32767).astype("<i2").tobytes(), check=True)
print("wrote audio/beat.wav")
