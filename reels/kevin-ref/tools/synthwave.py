"""80s synthwave bed, 100 BPM, A minor. Drop (drums + lead) on "Potenzial" at 8.20 s.
Writes audio/synthwave.wav (18 s)."""
import subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent.parent
SR, DUR, DROP, END = 48000, 18.0, 8.20, 15.3
N = int(SR * DUR)
BEAT = 0.6                          # 100 BPM
T0 = DROP - 12 * BEAT               # bar grid with the drop on a downbeat
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR)
    if i >= N: return
    if i < 0: sig = sig[-i:]; i = 0
    s = sig[: N - i] * g
    L[i:i + len(s)] += s * (1 - max(0, pan)); R[i:i + len(s)] += s * (1 + min(0, pan))

def lp(x, cut):
    y = np.zeros_like(x); c = 0.0
    cut = np.broadcast_to(cut, x.shape)
    for i in range(len(x)):
        c += cut[i] * (x[i] - c); y[i] = c
    return y

def saw(f, n, det=(-0.007, 0.0, 0.007)):
    t = np.arange(n) / SR
    return sum(2 * ((t * f * (1 + d) + d * 3) % 1) - 1 for d in det) / len(det)

def adsr(n, a=0.005, d=0.1, s=0.6, r=0.1):
    t = np.arange(n) / SR; e = np.ones(n) * s
    e[t < a] = t[t < a] / a
    m = (t >= a) & (t < a + d); e[m] = 1 - (1 - s) * (t[m] - a) / d
    rel = t > n / SR - r; e[rel] *= np.clip((n / SR - t[rel]) / r, 0, 1)
    return e

def kick(g=1.0):
    n = int(0.4 * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 30)) / SR
    return np.sin(ph) * np.exp(-t * 8) * g

def snare(g=1.0):
    """big gated-reverb 80s snare"""
    n = int(0.42 * SR); t = np.arange(n) / SR
    noise = rng.normal(0, 1, n); body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    tail = lp(noise, 0.35) * (t < 0.32) * np.exp(-t * 4)
    return (0.6 * body + 0.5 * noise * np.exp(-t * 25) + 0.55 * tail) * g * 0.6

def hat(g=1.0):
    n = int(0.05 * SR); x = rng.normal(0, 1, n); x = x - np.concatenate([[0], x[:-1]])
    return x * np.exp(-np.arange(n) / SR * 90) * 0.18 * g

A1, C2, E2, F1, G1 = 55.0, 65.41, 82.41, 43.65, 49.0
PROG = [(A1, (220, 261.6, 329.6)), (F1, (174.6, 220, 261.6)), (C2 / 2 * 2 / 2 * 2, (196, 261.6, 329.6)), (G1, (196, 246.9, 293.7))]

bar = 4 * BEAT
t = T0; k = 0
while t < END + 1e-6:
    root, chord = PROG[k % 4]
    # pad (whole song), brighter after the drop
    n = int(bar * SR)
    pad = sum(saw(f, n) for f in chord) / 3
    bright = 0.05 if t < DROP else 0.12
    pad = lp(pad, np.linspace(bright, bright * 0.7, n)) * adsr(n, 0.3, 0.2, 0.9, 0.3)
    add(pad, t, 0, 0.32)
    # 8th-note arpeggio bass with octave jumps
    for i in range(8):
        f = root * (2 if i % 2 else 1)
        m = int(BEAT / 2 * SR * 0.9)
        b = lp(saw(f, m, (-0.004, 0.004)), 0.12) * adsr(m, 0.004, 0.08, 0.4, 0.03)
        add(b, t + i * BEAT / 2, 0, 0.55 if t >= DROP else 0.35)
    if t >= DROP - 1e-6:
        for i in range(4):
            add(kick(1.0), t + i * BEAT)
            if i in (1, 3): add(snare(1.0), t + i * BEAT)
            add(hat(1.0), t + i * BEAT + BEAT / 2, 0.2)
        # lead arpeggio (16ths) over the chord
        notes = [chord[0] * 2, chord[1] * 2, chord[2] * 2, chord[1] * 2]
        for i in range(16):
            m = int(BEAT / 4 * SR * 0.85)
            ld = lp(saw(notes[i % 4], m, (-0.01, 0.01)), 0.3) * adsr(m, 0.003, 0.05, 0.3, 0.02)
            add(ld, t + i * BEAT / 4, (-0.3 if i % 2 else 0.3), 0.16)
    elif t >= DROP - bar - 1e-6:
        for i in range(8):                      # snare roll into the drop
            add(snare(0.25 + 0.1 * i), t + 2 * BEAT + i * BEAT / 4)
    t += bar; k += 1

# final chord + impact
n = int(2.6 * SR)
add(lp(sum(saw(f, n) for f in (220, 261.6, 329.6, 440)) / 4, 0.1) * adsr(n, 0.01, 0.4, 0.6, 1.5), END, 0, 0.5)
add(kick(1.2), DROP); add(kick(1.0), END)
# riser into the drop
n = int(1.2 * SR); tt = np.arange(n) / SR
add(lp(rng.normal(0, 1, n), np.linspace(0.02, 0.6, n)) * (tt / 1.2) ** 2 * 0.3, DROP - 1.2)

mix = np.stack([L, R], 1)
# simple stereo echo for the 80s space
d = int(BEAT * 0.75 * SR); wet = np.zeros_like(mix); wet[d:] = mix[:-d] * 0.25
mix = mix + wet[:, ::-1]
mix = np.tanh(mix * 1.2); mix /= np.max(np.abs(mix)) + 1e-9; mix *= 0.85
mix *= np.minimum(1, (DUR - np.arange(N) / SR) / 1.5)[:, None]
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "highpass=f=30,acompressor=threshold=-14dB:ratio=2.5", str(HERE / "audio" / "synthwave.wav")],
               input=(mix * 32767).astype("<i2").tobytes(), check=True)
print("wrote audio/synthwave.wav")
