# Tag 3 "Kamera kaputt" (Abstimmung Tag 2: B 7:0) – PART=1: 12 Uhr Cliffhanger, PART=2: 18 Uhr mit A/B
# Setup (einmal pro Lauf), siehe README.md in diesem Ordner:
#   /home/claude/{draw.py,scenes.py,audio.py,mix.sh,tts.py,fonts,timeline.json(dummy)} und /home/claude/tag2 (Hilfsmodul)
# Nutzung: python3 tag03.py <PART> tts | info | preview t1 t2 .. | scene <name..> | audio | all
import sys, json, math, subprocess, os, random
sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/home/claude/tag2")
import numpy as np, skia
from draw import *
from scenes import glow, float_hearts, vignette, doener
import tag2 as T2  # tiles, stamp, shopfront, broken_cam

PART = int(sys.argv[1])
FPS, SR = 30, 48000
SRC = os.path.dirname(os.path.abspath(__file__))
D = f"/home/claude/tag03_work/teil{PART}"
OUT = D + "/out"
os.makedirs(OUT, exist_ok=True)
# Stimmen (per Spektral-Abgleich mit Tag 2 v2 bestimmt, 2026-11-10)
VOICE = {"A": ("de-DE-FlorianMultilingualNeural", "+0Hz", "+7%"),
         "L": ("de-DE-SeraphinaMultilingualNeural", "+0Hz", "+0%"),
         "K": ("de-DE-ConradNeural", "+0Hz", "+0%")}
TEXT = {}
for ln in open(f"{SRC}/lines{PART}.tsv", encoding="utf-8"):
    i, who, txt = ln.rstrip("\n").split("\t")
    TEXT[i] = (who, txt)
DISPTXT = {}
for ln in open(f"{SRC}/disp.tsv", encoding="utf-8"):
    i, txt = ln.rstrip("\n").split("\t")
    DISPTXT[i] = txt

if len(sys.argv) > 2 and sys.argv[2] in ("tts", "all"):
    procs = []
    for i, (who, txt) in TEXT.items():
        v, p, r = VOICE[who]
        procs.append(subprocess.Popen(["python3", "/home/claude/tts.py", txt, v, f"{D}/{i}.mp3", p, r]))
    for pr in procs:
        pr.wait()
    for i in TEXT:
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f"{D}/{i}.mp3", "-ar", str(SR), "-ac", "1", f"{D}/{i}.wav"], check=True)
    print("tts ok", flush=True)


def load(i):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f"{D}/{i}.wav", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


AUD = {i: load(i) for i in TEXT}
DUR = {i: len(a) / SR for i, a in AUD.items()}
ST, SC, EV = {}, {}, {}


def put(i, t):
    ST[i] = t
    return t + DUR[i]


if PART == 1:
    e = put("a01", 0.05)
    EV["freeze"] = e + 0.25
    SC["cold"] = (0.0, EV["freeze"] + 0.8)
    s = SC["cold"][1]
    e = put("a02", s + 0.15)
    SC["vote"] = (s, e + 0.35)
    s = SC["vote"][1]
    e = put("a03", s + 0.25)
    SC["call"] = (s, e + 0.15)
    s = SC["call"][1]
    e = put("l01", s + 0.15)
    EV["nstamp"] = e - 0.35
    EV["cfreeze"] = e + 0.55  # Pause + Reaktion vor der Schlusszeile
    e = put("a04", EV["cfreeze"] + 0.25)
    SC["nose"] = (s, e + 1.25)
    NOSE_LINES, CLIFF = ["l01"], "a04"
    ORDER = ["cold", "vote", "call", "nose"]
else:
    s = 0.0
    e = put("r01", 0.3)
    e = put("a10", e + 0.25)
    EV["filter"] = ST["a10"] + 0.0
    e = put("l02", e + 0.25)
    e = put("a11", e + 0.2)
    e = put("l03", e + 0.35)
    EV["cfreeze"] = e + 0.2
    SC["nose"] = (s, EV["cfreeze"] + 0.5)
    s = SC["nose"][1]
    e = put("a07", s + 0.2)
    SC["poll"] = (s, e + 2.0)
    NOSE_LINES, CLIFF = ["r01", "a10", "l02", "a11", "l03"], None
    ORDER = ["nose", "poll"]
TOTAL = SC[ORDER[-1]][1]

WT, WTOK = {}, {}
for i in TEXT:
    w = json.load(open(f"{D}/{i}.mp3.json"))
    o0 = w[0][0]
    WT[i] = [(ST[i] + o - o0, t) for o, d, t in w]
