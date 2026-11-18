# Tag 8 "Lena zu Mama" (Abstimmung Tag 7: A 4:0) – ein Reel pro Tag (BEFEHLE.md Befehl 5), PART=1 = ganze Folge mit A/B
# Setup (einmal pro Lauf), siehe README.md in diesem Ordner:
#   /home/claude/{draw.py,scenes.py,audio.py,mix.sh,tts.py,fonts,timeline.json(dummy)} und /home/claude/tag2 (Hilfsmodul)
# Nutzung: python3 tag08.py <PART> tts | info | preview t1 t2 .. | scene <name..> | audio | all
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
D = f"/home/claude/tag08_work/teil{PART}"
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



# ---------------- Tag 8: Timeline ----------------
e = put("a01", 0.05)
SC["cold"] = (0.0, e + 0.15)
s = SC["cold"][1]
e = put("a02", s + 0.1)
e = put("a03", e + 0.08)
e = put("a04", e + 0.05)
e = put("a05", e + 0.08)
SC["chat"] = (s, e + 0.25)
s = SC["chat"][1]
e = put("a07", s + 0.1)
SC["gruppe"] = (s, e + 0.6)
s = SC["gruppe"][1]
e = put("a08", s + 0.1)
e = put("a09", e + 0.15)
SC["echt"] = (s, e + 0.35)
s = SC["echt"][1]
e = put("a10", s + 0.2)
SC["poll"] = (s, e + 0.75)
ORDER = ["cold", "chat", "gruppe", "echt", "poll"]
TOTAL = SC[ORDER[-1]][1]
CLIFF = None


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
    pill(c, "TAG 8", 540, 110, 44, fill=INK, col="#FFD84D", name="black")
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



def mama_icon(c, cx, cy, r, hair="#5A3A2A", scarf=None, glasses=False):
    if scarf:
        circ(c, cx, cy + r * 0.1, r * 1.22, scarf, 5)
    circ(c, cx, cy, r, "#F6C9A8", 5)
    if not scarf:
        oval(c, cx, cy - r * 0.55, r * 1.0, r * 0.5, hair, 0)
    circ(c, cx - r * 0.3, cy, r * 0.1, INK)
    circ(c, cx + r * 0.3, cy, r * 0.1, INK)
    if glasses:
        circ(c, cx - r * 0.32, cy, r * 0.26, None, max(3, r * 0.07))
        circ(c, cx + r * 0.32, cy, r * 0.26, None, max(3, r * 0.07))
    mp = skia.Path()
    mp.moveTo(cx - r * 0.25, cy + r * 0.4)
    mp.quadTo(cx, cy + r * 0.55, cx + r * 0.25, cy + r * 0.4)
    c.drawPath(mp, strokep(INK, max(3, r * 0.08)))


def voice_note(c, t, x, y, w, t0, dur_label="4:12"):
    """Sprachnachricht-Bubble mit Wellenform, Fortschritt laeuft"""
    rrect(c, x, y, w, 130, 34, "#FFFFFF", 6)
    circ(c, x + 70, y + 65, 40, "#2FBF71")
    p = skia.Path()
    p.moveTo(x + 58, y + 42)
    p.lineTo(x + 92, y + 65)
    p.lineTo(x + 58, y + 88)
    p.close()
    c.drawPath(p, fillp("#FFFFFF"))
    n = 26
    prog_ = min(1.0, max(0.0, (t - t0) / 6.0))
    r = random.Random(7)
    for k in range(n):
        hgt = 14 + r.random() * 60
        xx = x + 140 + k * (w - 260) / n
        col = "#2FBF71" if k / n < prog_ else "#C9C4BD"
        c.drawLine(xx, y + 65 - hgt / 2, xx, y + 65 + hgt / 2, strokep(col, 8))
    text(c, dur_label, x + w - 60, y + 78, "black", 34, INK)



def scissors(c, cx, cy, s=1.0):
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.drawLine(-30, -40, 30, 30, strokep("#8A8A8A", 12))
    c.drawLine(30, -40, -30, 30, strokep("#8A8A8A", 12))
    circ(c, -36, 42, 18, None, 8)
    circ(c, 36, 42, 18, None, 8)
    c.restore()


