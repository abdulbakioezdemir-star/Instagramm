# Tag 2 "Beides" – zwei Teile (PART=1: 12 Uhr Cliffhanger, PART=2: 18 Uhr mit A/B-Abstimmung)
# Setup (einmal pro Lauf), siehe README.md in diesem Ordner:
#   /home/claude/{draw.py,scenes.py,audio.py,mix.sh,tts.py,fonts,timeline.json(dummy)} und /home/claude/tag2 (Hilfsmodul)
# Nutzung: python3 tag02.py <PART> tts | info | preview t1 t2 .. | scene <name..> | audio | all
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
D = f"/home/claude/tag02_work/teil{PART}"
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
    e = put("c01", 0.05)
    EV["freeze"] = e + 0.05
    SC["cold"] = (0.0, EV["freeze"] + 0.85)
    s = SC["cold"][1]
    e = put("a01", s + 0.15)
    SC["vote"] = (s, e + 0.3)
    s = SC["vote"][1]
    EV["walk1"] = s + 0.9
    e = put("a02", s + 0.15)
    e = put("k01", e + 0.2)
    e = put("a03", e + 0.2)
    e = put("k02", e + 0.15)
    EV["kick"] = e - 0.05
    EV["land"] = EV["kick"] + 0.85
    EV["drop"] = EV["land"] + 0.3
    SC["doener"] = (s, EV["drop"] + 1.0)
    s = SC["doener"][1]
    e = put("a04", s + 0.2)
    e = put("a05", e + 0.25)
    SC["shower"] = (s, e + 0.35)
    s = SC["shower"][1]
    e = put("l01", s + 0.3)
    e = put("a06", e + 0.2)
    EV["cfreeze"] = e + 0.1
    e = put("a08", EV["cfreeze"] + 0.6)
    EV["teaser"] = e + 0.05
    SC["call"] = (s, e + 2.0)
    CALL_LINES, CLIFF = ["l01", "a06"], "a08"
    ORDER = ["cold", "vote", "doener", "shower", "call"]
else:
    s = 0.0
    e = put("r01", 0.35)
    e = put("a09", e + 0.3)
    e = put("a12", e + 0.25)
    e = put("l02", e + 0.35)
    e = put("a11", e + 0.25)
    EV["cfreeze"] = e + 0.1
    SC["call"] = (s, EV["cfreeze"] + 0.6)
    s = SC["call"][1]
    e = put("a07", s + 0.2)
    SC["poll"] = (s, e + 2.4)
    CALL_LINES, CLIFF = ["r01", "a09", "a12", "l02", "a11"], None
    ORDER = ["call", "poll"]
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


ENV_A, ENV_K = envelope(TR["A"]), envelope(TR["K"])


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
    pill(c, f"TAG 2 · TEIL {PART}/2", 540, 110, 44, fill=INK, col="#FFD84D", name="black")
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


