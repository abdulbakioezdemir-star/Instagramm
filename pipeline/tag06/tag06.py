# Tag 6 "Emre mit Doener bestechen" (Abstimmung Tag 5: A 5:0) – ein Reel pro Tag (BEFEHLE.md Befehl 5), PART=1 = ganze Folge mit A/B
# Setup (einmal pro Lauf), siehe README.md in diesem Ordner:
#   /home/claude/{draw.py,scenes.py,audio.py,mix.sh,tts.py,fonts,timeline.json(dummy)} und /home/claude/tag2 (Hilfsmodul)
# Nutzung: python3 tag06.py <PART> tts | info | preview t1 t2 .. | scene <name..> | audio | all
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
D = f"/home/claude/tag06_work/teil{PART}"
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
for i in DUR:  # Stille am Zeilenende kappen (Tempo, Ziel 28-32 s)
    _w = json.load(open(f"{D}/{i}.mp3.json"))
    DUR[i] = min(DUR[i], _w[-1][0] + _w[-1][1] + 0.12)
    AUD[i] = AUD[i][: int(DUR[i] * SR)]
ST, SC, EV = {}, {}, {}


def put(i, t):
    ST[i] = t
    return t + DUR[i]


e = put("a01", 0.05)
SC["cold"] = (0.0, e + 0.3)
s = SC["cold"][1]
e = put("k01", s + 0.15)
e = put("a02", e + 0.2)
e = put("k02", e + 0.3)
SC["shop"] = (s, e + 0.5)
s = SC["shop"][1]
e = put("a03", s + 0.15)
e = put("a04", e + 0.15)
e = put("a05", e + 0.35)
SC["chat"] = (s, e + 0.5)
s = SC["chat"][1]
e = put("a06", s + 0.4)
SC["poll"] = (s, e + 1.1)
CLIFF = None
ORDER = ["cold", "shop", "chat", "poll"]
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
ENV_K = envelope(TR["K"])


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
    pill(c, "TAG 6", 540, 110, 44, fill=INK, col="#FFD84D", name="black")
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