DISP = {}
for i in TEXT:
    toks = (DISPTXT.get(i) or TEXT[i][1]).split()
    n, m = len(toks), len(WT[i])
    if n == m:
        times = [x[0] for x in WT[i]]
    else:  # robust: Token gleichmaessig auf Wortgrenzen verteilen
        print("WARN token mismatch", i, n, m, file=sys.stderr)
        times = [WT[i][round(k * (m - 1) / max(n - 1, 1))][0] for k in range(n)]
    DISP[i] = toks
    WTOK[i] = times


def wt(i, k):
    return WTOK[i][min(k, len(WTOK[i]) - 1)]


def lend(i):
    return ST[i] + DUR[i]


CHUNKS = []
for i in TEXT:
    toks = DISP[i]
    cur = []
    for k, tok in enumerate(toks):
        cur.append((tok, WTOK[i][k]))
        if (tok[-1] in ".!?:…" and len(cur) >= 2) or len(cur) >= 5 or k == len(toks) - 1:
            CHUNKS.append(dict(who=TEXT[i][0], words=cur, start=cur[0][1] - 0.06, line=i))
            cur = []
CHUNKS.sort(key=lambda c: c["start"])
for k, ch in enumerate(CHUNKS):
    nxt = CHUNKS[k + 1]["start"] if k + 1 < len(CHUNKS) else 1e9
    ch["end"] = min(nxt, ST[ch["line"]] + DUR[ch["line"]] + 0.4)

N = int(TOTAL * SR) + 1
TR = {w: np.zeros(N, np.float32) for w in "ALK"}
for i, a in AUD.items():
    s0 = int(ST[i] * SR)
    TR[TEXT[i][0]][s0:s0 + len(a)] += a[: N - s0]
hop = SR // FPS
nf = int(TOTAL * FPS) + 2


def envelope(x):
    en = np.array([np.sqrt(np.mean(x[k * hop:(k + 1) * hop] ** 2) + 1e-12) if k * hop < N else 0 for k in range(nf)])
    nzv = en[en > 1e-3]
    en = np.clip(en / max(np.percentile(nzv, 95) if len(nzv) else 1, 1e-6), 0, 1)
    for k in range(1, nf):
        en[k] = max(en[k], en[k - 1] * 0.55)
    return en


ENV_A = envelope(TR["A"])
ENV_K = ENV_A


def mouth(t, env=None):
    env = ENV_A if env is None else env
    return float(env[min(max(int(t * FPS), 0), nf - 1)])


def base(t, **kw):
    d = dict(mouth=mouth(t), blink=(t % 3.3) < 0.11)
    d.update(kw)
    return d


def caps(c, t, cy=1050, tail=560, only=None):
    for ch in CHUNKS:
        if only is not None and ch["line"] not in only:
            continue
        if ch["start"] <= t < ch["end"]:
            caption(c, t, ch["who"], ch["words"], cy, tail_x=(tail if ch["who"] == "A" else None), appear=ch["start"])


def shake(c, t, t0, amp=28, dur=0.35):
    if t0 <= t < t0 + dur:
        k = 1 - (t - t0) / dur
        r = random.Random(int(t * 60))
        c.translate(r.uniform(-amp, amp) * k, r.uniform(-amp, amp) * k)


def tag_pill(c, t, t0):
    c.save()
    pop(c, t, t0, 540, 110)
    pill(c, f"TAG 3 · TEIL {PART}/2", 540, 110, 44, fill=INK, col="#FFD84D", name="black")
    c.restore()


