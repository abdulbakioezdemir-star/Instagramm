"""Synthesised soundtrack + sound design for the DönER Bro's motion video.

Everything is generated from scratch with numpy (no samples, no licences).
Event times are taken from scene2.html so every effect lands on its frame.

    python3 sound.py out.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 22.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

L = np.zeros(N); R = np.zeros(N)          # dry master
RL = np.zeros(N); RR = np.zeros(N)        # reverb send
DUCK = np.ones(N)                          # sidechain from kick


def t_(n):
    return np.arange(n) / SR


def place(sig, at, gain=1.0, pan=0.0, verb=0.0):
    """Add mono or stereo signal at time `at` (s)."""
    i = int(at * SR)
    if sig.ndim == 1:
        l = sig * np.cos((pan + 1) * np.pi / 4); r = sig * np.sin((pan + 1) * np.pi / 4)
        l *= np.sqrt(2); r *= np.sqrt(2)
    else:
        l, r = sig[0], sig[1]
    n = min(len(l), N - i)
    if n <= 0:
        return
    L[i:i + n] += l[:n] * gain; R[i:i + n] += r[:n] * gain
    if verb:
        RL[i:i + n] += l[:n] * gain * verb; RR[i:i + n] += r[:n] * gain * verb


def fft_filter(x, fn):
    """Static filter: fn(freqs) -> gain."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * fn(f), len(x))


def lowpass(x, fc, order=2):
    return fft_filter(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))


def highpass(x, fc, order=2):
    return fft_filter(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))


def bandpass(x, fc, q=1.0):
    return fft_filter(x, lambda f: np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) * q * 2) ** 2))


def sweep_filter(x, centers, width_oct=1.2, frame=2048, hop=512):
    """Time-varying band-pass via STFT; centers = array of Hz per sample."""
    win = np.hanning(frame)
    out = np.zeros(len(x) + frame); norm = np.zeros(len(x) + frame)
    f = np.fft.rfftfreq(frame, 1 / SR)
    xp = np.concatenate([x, np.zeros(frame)])
    for s in range(0, len(x), hop):
        c = centers[min(s + frame // 2, len(x) - 1)]
        g = np.exp(-0.5 * (np.log2(np.maximum(f, 1) / c) / width_oct) ** 2)
        seg = np.fft.irfft(np.fft.rfft(xp[s:s + frame] * win) * g, frame)
        out[s:s + frame] += seg * win; norm[s:s + frame] += win ** 2
    return out[:len(x)] / np.maximum(norm[:len(x)], 1e-6)


def env_adsr(n, a, d, s_lvl, r):
    e = np.ones(n) * s_lvl
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s_lvl, len(e[na:na + nd]))
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


# ---------------------------------------------------------------- instruments
def kick(dur=.45):
    t = t_(int(dur * SR))
    f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 7.5)
    click = highpass(rng.standard_normal(len(t)), 2500) * np.exp(-t * 300) * .25
    return np.tanh((body + click) * 1.6) * .9


def clap():
    n = int(.35 * SR); t = t_(n)
    nz = bandpass(rng.standard_normal(n), 1400, .7)
    e = np.zeros(n)
    for k, off in enumerate([0, .011, .022]):
        i = int(off * SR); e[i:] += np.exp(-(t[:n - i]) * (160 if k < 2 else 22))
    return nz * e * .55


def hat(open_=False):
    n = int((.25 if open_ else .06) * SR); t = t_(n)
    nz = highpass(rng.standard_normal(n), 7000, 3)
    return nz * np.exp(-t * (14 if open_ else 70)) * .22


def pluck(freq, dur=.9, bright=1.0):
    """Saz-like plucked string: harmonics with individual decays + slight vibrato."""
    n = int(dur * SR); t = t_(n)
    vib = 1 + .003 * np.sin(2 * np.pi * 5.5 * t) * (1 - np.exp(-t * 4))
    ph = 2 * np.pi * freq * np.cumsum(vib) / SR
    s = np.zeros(n)
    for h in range(1, 9):
        s += (np.sin(ph * h) / h ** (1.1 / bright)) * np.exp(-t * (3 + h * 2.2))
    s += highpass(rng.standard_normal(n), 3000) * np.exp(-t * 150) * .08
    return s * np.minimum(1, t * 400)


def pad_chord(freqs, dur, cutoff=1400):
    n = int(dur * SR); t = t_(n); s = np.zeros(n)
    for f0 in freqs:
        for det in (-0.12, 0, 0.11):
            f = f0 * 2 ** (det / 12)
            ph = rng.random() * 2 * np.pi
            saw = 2 * ((f * t + ph / (2 * np.pi)) % 1) - 1
            s += saw
    s = lowpass(s, cutoff, 2) / (len(freqs) * 3)
    return s * env_adsr(n, .6, .3, .9, .8)