def s_cold(c, t):
    c.save()
    shake(c, t, 0.0, 18, 0.4)
    living_room(c)
    tk = wf("a01", "kein") - 0.05
    if t < tk:
        st = base(t, eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", phone_r=True, rarm=-120, larm=-20)
    else:
        st = base(t, eyes="sad", mshape="grimace" if mouth(t) < 0.15 else "o", sweat=4, worried=True, phone_r=True, rarm=-120)
    ahmed(c, t, 540, 1840, 1.0, st)
    c.save()
    pop(c, t, 0.0, 540, 900, d=0.25)
    pill(c, "ERSTES DATE: BEI MAMA.", 540, 900, 62, fill="#E0245E", name="black", padx=36, pady=26)
    c.restore()
    if t >= tk:
        c.save()
        shake(c, t, tk, 24, 0.3)
        T2.stamp(c, t, tk, "0 DATES", 540, 360, "#E5484D", 130, -8)
        c.restore()
    c.restore()
    caps(c, t, cy=1110)


def s_chat(c, t):
    t0 = SC["chat"][0]
    clip = iris(c, t, t0, "#FFB3C7", prev="#F6E7C8", cy=700, d=0.35)
    background(c, t, "#FFB3C7", "#FFC6D5")
    tz = ST["a02"]
    tab = wf("a02", "Sonntag") - 0.05
    tok = wf("a05", "Okay") - 0.05
    msgs = []
    if t >= tab:
        msgs.append(("r", "Sonntag Hunger?", tab))
    if t >= ST["a03"]:
        msgs.append(("l", "Wer kocht?", ST["a03"]))
    if t >= ST["a04"]:
        msgs.append(("r", "Meine Mama.", ST["a04"]))
    if t >= ST["a05"]:
        msgs.append(("l", "Erst Mama, dann du?", ST["a05"]))
    if t >= tok:
        msgs.append(("l", "Okay, ich komme.", tok))
    c.save()
    sc = back(prog(t, t0, 0.3))
    c.translate(540, 700)
    c.scale(sc, sc)
    c.translate(-540, -700)
    chat_phone(c, 150, 200, 780, 1060, msgs, t=t, header="Lena", dots=(ST["a03"] - 0.6 < t < ST["a03"]))
    c.restore()
    if tz <= t < tab + 0.6:
        c.save()
        shake(c, t, tz, 18, 0.3)
        T2.stamp(c, t, tz, "20 MIN GETIPPT", 540, 1340, "#8E5CC2", 80, -6)
        c.restore()
    if t >= tok:
        c.save()
        shake(c, t, tok, 26, 0.3)
        T2.stamp(c, t, tok + 0.6, "SIE KOMMT!", 560, 1330, "#2FBF71", 100, 8)
        c.restore()
    if t < ST["a03"]:
        st = base(t, eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", phone_r=True, rarm=-120)
    elif t < tok:
        st = base(t, eyes="wide", mshape="grimace" if mouth(t) < 0.12 else "o", phone_r=True, rarm=-120, sweat=3, worried=True)
    else:
        st = base(t, eyes="heart", mshape="smile", rarm=-150, wave=0.6, hop=max(0, math.sin((t - tok) * 7) * 30))
    ahmed(c, t, 860, 1960, 0.55, st)
    tag_pill(c, t, t0 + 0.05)
    caps(c, t, cy=1560)
    if clip:
        c.restore()


def s_gruppe(c, t):
    t0 = SC["gruppe"][0]
    clip = iris(c, t, t0, "#C9B8FF", prev="#FFB3C7", cy=800, d=0.35)
    background(c, t, "#C9B8FF", "#D6C9FF")
    t47 = ST["a07"]
    tbek = wf("a07", "Bekannte") - 0.05
    tver = wf("a07", "Verlobte") - 0.05
    m1 = SC["gruppe"][0] + 0.35
    tm = wf("a07", "Mama") - 0.05
    msgs = [("r", "Ahmed: Sie ist nur eine Bekannte", tbek + 0.2)] if t >= tbek + 0.2 else []
    for k, (txt, dt) in enumerate([("Mama: Sonntag kommt Ahmeds VERLOBTE!", 0.0), ("Tante Fatma: Aus guter Familie?", 0.7), ("Onkel Hakan: Ich bring den Grill", 1.3), ("Oma: Wann ist die Hochzeit?", 1.9)]):
        if t >= tm + dt:
            msgs.append(("l", txt, tm + dt))
    c.save()
    sc = back(prog(t, t0, 0.3))
    c.translate(540, 700)
    c.scale(sc, sc)
    c.translate(-540, -700)
    chat_phone(c, 150, 200, 780, 1060, msgs, t=t, header="Familie (47)")
    rrect(c, 172, 222, 120, 130, 30, "#FFFFFF", 0)
    mama_icon(c, 242, 287, 42)
    c.restore()
    if t >= tver:
        c.save()
        shake(c, t, tver, 30, 0.35)
        T2.stamp(c, t, tver, "VERLOBTE?!", 560, 1340, "#E0245E", 120, -8)
        c.restore()
    if t < t47:
        st = base(t, eyes="wide", mshape="o", phone_r=True, rarm=-120, sweat=2)
    elif t < tver:
        st = base(t, eyes="sad", mshape="grimace" if mouth(t) < 0.12 else "o", phone_r=True, rarm=-120, sweat=4, worried=True)
    else:
        st = base(t, eyes="wide", mshape="grimace", sweat=8, worried=True, rarm=-150, larm=150)
    ahmed(c, t, 860, 1960, 0.55, st)
    tag_pill(c, t, t0 + 0.05)
    caps(c, t, cy=1560)
    if clip:
        c.restore()


def s_echt(c, t):
    t0 = SC["echt"][0]
    clip = iris(c, t, t0, "#FF9EB5", prev="#C9B8FF", cy=800, d=0.35)
    c.save()
    tg = wf("a09", "Gesicht") - 0.05
    te = wf("a09", "Emres") - 0.05
    shake(c, t, te, 26, 0.35)
    background(c, t, "#FF9EB5", "#FFB3C6")
    # Lenas Nachricht oben
    c.save()
    pop(c, t, ST["a08"], 540, 300, kind="el")
    rrect(c, 110, 210, 860, 190, 50, "#FFFFFF", 8)
    lena_avatar(c, 200, 305, 60)
    text(c, "Freu mich! Endlich", 590, 290, "black", 50, INK)
    text(c, "in echt <3", 590, 360, "black", 50, "#E0245E")
    c.restore()
    # Tinder-Karte: Emres Gesicht, Ahmeds Name
    c.save()
    sc = back(prog(t, t0 + 0.15, 0.35))
    c.translate(330, 820)
    c.scale(sc, sc)
    c.translate(-330, -820)
    card(c, 110, 470, 440, 620, "#FFFFFF", 40, 12, 8)
    c.save()
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(135, 495, 390, 450), 26, 26)
    c.clipRRect(rr, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(135, 495, 390, 450), fillp("#7FD1FF"))
    emre(c, 330, 750, 1.05, t)
    c.restore()
    text(c, "Ahmed, 27", 330, 1030, "black", 50, INK)
    c.restore()
    if t >= tg:
        c.save()
        pop(c, t, tg, 790, 780, kind="el")
        card(c, 600, 520, 380, 520, "#FFFFFF", 40, 12, 8)
        c.save()
        rr2 = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(622, 542, 336, 380), 26, 26)
        c.clipRRect(rr2, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(622, 542, 336, 380), fillp("#FFE08A"))
        small_head(c, t, 790, 790, 0.42, base(t, eyes="wide", mshape="grimace", sweat=5, worried=True))
        c.restore()
        text(c, "Ahmed, echt", 790, 1000, "black", 44, INK)
        c.restore()
        c.save()
        pop(c, t, tg + 0.15, 565, 760, kind="el")
        circ(c, 565, 760, 62, "#E0245E", 7)
        text(c, "VS", 565, 782, "black", 58, "#FFFFFF")
        c.restore()
    if t >= te:
        T2.stamp(c, t, te, "SONNTAG: ECHTES GESICHT", 540, 1190, "#E5484D", 66, -8)
    if t < tg:
        st = base(t, eyes="heart" if t < ST["a09"] else "wide", mshape="smile" if t < ST["a09"] else "o", rarm=-110)
    else:
        st = base(t, eyes="wide", mshape="grimace" if mouth(t) < 0.12 else "o", sweat=7, worried=True, rarm=-150, larm=150)
    ahmed(c, t, 780, 2010, 0.62, st)
    c.restore()
    tag_pill(c, t, t0 + 0.05)
    caps(c, t, cy=1480)
    if clip:
        c.restore()