def ice_cube(c, x, y, s=1.0, rot=0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    rrect(c, -60 * s, -60 * s, 120 * s, 120 * s, 22 * s, "#CFF1FF", 7, ink="#5FA9C9")
    rrect(c, -38 * s, -40 * s, 40 * s, 16 * s, 8 * s, "#FFFFFF", 0, a=200)
    c.restore()


def speed_lines(c, t, n=16, a=110):
    r = random.Random(int(t * 30))
    for j in range(n):
        y = r.uniform(150, 1800)
        x = r.uniform(-200, 800)
        c.drawLine(x, y, x + r.uniform(150, 400), y, strokep("#FFFFFF", 6, a))



# ---------------- shower base (used twice) ----------------
def shower_room(c, t, cold, steam=True):
    T2.tiles(c, "#9ED8F0" if not cold else "#BFE6FF", "#7FC3E0" if not cold else "#9FD4F5")
    if steam and not cold:
        for k in range(6):
            yy = 900 - ((t * 60 + k * 120) % 700)
            oval(c, 300 + k * 90 + 30 * math.sin(t + k), yy, 90, 50, "#FFFFFF", 0, a=70)
    c.drawLine(760, 0, 760, 420, strokep("#8E9AA6", 26))
    c.drawLine(760, 420, 640, 520, strokep("#8E9AA6", 26))
    sh = skia.Path()
    sh.moveTo(560, 560)
    sh.quadTo(640, 450, 720, 560)
    sh.close()
    drawpath(c, sh, "#BFC7CF", 9)
    r = random.Random(int(t * 30))
    wcol = "#3BA3FF" if not cold else "#BDEBFF"
    for k in range(34 if cold else 26):
        x = r.uniform(420, 860)
        y = 600 + ((t * 1000 + k * 97) % 900)
        c.drawLine(x, y, x - 6, y + 34, strokep(wcol, 8 if cold else 7))
    cur = skia.Path()
    cur.moveTo(0, 200)
    for k in range(7):
        cur.quadTo(30 + k * 45, 240 if k % 2 else 180, 45 + k * 45, 200)
    cur.lineTo(315, 1920)
    cur.lineTo(0, 1920)
    cur.close()
    drawpath(c, cur, "#FF8FC2", 8)
    c.drawLine(0, 190, 1080, 190, strokep("#8E9AA6", 14))
    if cold:
        for k in range(9):
            x = 60 + k * 120
            p = skia.Path()
            p.moveTo(x - 22, 0)
            p.lineTo(x + 22, 0)
            p.lineTo(x, 70 + (k % 3) * 40)
            p.close()
            drawpath(c, p, "#E6F7FF", 5, ink="#7FC3E0")


def frozen_ahmed(c, t, st, x=540):
    sh = math.sin(t * 70) * 8
    c.save()
    c.translate(sh, 0)
    ahmed(c, t, x, 1840, 1.0, st)
    # frost overlay on body
    c.restore()



def small_head(c, t, x, y, s, st):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.translate(-585, -470)
    ahmed_head(c, st, t)
    c.restore()


def rec_dot(c, t, x, y, label="KAMERA AN"):
    a = 255 if (t % 0.8) < 0.5 else 90
    w = tw(label, "black", 40) + 90
    rrect(c, x - w / 2, y - 38, w, 76, 38, "#1A1A1A", 0, a=220)
    circ(c, x - w / 2 + 38, y, 15, "#FF3B3B", a=a)
    text(c, label, x + 18, y + 14, "black", 40, "#FFFFFF")


def call_phone(c, t, sc=1.0, preview=None):
    """verbundener Videoanruf: Lena gross, Selfie-Vorschau unten rechts"""
    c.save()
    c.translate(540, 560)
    c.scale(sc, sc)
    c.translate(-540, -560)
    rrect(c, 250 + 14, 200 + 14, 580, 720, 60, INK)
    rrect(c, 250, 200, 580, 720, 60, "#1C1C2B", 9)
    lena_avatar(c, 540, 470, 150)
    text(c, "Lena · 00:0" + str(int(t) % 10), 540, 300, "xbold", 34, "#FFFFFF")
    # Selfie-Vorschau
    rrect(c, 640, 640, 160, 240, 22, "#2A2A3A", 6, ink="#FFFFFF")
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(643, 643, 154, 234))
    shower_mini = "#BFE6FF"
    c.drawRect(skia.Rect.MakeXYWH(643, 643, 154, 234), fillp(shower_mini))
    small_head(c, t, 720, 760, 0.17, preview or base(t, cap=True, eyes="wide", mshape="grimace", worried=True))
    c.restore()
    c.restore()


def s_cold(c, t):
    fr = EV["freeze"]
    tt = min(t, fr)
    c.save()
    shake(c, tt, 0.0, 16, 0.4)
    shower_room(c, tt, True, steam=False)
    call_phone(c, tt, 1.0)
    st = base(tt, cap=True, eyes="wide", mshape="grimace" if mouth(tt) < 0.15 else "o", sweat=4, worried=True, rarm=-150)
    frozen_ahmed(c, tt, st)
    # Hook-Text sofort (<= 8 Woerter)
    c.save()
    pop(c, tt, 0.0, 540, 1080, d=0.25)
    pill(c, "MEINE KAMERA WAR AN.", 540, 1080, 66, fill="#E0245E", name="black", padx=40, pady=26)
    c.restore()
    rec_dot(c, tt, 540, 990)
    tk = wt("a01", len(DISP["a01"]) - 1) - 0.05
    T2.stamp(c, tt, tk, "LIVE!", 760, 330, "#E5484D", 110, 10)
    c.restore()
    if t >= fr:
        k = clamp((t - fr) / 0.2)
        c.drawRect(skia.Rect.MakeWH(W, H), fillp("#000000", int(150 * k)))
        r = random.Random(int(t * 30))
        for j in range(10):
            y = r.uniform(0, H)
            c.drawRect(skia.Rect.MakeXYWH(0, y, W, r.uniform(6, 26)), fillp("#FFFFFF", 60))
        c.save()
        pop(c, t, fr + 0.05, 540, 820)
        for dx in (-70, 10):
            p = skia.Path()
            p.moveTo(540 + dx + 60, 760)
            p.lineTo(540 + dx, 820)
            p.lineTo(540 + dx + 60, 880)
            p.close()
            c.drawPath(p, fillp("#FFFFFF"))
        text(c, "1 MINUTE VORHER", 540, 1010, "black", 84, "#FFFFFF", stroke=14)
        text(c, "1 MINUTE VORHER", 540, 1010, "black", 84, "#FFFFFF")
        c.restore()
    else:
        caps(c, t, cy=1250)


