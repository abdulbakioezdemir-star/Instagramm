def tt(d):
    return np.arange(int(d * SR)) / SR


def env(d, a=0.005, r=None):
    t = tt(d)
    e = np.minimum(1, t / max(a, 1e-4))
    if r:
        e = e * np.exp(-t / r)
    return e


def fade_tail(x, f=0.05):
    n = min(len(x), int(f * SR))
    x = x.copy()
    x[-n:] *= np.linspace(1, 0, n)
    return x


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def lp(x, f, o=2):
    return sosfilt(butter(o, f, "lowpass", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "highpass", fs=SR, output="sos"), x)


def add(buf, t0, x, g=1.0):
    s = int(t0 * SR)
    if s >= len(buf) or s < 0:
        return
    e = min(len(buf), s + len(x))
    buf[s:e] += x[: e - s] * g


def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)


# ================= instruments =================
def piano(f, d=2.5, vel=1.0):
    t = tt(d)
    x = np.zeros_like(t)
    for h, (amp, dec) in enumerate([(1, 1.2), (0.5, 0.8), (0.28, 0.5), (0.15, 0.35), (0.08, 0.25), (0.05, 0.18)], 1):
        fh = f * h * (1 + 0.0004 * h * h)
        x += amp * np.sin(2 * np.pi * fh * t) * np.exp(-t / dec)
    x *= np.minimum(1, t / 0.004)
    return fade_tail(lp(x, 4500) * vel * 0.35)


def strings(f, d, att=0.5, rel=0.6, bright=2200):
    t = tt(d + rel)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6))
    x = np.zeros_like(t)
    for det in (-0.006, -0.002, 0.003, 0.007):
        ph = 2 * np.pi * np.cumsum(f * (1 + det) * vib) / SR
        x += ((ph / np.pi) % 2 - 1)
    e = np.minimum(1, t / att)
    e[t > d] *= np.exp(-(t[t > d] - d) / (rel / 3))
    return lp(x * e, bright) * 0.07


def pizz(f, vel=1.0):
    d = 0.4
    t = tt(d)
    x = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)) * np.exp(-t / 0.07)
    x *= np.minimum(1, t / 0.002)
    return lp(x, 3000) * 0.28 * vel


def taiko(vel=1.0, low=True):
    d = 0.9
    t = tt(d)
    f0 = 95 if low else 160
    f = f0 * np.exp(-t * 6) + f0 * 0.55
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.22)
    skin = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t / 0.03)
    return (body * 0.9 + skin * 0.35) * vel * 0.8


def braam(root=38, d=2.4):
    t = tt(d)
    x = np.zeros_like(t)
    for m, g in [(root, 1.0), (root + 12, 0.7), (root + 19, 0.45)]:
        for det in (-0.004, 0.0, 0.005):
            ph = 2 * np.pi * np.cumsum(np.full(len(t), mtof(m) * (1 + det))) / SR
            x += g * ((ph / np.pi) % 2 - 1)
    # opening then closing filter
    out = np.zeros_like(x)
    seg = int(0.02 * SR)
    for k in range(0, len(x), seg):
        tc = k / SR
        fc = 200 + 2600 * np.exp(-tc * 1.3) * min(1, tc / 0.05)
        out[k:k + seg] = lp(x[max(0, k - 2000):k + seg], fc)[-len(x[k:k + seg]):]
    e = np.minimum(1, t / 0.02) * np.exp(-t / 1.1)
    return fade_tail(out * e * 0.12, 0.3)


def harp_gliss(notes, step=0.045, vel=1.0):
    out = np.zeros(int((len(notes) * step + 1.5) * SR))
    for k, m in enumerate(notes):
        f = mtof(m)
        t = tt(1.4)
        x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t / 0.45) * np.minimum(1, t / 0.002)
        add(out, k * step, x, 0.12 * vel)
    return out


def bell(f, d=1.2, g=0.15):
    t = tt(d)
    x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.2)) * np.exp(-t / 0.4)
    return x * np.minimum(1, t / 0.002) * g