def s_poll(c, t):
    t0 = SC["poll"][0]
    clip = iris(c, t, t0, "#7EE0C3", prev="#FF9EB5", cy=900, d=0.35)
    background(c, t, "#7EE0C3", "#93E8CF")
    title(c, t, t0 + 0.05, "IHR ENTSCHEIDET!", 220, 112, "#FFFFFF")
    c.save()
    s = back(prog(t, t0 + 0.25, 0.4))
    c.translate(540, 640)
    c.scale(s, s)
    c.translate(-540, -640)
    card(c, 80, 360, 920, 560, "#FFFFFF", 34, 14, 8)
    text(c, "Sonntag: Lena trifft Mama", 540, 450, "black", 46, INK)
    tA, tB = ST["a10"], wf("a10", "B") - 0.05
    tend = wf("a10", "Schreibt") - 0.1
    for k, (lab, txt, ts) in enumerate([("A", "Emre mitnehmen", tA), ("B", "Friseur: wie Emre", tB)]):
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
            emre_avatar(c, 890, y + 65, 46, t)
        else:
            scissors(c, 890, y + 60, 0.9)
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
            pill(c, "FOLG MIR · TAG 9 MORGEN 12 UHR", 540, 1115, 42, fill=INK, col="#FFD84D", name="black")
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

    def ding(t0):
        add(sfx, t0, bell(1760, 0.3, 0.15))
        add(sfx, t0 + 0.08, bell(2349, 0.3, 0.12))

    def sad_trombone(t0):
        for j, m in enumerate([67, 66, 65, 62]):
            add(mus, t0 + j * 0.28, strings(mtof(m - 12), 0.32 if j < 3 else 0.9, 0.02, 0.2, 1500), 0.8)

    # cold
    add(sfx, 0.0, thud(), 0.8)
    add(mus, 0.0, braam(33, 2.0), 0.7)
    tk = wf("a01", "kein") - 0.05
    bounce(0.25, tk - 0.1)
    stampfx(tk)
    add(sfx, tk, buzzer(), 0.3)
    sad_trombone(tk + 0.1)
    # chat
    a, b = SC["chat"]
    stampfx(ST["a02"])
    tab = wf("a02", "Sonntag") - 0.05
    add(sfx, tab, whoosh(0.3), 0.5)
    tension(a + 0.3, ST["a05"] - 0.2, (50, 53, 50, 55))
    ding(ST["a03"])
    add(sfx, ST["a04"], whoosh(0.3), 0.4)
    ding(ST["a05"])
    tok = wf("a05", "Okay") - 0.05
    ding(tok)
    bounce(tok + 0.1, b)
    stampfx(tok + 0.6)
    # gruppe
    a, b = SC["gruppe"]
    tm = wf("a07", "Mama") - 0.05
    for dt in (0.0, 0.7, 1.3, 1.9):
        ding(tm + dt)
    tension(a + 0.1, wf("a07", "Verlobte") - 0.3)
    tver = wf("a07", "Verlobte") - 0.05
    add(sfx, tver, scratch(), 0.6)
    stampfx(tver)
    add(mus, tver, braam(36, 1.4), 0.8)
    # echt
    a, b = SC["echt"]
    ding(ST["a08"])
    bounce(ST["a08"], ST["a09"] - 0.1, (64, 71, 68, 71, 64, 71, 69, 71))
    add(mus, ST["a09"] - 0.3, riser(0.3), 0.5)
    tg = wf("a09", "Gesicht") - 0.05
    add(sfx, tg, pop_(), 0.6)
    te = wf("a09", "Emres") - 0.05
    stampfx(te)
    add(mus, te, braam(34, 1.2), 0.8)
    add(sfx, te, buzzer(), 0.35)
    # poll
    a, b = SC["poll"]
    cta = wf("a10", "Schreibt") - 0.1
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
    add(sfx, ST["a10"], pop_(), 0.35)
    add(sfx, wf("a10", "B") - 0.05, pop_(), 0.35)
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
FN = {"cold": s_cold, "chat": s_chat, "gruppe": s_gruppe, "echt": s_echt, "poll": s_poll}



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
        final(sys.argv[3] if len(sys.argv) > 3 else f"{D}/tag08.mp4")