def s_vote(c, t):
    t0 = SC["vote"][0]
    background(c, t, "#F9D85E", "#FBE07A")
    glow(c, 540, 560, 520, "#FFFFFF", 90)
    c.save()
    s = back(prog(t, t0 + 0.05, 0.35))
    c.translate(540, 560)
    c.scale(s, s)
    c.translate(-540, -560)
    card(c, 90, 330, 900, 460, "#FFFFFF", 34, 14, 8)
    text(c, "Eure Abstimmung", 540, 420, "black", 50, INK)
    for k, (lab, txt, col, n) in enumerate([("A", "Emre geht ran", "#F3F1EE", "0 Stimmen"), ("B", "Kamera kaputt", "#8FD3FF", "7 Stimmen")]):
        x0 = 150 + k * 420
        wob = math.sin(t * 9 + k * 3) * 4 * k
        c.save()
        c.translate(x0 + 180, 600)
        c.rotate(wob)
        c.translate(-(x0 + 180), -600)
        rrect(c, x0, 470, 360, 260, 30, col, 6)
        circ(c, x0 + 180, 545, 44, INK)
        text(c, lab, x0 + 180, 563, "black", 52, "#FFFFFF")
        text(c, txt, x0 + 180, 640, "black", 38, INK)
        text(c, n, x0 + 180, 708, "xbold", 34, "#555555")
        c.restore()
    c.restore()
    tb = wt("a02", 4) - 0.05
    c.save()
    shake(c, t, tb, 22, 0.3)
    T2.stamp(c, t, tb, "7 : 0", 540, 880, "#E0245E", 120, -8)
    c.restore()
    st = base(t, rarm=-150)
    sad_t = wt("a02", 9) - 0.05
    if t < sad_t:
        st.update(eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", wave=0.4)
    else:
        st.update(eyes="sad", mshape="grimace" if mouth(t) < 0.12 else "o", worried=True, larm=-20, rarm=-30)
    if tb < t < tb + 0.6:
        st["hop"] = max(0, math.sin((t - tb) * 8) * 60)
    ahmed(c, t, 540, 1840, 1.0, st)
    tag_pill(c, t, t0)
    caps(c, t)


def s_call(c, t):
    t0 = SC["call"][0]
    clip = iris(c, t, t0, "#BFE6FF", prev="#F9D85E", cy=600, d=0.35)
    c.save()
    shower_room(c, t, True, steam=False)
    s = back(prog(t, t0 + 0.15, 0.35))
    call_phone(c, t, s)
    for k in range(2):
        ice_cube(c, 330 + k * 420, 1700, 0.8, 8 - k * 16)
    # Daumen hoch, super selbstbewusst
    st = base(t, cap=True, eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", rarm=-160, wave=0.3)
    frozen_ahmed(c, t, st)
    tk = wt("a03", 6) - 0.05  # "Alles schwarz."
    if t > tk:
        # Erwartung: Bildschirm "schwarz"? -> nein, Vorschau zeigt alles
        c.save()
        pop(c, t, tk, 720, 1000, kind="el")
        pill(c, "KAMERA: KAPUTT (glaubt er)", 540, 1000, 46, fill="#2FBF71", name="black", padx=30, pady=20)
        c.restore()
    c.restore()
    tag_pill(c, t, t0 + 0.05)
    caps(c, t, cy=1180)
    if clip:
        c.restore()


def nose_cam(c, t, st, filt=False):
    """Front-Kamera von unten: Kinn, Nasenloecher, Duschvorhang"""
    m = st.get("mouth", 0)
    sh = math.sin(t * 70) * 6
    c.drawRect(skia.Rect.MakeWH(W, H), fillp("#BFE6FF"))
    # Duschdecke + Eiszapfen
    for k in range(9):
        x = 60 + k * 120
        p = skia.Path()
        p.moveTo(x - 22, 0)
        p.lineTo(x + 22, 0)
        p.lineTo(x, 70 + (k % 3) * 40)
        p.close()
        drawpath(c, p, "#E6F7FF", 5, ink="#7FC3E0")
    cur = skia.Path()
    cur.moveTo(0, 0)
    cur.lineTo(170, 0)
    cur.quadTo(150, 900, 190, 1920)
    cur.lineTo(0, 1920)
    cur.close()
    drawpath(c, cur, "#FF8FC2", 8)
    c.save()
    c.translate(sh, 0)
    # Haare/Duschhaube ganz oben klein
    oval(c, 540, 420, 260, 120, "#FFFFFF", 10)
    # Gesicht von unten: oben schmal, unten breit (Kinn nah an der Kamera)
    fp = skia.Path()
    fp.moveTo(330, 470)
    fp.cubicTo(250, 800, 120, 1400, 220, 1920)
    fp.lineTo(860, 1920)
    fp.cubicTo(960, 1400, 830, 800, 750, 470)
    fp.close()
    drawpath(c, fp, SKIN, 14)
    # Augen klein & besorgt
    for dx in (-90, 90):
        oval(c, 540 + dx, 560, 34, 26, "#FFFFFF", 7)
        circ(c, 540 + dx, 552, 12, INK)
    c.drawLine(420, 510, 480, 525, strokep(INK, 12))
    c.drawLine(660, 510, 600, 525, strokep(INK, 12))
    # Nase von unten: grosse Spitze + riesige Nasenloecher
    oval(c, 540, 900, 230, 180, "#E8B48E", 12)
    flare = 1 + 0.12 * math.sin(t * 6) + m * 0.15
    for dx in (-95, 95):
        oval(c, 540 + dx, 950, 62 * flare, 92 * flare, "#4A2A1C", 8)
        # Haerchen
        for j in range(3):
            c.drawLine(540 + dx - 20 + j * 20, 1010, 540 + dx - 26 + j * 24, 1040, strokep(INK, 5))
    # Mund
    oval(c, 540, 1220, 170, 22 + m * 70, "#73302F", 10)
    # Doppelkinn
    for k in range(3):
        a = skia.Path()
        a.moveTo(300 + k * 20, 1460 + k * 110)
        a.quadTo(540, 1560 + k * 120, 780 - k * 20, 1460 + k * 110)
        c.drawPath(a, strokep("#B5835F", 12))
    # Bartstoppeln
    r = random.Random(3)
    for k in range(60):
        x, y = r.uniform(300, 780), r.uniform(1280, 1800)
        circ(c, x, y, 5, "#6B4A36", a=150)
    c.restore()
    if filt:
        # Pseudo-Filter: Schneeflocken + Label
        r = random.Random(int(t * 10))
        for k in range(18):
            x = (k * 137 + t * 80) % 1080
            y = (k * 211 + t * 260) % 1920
            star(c, x, y, 14, "#FFFFFF", 3)
    # Videoanruf-UI
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 130), fillp("#000000", 120))
    text(c, "Lena · Videoanruf", 300, 85, "xbold", 40, "#FFFFFF")
    rrect(c, 760, 170, 260, 360, 28, "#1C1C2B", 7, ink="#FFFFFF")
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(764, 174, 252, 352))
    lena_avatar(c, 890, 340, 100)
    c.restore()
    rec_dot(c, t, 300, 210)
    for k, (col, x) in enumerate([("#E5484D", 400), ("#555566", 540), ("#555566", 680)]):
        circ(c, x, 1800, 56, col, 6, ink="#FFFFFF")
    c.drawLine(372, 1800, 428, 1800, strokep("#FFFFFF", 10))


