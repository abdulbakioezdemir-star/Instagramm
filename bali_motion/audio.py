"""Soundtrack + Sound Design for the Bali motion edit (no voice).

120 BPM, 16 s = 8 bars. Every transition in render.py lands on the same
beat grid (1 beat = 15 frames @ 30 fps = 0.5 s).
"""
import numpy as np
import wave

SR = 44100
BPM = 120
BEAT = 60 / BPM          # 0.5 s
BAR = 4 * BEAT           # 2.0 s
LENGTH = 17.0            # 16 s video + reverb tail (trimmed when muxing)
N = int(SR * LENGTH)
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)


def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0]
    gl = gain * np.sqrt(0.5 * (1 - pan))
    gr = gain * np.sqrt(0.5 * (1 + pan))
    L[i0:i0 + len(sig)] += sig * gl
    R[i0:i0 + len(sig)] += sig * gr


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def onepole_lp(x, cutoff):
    """Time-varying one-pole lowpass. cutoff: scalar or array (Hz)."""
    cutoff = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def fft_band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def reverb(x, seconds=2.2, mix=0.35):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 6.0 / seconds)
    ir = fft_band(ir, 200, 9000)
    ir /= np.sqrt(np.sum(ir ** 2))
    m = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]
    return x * (1 - mix) + y * mix * 0.6


# ---------------------------------------------------------------- instruments
def gamelan(freq, dur=1.6, bright=1.0):
    """Metallophone (gangsa): inharmonic partials + detuned 'ombak' shimmer."""
    t = tt(dur)
    out = np.zeros_like(t)
    for ratio, amp, dec in [(1, 1, 2.2), (2.76, .45 * bright, 5), (5.40, .22 * bright, 9), (8.93, .1 * bright, 14)]:
        for det in (-2.5, 2.5):
            out += amp * np.sin(2 * np.pi * (freq * ratio + det) * t) * np.exp(-t * dec)
    out += 0.3 * np.sin(2 * np.pi * freq * 4.1 * t) * np.exp(-t * 60)  # mallet strike
    return out * 0.25


def gong(freq=62, dur=5.0):
    t = tt(dur)
    wob = 1 + 0.004 * np.sin(2 * np.pi * 3.2 * t)
    out = (np.sin(2 * np.pi * freq * wob * t) * np.exp(-t * 0.7)
           + 0.5 * np.sin(2 * np.pi * freq * 2.01 * t) * np.exp(-t * 1.2)
           + 0.3 * np.sin(2 * np.pi * freq * 2.93 * t) * np.exp(-t * 1.8)
           + 0.2 * np.sin(2 * np.pi * freq * 4.2 * t) * np.exp(-t * 3))
    att = np.minimum(1, t / 0.01)
    return out * att * 0.5


def kick(dur=0.45, punch=1.0):
    t = tt(dur)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7)
    click = rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.3
    return np.tanh((body + click) * 1.6 * punch)


def clap(dur=0.3):
    t = tt(dur)
    n = fft_band(rng.standard_normal(len(t)), 900, 6000)
    n /= np.abs(n).max()
    env = np.exp(-t * 18)
    for d in (0.0, 0.011, 0.022):
        env += np.where(t > d, np.exp(-(t - d) * 120), 0) * 0.6
    return n * env * 0.5


def hat(dur=0.08, open_=False):
    t = tt(0.3 if open_ else dur)
    n = fft_band(rng.standard_normal(len(t)), 7000, 16000)
    n /= np.abs(n).max()
    return n * np.exp(-t * (12 if open_ else 60)) * 0.3


def whoosh(dur=0.6, up=True, lo=300, hi=7000):
    t = tt(dur)
    x = t / dur
    env = np.sin(np.pi * x) ** 2
    sweep = lo + (hi - lo) * (x if up else 1 - x) ** 1.5
    n = rng.standard_normal(len(t))
    y = onepole_lp(n, sweep) - onepole_lp(n, sweep * 0.25)
    return y / (np.abs(y).max() + 1e-9) * env * 0.7


def riser(dur):
    t = tt(dur)
    x = t / dur
    n = rng.standard_normal(len(t))
    noise = onepole_lp(n, 400 + 9000 * x ** 2)
    noise /= np.abs(noise).max()
    f = 180 + 1400 * x ** 2.2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    return (noise * 0.6 + tone * 0.25) * x ** 2


