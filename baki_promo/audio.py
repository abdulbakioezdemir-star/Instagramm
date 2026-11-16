"""Soundtrack + sound design for the BAKI MOTIONS promo (no voice).

120 BPM, 16 s. Beat = 0.5 s = 15 frames. Key moments (must match render.py):
  1.0 s  avatar pulse (pop)            2.0 s  logo bursts out of the avatar (drop)
  3.0 s  "BAKI MOTIONS" slam           5.0/6.0/7.0 s service cards fly in
  8.0 s  cards out (whoosh)            9.0 s  portfolio, 9.5/10.0 s reels pop out
  13.0 s CTA impact                    15.0 s button pulse, 16 s end
"""
import numpy as np
import wave

SR = 44100
BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * 16.0)
rng = np.random.default_rng(11)
L = np.zeros(N)
R = np.zeros(N)


def tt(d):
    return np.arange(int(d * SR)) / SR


def add(sig, t0, gain=1.0, pan=0.0, buf=None):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0]
    l, r = (L, R) if buf is None else buf
    l[i0:i0 + len(sig)] += sig * gain * np.sqrt(0.5 * (1 - pan))
    r[i0:i0 + len(sig)] += sig * gain * np.sqrt(0.5 * (1 + pan))


def onepole_lp(x, cutoff):
    cutoff = np.broadcast_to(np.asarray(cutoff, float), x.shape)
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


def reverb(x, seconds=2.0, mix=0.3):
    n = int(seconds * SR)
    ir = fft_band(rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 6 / seconds), 200, 9000)
    ir /= np.sqrt(np.sum(ir ** 2))
    m = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]
    return x * (1 - mix) + y * mix * 0.6


def kick(punch=1.0):
    t = tt(0.45)
    f = 45 + 120 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return np.tanh((body + rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.3) * 1.7 * punch)


def clap(d=0.3):
    t = tt(d)
    n = fft_band(rng.standard_normal(len(t)), 900, 7000)
    n /= np.abs(n).max()
    env = np.exp(-t * 16)
    for dd in (0.0, 0.01, 0.021):
        env += np.where(t > dd, np.exp(-(t - dd) * 120), 0) * 0.6
    return n * env * 0.5


def hat(open_=False):
    t = tt(0.3 if open_ else 0.07)
    n = fft_band(rng.standard_normal(len(t)), 7000, 16000)
    return n / np.abs(n).max() * np.exp(-t * (12 if open_ else 65)) * 0.3


def pluck(freq, d=0.6):
    t = tt(d)
    saw = 2 * ((freq * t) % 1) - 1 + 2 * ((freq * 1.005 * t) % 1) - 1
    y = onepole_lp(saw, 300 + 5000 * np.exp(-t * 12))
    return y * np.exp(-t * 5) * 0.25


def pad(freqs, d):
    t = tt(d)
    out = sum(np.sin(2 * np.pi * (f + dt) * t) + 0.25 * np.sin(4 * np.pi * (f + dt) * t) for f in freqs for dt in (-0.7, 0, 0.8))
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
    return out / len(freqs) * env * 0.06


def whoosh(d=0.6, up=True, lo=300, hi=8000):
    t = tt(d)
    x = t / d
    sweep = lo + (hi - lo) * (x if up else 1 - x) ** 1.5
    n = rng.standard_normal(len(t))
    y = onepole_lp(n, sweep) - onepole_lp(n, sweep * 0.25)
    return y / (np.abs(y).max() + 1e-9) * np.sin(np.pi * x) ** 2 * 0.7


def riser(d):
    t = tt(d)
    x = t / d
    noise = onepole_lp(rng.standard_normal(len(t)), 400 + 9000 * x ** 2)
    noise /= np.abs(noise).max()
    f = 200 + 1500 * x ** 2.2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return (noise * 0.6 + tone * 0.25) * x ** 2


def impact(d=2.0):
    t = tt(d)
    sub = np.sin(2 * np.pi * np.cumsum(30 + 45 * np.exp(-t * 4)) / SR) * np.exp(-t * 1.7)
    crash = fft_band(rng.standard_normal(len(t)), 2000, 14000) * np.exp(-t * 3)
    return np.tanh(sub * 1.5) * 0.9 + crash / np.abs(crash).max() * 0.25


def pop():
    t = tt(0.18)
    f = 300 + 900 * (1 - np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22) * 0.6


def shimmer(d=1.5):
    t = tt(d)
    out = np.zeros_like(t)
    for i, f in enumerate([1760, 2217, 2637, 3520, 4434]):
        st = i * 0.05
        out += np.where(t > st, np.sin(2 * np.pi * f * (t - st)) * np.exp(-(t - st) * 3), 0)
    return out * 0.08


def click():
    t = tt(0.04)
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 150) * 0.4


