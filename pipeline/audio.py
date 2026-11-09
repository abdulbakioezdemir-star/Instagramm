import numpy as np, json, subprocess
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
TL = json.load(open("/home/claude/timeline.json"))
TOTAL = TL["total"]
EV = TL["ev"]
SC = {n: (a, b) for n, a, b in TL["scenes"]}
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(3)
WT = {l["id"]: [w[0] for w in l["words"]] for l in TL["lines"]}
LN = {l["id"]: l for l in TL["lines"]}


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


# ================= SFX track =================
sfx = np.zeros(N)
# intro flips + big hit
for ft in [0.0, 0.2, 0.38, 0.54, 0.68, 0.8, 0.91, 1.01, 1.1, 1.18]:
    add(sfx, ft, pageflip(), 0.5)
add(sfx, 1.25, thud(), 0.8)
add(sfx, 1.25, cymbal_swell(0.0001 + 0.01), 0)
# hook
hk = SC["hook"][0]
add(sfx, hk - 0.15, whoosh(0.35), 0.4)
j = 0
while hk + 0.2 + j * 0.3 < WT["a01"][6] - 0.25:
    add(sfx, hk + 0.2 + j * 0.3 + 0.15, whoosh(0.18), 0.18)
    j += 1
add(sfx, WT["a01"][6], thud(), 0.6)
add(sfx, WT["a01"][6] + 0.05, buzzer(), 0.6)
add(sfx, EV["notif"], bell(1318.5, 0.8, 0.2))
add(sfx, EV["notif"] + 0.12, bell(1760, 0.9, 0.2))
add(sfx, EV["notif"] + 0.25, heartbeat(), 0.8)
# match
add(sfx, EV["match"] - 0.1, whoosh(0.4), 0.4)
add(sfx, EV["match"] + 0.05, harp_gliss([62, 66, 69, 74, 78, 81, 86, 90, 93], 0.04), 1.4)
add(sfx, EV["match"] + 0.1, sparkle(8, 84), 1.2)
for k in range(5):
    add(sfx, EV["match"] + 0.55 + k * 0.85, heartbeat(), 0.6)
add(sfx, WT["a03"][6], pop(300, 900, 0.12), 0.3)
# chat
add(sfx, EV["chat"] - 0.1, whoosh(0.4), 0.35)
add(sfx, EV["l01msg"], sparkle(4, 91), 1.0)
add(sfx, EV["l01msg"], pop(900, 500, 0.12), 0.3)
rr = np.random.default_rng(9)
t = EV["type0"]
while t < EV["type1"]:
    add(sfx, t, click(), 0.5)
    t += rr.uniform(0.05, 0.11)
add(sfx, EV["send"], pop(500, 1200, 0.12), 0.4)
add(sfx, EV["l02msg"], pop(900, 500, 0.12), 0.35)
add(sfx, EV["l02msg"], sparkle(3, 91), 0.8)
add(sfx, EV["fail"], thud(), 0.7)
add(sfx, EV["fail"] + 0.05, buzzer(), 0.7)
# secret
add(sfx, SC["secret"][0] - 0.1, whoosh(0.4), 0.35)
add(sfx, WT["a06"][9], thud(), 0.75)
add(sfx, EV["versions"] + 0.1, pop(), 0.25)
add(sfx, EV["versions"] + 0.35, pop(), 0.25)
add(sfx, EV["versions"] + 0.6, bell(880, 0.4, 0.12))
# date
add(sfx, SC["date"][0] - 0.1, whoosh(0.4), 0.35)
add(sfx, EV["l03msg"], pop(900, 500, 0.12), 0.3)
add(sfx, EV["l03msg"], sparkle(5, 88), 1.0)
tsun = WT["l03"][12]
add(sfx, tsun - 0.3, harp_gliss([65, 69, 72, 77, 81, 84, 89], 0.06), 1.3)
add(sfx, WT["a08"][1], pop(500, 1200, 0.12), 0.35)
add(sfx, EV["freeze"], scratch(), 0.85)
add(sfx, EV["freeze"] + 0.3, thud(), 0.7)
add(sfx, EV["freeze"] + 0.3, braam(33, 1.6), 0.8)
# money
add(sfx, SC["money"][0] - 0.1, whoosh(0.4), 0.35)
for k in (0, 6, 10):
    add(sfx, WT["a10"][k], pop(), 0.25)