def impact(dur=2.5):
    t = tt(dur)
    f = 30 + 40 * np.exp(-t * 4)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    crash = fft_band(rng.standard_normal(len(t)), 2000, 14000) * np.exp(-t * 3)
    crash /= np.abs(crash).max()
    return np.tanh(sub * 1.5) * 0.9 + crash * 0.25


def glitch_tick():
    t = tt(0.05)
    return np.sign(np.sin(2 * np.pi * 2400 * t)) * np.exp(-t * 90) * 0.2


def pad(freqs, dur):
    t = tt(dur)
    out = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0, 0.7):
            ph = 2 * np.pi * (f + det) * t
            out += np.sin(ph) + 0.3 * np.sin(2 * ph)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8)
    return out / len(freqs) * env * 0.08


def ocean(dur):
    t = tt(dur)
    n = onepole_lp(rng.standard_normal(len(t)), 900)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / 3.2 - 1.5) ** 2
    return n / np.abs(n).max() * swell * 0.25


# ------------------------------------------------------------ arrangement
# Slendro-ish scale on D
D = 293.66
SCALE = [D * r for r in (1, 1.149, 1.320, 1.516, 1.741, 2, 2.298, 2.640)]
MOTIF = [0, 2, 3, 5, 3, 2, 4, 2,  0, 2, 3, 5, 6, 5, 3, 4]   # eighth notes

music = np.zeros(N)
music_r = np.zeros(N)

# Ambience
amb = ocean(4.2)
add(amb, 0.0, 0.8, -0.2)
add(ocean(4.0), 12.0, 0.6, 0.2)

# Pads (whole song apart from the 4-frame silence)
chords = [[D / 2, D * 0.66, D * 0.87], [D / 2 * 1.149, D * 0.76, D], [D / 2 * 1.32, D * 0.87, D * 1.149], [D / 2, D * 0.66, D]]
pad_bus = np.zeros(N)
for b in range(8):
    if b == 3:
        dur = BAR - 0.14
    else:
        dur = BAR + 0.3
    p = pad(chords[b % 4], dur)
    i0 = int(b * BAR * SR)
    pad_bus[i0:i0 + len(p)] += p[: N - i0]

# Gamelan melody: bars 1-4 & 7-8 (eighths), drop bars 5-6 doubled octave
gam_bus_l = np.zeros(N)
gam_bus_r = np.zeros(N)
for b in range(8):
    for k in range(8):
        t0 = b * BAR + k * BEAT / 2
        if b == 3 and t0 >= 4 * BAR - 0.14:
            continue
        if b == 0 and k < 2:
            continue
        note = SCALE[MOTIF[(b * 8 + k) % 16]]
        g = gamelan(note * (2 if b in (4, 5) else 1), bright=1.2 if b in (4, 5) else 1)
        vel = 0.7 + 0.3 * (k % 2 == 0)
        i0 = int(t0 * SR)
        seg = g[: N - i0] * vel
        pan = -0.35 if k % 2 == 0 else 0.35
        gam_bus_l[i0:i0 + len(seg)] += seg * np.sqrt(0.5 * (1 - pan))
        gam_bus_r[i0:i0 + len(seg)] += seg * np.sqrt(0.5 * (1 + pan))

gam_bus_l = reverb(gam_bus_l, 2.4, 0.4)
gam_bus_r = reverb(gam_bus_r, 2.6, 0.4)
pad_bus = reverb(pad_bus, 3.0, 0.5)
L += gam_bus_l + pad_bus
R += gam_bus_r + np.roll(pad_bus, int(0.012 * SR))

# Drums
kick_env = np.zeros(N)


def place_kick(t0, punch=1.0, gain=0.9):
    add(kick(punch=punch), t0, gain)
    i0 = int(t0 * SR)
    e = np.exp(-tt(0.4) * 9)
    kick_env[i0:i0 + len(e)] = np.maximum(kick_env[i0:i0 + len(e)], e[: N - i0])


for b in range(8):
    for beat in range(4):
        t0 = b * BAR + beat * BEAT
        if b in (1, 2) and beat in (0, 2):
            place_kick(t0, 0.8, 0.7)
        if b == 3 and beat in (0, 2):
            place_kick(t0, 0.9, 0.8)
        if b in (4, 5, 7):
            place_kick(t0)
        if b in (4, 5, 7) and beat in (1, 3):
            add(clap(), t0, 0.7)
        if b in (2, 3, 4, 5, 7):
            add(hat(), t0 + BEAT / 2, 0.6, 0.3)
        if b in (4, 5):
            add(hat(), t0 + BEAT / 4, 0.25, -0.3)
            add(hat(), t0 + 3 * BEAT / 4, 0.25, -0.3)