# ------------------------------------------------------------ music
A = 220.0
prog = [[A, A * 1.2, A * 1.5], [A * 0.89, A * 1.122, A * 1.335], [A * 0.749, A * 0.944, A * 1.122], [A * 0.841, A, A * 1.26]]
music_l, music_r = np.zeros(N), np.zeros(N)
for b in range(8):
    add(pad([f / 2 for f in prog[b % 4]], BAR + 0.4), b * BAR, 1.0, 0, (music_l, music_r))
# plucks: arpeggio 16ths from bar 2, eighths in intro
arp = [0, 1, 2, 1, 2, 0, 1, 2]
for b in range(8):
    step = BEAT / 2 if b == 0 else BEAT / 4
    n = int(BAR / step)
    for k in range(n):
        if b == 0 and k < 2:
            continue
        ch = prog[b % 4]
        f = ch[arp[k % 8]] * (2 if (k // 8) % 2 else 1)
        add(pluck(f), b * BAR + k * step, 0.55 if b else 0.4, -0.4 if k % 2 else 0.4, (music_l, music_r))
L += reverb(music_l, 1.8, 0.35)
R += reverb(music_r, 2.0, 0.35)

kenv = np.zeros(N)
for b in range(8):
    for be in range(4):
        t0 = b * BAR + be * BEAT
        if b >= 1 and not (b == 6 and be >= 2):   # bar 7 second half: break before CTA
            add(kick(), t0, 0.85)
            i0 = int(t0 * SR)
            e = np.exp(-tt(0.4) * 9)
            kenv[i0:i0 + len(e)] = np.maximum(kenv[i0:i0 + len(e)], e[: N - i0])
            if be in (1, 3):
                add(clap(), t0, 0.6)
            add(hat(), t0 + BEAT / 2, 0.55, 0.3)
            if b in (2, 3, 4, 5, 7):
                add(hat(), t0 + BEAT / 4, 0.2, -0.3)
                add(hat(), t0 + 3 * BEAT / 4, 0.2, -0.3)
# sub bass, side-chained
bass = np.zeros(N)
for b in range(1, 8):
    root = prog[b % 4][0] / 4
    t = tt(BAR)
    bass_seg = np.tanh(1.8 * np.sin(2 * np.pi * root * t)) * 0.3
    i0 = int(b * BAR * SR)
    bass[i0:i0 + len(t)] += bass_seg[: N - i0]
bass *= 1 - 0.85 * kenv
L += bass
R += bass

# ------------------------------------------------------------ sound design
add(whoosh(1.2, up=True, lo=150, hi=3000), 0.0, 0.35)        # camera push-in
add(pop(), 1.0, 0.7)                                          # avatar pulse
add(riser(1.0), 1.0, 0.5)
add(impact(2.0), 2.0, 0.9)                                    # logo bursts out
add(whoosh(0.8, up=True, lo=400, hi=10000), 1.85, 0.6)
add(shimmer(1.5), 2.1, 0.8, 0.2)
for i, tw in enumerate([2.25, 2.5, 2.75]):                    # spin swishes
    add(whoosh(0.25, up=i % 2 == 0, lo=1500, hi=9000), tw, 0.25, (-1) ** i * 0.6)
add(impact(1.0), 3.0, 0.45)                                   # name slam
add(whoosh(0.5, up=True, lo=500, hi=9000), 4.75, 0.6)         # transition to services
for i, tc in enumerate([5.0, 6.0, 7.0]):                      # cards fly in
    add(whoosh(0.35, up=False, lo=800, hi=9000), tc - 0.2, 0.5, (-1) ** i * 0.7)
    add(click(), tc, 0.8, (-1) ** i * 0.3)
add(whoosh(0.6, up=True, lo=300, hi=10000), 7.75, 0.7)        # cards out
add(impact(0.8), 9.0, 0.4)
for i, tp in enumerate([9.5, 10.0]):                          # reels pop out
    add(pop(), tp, 0.6, (-1) ** i * 0.5)
    add(whoosh(0.3, up=True, lo=1000, hi=9000), tp - 0.15, 0.4, (-1) ** i * 0.5)
add(riser(1.0), 12.0, 0.55)                                   # build into CTA
add(impact(2.5), 13.0, 1.0)
add(shimmer(2.0), 13.05, 0.8, -0.2)
add(whoosh(0.8, up=True, lo=200, hi=9000), 12.6, 0.6)
for tb in (14.0, 15.0):
    add(click(), tb, 0.6)

fade = np.ones(N)
f0 = int(15.3 * SR)
fade[f0:] = np.linspace(1, 0, N - f0)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L / peak * 1.4) / np.tanh(1.4) * 0.89
R = np.tanh(R / peak * 1.4) / np.tanh(1.4) * 0.89
st = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open("out/soundtrack.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(st.tobytes())
print("soundtrack.wav", st.shape)