def bass_note(freq, dur):
    n = int(dur * SR); t = t_(n)
    s = np.sin(2 * np.pi * freq * t) + .35 * np.sin(2 * np.pi * freq * 2 * t) + .12 * np.sin(2 * np.pi * freq * 3 * t)
    return np.tanh(s * 1.4) * env_adsr(n, .005, .12, .7, .06) * .55


# ---------------------------------------------------------------- sfx
def whoosh(dur=1.0, f0=300, f1=4000, peak=.6, gain=1.0):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    centers = f0 * (f1 / f0) ** (np.clip(t / peak, 0, 1) if f1 > f0 else t)
    # rise then fall
    cen = np.where(t < peak, f0 * (f1 / f0) ** (t / peak), f1 * (f0 * 1.5 / f1) ** ((t - peak) / (1 - peak)))
    nz = rng.standard_normal(n)
    s = sweep_filter(nz, cen, 0.9)
    amp = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5))
    s = s * amp
    s /= np.max(np.abs(s)) + 1e-9
    # stereo movement left -> right
    pan = np.linspace(-.7, .7, n)
    l = s * np.cos((pan + 1) * np.pi / 4) * 1.41; r = s * np.sin((pan + 1) * np.pi / 4) * 1.41
    return np.stack([l, r]) * gain


def impact(dur=3.0):
    n = int(dur * SR); t = t_(n)
    f = 32 + 90 * np.exp(-t * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    crack = lowpass(rng.standard_normal(n), 3000) * np.exp(-t * 18) * .6
    tail = lowpass(rng.standard_normal(n), 600) * np.exp(-t * 2.5) * .25
    return np.tanh((boom * 1.3 + crack + tail) * 1.3)


def shimmer(dur=2.2, base=1318.5):
    n = int(dur * SR); t = t_(n); s = np.zeros(n)
    for k, m in enumerate([1, 1.5, 2, 3, 4]):
        s += np.sin(2 * np.pi * base * m * t + k) * np.exp(-t * (2 + k)) / (k + 1)
    return s * np.minimum(1, t * 60) * .25


def reverse_swell(dur=1.0):
    n = int(dur * SR); t = t_(n)
    nz = highpass(rng.standard_normal(n), 1800, 2)
    e = (t / dur) ** 3
    return nz * e * .5


def riser(dur=1.2, f0=200, f1=1600):
    n = int(dur * SR); tt = np.linspace(0, 1, n)
    f = f0 * (f1 / f0) ** tt
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = (2 * ((np.cumsum(f) / SR) % 1) - 1) * .4 + np.sin(ph) * .6
    nz = sweep_filter(rng.standard_normal(n), f * 2, 1.0) * .6
    return (saw * .35 + nz) * tt ** 2 * .7


def plop(f0=520, f1=170, dur=.12):
    n = int(dur * SR); t = t_(n)
    f = f1 + (f0 - f1) * np.exp(-t * 45)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 32) * .8


def thump(heavy=1.0):
    n = int(.28 * SR); t = t_(n)
    f = 55 + 80 * np.exp(-t * 35)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
    soft = lowpass(rng.standard_normal(n), 900) * np.exp(-t * 60) * .5
    return (body * heavy + soft) * .9


def tick():
    n = int(.08 * SR); t = t_(n)
    s = bandpass(rng.standard_normal(n), 4200, 1.2) * np.exp(-t * 120)
    s += np.sin(2 * np.pi * 1760 * t) * np.exp(-t * 60) * .25
    return s * .5


def sizzle(dur):
    n = int(dur * SR); t = t_(n)
    base = bandpass(rng.standard_normal(n), 6500, .6) * .25
    crackle = np.zeros(n)
    idx = rng.choice(n, int(dur * 90), replace=False)
    crackle[idx] = rng.standard_normal(len(idx)) * 3
    crackle = highpass(lowpass(crackle, 9000), 1500)
    mod = .6 + .4 * np.sin(2 * np.pi * .7 * t) * np.sin(2 * np.pi * 1.9 * t)
    return (base * mod + crackle * .35)


def neon_buzz(dur):
    n = int(dur * SR); t = t_(n)
    saw = 2 * ((100 * t) % 1) - 1
    s = lowpass(saw, 1800) * .25 + np.sin(2 * np.pi * 50 * t) * .15
    flick = (rng.random(int(dur * 40)) > .25).astype(float)
    flick = np.repeat(flick, int(np.ceil(n / len(flick))))[:n]
    flick = lowpass(flick, 60)
    return s * flick