# Snare roll accelerating into the drop (bar 4)
roll_t = 3 * BAR + 2 * BEAT
step = BEAT / 2
while roll_t < 4 * BAR - 0.14:
    add(clap(0.12), roll_t, 0.25 + 0.5 * (roll_t - 3 * BAR) / BAR)
    roll_t += step
    step = max(BEAT / 8, step * 0.82)

# Sub bass in drop, side-chained
bass = np.zeros(N)
roots = [D / 4, D / 4 * 1.149, D / 4 * 1.32, D / 4]
for b in (4, 5, 7):
    for beat in range(4):
        t0 = b * BAR + beat * BEAT + BEAT / 2
        t = tt(BEAT * 0.9)
        f = roots[(b * 4 + beat) // 4 % 4]
        tone = np.tanh(2.0 * np.sin(2 * np.pi * f * t)) * np.minimum(1, t / 0.01) * np.exp(-t * 2)
        i0 = int(t0 * SR)
        bass[i0:i0 + len(t)] += tone[: N - i0] * 0.35
bass *= 1 - 0.8 * kick_env
L += bass
R += bass

# ------------------------------------------------------------ sound design
# Title slam (frame 30 = 1.0 s): gong + impact
add(gong(62), 1.0, 0.9)
add(impact(1.8), 1.0, 0.5)
add(whoosh(0.9, up=True), 0.12, 0.5)            # title flies in
# Title flies into camera before cut 1
add(whoosh(0.5, up=True, lo=600, hi=9000), 3.6, 0.6, 0.3)
# Cut 1 (4.0 s): whip pan
add(whoosh(0.45, up=False, lo=500, hi=8000), 3.85, 0.7, -0.5)
add(whoosh(0.35, up=True, lo=800, hi=9000), 4.0, 0.5, 0.5)
# Cut 2 (6.0 s): 3D flip
add(whoosh(0.6, up=True, lo=200, hi=5000), 5.7, 0.7)
add(impact(0.8), 6.0, 0.35)
# Build into drop: riser 6.2 -> 7.86, then 4 frames silence
add(riser(1.66), 6.2, 0.55)
# Drop (8.0 s): impact + gong + reversed crash
add(impact(2.5), 8.0, 1.0)
add(gong(55, 4.0), 8.0, 0.6)
# Fast cuts in the drop: whoosh/tick on every cut
cuts = [8.5, 9.0, 9.5, 10.0, 10.25, 10.5, 10.75, 11.0, 11.25, 11.5, 11.75]
for i, c in enumerate(cuts):
    add(whoosh(0.22, up=i % 2 == 0, lo=1500, hi=12000), c - 0.11, 0.45, (-1) ** i * 0.6)
    add(glitch_tick(), c, 0.6, (-1) ** i * 0.4)
# Breakdown in (12.0 s)
add(whoosh(1.0, up=False, lo=200, hi=6000), 11.6, 0.6)
# Final cut (14.0 s): zoom burst + gong
add(whoosh(0.5, up=True, lo=400, hi=10000), 13.6, 0.7)
add(gong(62, 3.0), 14.0, 0.9)
add(impact(2.0), 14.0, 0.6)

# 4-frame silence before drop (7.867 s – 8.0 s): hard mute everything
s0, s1 = int((4 * BAR - 4 / 30) * SR), int(4 * BAR * SR)
L[s0:s1] = 0
R[s0:s1] = 0

# Master: glue, soft clip, fade out, normalise
fade = np.ones(N)
f0 = int(15.2 * SR)
fade[f0:] = np.clip(1 - (np.arange(N - f0) / SR) / 1.0, 0, 1)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L / peak * 1.4) / np.tanh(1.4)
R = np.tanh(R / peak * 1.4) / np.tanh(1.4)
L *= 0.89
R *= 0.89

stereo = (np.stack([L, R], 1)[: int(16 * SR)] * 32767).astype(np.int16)
with wave.open("out/soundtrack.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(stereo.tobytes())
print("soundtrack.wav written", stereo.shape)
