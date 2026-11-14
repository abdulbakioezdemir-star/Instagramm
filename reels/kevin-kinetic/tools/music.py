"""Synthesised instrumental bed in the style of the reference reel:
steady pulse, short pluck stab on every spoken word, full beat from "Potenzial" on.
Writes audio/music.wav (48 kHz stereo, 18 s)."""
import json, math, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent.parent
SR, DUR = 48000, 18.0
N = int(SR * DUR)
WORDS = json.load(open(HERE / "tools" / "words.json"))
DROP = 8.20                    # "Potenzial"
END = 15.30                    # end card
BPM = 150.0
BEAT = 60 / BPM
T0 = DROP - 20 * BEAT          # grid so that the drop is a downbeat
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0: return
    s = sig[: max(0, N - i)] * gain
    L[i:i + len(s)] += s * (1 - max(0, pan)); R[i:i + len(s)] += s * (1 + min(0, pan))

def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)

def kick(g=1.0):
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 7) + 0.25 * np.exp(-t * 300) * rng.normal(0, 1, n)) * g

def hat(g=1.0, length=0.04):
    n = int(length * SR); x = rng.normal(0, 1, n)
    x = x - np.concatenate([[0], x[:-1]])                       # crude high-pass
    return x * np.exp(-np.arange(n) / SR / (length / 4)) * 0.25 * g

def pluck(freq, dur=0.55, bright=0.6):
    """Karplus-Strong pluck"""
    n = int(dur * SR); p = int(SR / freq)
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = bright * buf[i % p] + (1 - bright) * 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996 if False else 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.995
    return out * env(n, 0.002, dur / 3)

def stab(freqs, dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f in freqs:
        for det in (-0.006, 0.006):
            x += 2 * ((t * f * (1 + det)) % 1) - 1               # saw
    # one-pole low-pass that closes quickly = "plucky" synth
    y = np.zeros(n); a = 0.35; c = 0.0
    cut = 0.08 + 0.55 * np.exp(-t * 22)
    for i in range(n):
        c += cut[i] * (x[i] - c); y[i] = c
    return y * env(n, 0.003, 0.12) * 0.18

def pad(freqs, dur, g=0.05):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.0, 0.005):
            x += np.sin(2 * np.pi * f * (1 + det) * t + det * 900)
    fade = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.0)
    return x * fade * g / len(freqs)

def sub(freq, dur=0.32, g=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * env(n, 0.004, 0.12) * g

A2, C3, E3, G3, A3, C4, E4, G4, A4 = 110, 130.8, 164.8, 196, 220, 261.6, 329.6, 392, 440
CHORDS = [(A3, C4, E4), (220 * 2 ** (-4 / 12), A3, C4), (C4, E4, G4), (G3, 246.9, 293.7)]   # Am F C G

# pad bed: whole piece, darker before the drop
add(pad((A2, E3, A3), DROP + 0.2, 0.06), 0)
for k in range(5):
    add(pad(CHORDS[k % 4], 2.0, 0.07), DROP + k * 4 * BEAT)
add(pad((A2, E3, A3, C4), DUR - END, 0.07), END)

# pre-drop pulse: soft half-time kick and tick
t = T0
while t < DROP - 1e-6:
    if t >= 0:
        add(kick(0.35), t)
        add(hat(0.5), t + BEAT, pan=0.2)
    t += 2 * BEAT
# riser into the drop
n = int(0.8 * SR); tt = np.arange(n) / SR
ris = rng.normal(0, 1, n); ris = ris - np.concatenate([[0], ris[:-1]])
add(ris * (tt / 0.8) ** 2.5 * 0.18, DROP - 0.8, gain=1.0)

# drop: four on the floor, off-beat hats and bass
t = DROP; b = 0
while t < END - 1e-6:
    add(kick(0.9), t)
    add(hat(1.0), t + BEAT / 2, pan=0.25)
    if b % 2 == 1: add(hat(0.6, 0.08), t, pan=-0.25)
    root = [55.0, 87.3, 65.4, 98.0][(b // 4) % 4]
    add(sub(root, 0.3, 0.55), t + BEAT / 2)
    t += BEAT; b += 1
# impact on the drop and on the end card
add(kick(1.3), DROP); add(kick(1.1), END)

# one stab per spoken word (the reference's signature)
for i, w in enumerate(WORDS):
    if w["t"] >= END: break
    ch = CHORDS[int((w["t"] - DROP) / (4 * BEAT)) % 4] if w["t"] >= DROP else CHORDS[0]
    up = 2 if w.get("accent") else 1
    add(stab([f * up for f in ch], 0.3), w["t"], pan=(-0.15 if i % 2 else 0.15), gain=1.25 if w.get("accent") else 0.9)
# final chord
add(stab([A3, C4, E4, A4], 1.2), END, gain=1.4)

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.1)                                       # gentle glue
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.85
fade = np.minimum(1, (DUR - np.arange(N) / SR) / 1.5)[:, None]
mix *= fade
pcm = (mix * 32767).astype("<i2").tobytes()
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                "-af", "highpass=f=30,acompressor=threshold=-14dB:ratio=2.5:attack=10:release=120",
                str(HERE / "audio" / "music.wav")], input=pcm, check=True)
print("wrote audio/music.wav")
