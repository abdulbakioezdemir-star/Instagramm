"""Dark trap instrumental, 139 BPM, F minor. Grid starts at 0 so the world changes sit on beats:
3.45 (grey world, beat 8), 8.2 (neon drop, beat 19), 12.52 (logo, beat 29). Silence 7.88-8.2.
Writes audio/beat.wav (18 s)."""
import subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent.parent
SR, DUR = 48000, 18.0
N = int(SR * DUR)
B = 8.2 / 19                       # one beat
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
for k in range(int(DUR / bar) + 1):
    t0 = k * bar
    root, chord = CH[k % 4]
    if t0 >= 17.5: break
    sec = "intro" if t0 < 3.44 else "verse" if t0 < 7.8 else "drop" if t0 < 12.5 else "outro"
    # pad, ducked to nothing inside the silence
    add(pad(chord, bar + 0.3, 0.03 if sec == "intro" else 0.05), t0, 0, 0.9 if sec != "outro" else 0.7)
    for st in range(16):
        t = t0 + st * S
        if 7.86 <= t < 8.19: continue                                  # the pause before the reveal
        if sec == "intro":
            if st in (0, 8): add(b808(root * 2, 0.8, 0.5), t)
            if st % 4 == 2: add(hat(0.5), t, 0.2)
        elif sec in ("verse", "drop"):
            if st in (0, 6, 10) or (sec == "drop" and st == 14):
                add(kick(1.0), t); add(b808(root * 2 * (1.5 if st == 14 else 1), 0.7 if st else 1.0, 0.9), t)
            if st == 8: add(clap(1.0 if sec == "verse" else 1.15), t)
            if st % 2 == 0: add(hat(0.8 if st % 4 else 1.0), t, 0.25)
            if sec == "drop" and st in (13, 15): add(hat(0.6), t, -0.2)
            if st in (12,) and k % 2: [add(hat(0.45, 0.025), t + j * S / 3, -0.2) for j in range(6)]   # 1/48 roll
            if st % 4 == 0: add(bell(MEL[(k * 4 + st // 4) % 8] * (2 if sec == "drop" else 1), 1.0 if sec == "drop" else 0.8), t, 0.3 if st % 8 else -0.3)
        else:  # outro
            if st == 0: add(b808(root * 2, 1.4, 0.6), t)
            if st == 8: add(clap(0.5), t)
            if st % 4 == 2: add(hat(0.45), t, 0.2)
            if st % 8 == 0: add(bell(MEL[(k + st // 8) % 8], 0.6), t, 0.2)
add(kick(1.3), 8.2); add(b808(F1 * 2, 1.6, 1.2), 8.2)               # the drop
add(b808(F1 * 2, 2.2, 0.8), 12.52)                                   # logo hit

mix = np.stack([L, R], 1)
d = int(B * 0.75 * SR); wet = np.zeros_like(mix); wet[d:] = mix[:-d] * 0.18; mix = mix + wet[:, ::-1]
tm = np.arange(N) / SR
mix *= np.where((tm > 7.88) & (tm < 8.2), 0.0, 1.0)[:, None]         # hard silence
mix = np.tanh(mix * 1.3); mix /= np.max(np.abs(mix)) + 1e-9; mix *= 0.9
mix *= np.minimum(1, (DUR - tm) / 1.2)[:, None]
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "highpass=f=28", str(HERE / "audio" / "beat.wav")], input=(mix * 32767).astype("<i2").tobytes(), check=True)
print("wrote audio/beat.wav")