def s_nose(c, t):
    t0 = SC["nose"][0]
    cf = EV["cfreeze"]
    frz = t >= cf
    ta = min(t, cf)
    c.save()
    if PART == 1:
        shake(c, ta, t0, 40, 0.35)
    if frz:
        z = eo(prog(t, cf, 0.25))
        c.translate(540, 950)
        c.scale(1 + z * 0.2, 1 + z * 0.2)
        c.translate(-540, -950)
    st = base(ta, cap=True)
    filt = PART == 2 and ta >= EV["filter"] + 1.2
    nose_cam(c, ta, st, filt)
    if PART == 1:
        if not frz:
            T2.stamp(c, ta, EV["nstamp"], "HD-NASENLÖCHER", 540, 700, "#E5484D", 80, -8)
    else:
        if filt:
            c.save()
            pop(c, ta, EV["filter"] + 1.2, 540, 700)
            pill(c, "FILTER: PLEITE & KALT", 540, 700, 54, fill="#1F4BD8", name="black", padx=36, pady=22)
            c.restore()
        if ta >= ST["l03"] + 0.1:
            T2.stamp(c, ta, ST["l03"] + 0.1, "ERWISCHT", 540, 1060, "#E0245E", 100, 8)
    c.restore()
    if PART == 2 and t < 2.4:
        # Hook-Text statt Rueckblick (LEARNINGS 11.11.: "Vorhin bei..." -> hoehere Skip-Rate)
        k = 1 - clamp((t - 2.05) / 0.35)
        c.drawRect(skia.Rect.MakeXYWH(0, 1470, W, 230), fillp("#000000", int(185 * k)))
        if k > 0.05:
            text(c, "SIE SAH NUR", 540, 1560, "black", 76, "#FFD84D")
            text(c, "MEINE NASENLÖCHER.", 540, 1652, "black", 76, "#FFD84D")
    if frz:
        a = int(120 * clamp(prog(t, cf, 0.12)))
        c.drawRect(skia.Rect.MakeWH(W, H), fillp("#000000", a))
        if CLIFF:
            title(c, t, cf + 0.05, "SIE HAT", 300, 140, "#FFD84D", wob=False)
            title(c, t, cf + 0.15, "MICH GESEHEN!", 450, 120, "#FFD84D", wob=False)
            caps(c, t, cy=1130, only=[CLIFF])
            ti = wt(CLIFF, 9) - 0.1
            if t > ti:
                c.save()
                pop(c, t, ti, 540, 1450, kind="el")
                bb = 1 + 0.04 * math.sin(t * 9)
                c.translate(540, 1450)
                c.scale(bb, bb)
                c.translate(-540, -1450)
                pill(c, "TEIL 2 · HEUTE 18 UHR", 540, 1450, 62, fill="#E0245E", name="black", padx=40, pady=26)
                c.restore()
        else:
            title(c, t, cf + 0.05, "ERWISCHT?", 330, 140, "#FFD84D", wob=False)
    else:
        caps(c, t, cy=1300)