for k in range(4):
    add(sfx, WT["a10"][1] + k * 0.12, coin(), 0.8)
add(sfx, LN["a10"]["end"] + 0.1, pop(), 0.25)
add(sfx, EV["tromb"], trombone(), 1.0)
# poll
add(sfx, SC["poll"][0] - 0.15, whoosh(0.45), 0.4)
add(sfx, WT["a11"][4], pop(), 0.3)
add(sfx, WT["a11"][8], pop(), 0.3)
add(sfx, WT["a13"][3] - 0.1, pop(), 0.3)

# ================= MUSIC track =================
mus = np.zeros(N)


def chord_pad(t0, t1, chords, bar, oct_=0, g=1.0, bright=2000):
    k = 0
    t = t0
    while t < t1:
        ch = chords[k % len(chords)]
        d = min(bar, t1 - t)
        for m in ch:
            add(mus, t, strings(mtof(m + oct_), d, att=min(0.5, d / 3), rel=0.8, bright=bright), g)
        t += bar
        k += 1


def piano_arp(t0, t1, chords, bar, g=1.0, pattern=(0, 1, 2, 3, 2, 1), sub=6):
    k = 0
    t = t0
    while t < t1:
        ch = chords[k % len(chords)]
        add(mus, t, piano(mtof(ch[0] - 12), 3.0, 0.8), g)
        notes = [ch[0], ch[1], ch[2], ch[0] + 12]
        for j in range(sub):
            ts = t + j * bar / sub
            if ts >= t1:
                break
            add(mus, ts, piano(mtof(notes[pattern[j % len(pattern)]] + 12), 1.6, 0.55), g)
        t += bar
        k += 1


# --- intro: taiko build + braam
for k, ft in enumerate([0.0, 0.38, 0.68, 0.91, 1.1]):
    add(mus, ft, taiko(0.6 + k * 0.1, low=k % 2 == 0))
add(mus, 0.05, riser(1.2), 1.0)
add(mus, 1.25, braam(38, 2.6), 1.0)
add(mus, 1.25, taiko(1.2))
add(mus, 1.25, cymbal_swell(0.6)[::-1], 1.0)

# --- hook: comedic-cinematic pizz ostinato (D minor), 104 bpm
beat = 60 / 104
t0, t1 = SC["hook"]
seq = [50, 57, 53, 57, 50, 57, 55, 57]
t = t0 + 0.1
k = 0
while t < t1 - 0.05:
    add(mus, t, pizz(mtof(seq[k % 8]), 1.0 if k % 2 == 0 else 0.7))
    if k % 4 == 0:
        add(mus, t, taiko(0.35))
    t += beat / 2
    k += 1
chord_pad(t0 + 0.1, t1, [[50, 57, 62], [46, 53, 58], [48, 55, 60], [45, 52, 57]], 4 * beat, g=0.6, bright=1400)

# --- match + chat: romantic piano & strings (D major-ish), 84 bpm
rb = 60 / 84 * 4
rom = [[62, 66, 69], [57, 61, 64], [59, 62, 66], [55, 59, 62]]  # D A Bm G
t0 = SC["match"][0]
t1 = EV["fail"]
piano_arp(t0, t1, rom, rb, g=0.9)
chord_pad(t0, t1, rom, rb, oct_=-12, g=0.55, bright=1600)
chord_pad(t0 + 2 * rb, t1, rom, rb, oct_=0, g=0.3, bright=2600)

# after fail: sparse piano until scene end
t0, t1 = EV["fail"] + 0.6, SC["english"][1]
piano_arp(t0, t1, [[57, 60, 64]], rb, g=0.45, pattern=(0, 2), sub=2)