def thumbs_up(c, cx, cy, s=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    rrect(c, -26, -150, 62, 140, 31, "#FFC83D", 9)          # Daumen
    rrect(c, -70, -40, 150, 150, 36, "#FFC83D", 9)          # Faust
    for k in range(3):
        c.drawLine(-10, 0 + k * 36, 72, 0 + k * 36, strokep(INK, 7))
    rrect(c, -110, -30, 46, 150, 16, "#3B82F6", 8)           # Aermel
    c.restore()


def living_room(c):
    c.drawRect(skia.Rect.MakeWH(W, H), fillp("#F6E7C8"))
    for k in range(12):
        c.drawLine(k * 100, 0, k * 100, 1300, strokep("#EBD7B0", 30))
    c.drawRect(skia.Rect.MakeXYWH(0, 1300, W, 620), fillp("#B98A5E"))
    rrect(c, 80, 1080, 300, 240, 30, "#8E5CC2", 8)  # Sofa
    rrect(c, 780, 300, 200, 260, 10, "#9ED8F0", 8)  # Fenster



def wf(i, word, nth=0):
    """Zeit des n-ten edge-tts-Wortes in Zeile i, das mit `word` beginnt"""
    hits = [tt for tt, w in WT[i] if w.lower().strip(".,:!?").startswith(word.lower())]
    return hits[min(nth, len(hits) - 1)] if hits else ST[i]


def chef(c, t, x, y, s, angry=False, point=False):
    m = mouth(t, ENV_K)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    oval(c, 0, -10, 190, 22, "#000000", a=45)
    oval(c, 0, -300, 230, 280, "#E5484D", 11)
    rrect(c, -150, -420, 300, 400, 60, "#FFFFFF", 10)
    c.drawLine(-150, -330, 150, -330, strokep("#DDDDDD", 6))
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
    oval(c, 0, -690, 150, 140, "#C98F66", 11)
    rrect(c, -110, -900, 220, 90, 20, "#FFFFFF", 9)
    for dx in (-80, 0, 80):
        circ(c, dx, -910, 70, "#FFFFFF", 9)
    rrect(c, -112, -840, 224, 40, 10, "#FFFFFF", 9)
    bl = 30 if angry else 0
    c.drawLine(-95, -735 - bl * 0.3, -25, -725 + bl * 0.4, strokep(INK, 16))
    c.drawLine(95, -735 - bl * 0.3, 25, -725 + bl * 0.4, strokep(INK, 16))
    circ(c, -55, -690, 14, INK)
    circ(c, 55, -690, 14, INK)
    oval(c, 0, -650, 34, 28, "#B07850", 8)
    oval(c, 0, -585 + m * 10, 40, 8 + m * 30, "#73302F", 8)
    mp = skia.Path()
    mp.moveTo(-120, -600)
    mp.quadTo(-60, -650, 0, -615)
    mp.quadTo(60, -650, 120, -600)
    mp.quadTo(60, -605, 0, -595)
    mp.quadTo(-60, -605, -120, -600)
    mp.close()
    drawpath(c, mp, "#1A1A1A", 0)
    c.restore()


def coins(c, t, x, y, s=1.0, shake_=0.0):
    """3,40 EUR in der offenen Hand: ein paar Muenzen"""
    c.save()
    c.translate(x + math.sin(t * 40) * shake_, y)
    c.scale(s, s)
    for k, (dx, dy, r, col) in enumerate([(-40, 10, 34, "#E8C04A"), (10, -14, 40, "#D9D9D9"), (55, 16, 28, "#C98A3A"), (-5, 30, 24, "#C98A3A")]):
        circ(c, dx, dy, r, col, 6)
        circ(c, dx, dy, r * 0.62, col, 3, ink="#00000055" if False else "#8A6A20")
    c.restore()


def price_board(c, t, t0):
    c.save()
    pop(c, t, t0, 540, 260, kind="el")
    card(c, 250, 170, 580, 190, "#1A1A1A", 26, 10, 7)
    text(c, "DÖNER", 400, 288, "black", 64, "#FFFFFF")
    text(c, "8,50 €", 680, 290, "black", 70, "#FFD84D")
    c.restore()


def s_cold(c, t):
    c.save()
    shake(c, t, 0.0, 18, 0.4)
    background(c, t, "#FFB86B", "#FFC88A")
    c.save()
    c.translate(540, 560)
    c.scale(0.86, 0.86)
    c.translate(-540, -560)
    T2.shopfront(c, t)
    c.restore()
    tm = wf("a01", "drei") - 0.05
    if t < tm:
        st = base(t, eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", rarm=-150, larm=-20, wave=0.3)
    else:
        st = base(t, eyes="wide", mshape="grimace" if mouth(t) < 0.15 else "o", sweat=4, worried=True, rarm=-110)
    ahmed(c, t, 540, 1840, 1.0, st)
    if t >= tm:
        coins(c, t, 890, 1330, 1.1, 4)
    c.save()
    pop(c, t, 0.0, 540, 1010, d=0.25)
    pill(c, "ICH BESTECHE MEINEN COUSIN.", 540, 1010, 58, fill="#E0245E", name="black", padx=36, pady=26)
    c.restore()
    if t >= tm:
        c.save()
        shake(c, t, tm, 24, 0.3)
        T2.stamp(c, t, tm, "3,40 €", 540, 330, "#E5484D", 130, 10)
        c.restore()
    c.restore()
    caps(c, t, cy=1250)


def s_shop(c, t):
    t0 = SC["shop"][0]
    clip = iris(c, t, t0, "#FFE3B8", prev="#FFB86B", cy=900, d=0.35)
    c.save()
    shake(c, t, ST["k02"], 22, 0.3)
    background(c, t, "#FFE3B8", "#FFEFD2")
    # Theke
    rrect(c, -20, 1380, 1120, 600, 0, "#B98A5E", 8)
    rrect(c, -20, 1360, 1120, 60, 10, "#D9D9D9", 8)
    price_board(c, t, ST["k01"] - 0.05)
    tsv = wf("k02", "Serviette") - 0.05
    chef(c, t, 780, 1400, 0.95, angry=(t >= tsv), point=(ST["k01"] < t < ST["a02"]))
    if t < ST["a02"]:
        st = base(t, eyes="wide", mshape="o", sweat=2, rarm=-110)
    elif t < ST["k02"]:
        st = base(t, eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", rarm=-150, wave=0.3)
    else:
        st = base(t, eyes="sad", mshape="grimace", worried=True, rarm=-110, sweat=3)
    ahmed(c, t, 280, 1840, 0.85, st)
    coins(c, t, 470, 1330, 0.8)
    if t >= tsv:
        c.save()
        rrect(c, 430, 1230, 220, 120, 10, "#FFFFFF", 6)
        for k in range(3):
            c.drawLine(450, 1260 + k * 30, 630, 1260 + k * 30, strokep("#E5E0DA", 4))
        c.restore()
        T2.stamp(c, t, tsv, "SERVIETTE: 3,40 €", 540, 560, "#E0245E", 86, -8)
    c.restore()
    tag_pill(c, t, t0 + 0.05)
    caps(c, t, cy=1000 if t < ST["k02"] else 1000)
    if clip:
        c.restore()


def s_chat(c, t):
    t0 = SC["chat"][0]
    clip = iris(c, t, t0, "#C9B8FF", prev="#FFE3B8", cy=700, d=0.35)
    background(c, t, "#C9B8FF", "#D6C9FF")
    tthumb = wf("a03", "Daumen") - 0.05
    tsend = wf("a03", "Döner") - 0.05
    tfast = tsend + 0.25  # Emre antwortet sofort
    tlist = wf("a04", "Extra") - 0.05
    msgs = [("r", "Bruder", t0 + 0.05), ("r", "Bruder?", t0 + 0.2), ("r", "Brauch dich morgen, Notfall", t0 + 0.4)]
    if t >= tthumb:
        msgs.append(("l", "(Daumen hoch)", tthumb))
    msgs.append(("r", "Döner geht auf mich", tsend))
    msgs.append(("l", "BIN DA", tfast))
    msgs.append(("l", "extra Fleisch, Pommes, Ayran", tlist))
    c.save()
    s = back(prog(t, t0, 0.3))
    c.translate(540, 700)
    c.scale(s, s)
    c.translate(-540, -700)
    chat_phone(c, 150, 200, 780, 1060, msgs, t=t, header="Emre (Cousin)")
    rrect(c, 172, 222, 120, 130, 30, "#FFFFFF", 0)
    emre_avatar(c, 242, 287, 42, t)
    c.restore()
    if tthumb <= t < tsend:
        c.save()
        pop(c, t, tthumb, 330, 900, kind="el")
        rrect(c, 200, 790, 260, 230, 40, "#FFFFFF", 6)
        thumbs_up(c, 345, 950, 0.85)
        c.restore()
        T2.stamp(c, t, tthumb + 0.25, "SEIT 3 WOCHEN", 680, 900, "#E5484D", 66, -10)
    t08 = ST["a04"] - 0.05
    if t >= t08 and t < tlist + 0.6:
        c.save()
        shake(c, t, t08, 26, 0.3)
        T2.stamp(c, t, t08, "0,8 SEKUNDEN", 540, 1330, "#2FBF71", 96, -8)
        c.restore()
    tbroke = ST["a05"] - 0.05
    if t < tsend:
        st = base(t, eyes="wide", mshape="grimace" if mouth(t) < 0.12 else "o", worried=True, phone_r=True, rarm=-120)
    elif t < tbroke:
        st = base(t, eyes="wide", mshape="o", phone_r=True, rarm=-120, hop=max(0, math.sin((t - tsend) * 9) * 30) if t < tsend + 0.4 else 0)
    else:
        st = base(t, eyes="sad", mshape="grimace" if mouth(t) < 0.12 else "o", worried=True, sweat=5, rarm=-110)
    ahmed(c, t, 820, 1900, 0.62, st)
    if t >= tbroke:
        coins(c, t, 600, 1640, 0.9, 3)
        T2.stamp(c, t, wf("a05", "drei") - 0.05, "IMMER NOCH 3,40 €", 540, 1330, "#E0245E", 84, 6)
    tag_pill(c, t, t0 + 0.05)
    caps(c, t, cy=1500)
    if clip:
        c.restore()


def mama_icon(c, cx, cy, r):
    circ(c, cx, cy, r, "#F6C9A8", 5)
    oval(c, cx, cy - r * 0.55, r * 1.0, r * 0.5, "#5A3A2A", 0)
    circ(c, cx - r * 0.3, cy, r * 0.1, INK)
    circ(c, cx + r * 0.3, cy, r * 0.1, INK)


def s_poll(c, t):
    t0 = SC["poll"][0]
    clip = iris(c, t, t0, "#7EE0C3", prev="#C9B8FF", cy=900, d=0.35)
    background(c, t, "#7EE0C3", "#93E8CF")
    title(c, t, t0 + 0.05, "IHR ENTSCHEIDET!", 220, 112, "#FFFFFF")
    c.save()
    s = back(prog(t, t0 + 0.25, 0.4))
    c.translate(540, 640)
    c.scale(s, s)
    c.translate(-540, -640)
    card(c, 80, 360, 920, 560, "#FFFFFF", 34, 14, 8)
    text(c, "Emres Bestellung: 14,90 €", 540, 450, "black", 44, INK)
    tA, tB = ST["a06"], wf("a06", "B") - 0.05
    tend = wf("a06", "Schreibt") - 0.1
    for k, (lab, txt, ts) in enumerate([("A", "Mama um Geld fragen", tA), ("B", "Döner auf Raten", tB)]):
        if t < ts:
            continue
        y = 510 + k * 180
        x = back(prog(t, ts, 0.35))
        c.save()
        c.translate(540, y + 65)
        c.scale(x, x)
        c.translate(-540, -(y + 65))
        sel = (k == 0 and t < tB) or (k == 1 and tB <= t < tend)
        rrect(c, 130, y, 820, 130, 30, ("#FFD84D" if k == 0 else "#8FD3FF") if sel else "#F3F1EE", 6)
        circ(c, 205, y + 65, 42, INK)
        text(c, lab, 205, y + 82, "black", 48, "#FFFFFF")
        text(c, txt, 270, y + 80, "black", 40, INK, "l")
        if k == 0:
            mama_icon(c, 900, y + 65, 42)
        else:
            doener(c, 900, y + 60, 0.42)
        c.restore()
    c.restore()
    st = base(t, rarm=-150)
    if t > tend:
        st.update(wave=1, hop=max(0, math.sin((t - tend) * 7) * 40))
    ahmed(c, t, 540, 1840, 1.0, st)
    if t > tend:
        c.save()
        pop(c, t, tend, 540, 1010, kind="el")
        bb = 1 + 0.05 * math.sin(t * 10)
        c.translate(540, 1010)
        c.scale(bb, bb)
        c.translate(-540, -1010)
        pill(c, "KOMMENTIERE A ODER B", 540, 1010, 58, fill="#E0245E", name="black", padx=40, pady=24)
        c.restore()
        if t > tend + 0.5:
            c.save()
            pop(c, t, tend + 0.5, 540, 1115)
            pill(c, "FOLG MIR · TAG 7 MORGEN 12 UHR", 540, 1115, 42, fill=INK, col="#FFD84D", name="black")
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
    Nn = int(TOTAL * SR)
    mus = np.zeros(Nn + SR)
    sfx = np.zeros(Nn + SR)
    beat = 60 / 112

    def tension(a, b, notes=(50, 50, 53, 50)):
        t, k = a, 0
        while t < b:
            add(mus, t, pizz(mtof(notes[k % 4]), 1.0))
            if k % 2 == 0:
                add(mus, t, taiko(0.35))
            t += beat / 2
            k += 1

    def bounce(a, b, seq=(62, 69, 66, 69, 62, 69, 67, 69)):
        t, k = a, 0
        while t < b:
            add(mus, t, pizz(mtof(seq[k % 8]), 1.0 if k % 2 == 0 else 0.7))
            if k % 4 == 0:
                add(mus, t, taiko(0.3))
            t += beat / 2
            k += 1

    def stampfx(t0):
        add(sfx, t0, thud(), 0.9)
        add(sfx, t0 + 0.05, bell(2637, 0.4, 0.15))

    def coin(t0):
        for j in range(3):
            add(sfx, t0 + j * 0.07, bell(3520 + j * 400, 0.25, 0.12))

    # cold
    a, b = SC["cold"]
    add(sfx, 0.0, thud(), 0.8)
    add(mus, 0.0, braam(33, 2.0), 0.7)
    tm = wf("a01", "drei") - 0.05
    bounce(0.25, tm)
    stampfx(tm)
    coin(tm)
    add(sfx, tm, buzzer(), 0.3)
    tension(tm + 0.2, b)
    # shop
    a, b = SC["shop"]
    bounce(a + 0.05, ST["k02"], (60, 67, 64, 67, 60, 67, 65, 67))
    add(sfx, ST["k01"] - 0.05, bell(1760, 0.5, 0.2))  # Kasse
    tsv = wf("k02", "Serviette") - 0.05
    add(mus, tsv - 0.4, riser(0.4), 0.5)
    stampfx(tsv)
    add(mus, tsv, braam(36, 1.2), 0.6)
    # chat
    a, b = SC["chat"]
    tension(a + 0.05, wf("a03", "Döner") - 0.05, (50, 53, 50, 55))
    add(sfx, wf("a03", "Daumen") - 0.05, pop_(), 0.5)
    stampfx(wf("a03", "Daumen") + 0.2)
    tsend = wf("a03", "Döner") - 0.05
    add(sfx, tsend, whoosh(0.3), 0.5)
    add(sfx, tsend + 0.25, pop_(), 0.6)
    t08 = ST["a04"] - 0.05
    stampfx(t08)
    bounce(t08 + 0.1, ST["a05"] - 0.3)
    add(sfx, wf("a04", "Extra") - 0.05, pop_(), 0.5)
    tb = ST["a05"] - 0.05
    for j, m in enumerate([67, 66, 65, 62]):
        add(mus, tb + j * 0.28, strings(mtof(m - 12), 0.32 if j < 3 else 0.9, 0.02, 0.2, 1500), 0.8)
    stampfx(wf("a05", "drei") - 0.05)
    coin(wf("a05", "drei") - 0.05)
    # poll
    a, b = SC["poll"]
    cta = wf("a06", "Schreibt") - 0.1
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
    add(sfx, ST["a06"], pop_(), 0.35)
    add(sfx, wf("a06", "B") - 0.05, pop_(), 0.35)
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

FN = {"cold": s_cold, "shop": s_shop, "chat": s_chat, "poll": s_poll}


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
        final(sys.argv[3] if len(sys.argv) > 3 else f"{D}/tag06.mp4")