def s_poll(c, t):
    t0 = SC["poll"][0]
    clip = iris(c, t, t0, "#7EE0C3", prev="#333333", cy=900, d=0.35)
    background(c, t, "#7EE0C3", "#93E8CF")
    title(c, t, t0 + 0.05, "IHR ENTSCHEIDET!", 220, 112, "#FFFFFF")
    c.save()
    s = back(prog(t, t0 + 0.25, 0.4))
    c.translate(540, 640)
    c.scale(s, s)
    c.translate(-540, -640)
    card(c, 80, 360, 920, 560, "#FFFFFF", 34, 14, 8)
    text(c, "Lena: Wer bist du wirklich?", 540, 450, "black", 46, INK)
    ia, ib, iend = 2, 7, len(DISP["a07"]) - 4
    for k, (lab, txt, ts) in enumerate([("A", "Die Wahrheit sagen", wt("a07", ia)), ("B", "\"Emres Zwilling\"", wt("a07", ib))]):
        if t < ts:
            continue
        y = 510 + k * 180
        x = back(prog(t, ts, 0.35))
        c.save()
        c.translate(540, y + 65)
        c.scale(x, x)
        c.translate(-540, -(y + 65))
        sel = (k == 0 and t < wt("a07", ib)) or (k == 1 and wt("a07", ib) <= t < wt("a07", iend))
        rrect(c, 130, y, 820, 130, 30, ("#FFD84D" if k == 0 else "#8FD3FF") if sel else "#F3F1EE", 6)
        circ(c, 205, y + 65, 42, INK)
        text(c, lab, 205, y + 82, "black", 48, "#FFFFFF")
        text(c, txt, 275, y + 82, "black", 46, INK, "l")
        if k == 0:
            heart(c, 880, y + 65, 40, "#F0507F", 6)
        else:
            emre_avatar(c, 870, y + 65, 48, t)
        c.restore()
    c.restore()
    cta = wt("a07", iend) - 0.1
    st = base(t, rarm=-150)
    if t > cta:
        st.update(wave=1, hop=max(0, math.sin((t - cta) * 7) * 40))
    ahmed(c, t, 540, 1840, 1.0, st)
    if t > cta:
        c.save()
        pop(c, t, cta, 540, 1010, kind="el")
        bb = 1 + 0.05 * math.sin(t * 10)
        c.translate(540, 1010)
        c.scale(bb, bb)
        c.translate(-540, -1010)
        pill(c, "KOMMENTIERE A ODER B", 540, 1010, 58, fill="#E0245E", name="black", padx=40, pady=24)
        c.restore()
        if t > cta + 0.6:
            c.save()
            pop(c, t, cta + 0.6, 540, 1115)
            pill(c, "TAG 4 – MORGEN 12 UHR", 540, 1115, 44, fill=INK, col="#FFD84D", name="black")
            c.restore()
    else:
        caps(c, t)
    if clip:
        c.restore()


def frame(c, name, t):
    a, b = SC[name]
    z = 1.0 + 0.03 * (t - a) / (b - a)
    c.save()
    c.translate(540, 1056)
    c.scale(z, z)
    c.translate(-540, -1056)
    FN[name](c, t)
    c.restore()
    c.drawImage(vignette(), 0, 0)


def scene_at(t):
    for n in ORDER:
        if SC[n][0] <= t < SC[n][1]:
            return n
    return ORDER[-1]