def rustle(dur):
    n = int(dur * SR); t = t_(n)
    s = bandpass(rng.standard_normal(n), 2500, .5)
    grains = np.zeros(n); idx = rng.choice(n, int(dur * 160), replace=False); grains[idx] = 1
    grains = lowpass(grains, 300) * 40
    return s * np.clip(grains, 0, 1) * .45


# ---------------------------------------------------------------- music
BPM = 120; BEAT = 60 / BPM; BAR = 4 * BEAT
E2, F2 = 82.41, 87.31
# E Phrygian dominant (Hijaz) – E F G# A B C D
NOTE = {'E4': 329.63, 'F4': 349.23, 'G#4': 415.30, 'A4': 440.0, 'B4': 493.88, 'C5': 523.25,
        'D5': 587.33, 'E5': 659.25, 'B3': 246.94, 'G#3': 207.65}

DRUMS_ON = [(2.5, 17.5), (19.0, 21.5)]
def drums_active(t):
    return any(a <= t < b for a, b in DRUMS_ON)

kk, cl = kick(), clap()
beat_t = 0.0
for b in range(int(DUR / BEAT) + 1):
    t0 = b * BEAT
    if not drums_active(t0):
        continue
    pos = b % 4
    place(kk, t0, .95)
    i = int(t0 * SR); n = int(.32 * SR)
    if i + n < N:
        DUCK[i:i + n] = np.minimum(DUCK[i:i + n], 1 - .7 * np.exp(-t_(n) * 10))
    if pos in (1, 3):
        place(cl, t0, .5, pan=0, verb=.35)
    # hats: offbeat 8ths + quiet 16ths
    if drums_active(t0 + BEAT / 2):
        place(hat(open_=(b % 8 == 7)), t0 + BEAT / 2, .9, pan=.25)
    for s16 in (BEAT / 4, 3 * BEAT / 4):
        if drums_active(t0 + s16) and t0 > 7:
            place(hat(), t0 + s16, .35, pan=-.2)

# bass: E / F alternating per bar, syncopated
bass = np.zeros(N)
for bar in range(int(DUR / BAR) + 1):
    t0 = bar * BAR
    root = E2 if bar % 2 == 0 else F2
    for off, ln, oct_ in [(0, .4, 1), (.75, .2, 1), (1.0, .4, 1), (1.5, .25, 2), (1.75, .2, 1)]:
        tt = t0 + off
        if drums_active(tt) and tt + ln < DUR:
            bn = bass_note(root * oct_, ln)
            i = int(tt * SR); bass[i:i + len(bn)] += bn
place(bass * 0 + bass, 0, .9)

# pad – E major / F major (Hijaz colour), filtered intro opening up
for bar in range(int(DUR / BAR) + 1):
    t0 = bar * BAR
    if t0 >= 21.0: break
    chord = [164.81, 207.65, 246.94, 329.63] if bar % 2 == 0 else [174.61, 220.0, 261.63, 349.23]
    cut = 500 + 1600 * min(1, t0 / 3.0)
    p = pad_chord(chord, BAR + .8, cut)
    place(np.stack([p, np.roll(p, 220)]), t0, .32, verb=.6)
# final chord, ring-out
place(np.stack([pad_chord([164.81, 207.65, 246.94, 329.63, 493.88], 2.8, 2200)] * 2), 19.9, .3, verb=.8)

# saz motif (Hijaz) – sparse, on food scenes
motif = [('E4', 0), ('F4', .25), ('G#4', .5), ('A4', 1.0), ('G#4', 1.25), ('F4', 1.5), ('E4', 1.75),
         ('B4', 2.0), ('C5', 2.5), ('B4', 2.75), ('A4', 3.0), ('G#4', 3.25), ('F4', 3.5), ('E4', 3.75)]
for start in (4.5, 8.5, 12.5):
    for nm, off in motif:
        place(pluck(NOTE[nm], .8), start + off, .28, pan=.3 * np.sin(off * 3), verb=.45)
# outro motif – rising, resolves on the ring
for nm, off in [('B3', 0), ('E4', .25), ('G#4', .5), ('B4', .75), ('E5', 1.0)]:
    place(pluck(NOTE[nm], 1.6, 1.4), 20.0 + off, .3, verb=.6)