# ---------------- scenes ----------------
def s_cold(c, t):
    fr = EV["freeze"]
    tt = min(t, fr)
    c.save()
    shake(c, tt, 0.0, 34, fr)
    shower_room(c, tt, True)
    T2.stamp(c, tt, wt("c01", 1) - 0.05, "KALT!!!", 540, 430, "#1F4BD8", 130, -8)
    st = base(tt, cap=True, eyes="wide", mshape="o", sweat=0, rarm=-170, larm=-30, worried=True)
    frozen_ahmed(c, tt, st)
    # ice cube falls on head
    ic = clamp((tt - 1.2) / 0.35)
    if tt > 1.2:
        y = 200 + eo(ic) * 900 if ic < 1 else 1100 + math.sin((tt - 1.55) * 30) * 4
        ice_cube(c, 560, y, 0.9, tt * 200 if ic < 1 else 12)
    c.restore()
    if t >= fr:
        # rewind effect
        k = clamp((t - fr) / 0.2)
        c.drawRect(skia.Rect.MakeWH(W, H), fillp("#000000", int(140 * k)))
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
        text(c, "3 STUNDEN VORHER", 540, 1010, "black", 84, "#FFFFFF", stroke=14)
        text(c, "3 STUNDEN VORHER", 540, 1010, "black", 84, "#FFFFFF")
        c.restore()
    else:
        caps(c, t, cy=1050)


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
    for k, (lab, txt, col) in enumerate([("A", "Arbeit", "#FFD84D"), ("B", "Duschen", "#8FD3FF")]):
        x0 = 150 + k * 420
        wob = math.sin(t * 9 + k * 3) * 4
        c.save()
        c.translate(x0 + 180, 600)
        c.rotate(wob)
        c.translate(-(x0 + 180), -600)
        rrect(c, x0, 470, 360, 260, 30, col, 6)
        circ(c, x0 + 180, 545, 44, INK)
        text(c, lab, x0 + 180, 563, "black", 52, "#FFFFFF")
        text(c, txt, x0 + 180, 640, "black", 44, INK)
        text(c, "2 Stimmen", x0 + 180, 708, "xbold", 34, "#555555")
        c.restore()
    text(c, ":", 540, 610, "black", 90, INK)
    c.restore()
    tb = wt("a01", 11) - 0.05
    c.save()
    shake(c, t, tb, 22, 0.3)
    T2.stamp(c, t, tb, "BEIDES!", 540, 560, "#E0245E", 130, -10)
    c.restore()
    st = base(t, rarm=-150)
    if t < wt("a01", 7):
        st.update(eyes="derp", larm=-40, rarm=-170)
    else:
        st.update(eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", wave=0.5)
    if t > tb:
        st["hop"] = max(0, math.sin((t - tb) * 8) * 60)
    ahmed(c, t, 540, 1840, 1.0, st)
    tag_pill(c, t, t0)
    caps(c, t)


def chef(c, t, x, y, s, angry=False, point=False):
    m = mouth(t, ENV_K)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, -10, 190, 22, "#000000", a=45)
    # body
    oval(c, 0, -300, 230, 280, "#E5484D", 11)
    rrect(c, -150, -420, 300, 400, 60, "#FFFFFF", 10)
    c.drawLine(-150, -330, 150, -330, strokep("#DDDDDD", 6))
    # arms
    c.save()
    c.translate(190, -430)
    c.rotate(-100 if point else 15)
    oval(c, 0, 90, 46, 110, "#E5484D", 10)
    circ(c, 0, 200, 40, "#C98F66", 10)
    c.restore()
    c.save()
    c.translate(-190, -430)
    c.rotate(-15)
    oval(c, 0, 90, 46, 110, "#E5484D", 10)
    circ(c, 0, 200, 40, "#C98F66", 10)
    c.restore()
    # head
    oval(c, 0, -690, 150, 140, "#C98F66", 11)
    # hat
    rrect(c, -110, -900, 220, 90, 20, "#FFFFFF", 9)
    for dx in (-80, 0, 80):
        circ(c, dx, -910, 70, "#FFFFFF", 9)
    rrect(c, -112, -840, 224, 40, 10, "#FFFFFF", 9)
    # brows
    bl = 30 if angry else 0
    c.drawLine(-95, -735 - bl * 0.3, -25, -725 + bl * 0.4, strokep(INK, 16))
    c.drawLine(95, -735 - bl * 0.3, 25, -725 + bl * 0.4, strokep(INK, 16))
    circ(c, -55, -690, 14, INK)
    circ(c, 55, -690, 14, INK)
    oval(c, 0, -650, 34, 28, "#B07850", 8)
    # mouth + big moustache
    oval(c, 0, -585 + m * 10, 40, 8 + m * 30, "#73302F", 8)
    mp = skia.Path()
    mp.moveTo(-120, -600)
    mp.quadTo(-60, -650, 0, -615)
    mp.quadTo(60, -650, 120, -600)
    mp.quadTo(60, -605, 0, -595)
    mp.quadTo(-60, -605, -120, -600)
    mp.close()
    drawpath(c, mp, "#1A1A1A", 0)
    if angry:
        for k in range(3):
            a = -0.6 + k * 0.6
            c.drawLine(170 * math.cos(a - 1.57) * 0 + 140 + k * 15, -820 - k * 10, 175 + k * 15, -860 - k * 20, strokep("#E5484D", 10))
    c.restore()


def dizzy(c, t, cx, cy):
    for k in range(4):
        a = t * 6 + k * 1.57
        star(c, cx + math.cos(a) * 130, cy + math.sin(a) * 40, 26, "#FFD84D", 5)