def render_scene(name):
    a, b = SC[name]
    f0, f1 = round(a * FPS), round(b * FPS)
    tmp = f"{OUT}/{ORDER.index(name)}_{name}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "1080x1920", "-r", "30", "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30", tmp], stdin=subprocess.PIPE)
    s = skia.Surface(1080, 1920)
    c = s.getCanvas()
    for f in range(f0, f1):
        c.save()
        frame(c, name, f / FPS)
        c.restore()
        p.stdin.write(s.makeImageSnapshot().tobytes())
    p.stdin.close()
    assert p.wait() == 0
    os.replace(tmp, tmp.replace(".tmp", ""))



def build_audio():
    ns = {}
    src = open("/home/claude/audio.py").read()
    exec(src[: src.index("# ================= SFX track")], ns)
    g = ns.__getitem__
    add, pizz, taiko, piano, strings, bell, pop_, braam, riser, whoosh, thud, buzzer, scratch, mtof, tt, bp = (g(k) for k in ["add", "pizz", "taiko", "piano", "strings", "bell", "pop", "braam", "riser", "whoosh", "thud", "buzzer", "scratch", "mtof", "tt", "bp"])
    rng = np.random.default_rng(7)
    Nn = int(TOTAL * SR)
    mus = np.zeros(Nn + SR)
    sfx = np.zeros(Nn + SR)
    beat = 60 / 112

    def water(a, b, g=0.08):
        n = rng.standard_normal(int((b - a) * SR))
        add(sfx, a, bp(n, 1500, 7000) * g * np.minimum(1, tt(b - a) / 0.2))

    def tension(a, b, notes=(50, 50, 53, 50)):
        t, k = a, 0
        while t < b:
            add(mus, t, pizz(mtof(notes[k % 4]), 1.0))
            if k % 2 == 0:
                add(mus, t, taiko(0.35))
            t += beat / 2
            k += 1

    if "cold" in SC:
        fr = EV["freeze"]
        water(0, fr, 0.07)
        add(sfx, 0.0, thud(), 0.8)
        add(mus, 0.0, braam(33, 2.0), 0.7)
        tension(0.3, fr - 0.1)
        add(sfx, wt("a01", len(DISP["a01"]) - 1) - 0.05, thud(), 0.9)
        add(sfx, wt("a01", len(DISP["a01"]) - 1) - 0.05, buzzer(), 0.4)
        d = SC["cold"][1] - fr
        t_ = tt(d)
        f = 1400 * np.exp(-t_ * 3) + 200
        ph = 2 * np.pi * np.cumsum(f) / SR
        rw = (((ph / np.pi) % 2) - 1) * 0.12 + bp(rng.standard_normal(len(t_)), 600, 4000) * 0.2
        add(sfx, fr, rw * np.minimum(1, (d - t_) / 0.1))
        add(sfx, fr, scratch(), 0.6)
    if "vote" in SC:
        a, b = SC["vote"]
        seq = [62, 69, 66, 69, 62, 69, 67, 69]
        sad_t = wt("a02", 9) - 0.05
        t, k = a, 0
        while t < sad_t:
            add(mus, t, pizz(mtof(seq[k % 8]), 1.0 if k % 2 == 0 else 0.7))
            if k % 4 == 0:
                add(mus, t, taiko(0.3))
            t += beat / 2
            k += 1
        add(sfx, wt("a02", 4) - 0.05, thud(), 0.8)
        # trauriges Posaunen-Abwaerts
        for j, m in enumerate([67, 66, 65, 62]):
            add(mus, sad_t + j * 0.28, strings(mtof(m - 12), 0.32 if j < 3 else 0.9, 0.02, 0.2, 1500), 0.8)
    if "call" in SC:
        a, b = SC["call"]
        water(a, b, 0.06)
        t = a + 0.1
        while t < b:
            add(mus, t, piano(mtof(74 + [0, 4, 7, 12][int((t - a) / (beat / 2)) % 4]), 1.2, 0.45))
            t += beat / 2
        add(sfx, wt("a03", 6) - 0.05, pop_(), 0.4)
    # nose-cam
    a, b = SC["nose"]
    cf = EV["cfreeze"]
    if PART == 1:
        add(sfx, a, scratch(), 0.8)
        add(sfx, a + 0.02, thud(), 0.8)
        tension(a + 0.2, cf, (50, 51, 50, 53))
        add(sfx, EV["nstamp"], thud(), 0.9)
        add(sfx, EV["nstamp"] + 0.05, bell(2637, 0.4, 0.15))
    else:
        add(sfx, 0.0, thud(), 0.7)
        add(mus, 0.0, braam(36, 1.6), 0.6)
        tension(0.3, cf)
        add(sfx, EV["filter"] + 1.2, pop_(), 0.45)
        for kk, m in enumerate([86, 90, 93]):
            add(sfx, EV["filter"] + 1.2 + kk * 0.07, bell(mtof(m), 0.5, 0.08))
        add(sfx, ST["l03"] + 0.1, thud(), 0.8)
    add(mus, cf - 0.8, riser(0.8), 0.8)
    add(sfx, cf, thud(), 0.9)
    add(mus, cf, braam(38, 1.6), 0.8)
    if CLIFF:
        for m in [50, 53, 57]:
            add(mus, cf + 0.4, strings(mtof(m), b - cf - 0.4, 0.5, 0.6, 1800), 0.55)
        tz = wt(CLIFF, 9) - 0.1
        add(mus, tz - 0.9, riser(0.9), 0.8)
        add(mus, tz, taiko(1.0))
        add(sfx, tz, thud(), 0.8)
        for kk, m in enumerate([74, 78, 81, 86]):
            add(mus, tz + kk * 0.09, bell(mtof(m), 1.2, 0.12))
    if "poll" in SC:
        a, b = SC["poll"]
        cta = wt("a07", len(DISP["a07"]) - 4) - 0.1
        osti = [62, 69, 65, 69, 62, 70, 65, 70]
        t, k = a + 0.2, 0
        while t < cta:
            add(mus, t, pizz(mtof(osti[k % 8] - 12), 0.8))
            add(mus, t, strings(mtof(osti[k % 8]), beat / 4, 0.01, 0.05, 3000), 0.5)
            if k % 8 == 0:
                add(mus, t, taiko(0.6))
            t += beat / 4
            k += 1
        add(mus, cta - 1.0, riser(1.0), 0.9)
        add(mus, cta, braam(38, 2.4), 0.9)
        add(mus, cta, taiko(1.2))
        for m in [62, 66, 69, 74]:
            add(mus, cta, strings(mtof(m), b - cta, 0.3, 0.5, 3200), 0.7)
        for kk, m in enumerate([74, 78, 81, 86]):
            add(mus, cta + kk * 0.09, bell(mtof(m), 1.4, 0.12))
        add(sfx, wt("a07", 2), pop_(), 0.35)
        add(sfx, wt("a07", 7), pop_(), 0.35)
    for n in ORDER[1:]:
        add(sfx, SC[n][0] - 0.1, whoosh(0.35), 0.4)
    mus, sfx = mus[:Nn], sfx[:Nn]
    fade = np.minimum(1, (Nn - np.arange(Nn)) / (0.4 * SR))
    mus *= fade

    def wav(name, x, norm=None):
        if norm:
            x = x / (np.abs(x).max() + 1e-9) * norm
        x = np.clip(x, -1, 1).astype(np.float32)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", f"{D}/{name}.wav"], input=x.tobytes(), check=True)
    wav("voice", (TR["A"] + TR["L"] + TR["K"])[:Nn])
    wav("sfx", sfx, 0.8)
    wav("music", mus, 0.9)
    subprocess.run(["bash", "-c", f"cd {D} && bash /home/claude/mix.sh"], check=True)