def sparkle(n=6, base=88):
    out = np.zeros(int(1.6 * SR))
    scale = [0, 2, 4, 7, 9, 12, 14, 16]
    for k in range(n):
        add(out, k * 0.06, bell(mtof(base + scale[k % len(scale)]), 1.0, 0.07))
    return out


def heartbeat():
    out = np.zeros(int(0.7 * SR))
    for k, (dt, g) in enumerate([(0, 1.0), (0.2, 0.7)]):
        d = 0.25
        t = tt(d)
        f = 70 * np.exp(-t * 10) + 40
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07) * np.minimum(1, t / 0.003)
        add(out, dt, x, g)
    return out * 0.9


def riser(d=1.2):
    t = tt(d)
    n = rng.standard_normal(len(t))
    out = np.zeros_like(n)
    seg = int(0.03 * SR)
    for k in range(0, len(n), seg):
        fc = 400 + 7000 * (k / len(n)) ** 2
        out[k:k + seg] = bp(n[max(0, k - 3000):k + seg], fc * 0.7, min(fc * 1.3, 20000))[-len(n[k:k + seg]):]
    return out * (t / d) ** 2 * 0.35


def whoosh(d=0.45):
    n = rng.standard_normal(int(d * SR))
    t = tt(d)
    shape = np.sin(np.pi * t / d) ** 2
    return (bp(n, 300, 1500) * (1 - t / d) + bp(n, 1500, 6000) * (t / d)) * shape * 0.5


def pageflip():
    d = 0.12
    n = bp(rng.standard_normal(int(d * SR)), 1500, 7000) * np.sin(np.pi * tt(d) / d) ** 1.5
    return n * 0.5


def pop(f0=420, f1=950, d=0.09):
    t = tt(d)
    f = f0 + (f1 - f0) * (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.002, 0.03)


def click(hi=True):
    d = 0.018
    n = rng.standard_normal(int(d * SR)) * env(d, 0.0005, 0.004)
    return hp(n, 2500 if hi else 900) * 0.45


def thud():
    d = 0.35
    t = tt(d)
    f = 120 * np.exp(-t * 8) + 45
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.002, 0.09)
    return x * 0.9 + lp(rng.standard_normal(len(t)), 2000) * env(d, 0.001, 0.02) * 0.4


def buzzer():
    d = 0.42
    t = tt(d)
    x = np.sign(np.sin(2 * np.pi * 140 * t)) + 0.6 * np.sign(np.sin(2 * np.pi * 147 * t))
    return lp(x, 1600) * env(d, 0.005) * np.minimum(1, (d - t) / 0.05) * 0.15


def scratch():
    d = 0.55
    t = tt(d)
    f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3.2 * t)) * np.exp(-t * 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = (ph / np.pi) % 2 - 1
    return (saw * 0.35 + bp(rng.standard_normal(len(t)), 800, 5000) * 0.6) * env(d, 0.003) * np.minimum(1, (d - t) / 0.08) * 0.6


def trombone():
    notes = [(293.7, 0.32), (277.2, 0.32), (261.6, 0.32), (246.9, 1.1)]
    out = []
    for k, (f, d) in enumerate(notes):
        t = tt(d)
        vib = 1 + (0.025 * np.sin(2 * np.pi * 6 * t) * np.minimum(1, t / 0.3) if k == 3 else 0)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        x = sum(np.sin(h * ph) / h ** 0.9 for h in range(1, 9))
        out.append(lp(x, 2200) * np.minimum(1, t / 0.04) * np.minimum(1, (d - t) / 0.06))
    return np.concatenate(out) * 0.2


def coin():
    d = 0.3
    t = tt(d)
    return (np.sin(2 * np.pi * 2637 * t) + 0.6 * np.sin(2 * np.pi * 3520 * t)) * env(d, 0.001, 0.08) * 0.13


def cymbal_swell(d=1.0):
    n = hp(rng.standard_normal(int(d * SR)), 5000)
    return n * (tt(d) / d) ** 3 * 0.25