def s_doener(c, t):
    t0 = SC["doener"][0]
    kick, land, drop = EV["kick"], EV["land"], EV["drop"]
    clip = iris(c, t, t0, "#FFB86B", prev="#F9D85E", cy=900, d=0.35)
    c.save()
    shake(c, t, ST["k02"], 26, 0.35)
    shake(c, t, land, 40, 0.4)
    background(c, t, "#FFB86B", "#FFC88A")
    c.save()
    s = back(prog(t, t0 + 0.05, 0.4))
    c.translate(540, 560)
    c.scale(s * 0.86, s * 0.86)
    c.translate(-540, -560)
    T2.shopfront(c, t)
    c.restore()
    # chef right
    angry = t >= ST["k02"] - 0.05
    chef(c, t, 800, 1840, 0.95 + (0.05 * math.sin((t - ST["k02"]) * 30) if angry and t < ST["k02"] + 0.4 else 0), angry=angry, point=angry)
    # Ahmed
    if t < kick:
        x = -200 + eo(prog(t, t0, EV["walk1"] - t0)) * 520
        step = math.sin(t * 16) * 14 if t < EV["walk1"] else 0
        st = base(t, rarm=-60 + step, larm=step)
        st["hop"] = abs(step) * 1.5
        if t > ST["a03"]:
            st.update(eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", rarm=-150)
        if t > ST["k02"] - 0.05:
            st.update(eyes="wide", mshape="o", sweat=3)
        ahmed(c, t, x, 1840, 0.85, st)
    elif t < land:
        u = (t - kick) / (land - kick)
        x = 320 - u * 90
        y = 1840 - math.sin(u * math.pi) * 1700
        speed_lines(c, t)
        c.save()
        c.translate(x, y - 300)
        c.rotate(u * 900)
        c.translate(-x, -(y - 300))
        ahmed(c, t, x, y, 0.75, base(t, eyes="wide", mshape="o", rarm=-170, larm=-40))
        c.restore()
    else:
        c.save()
        c.translate(250, 1500)
        c.rotate(170)
        ahmed(c, t, 0, 300, 0.7, base(t, eyes="derp", mshape="o"))
        c.restore()
        oval(c, 250, 1720, 230, 50, "#C9A97A", 0, a=150 if t < land + 0.5 else 80)
        if t > drop:
            u = clamp((t - drop) / 0.3)
            doener(c, 270, 900 + eo(u) * 660, 0.9)
        dizzy(c, t, 250, 1660)
        T2.stamp(c, t, land + 0.05, "GEFEUERT", 540, 1000, "#E5484D", 90, -12)
    c.restore()
    tag_pill(c, t, t0 + 0.05)
    if t < kick + 0.3:
        caps(c, t)
    if clip:
        c.restore()


def s_shower(c, t):
    t0 = SC["shower"][0]
    cold_t = EV["cold2"]
    cold = t >= cold_t
    clip = iris(c, t, t0, "#9ED8F0", prev="#FFB86B", cy=900, d=0.35)
    c.save()
    shake(c, t, cold_t, 30, 0.5)
    shower_room(c, t, cold)
    if not cold:
        for k in range(3):
            a = t * 2 + k * 2
            heart(c, 540 + math.cos(a) * 300, 900 + math.sin(a * 1.3) * 120, 26, "#FF8FC2", 5, a=200)
    if cold:
        T2.stamp(c, t, cold_t + 0.02, "EISKALT!", 540, 430, "#1F4BD8", 110, -8)
    bill_t = wt("a05", 4) - 0.1
    if t >= bill_t:
        c.save()
        pop(c, t, bill_t, 790, 700)
        c.translate(790, 700)
        c.rotate(8)
        card(c, -200, -150, 400, 300, "#FFFFFF", 18, 10, 6)
        text(c, "STROMRECHNUNG", 0, -85, "black", 40, INK)
        text(c, "offen: 89,90 €", 0, -20, "xbold", 38, "#555555")
        rrect(c, -150, 30, 300, 80, 14, None, 8, ink="#E5484D")
        text(c, "UNBEZAHLT", 0, 88, "black", 48, "#E5484D")
        c.restore()
    st = base(t, cap=True, rarm=-150)
    if not cold:
        st.update(eyes="heart" if t > wt("a04", 4) else "smug", mshape="smile" if mouth(t) > 0.12 else "grin", wave=0.4)
        ahmed(c, t, 540, 1840, 1.0, st)
    else:
        st.update(eyes="wide", mshape="grimace", worried=True, rarm=-170, larm=-30)
        frozen_ahmed(c, t, st)
    c.restore()
    tag_pill(c, t, t0 + 0.05)
    caps(c, t)
    if clip:
        c.restore()


if PART == 1:
    EV["cold2"] = wt("a05", 3) - 0.15
A_CALL = [i for i in CALL_LINES if TEXT[i][0] == "A"]
FIRST_A = A_CALL[0]
LAST = CALL_LINES[-1]


def s_call(c, t):
    t0 = SC["call"][0]
    cf = EV["cfreeze"]
    frz = t >= cf
    ta = min(t, cf)
    clip = iris(c, t, t0, "#BFE6FF", prev="#9ED8F0", cy=600, d=0.35) if PART == 1 else None
    c.save()
    if frz:
        z = eo(prog(t, cf, 0.25))
        c.translate(540, 900)
        c.scale(1 + z * 0.25, 1 + z * 0.25)
        c.translate(-540, -900)
    shake(c, ta, ST[FIRST_A], 26, 0.35)
    if PART == 2:
        shake(c, ta, ST["a12"], 18, 2.0)
    shower_room(c, ta, True, steam=False)
    ring = math.sin(ta * 40) * 7 * (1 if (ta - t0) % 1.0 < 0.5 else 0)
    c.save()
    c.translate(ring, 0)
    s = back(prog(ta, t0 + 0.2, 0.35)) if PART == 1 else 1.0
    c.translate(540, 560)
    c.scale(s, s)
    c.translate(-540, -560)
    rrect(c, 250 + 14, 220 + 14, 580, 680, 60, INK)
    rrect(c, 250, 220, 580, 680, 60, "#1C1C2B", 9)
    lena_avatar(c, 540, 420, 110)
    text(c, "Lena", 540, 600, "black", 56, "#FFFFFF")
    text(c, "Videoanruf…", 540, 650, "semi", 36, "#BBBBBB")
    for k, (col, x) in enumerate([("#E5484D", 420), ("#2FBF71", 660)]):
        pul = 1 + 0.1 * math.sin(ta * 10 + k)
        circ(c, x, 790, 52 * pul, col, 6)
    c.drawLine(395, 790, 445, 790, strokep("#FFFFFF", 10))
    c.drawLine(640, 780, 680, 800, strokep("#FFFFFF", 10))
    c.restore()
    # Finger schwebt ueber "Annehmen"
    fin_t = wt(A_CALL[-1], len(DISP[A_CALL[-1]]) - 1) - 0.3
    if ta > fin_t:
        u = eo(prog(ta, fin_t, 0.6))
        fx, fy = 900 - u * 230, 1150 - u * 330
        c.drawLine(1180, 1500, fx + 40, fy + 120, strokep(INK, 70))
        c.drawLine(1180, 1500, fx + 40, fy + 120, strokep(SHIRT, 56))
        circ(c, fx + 30, fy + 105, 48, SKIN, 10)
        c.save()
        c.translate(fx + 10, fy + 70)
        c.rotate(-35)
        rrect(c, -16, -90, 32, 100, 16, SKIN, 9)
        c.restore()
    if ST[FIRST_A] < ta or PART == 2:
        for k in range(2):
            ice_cube(c, 330 + k * 420, 1700, 0.8, 8 - k * 16)
    st = base(ta, cap=True, eyes="wide", mshape="grimace" if mouth(ta) < 0.15 else "o", sweat=4, worried=True, rarm=-150)
    if PART == 2 and ST["a11"] <= ta < ST["a11"] + DUR["a11"] * 0.55:
        st.update(eyes="heart", mshape="smile" if mouth(ta) > 0.12 else "grin", worried=False)
    frozen_ahmed(c, ta, st)
    c.restore()
    if PART == 2 and t < 1.6:
        # Rueckblick-Banner
        k = 1 - clamp((t - 1.25) / 0.35)
        c.drawRect(skia.Rect.MakeXYWH(0, 1290, W, 150), fillp("#000000", int(170 * k)))
        text(c, "VORHIN BEI AHMED…", 540, 1392, "black", 74, "#FFD84D")
    if frz:
        a = int(110 * clamp(prog(t, cf, 0.12)))
        c.drawRect(skia.Rect.MakeWH(W, H), fillp("#000000", a))
        title(c, t, cf + 0.05, "ANNEHMEN?", 330, 140, "#FFD84D", wob=False)
        if CLIFF:
            caps(c, t, cy=1130, only=[CLIFF])
            tz = EV["teaser"] - 0.6
            if t > wt(CLIFF, 8) - 0.1:
                c.save()
                pop(c, t, wt(CLIFF, 8) - 0.1, 540, 1400, kind="el")
                bb = 1 + 0.04 * math.sin(t * 9)
                c.translate(540, 1400)
                c.scale(bb, bb)
                c.translate(-540, -1400)
                pill(c, "TEIL 2 · HEUTE 18 UHR", 540, 1400, 62, fill="#E0245E", name="black", padx=40, pady=26)
                c.restore()
    else:
        caps(c, t)
    tag_pill(c, t, t0 + 0.05)
    if clip:
        c.restore()


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
    text(c, "Lena ruft an. Was tun?", 540, 450, "black", 50, INK)
    for k, (lab, txt, ts) in enumerate([("A", "Emre geht ran", wt("a07", 2)), ("B", "Kamera \"kaputt\"", wt("a07", 6))]):
        if t < ts:
            continue
        y = 510 + k * 180
        x = back(prog(t, ts, 0.35))
        c.save()
        c.translate(540, y + 65)
        c.scale(x, x)
        c.translate(-540, -(y + 65))
        sel = (k == 0 and t < wt("a07", 6)) or (k == 1 and wt("a07", 6) <= t < wt("a07", 13))
        rrect(c, 130, y, 820, 130, 30, ("#FFD84D" if k == 0 else "#8FD3FF") if sel else "#F3F1EE", 6)
        circ(c, 205, y + 65, 42, INK)
        text(c, lab, 205, y + 82, "black", 48, "#FFFFFF")
        text(c, txt, 275, y + 82, "black", 48, INK, "l")
        if k == 0:
            emre_avatar(c, 870, y + 65, 48, t)
        else:
            T2.broken_cam(c, 870, y + 65, 0.9)
        c.restore()
    c.restore()
    cta = wt("a07", 13) - 0.1
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
            pill(c, "TAG 3 – MORGEN 12 UHR", 540, 1115, 44, fill=INK, col="#FFD84D", name="black")
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
    rng = np.random.default_rng(5)
    Nn = int(TOTAL * SR)
    mus = np.zeros(Nn + SR)
    sfx = np.zeros(Nn + SR)
    beat = 60 / 112

    def water(a, b, g=0.12, cold_from=None):
        n = rng.standard_normal(int((b - a) * SR))
        w = bp(n, 1500, 7000) * g * np.minimum(1, tt(b - a) / 0.2)
        if cold_from is not None:
            ci = int((cold_from - a) * SR)
            w[ci:] *= 1.5
        add(sfx, a, w)

    if "cold" in SC:
        water(0, EV["freeze"], 0.15)
        add(sfx, 0.0, thud(), 0.8)
        add(sfx, wt("c01", 1) - 0.05, thud(), 0.7)
        add(sfx, 1.55, bell(2637, 0.4, 0.2))
        add(sfx, 1.55, thud(), 0.6)
        add(mus, 0.0, braam(33, 2.0), 0.7)
        d = SC["cold"][1] - EV["freeze"]
        t_ = tt(d)
        f = 1400 * np.exp(-t_ * 3) + 200
        ph = 2 * np.pi * np.cumsum(f) / SR
        rw = (((ph / np.pi) % 2) - 1) * 0.12 + bp(rng.standard_normal(len(t_)), 600, 4000) * 0.2
        add(sfx, EV["freeze"], rw * np.minimum(1, (d - t_) / 0.1))
        add(sfx, EV["freeze"], scratch(), 0.6)
    if "vote" in SC:
        a, b = SC["vote"]
        seq = [62, 69, 66, 69, 62, 69, 67, 69]
        t, k = a, 0
        while t < b:
            add(mus, t, pizz(mtof(seq[k % 8]), 1.0 if k % 2 == 0 else 0.7))
            if k % 4 == 0:
                add(mus, t, taiko(0.3))
            t += beat / 2
            k += 1
        add(sfx, wt("a01", 11) - 0.05, thud(), 0.8)
    if "doener" in SC:
        a, b = SC["doener"]
        sc_ = [62, 63, 66, 67, 69, 70, 72, 74]
        pat = [0, 1, 2, 1, 3, 2, 1, 0, 4, 5, 4, 3, 2, 1, 2, 0]
        t, k = a + 0.05, 0
        while t < ST["k02"] - 0.05:
            add(mus, t, pizz(mtof(sc_[pat[k % 16]] + 12), 0.9))
            if k % 2 == 0:
                add(mus, t, taiko(0.42 if k % 4 == 0 else 0.22, low=k % 4 == 0))
            t += beat / 2
            k += 1
        for j in range(5):
            add(sfx, a + 0.1 + j * 0.18, thud(), 0.15)
        add(sfx, ST["k02"], thud(), 0.9)
        add(sfx, EV["kick"], whoosh(0.8), 0.8)
        d = EV["land"] - EV["kick"]
        t_ = tt(d)
        f = 300 + 500 * np.sin(np.pi * t_ / d)
        add(sfx, EV["kick"], np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 * np.minimum(1, (d - t_) / 0.05))
        add(sfx, EV["land"], thud(), 1.0)
        add(sfx, EV["land"] + 0.02, thud(), 0.7)
        add(sfx, EV["drop"] + 0.3, pop_(500, 200, 0.15), 0.5)
        for j in range(4):
            add(sfx, EV["land"] + 0.3 + j * 0.15, bell(mtof(88 + j * 3), 0.4, 0.06))
    if "shower" in SC:
        a, b = SC["shower"]
        cold_t = EV["cold2"]
        water(a, b, 0.11, cold_t)
        for m in [62, 66, 69]:
            add(mus, a, strings(mtof(m), cold_t - a, 0.4, 0.2, 2200), 0.6)
        t = a
        while t < cold_t:
            add(mus, t, piano(mtof(74 + [0, 4, 7, 12][int((t - a) / (beat / 2)) % 4]), 1.2, 0.5))
            t += beat / 2
        add(sfx, cold_t, scratch(), 0.7)
        add(sfx, cold_t + 0.02, thud(), 0.6)
        add(sfx, wt("a05", 4) - 0.1, pop_(), 0.3)
    # call: ringtone + tension
    a, b = SC["call"]
    cf = EV["cfreeze"]
    if PART == 2:
        add(sfx, 0.0, thud(), 0.7)
        add(mus, 0.0, braam(36, 1.6), 0.6)
        # Zittern / Erdbeben-Gag
        add(sfx, ST["a12"], bp(rng.standard_normal(int(DUR["a12"] * SR)), 40, 160) * 0.5)
    t = a + 0.2
    while t < cf - 0.2:
        for kk, m in enumerate([76, 79, 84, 79, 76, 79]):
            add(sfx, t + kk * 0.11, bell(mtof(m), 0.3, 0.09))
        t += 1.3
    t, k = a + 0.2, 0
    while t < cf:
        add(mus, t, pizz(mtof([50, 50, 53, 50][k % 4]), 1.0))
        if k % 2 == 0:
            add(mus, t, taiko(0.35))
        t += beat / 2
        k += 1
    add(mus, cf - 0.8, riser(0.8), 0.8)
    add(sfx, cf, thud(), 0.9)
    add(mus, cf, braam(38, 1.6), 0.8)
    if CLIFF:
        for m in [50, 53, 57]:
            add(mus, cf + 0.4, strings(mtof(m), b - cf - 0.4, 0.5, 0.6, 1800), 0.55)
        tz = wt(CLIFF, 8) - 0.1
        add(mus, tz - 0.9, riser(0.9), 0.8)
        add(mus, tz, taiko(1.0))
        add(sfx, tz, thud(), 0.8)
        for kk, m in enumerate([74, 78, 81, 86]):
            add(mus, tz + kk * 0.09, bell(mtof(m), 1.2, 0.12))
    if "poll" in SC:
        a, b = SC["poll"]
        cta = wt("a07", 13) - 0.1
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
        add(sfx, wt("a07", 6), pop_(), 0.35)
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


FN = {"cold": s_cold, "vote": s_vote, "doener": s_doener, "shower": s_shower, "call": s_call}
if "poll" in SC:
    FN["poll"] = s_poll


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
        final(sys.argv[3] if len(sys.argv) > 3 else f"{D}/tag02_teil{PART}.mp4")