def final(outfile):
    lst = f"{OUT}/list.txt"
    with open(lst, "w") as f:
        for k, n in enumerate(ORDER):
            f.write(f"file '{OUT}/{k}_{n}.mp4'\n")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", f"{D}/mix.wav",
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", outfile], check=True)
    print("final", outfile)

FN = {"cold": s_cold, "vote": s_vote, "call": s_call, "nose": s_nose, "poll": s_poll}


if __name__ == "__main__":
    cmd = sys.argv[2] if len(sys.argv) > 2 else "info"
    if cmd in ("info", "tts"):
        print({k: (round(a, 2), round(b, 2)) for k, (a, b) in SC.items()}, {k: round(v, 2) for k, v in EV.items()}, "TOTAL", round(TOTAL, 2))
    elif cmd == "preview":
        from PIL import Image
        ims = []
        for t in [float(x) for x in sys.argv[3:]]:
            s = skia.Surface(1080, 1920)
            c = s.getCanvas()
            frame(c, scene_at(t), t)
            ims.append(Image.frombytes("RGBA", (1080, 1920), s.makeImageSnapshot().tobytes(), "raw", "BGRA").convert("RGB").resize((360, 640)))
        cols = min(6, len(ims))
        rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (360 * cols, 640 * rows))
        for i, im in enumerate(ims):
            sh.paste(im, ((i % cols) * 360, (i // cols) * 640))
        sh.save(f"{D}/prev.png")
        print(f"{D}/prev.png")
    elif cmd == "scene":
        for n in sys.argv[3:]:
            render_scene(n)
            print("ok", n, flush=True)
    elif cmd == "audio":
        build_audio()
        print("audio ok")
    elif cmd == "all":
        procs = [subprocess.Popen(["python3", os.path.abspath(__file__), str(PART), "scene", n]) for n in ORDER]
        build_audio()
        assert all(p.wait() == 0 for p in procs)
        final(sys.argv[3] if len(sys.argv) > 3 else f"{D}/tag03_teil{PART}.mp4")