# ---------------------------------------------------------------- sound design (synced to scene2.html)
place(riser(2.4, 110, 1200), .1, .3, verb=.3)                  # intro build-up
place(impact(1.6) * .35, .35, .45, verb=.4)                     # wordmark
place(shimmer(1.6, 987.8), .4, .45, verb=.6)
place(reverse_swell(.9), 1.6, .45, verb=.3)                     # zoom-through into the döner
place(whoosh(1.1, 250, 6000, .6, 1.0), 1.85, .6, verb=.3)
place(impact(2.0), 2.5, .75, verb=.45)                          # drop: beat starts
for tt in (3.1, 7.55, 10.25, 13.2, 19.6):                       # text reveals
    place(tick(), tt, .55, verb=.3)
place(sizzle(4.8), 2.45, .3, verb=.15)                          # döner sizzling
for tt in (3.25, 5.3):                                          # glow sweeps over the döner
    place(shimmer(1.4, 1318.5), tt + .2, .35, verb=.7)
    place(whoosh(.9, 1500, 7000, .5, .5), tt, .18, verb=.4)
place(whoosh(.8, 300, 5000, .5, 1.0), 6.8, .6, verb=.25)        # whip -> dürüm
place(thump(1.0), 7.2, .35)
place(whoosh(.8, 300, 5000, .5, 1.0), 9.5, .6, verb=.25)        # whip -> burger
place(thump(1.0), 9.9, .35)
place(sizzle(1.6) * .6, 10.0, .25)
place(reverse_swell(.6), 12.25, .4)                             # spin -> pizza
place(whoosh(.9, 200, 4000, .5, 1.0), 12.35, .6, verb=.3)
place(impact(1.2) * .5, 12.8, .5, verb=.3)
for tt in (15.5, 16.0, 16.5, 17.0):                             # flash cuts on the beat
    place(impact(.8) * .6, tt, .45, verb=.25)
    place(whoosh(.35, 1200, 6000, .5, .5), tt - .17, .3)
place(reverse_swell(1.0), 17.2, .5, verb=.3)                    # zoom into the storefront
place(whoosh(1.0, 200, 6000, .55, 1.0), 17.35, .6, verb=.3)
place(riser(1.3, 200, 2400), 17.7, .25, verb=.3)
place(whoosh(.5, 800, 3000, .5, .5), 18.3, .3)                  # logo lands centre
place(reverse_swell(.6), 18.4, .45)
RING_T = 19.0
place(impact(3.2), RING_T, .9, verb=.5)                          # ring draws around the logo
place(whoosh(.6, 1500, 7000, .7, .7), RING_T, .3, verb=.4)
place(neon_buzz(.6), RING_T, .2)
place(shimmer(2.6, 1318.5), RING_T + .5, .55, verb=.7)

# ---------------------------------------------------------------- mix
music_bus_l, music_bus_r = L.copy(), R.copy()
# reverb: stereo exponential-decay noise IR
ir_n = int(1.9 * SR); tir = t_(ir_n)
irl = lowpass(rng.standard_normal(ir_n), 5000) * np.exp(-tir * 3.2)
irr = lowpass(rng.standard_normal(ir_n), 5000) * np.exp(-tir * 3.2)
def conv(x, h):
    n = 1 << int(np.ceil(np.log2(len(x) + len(h))))
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(h, n), n)[:len(x)]
wl, wr = conv(RL, irl), conv(RR, irr)
wl *= .5 / (np.max(np.abs(wl)) + 1e-9) * np.max(np.abs(RL) + 1e-9) * 3
wr *= .5 / (np.max(np.abs(wr)) + 1e-9) * np.max(np.abs(RR) + 1e-9) * 3

# sidechain everything except kick a bit (kick is short, ducking barely touches it)
duck = .55 + .45 * DUCK
mixL = (L * duck + wl * .35); mixR = (R * duck + wr * .35)

# fades
fade = np.ones(N)
fi = int(.05 * SR); fade[:fi] = np.linspace(0, 1, fi)
fo0 = int(21.4 * SR); fade[fo0:] = np.linspace(1, 0, N - fo0) ** 1.5
mixL *= fade; mixR *= fade

# gentle master: highpass rumble, soft clip, normalise to -1 dBFS
mixL = highpass(mixL, 28); mixR = highpass(mixR, 28)
peak = max(np.max(np.abs(mixL)), np.max(np.abs(mixR)))
mixL /= peak; mixR /= peak
mixL = np.tanh(mixL * 1.1) / np.tanh(1.1); mixR = np.tanh(mixR * 1.1) / np.tanh(1.1)
mixL *= .89; mixR *= .89

out = sys.argv[1] if len(sys.argv) > 1 else 'soundtrack.wav'
pcm = (np.stack([mixL, mixR], 1) * 32767).astype('<i2')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', out, f'{DUR}s')