# --- secret: sneaky pizz (tiptoe) in E minor
t0, t1 = SC["secret"]
sb = 60 / 112
seq = [52, None, 55, None, 59, 58, 57, None, 52, None, 55, None, 50, 51, 52, None]
t = t0 + 0.15
k = 0
while t < t1:
    n = seq[k % len(seq)]
    if n:
        add(mus, t, pizz(mtof(n), 0.9))
        add(mus, t, pizz(mtof(n - 12), 0.6))
    if k % 4 == 0:
        add(mus, t, bell(mtof(88 if (k // 4) % 2 == 0 else 91), 0.3, 0.03))
    t += sb / 2
    k += 1

# --- date: romantic again, bigger swell into "Sonnenuntergang"
t0 = SC["date"][0]
t1 = EV["freeze"]
rom2 = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]  # C G Am F
piano_arp(t0, t1, rom2, rb, g=0.85)
chord_pad(t0, t1, rom2, rb, oct_=-12, g=0.5, bright=1600)
chord_pad(tsun - 0.3, t1, [[60, 64, 67, 72]], t1 - tsun + 0.3, oct_=0, g=0.55, bright=3200)

# --- money: sad solo piano (A minor), slow
t0, t1 = SC["money"][0] + 0.2, EV["tromb"] - 0.1
sad = [[57, 60, 64], [53, 57, 60], [52, 55, 59], [52, 56, 59]]
piano_arp(t0, t1, sad, 60 / 70 * 4, g=0.7, pattern=(0, 1, 2, 1), sub=4)

# --- poll: epic build (D minor -> D major hit)
t0, t1 = SC["poll"]
eb = 60 / 120
cta = EV["cta"]
osti = [62, 69, 65, 69, 62, 69, 65, 69, 62, 70, 65, 70, 62, 69, 64, 69]
t = t0 + 0.3
k = 0
while t < cta:
    add(mus, t, pizz(mtof(osti[k % 16] - 12), 0.8))
    add(mus, t, strings(mtof(osti[k % 16]), eb / 4 * 0.9, att=0.01, rel=0.05, bright=3000), 0.6)
    if k % 8 == 0:
        add(mus, t, taiko(0.7))
    if k % 8 == 4:
        add(mus, t, taiko(0.45, low=False))
    t += eb / 4
    k += 1
chord_pad(t0 + 0.3, cta, [[50, 57, 62], [46, 53, 58], [48, 55, 60], [45, 52, 57]], 4 * eb, oct_=-12, g=0.6, bright=1800)
add(mus, cta - 1.2, riser(1.2), 0.9)
add(mus, cta, braam(38, 3.0), 0.9)
add(mus, cta, taiko(1.3))
end_ch = [62, 66, 69, 74]
chord_pad(cta, TOTAL, [end_ch], TOTAL - cta, oct_=0, g=0.75, bright=3500)
for k, m in enumerate([74, 78, 81, 86]):
    add(mus, cta + 0.05 + k * 0.1, bell(mtof(m), 1.6, 0.12))
for k in range(int((TOTAL - cta) / eb)):
    add(mus, cta + k * eb, taiko(0.5 if k % 2 == 0 else 0.3, low=k % 2 == 0))

# reverb (hall)
ir_t = tt(2.4)
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55)
ir = lp(ir, 6000)
ir /= np.sqrt(np.sum(ir ** 2))
wet = fftconvolve(mus, ir)[:N]
mus = mus * 0.75 + wet * 0.55
wets = fftconvolve(sfx, ir)[:N]
sfx = sfx + wets * 0.15

fe = int((TOTAL - 1.0) * SR)
mus[fe:] *= np.linspace(1, 0, N - fe) ** 2
mus = mus[: int(TOTAL * SR)]
sfx = sfx[: int(TOTAL * SR)]

voice = np.load("/home/claude/ahmed.npy").astype(np.float64) + np.load("/home/claude/lena.npy")
voice = voice[: int(TOTAL * SR)]


def wav(name, x, norm=None):
    if norm:
        x = x / (np.abs(x).max() + 1e-9) * norm
    x = np.clip(x, -1, 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", f"/home/claude/{name}.wav"], input=x.tobytes(), check=True)


wav("voice", voice)
wav("sfx", sfx, 0.8)
wav("music", mus, 0.9)
print("ok")
