import json, math, random
import skia
from draw import *

TL = json.load(open("/home/claude/timeline.json"))
MOUTH = TL["mouth"]
EV = TL["ev"]
T1 = TL["t1"]
SC = {n: (a, b) for n, a, b in TL["scenes"]}
FPS = 30

DISPLAY = {
    "a01": ["Bruder…", "847", "Mal", "nach", "rechts", "gewischt.", "Null", "Matches."],
    "a03": ["Digga…", "Lena,", "24.", "Dieses", "Lächeln…", "mein", "Herz", "macht", "gerade", "Parkour."],
    "l01": ["Hey", "Ahmed.", "Dein", "Profil", "hat", "mich", "direkt", "angelächelt."],
    "a04": ["Okay,", "cool", "bleiben.", "Ich", "schreib", "auf", "Englisch,", "wirkt", "internationaler."],
    "l02": ["Haha,", "süß.", "Du", "weißt", "aber,", "dass", "ich", "aus", "Gelsenkirchen", "komme?"],
    "a05": ["…Okay.", "Deutsch", "geht", "auch."],
    "a06": ["Psst.", "Kleines", "Geheimnis:", "Das", "auf", "meinem", "Profilbild…", "ist", "mein", "Cousin", "Emre."],
    "l03": ["In", "30", "Tagen", "bin", "ich", "in", "deiner", "Stadt.", "Treffen", "wir", "uns…", "bei", "Sonnenuntergang?"],
    "a08": ["Sonnenuntergang?", "Ja", "klar.", "Ganz", "easy."],
    "a09": ["…Problem."],
    "a10": ["Kontostand:", "3", "Euro", "40.", "Und", "ein", "Pfandbon.", "Reicht", "für", "einen", "halben", "Döner."],
    "a11": ["Bruder,", "ich", "brauch", "euch.", "A:", "Arbeit", "suchen.", "Oder", "B:", "endlich", "duschen."],
    "a12": ["Beides", "gleichzeitig?", "Nein", "Bruder,", "so", "stark", "bin", "ich", "nicht."],
    "a13": ["Stimmt", "ab,", "wallah!", "Tag", "2", "kommt", "morgen."],
}

CHUNKS = []
LINES = {l["id"]: l for l in TL["lines"]}
WT = {}
for l in TL["lines"]:
    toks = DISPLAY[l["id"]]
    ws = l["words"]
    assert len(toks) == len(ws), (l["id"], len(toks), len(ws))
    WT[l["id"]] = [w[0] for w in ws]
    cur = []
    for k, (tok, w) in enumerate(zip(toks, ws)):
        cur.append((tok, w[0]))
        brk = (tok[-1] in ".!?:…" and len(cur) >= 2) or len(cur) >= 5
        if brk or k == len(toks) - 1:
            CHUNKS.append(dict(who=l["who"], words=cur, start=cur[0][1] - 0.06, line=l["id"]))
            cur = []
for k, ch in enumerate(CHUNKS):
    line = LINES[ch["line"]]
    nxt = CHUNKS[k + 1]["start"] if k + 1 < len(CHUNKS) else 1e9
    ch["end"] = min(nxt, line["end"] + 0.4)


def wt(i, k):
    return WT[i][k]


def mouth_at(t):
    f = int(t * FPS)
    return MOUTH[f] if 0 <= f < len(MOUTH) else 0.0


def blink(t):
    return (t % 3.3) < 0.11


def draw_caption(c, t, cy=1050, tail=True, only=None):
    for ch in CHUNKS:
        if only and ch["line"] not in only:
            continue
        if ch["start"] <= t < ch["end"]:
            caption(c, t, ch["who"], ch["words"], cy, tail_x=(560 if ch["who"] == "A" and tail else None), appear=ch["start"])


def base_state(t):
    return dict(mouth=mouth_at(t), blink=blink(t))


def float_hearts(c, t, n=7, alpha=150, seed=1, col="#FFFFFF"):
    r = random.Random(seed)
    for k in range(n):
        x0 = r.uniform(60, 1020)
        sp = r.uniform(60, 130)
        ph = r.uniform(0, 30)
        sz = r.uniform(14, 30)
        y = 1950 - ((t * sp + ph * 60) % 2100)
        x = x0 + math.sin(t * 1.3 + k) * 30
        heart(c, x, y, sz, col, 0, a=alpha)


def glow(c, cx, cy, r, col, a=120):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, [C(col, a), C(col, 0)]))
    c.drawCircle(cx, cy, r, p)


def grad_text(c, s, x, y, name, size, cols, stroke=0):
    f = font(name, size)
    w = f.measureText(s)
    x0 = x - w / 2
    if stroke:
        c.drawString(s, x0, y, f, strokep(INK, stroke))
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y - size * 0.8), skia.Point(0, y + size * 0.1)], [C(cc) for cc in cols]))
    c.drawString(s, x0, y, f, p)
    return w


def head_only(c, cx, cy, s, st, t):
    c.save()
    c.translate(cx, cy)
    c.scale(s, s)
    c.translate(-585, -470)
    ahmed_head(c, st, t)
    c.restore()


def halftone(c, x, y, w, h, col, dot="#000000", a=40):
    rrect(c, x, y, w, h, 0, col)
    p = fillp(dot, a)
    yy = y + 14
    k = 0
    while yy < y + h:
        xx = x + 14 + (k % 2) * 13
        while xx < x + w:
            c.drawCircle(xx, yy, 5, p)
            xx += 26
        yy += 22
        k += 1


# ------------------------------------------------------------------ INTRO (comic flip, cinematic)
PANELS = ["face", "phone", "lena", "emre", "money", "shower", "heart", "face2"]
PCOL = ["#F9D85E", "#FF9EC0", "#FFB3C7", "#7FD1FF", "#FF6B4A", "#7EE0C3", "#F0507F", "#B79CF2"]


def panel_content(c, kind, t):
    cx, cy = 540, 960
    if kind in ("face", "face2"):
        head_only(c, cx, cy + 40, 0.95, dict(eyes="derp" if kind == "face" else "wide", mshape="smile" if kind == "face" else "o", mouth=0.4, sweat=1 if kind == "face" else 3), t)
    elif kind == "phone":
        c.save()
        c.translate(cx, cy)
        c.rotate(-8)
        rrect(c, -190, -340, 380, 680, 50, "#F27BAE", 12)
        rrect(c, -160, -300, 320, 590, 26, "#FFFFFF", 0)
        heart(c, 0, -20, 110, "#F0507F", 10)
        text(c, "MATCH", 0, 190, "black", 70, INK)
        c.restore()
    elif kind == "lena":
        lena_avatar(c, cx, cy, 330)
    elif kind == "emre":
        emre_avatar(c, cx, cy, 330, t)
    elif kind == "money":
        for k, (dx, dy) in enumerate([(-150, -60), (60, 40), (180, -140), (-40, 180)]):
            circ(c, cx + dx, cy + dy, 120, "#E9C46A", 12)
            text(c, "€", cx + dx, cy + dy + 45, "black", 130, INK)
        title_txt(c, "3,40 €", cx, cy + 470, 150, "#FFFFFF")
    elif kind == "shower":
        shower(c, cx, cy - 40, 5.0, t)
    elif kind == "heart":
        heart(c, cx, cy, 300 * (1 + 0.06 * math.sin(t * 20)), "#E0245E", 14)


def title_txt(c, s, x, y, size, col):
    text(c, s, x + 10, y + 12, "lilita", size, INK, stroke=24)
    text(c, s, x, y, "lilita", size, col, stroke=22)
    text(c, s, x, y, "lilita", size, col)


def s_intro(c, t):
    c.clear(C("#0B0C16"))
    flip_end = 1.25
    if t < flip_end:
        # accelerating flips
        times = [0.0, 0.2, 0.38, 0.54, 0.68, 0.8, 0.91, 1.01, 1.1, 1.18]
        k = max(i for i, x in enumerate(times) if x <= t)
        k = min(k, len(PANELS) - 1)
        t0 = times[k]
        t1 = times[k + 1] if k + 1 < len(times) else flip_end
        x = (t - t0) / max(t1 - t0, 1e-3)
        zoom = 1.0 + 0.25 * (t / flip_end)
        c.save()
        c.translate(540, 960)
        c.scale(zoom, zoom)
        sq = math.cos(min(x, 1) * math.pi * 0.5) ** 0.3 if x > 0.75 else 1.0
        sq = max(0.02, 1 - eio((x - 0.7) / 0.3)) if x > 0.7 else 1.0
        c.scale(sq, 1)
        c.rotate((k % 2 * 2 - 1) * 3)
        c.translate(-540, -960)
        card(c, 80, 240, 920, 1440, PCOL[k], 10, 18, 10)
        c.save()
        cl = skia.Path()
        cl.addRect(skia.Rect.MakeXYWH(85, 245, 910, 1430))
        c.clipPath(cl, doAntiAlias=True)
        halftone(c, 85, 245, 910, 1430, PCOL[k])
        panel_content(c, PANELS[k], t)
        c.restore()
        c.restore()
        # speed lines
        r = random.Random(int(t * 30))
        for j in range(14):
            yy = r.uniform(0, 1920)
            c.drawLine(0, yy, r.uniform(80, 260), yy, strokep("#FFFFFF", 4, 90))
            c.drawLine(1080, yy + 40, 1080 - r.uniform(80, 260), yy + 40, strokep("#FFFFFF", 4, 90))
    else:
        tt = t - flip_end
        glow(c, 540, 900, 900, "#E0245E", 110)
        glow(c, 540, 900, 500, "#FFB347", 90)
        # rays
        c.save()
        c.translate(540, 900)
        c.rotate(tt * 20)
        for k in range(12):
            a0 = 2 * math.pi * k / 12
            pa = skia.Path()
            pa.moveTo(0, 0)
            pa.lineTo(1600 * math.cos(a0), 1600 * math.sin(a0))
            pa.lineTo(1600 * math.cos(a0 + 0.12), 1600 * math.sin(a0 + 0.12))
            pa.close()
            c.drawPath(pa, fillp("#FFFFFF", 14))
        c.restore()
        s = 1.35 - 0.35 * eo(tt / 0.45)
        c.save()
        c.translate(540, 900)
        c.scale(s, s)
        c.translate(-540, -900)
        a = int(255 * clamp(tt / 0.15))
        text(c, "TAG 1", 548, 832, "lilita", 260, "#000000", a=a, stroke=30)
        grad_text(c, "TAG 1", 540, 820, "lilita", 260, ["#FFF4C2", "#FFC93C", "#F08A24"], stroke=26)
        text(c, "DAS MATCH", 540, 1000, "black", 110, "#FFFFFF", a=a)
        c.restore()
        # light sweep across title
        sx = -300 + eio(tt / 0.7) * 1700
        p = skia.Paint(AntiAlias=True)
        p.setShader(skia.GradientShader.MakeLinear([skia.Point(sx - 120, 0), skia.Point(sx + 120, 0)], [C("#FFFFFF", 0), C("#FFFFFF", 110), C("#FFFFFF", 0)]))
        c.save()
        c.rotate(12)
        c.drawRect(skia.Rect.MakeXYWH(-400, 500, 2000, 700), p)
        c.restore()
        text(c, "EINE  AHMED  STORY", 540, 1120, "xbold", 40, "#FFD84D", a=int(255 * clamp((tt - 0.25) / 0.3)))
        # flash
        fa = int(255 * clamp(1 - tt / 0.18))
        if fa > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), fillp("#FFFFFF", fa))
    # letterbox bars
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 120), fillp("#000000"))
    c.drawRect(skia.Rect.MakeXYWH(0, H - 120, W, 120), fillp("#000000"))


# ------------------------------------------------------------------ HOOK
def s_hook(c, t):
    t0 = SC["hook"][0]
    clip = iris(c, t, t0, "#F9D85E", prev="#0B0C16", cy=900, d=0.35)
    background(c, t, "#F9D85E", "#FBE07A")
    n0, step = t0 + 0.2, 0.3
    last = wt("a01", 6) - 0.25
    k = int((t - n0) / step) if t > n0 else 0
    cx, cy = 540, 585
    for j in (k + 1, k):
        tj = n0 + j * step
        if tj > last:
            continue
        x = (t - tj) / step
        c.save()
        if x < 0:
            c.translate(cx, cy)
            c.scale(0.92, 0.92)
        else:
            fly = clamp((x - 0.5) / 0.5)
            c.translate(cx + eo(fly) * 950, cy + eo(fly) * 90)
            c.rotate(eo(fly) * 28)
        random.seed(j)
        bgc = random.choice(["#8FD3FF", "#FFB3C7", "#B79CF2", "#9BE3B0", "#FFD08A"])
        card(c, -190, -230, 380, 460, "#FFFFFF", 30, 12, 7)
        rrect(c, -170, -210, 340, 330, 20, bgc)
        circ(c, 0, -90, 70, "#FFFFFF", 0, a=170)
        oval(c, 0, 60, 110, 70, "#FFFFFF", 0, a=170)
        rrect(c, -150, 140, 200, 26, 13, "#DDDDDD")
        rrect(c, -150, 180, 130, 22, 11, "#EEEEEE")
        if x > 0.25:
            c.save()
            c.translate(-60, -120)
            c.rotate(-18)
            rrect(c, -95, -38, 190, 76, 14, "#FFFFFF", 7, ink="#2FBF71")
            text(c, "LIKE", 0, 22, "black", 52, "#2FBF71")
            c.restore()
        c.restore()
    # "NULL MATCHES" stamp
    tn = wt("a01", 6)
    if tn < t < EV["notif"]:
        x = prog(t, tn, 0.25)
        c.save()
        c.translate(540, 585)
        c.rotate(-10)
        ss = 2.4 - 1.4 * eo(x)
        c.scale(ss, ss)
        a = int(255 * clamp(x * 3))
        rrect(c, -300, -80, 600, 160, 20, "#FFFFFF", 0, a=int(a * 0.9))
        rrect(c, -300, -80, 600, 160, 20, None, 12, ink="#E5484D", a=a)
        text(c, "0 MATCHES", 0, 32, "black", 96, "#E5484D", a=a)
        c.restore()
    if t > EV["notif"]:
        c.save()
        pop(c, t, EV["notif"], 540, 560)
        card(c, 150, 470, 780, 180, "#FFFFFF", 36, 12, 7)
        rrect(c, 185, 505, 110, 110, 26, "#F0507F")
        heart(c, 240, 565, 34 * (1 + 0.15 * abs(math.sin(t * 8))), "#FFFFFF", 0)
        text(c, "Neues Match!", 325, 552, "black", 52, INK, "l")
        text(c, "Jemand mag dich zurück", 325, 600, "semi", 32, "#777777", "l")
        c.restore()
        c.save()
        pop(c, t, EV["notif"] + 0.25, 540, 850)
        pill(c, "Bis heute…", 540, 850, 54, fill="#E0245E")
        c.restore()
    else:
        cnt = int(847 * eio(prog(t, t0 + 0.3, wt("a01", 5) - t0 - 0.3)))
        c.save()
        pop(c, t, t0 + 0.2, 540, 850)
        pill(c, f"{cnt}× nach rechts gewischt", 540, 850, 44)
        c.restore()
    for k2 in range(2):
        a = t * (3 + k2) + k2 * 2
        fx = 540 + math.cos(a) * (300 - k2 * 60)
        fy = 1350 + math.sin(a * 1.7) * 120
        oval(c, fx - 9, fy - 9, 9, 6, "#FFFFFF", 3, a=200)
        oval(c, fx + 9, fy - 9, 9, 6, "#FFFFFF", 3, a=200)
        circ(c, fx, fy, 8, INK)
    st = base_state(t)
    st.update(phone_r=True, rarm=-150, buzz=1.0 if EV["notif"] < t < EV["notif"] + 0.6 else 0.0)
    if t > EV["notif"]:
        st["eyes"] = "wide"
        st["mshape"] = "o"
    elif t > tn:
        st["eyes"] = "sad"
        st["mshape"] = "sad"
    st["rarm"] += math.sin(t * 22) * 6 if t < last else 0
    ahmed(c, t, 540, 1840, 1.0, st)
    c.save()
    pop(c, t, t0 + 0.05, 540, 150)
    pill(c, "TAG 1", 540, 150, 50, fill=INK, col="#FFD84D", name="black")
    c.restore()
    draw_caption(c, t)
    if clip:
        c.restore()


# ------------------------------------------------------------------ MATCH
HEARTS = [(random.Random(i).uniform(0, 2 * math.pi), random.Random(i + 99).uniform(500, 1100), random.Random(i + 7).uniform(18, 46)) for i in range(26)]


def s_match(c, t):
    t0 = SC["match"][0]
    clip = iris(c, t, t0, "#FF9EC0", prev="#F9D85E", cy=640)
    background(c, t, "#FF9EC0", "#FFB5CF")
    glow(c, 540, 650, 520 * (1 + 0.04 * math.sin(t * 6)), "#FFFFFF", 110)
    float_hearts(c, t, 9, 120, 3)
    bt = t - t0 - 0.15
    if 0 < bt < 2.2:
        for (a, v, s) in HEARTS:
            x = 540 + math.cos(a) * v * bt
            y = 640 + math.sin(a) * v * bt + 700 * bt * bt
            heart(c, x, y, s, "#F0507F", 5, a=int(255 * clamp(1.8 - bt)))
    sl = eo(prog(t, t0 + 0.15, 0.45))
    lena_avatar(c, -200 + sl * 500, 640, 150)
    emre_avatar(c, 1280 - sl * 500, 640, 150, t)
    if sl > 0.5:
        c.save()
        pop(c, t, t0 + 0.4, 300, 830)
        pill(c, "Lena, 24", 300, 830, 40)
        c.restore()
        c.save()
        pop(c, t, t0 + 0.5, 780, 830)
        pill(c, "Ahmed, 27", 780, 830, 40)
        c.restore()
    beat = (t - t0) % 0.85
    hb = 1 + 0.18 * math.exp(-beat * 14) + 0.12 * math.exp(-max(0, beat - 0.2) * 14) * (beat > 0.2)
    c.save()
    pop(c, t, t0 + 0.55, 540, 650)
    heart(c, 540, 650, 62 * hb, "#E0245E", 8)
    c.restore()
    st = base_state(t)
    st.update(eyes="heart", phone_r=True, rarm=-150)
    hop_t = t - t0 - 0.1
    st["hop"] = max(0, math.sin(hop_t * 9) * 70) if 0 < hop_t < 0.7 else 0
    # "mein Herz macht Parkour": heart bouncing out of chest
    tp = wt("a03", 6)
    if tp < t < tp + 2.2:
        x = t - tp
        hx = 420 + x * 120
        hy = 1480 - abs(math.sin(x * 6)) * 260 - x * 60
        c.save()
        c.translate(hx, hy)
        c.rotate(x * 280)
        heart(c, 0, 0, 46, "#E0245E", 7)
        c.restore()
    ahmed(c, t, 540, 1840, 1.0, st)
    c.save()
    pop(c, t, t0 + 0.05, 540, 150)
    pill(c, "IT'S A", 540, 150, 44, fill=INK, col="#FFFFFF", name="black")
    c.restore()
    title(c, t, t0 + 0.15, "MATCH!", 300, 170, "#FFFFFF")
    if t > wt("a03", 4):
        for k in range(4):
            a = t * 3 + k * 1.6
            star(c, 540 + math.cos(a) * 420, 640 + math.sin(a) * 260, 26 + 10 * math.sin(t * 9 + k), "#FFFFFF", 5)
    draw_caption(c, t)
    if clip:
        c.restore()


# ------------------------------------------------------------------ CHAT
def typed(t):
    if t < EV["type0"]:
        return None
    if t < EV["type1"]:
        return T1[: max(1, int(len(T1) * prog(t, EV["type0"], EV["type1"] - EV["type0"])))]
    if t < EV["send"]:
        return T1
    return None


def s_english(c, t):
    t0 = SC["english"][0]
    clip = iris(c, t, t0, "#FFC6DA", prev="#FF9EC0", cy=1300)
    background(c, t, "#FFC6DA", None)
    float_hearts(c, t, 6, 90, 5)
    c.save()
    pop(c, t, t0 + 0.1, 540, 120)
    if t < STARTS_A04():
        pill(c, "LENA SCHREIBT ZUERST", 540, 120, 46, fill="#E0245E", col="#FFFFFF", name="black")
    else:
        pill(c, "STRATEGIE: ENGLISCH", 540, 120, 46, fill="#1F4BD8", col="#FFFFFF", name="black")
    c.restore()
    msgs = [("l", "Hey Ahmed :) Dein Profil hat mich direkt angelächelt", EV["l01msg"]),
            ("r", T1, EV["send"]),
            ("l", "Haha, süß. Du weißt aber, dass ich aus Gelsenkirchen komme?", EV["l02msg"])]
    c.save()
    s = eo(prog(t, t0 + 0.05, 0.4))
    c.translate(0, (1 - s) * 900)
    chat_phone(c, 130, 210, 820, 700, msgs, typing_text=typed(t), dots=(EV["dots0"] < t < EV["dots1"]), t=t)
    c.restore()
    st = base_state(t)
    st.update(phone_r=True, rarm=-150)
    if t < STARTS_A04():
        st["eyes"] = "heart"
    if EV["send"] < t < EV["l02msg"] + 0.6:
        st["eyes"] = "smug"
        st["mshape"] = "grin"
    if t > EV["l02msg"] + 1.0:
        st["eyes"] = "wide"
        st["mshape"] = "o" if t < LINES["a05"]["start"] else ("grimace" if mouth_at(t) < 0.2 else "smile")
        st["sweat"] = 3
    ahmed(c, t, 540, 1840, 1.0, st)
    if t > EV["fail"]:
        c.save()
        c.translate(540, 560)
        c.rotate(-12)
        x = prog(t, EV["fail"], 0.3)
        sc = 2.4 - 1.4 * eo(x)
        c.scale(sc, sc)
        a = int(255 * clamp(x * 3))
        rrect(c, -330, -75, 660, 150, 20, "#FFFFFF", 0, a=int(a * 0.85))
        rrect(c, -330, -75, 660, 150, 20, None, 12, ink="#E5484D", a=a)
        text(c, "ENGLISCH: FAIL", 0, 30, "black", 84, "#E5484D", a=a)
        c.restore()
    draw_caption(c, t)
    if clip:
        c.restore()


def STARTS_A04():
    return LINES["a04"]["start"]


# ------------------------------------------------------------------ SECRET
def s_secret(c, t):
    t0 = SC["secret"][0]
    clip = iris(c, t, t0, "#B79CF2", prev="#FFC6DA", cy=600)
    background(c, t, "#B79CF2", "#C5AFF7")
    t_cous = wt("a06", 9)
    tv = EV["versions"]
    mv = eio(prog(t, tv - 0.1, 0.5))
    c.save()
    cx = 540 - mv * 250
    cyc = 600 - mv * 20
    sc = 0.85 - mv * 0.35
    s_in = back(prog(t, t0 + 0.15, 0.45))
    wig = math.sin(t * 18) * 3 if wt("a06", 6) < t < wt("a06", 6) + 0.5 else 0
    c.translate(cx, cyc)
    c.scale(sc * s_in, sc * s_in)
    c.rotate(wig - 3)
    card(c, -300, -380, 600, 760, "#FFFFFF", 40, 16, 8)
    c.save()
    cl = skia.Path()
    cl.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-280, -360, 560, 540), 28, 28))
    c.clipPath(cl, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeXYWH(-280, -360, 560, 540), fillp("#7FD1FF"))
    for k in range(6):
        circ(c, -200 + k * 90, 120 + (k % 2) * 30, 70, "#FFFFFF", 0, a=60)
    emre(c, 0, -110, 1.05, t)
    c.restore()
    text(c, "Ahmed, 27", -260, 260, "black", 58, INK, "l")
    checkmark(c, -260 + tw("Ahmed, 27", "black", 58) + 40, 240, 22)
    text(c, "Fitness · Reisen · 100% ehrlich", -260, 320, "semi", 32, "#666666", "l")
    if t > t_cous:
        x = prog(t, t_cous, 0.28)
        c.save()
        c.translate(0, -60)
        c.rotate(-14)
        ss = 2.6 - 1.6 * eo(x)
        c.scale(ss, ss)
        a = int(255 * clamp(x * 3))
        rrect(c, -250, -70, 500, 140, 18, "#FFFFFF", 0, a=int(a * 0.8))
        rrect(c, -250, -70, 500, 140, 18, None, 12, ink="#E5484D", a=a)
        text(c, "COUSIN EMRE", 0, 28, "black", 74, "#E5484D", a=a)
        c.restore()
    c.restore()
    if t > tv:
        c.save()
        pop(c, t, tv + 0.1, 290, 230)
        pill(c, "VERSION 2.0", 290, 230, 40, fill="#2FBF71", name="black")
        c.restore()
        c.save()
        pop(c, t, tv + 0.35, 780, 520)
        pill(c, "AHMED 1.0", 780, 470, 46, fill=INK, col="#FFD84D", name="black")
        text(c, "(Beta)", 780, 560, "black", 40, INK)
        p = strokep(INK, 10)
        c.drawLine(780, 600, 700, 800, p)
        c.drawLine(700, 800, 690, 750, p)
        c.drawLine(700, 800, 745, 775, p)
        c.restore()
        c.save()
        pop(c, t, tv + 0.6, 540, 930)
        card(c, 170, 870, 740, 120, "#FFFFFF", 26, 10, 6)
        text(c, "Update wird installiert…", 210, 917, "xbold", 34, INK, "l")
        rrect(c, 210, 942, 660, 26, 13, "#EEEEEE", 4)
        pct = 0.03 if int(t * 4) % 2 else 0.02
        rrect(c, 210, 942, 660 * pct + 20, 26, 13, "#2FBF71", 4)
        text(c, "3%", 870, 917, "black", 34, "#E5484D", "r")
        c.restore()
    st = base_state(t)
    st.update(rarm=-30, look=(-25, 0))
    if t < wt("a06", 3):
        st["eyes"] = "smug"
        st["mshape"] = "grin" if mouth_at(t) < 0.15 else "smile"
        st["rarm"] = -125
    if t > t_cous:
        st["sweat"] = 2
        st["look"] = (0, 0)
    if t > tv:
        st["eyes"] = "derp"
        st["wave"] = 0.6
        st["rarm"] = -150
    ahmed(c, t, 540, 1840, 1.0, st)
    c.save()
    pop(c, t, t0 + 0.1, 540, 100)
    pill(c, "PSST… GEHEIMNIS", 540, 100, 44, fill=INK, col="#FFFFFF", name="black")
    c.restore()
    draw_caption(c, t)
    if clip:
        c.restore()


# ------------------------------------------------------------------ DATE (romantic + freeze)
def calendar_icon(c, cx, cy, s=1.0):
    rrect(c, cx - 50 * s, cy - 45 * s, 100 * s, 95 * s, 14 * s, "#FFFFFF", 6)
    rrect(c, cx - 50 * s, cy - 45 * s, 100 * s, 30 * s, 10 * s, "#E5484D", 6)
    text(c, "30", cx, cy + 36 * s, "black", 46 * s, INK)


def sunset_bg(c, t, k):
    """k in 0..1 blend from pink to sunset"""
    p = skia.Paint(AntiAlias=True)
    top = "#FF7EB0" if k < 0.5 else "#FF6F91"
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [C("#6A4C93"), C("#FF6F91"), C("#FFB86B")]))
    p.setAlpha(int(255 * k))
    c.drawRect(skia.Rect.MakeWH(W, H), p)
    sy = 1250 - 260 * eo(k)
    glow(c, 540, sy, 520, "#FFE29A", int(150 * k))
    circ(c, 540, sy, 190, "#FFD36E", 0, a=int(255 * k))
    for j in range(4):
        c.drawRect(skia.Rect.MakeXYWH(300, sy + 40 + j * 38, 480, 12), fillp("#FF8FA3", int(160 * k)))


def s_date(c, t):
    t0 = SC["date"][0]
    tf = EV["freeze"]
    frz = t >= tf
    ta = min(t, tf)
    clip = iris(c, t, t0, "#FF9EC0", prev="#B79CF2", cy=600)
    c.save()
    if frz:
        z = eo(prog(t, tf + 0.12, 0.3))
        zs = 1 + z * 1.3
        c.translate(540, 1365 - z * 480)
        c.scale(zs, zs)
        c.translate(-540, -1365)
    background(c, ta, "#FF9EC0", None)
    tsun = wt("l03", 12) - 0.1
    k = eio(prog(ta, tsun, 0.9))
    if k > 0:
        sunset_bg(c, ta, k)
    float_hearts(c, ta, 8, 140, 9)
    c.save()
    pop(c, ta, wt("l03", 1), 580, 110)
    w, h = pill(c, "NOCH 30 TAGE", 580, 110, 46, fill=INK, name="black")
    calendar_icon(c, 580 - w / 2 - 10, 110, 0.85)
    c.restore()
    msgs = [("l", "In 30 Tagen bin ich in deiner Stadt. Treffen wir uns… bei Sonnenuntergang?", EV["l03msg"]),
            ("r", "Ja klar, ganz easy", wt("a08", 1))]
    c.save()
    s = eo(prog(ta, t0, 0.4))
    c.translate(0, (1 - s) * 900)
    chat_phone(c, 130, 210, 820, 700, msgs, typing_text=None, t=ta)
    c.restore()
    st = base_state(ta)
    st.update(phone_r=True, rarm=-150)
    if ta < LINES["a08"]["start"] + 0.9:
        st["eyes"] = "heart"
    else:
        st["eyes"] = "smug"
        st["mshape"] = "smile" if mouth_at(ta) > 0.12 else "grin"
    if frz:
        st = dict(eyes="wide", mshape="grimace", mouth=mouth_at(t), sweat=4, phone_r=True, rarm=-150, bob=0, look=(0, 0))
    ahmed(c, ta, 540, 1840, 1.0, st)
    c.restore()
    if frz:
        a = int(120 * clamp(prog(t, tf, 0.12)))
        c.drawRect(skia.Rect.MakeWH(W, H), fillp("#000000", a))
        if t > tf + 0.3:
            title(c, t, tf + 0.3, "PROBLEM.", 330, 150, "#FF4D4D", wob=False)
        draw_caption(c, t, cy=1650, tail=False, only=["a09"])
    else:
        draw_caption(c, t)
    if clip:
        c.restore()


# ------------------------------------------------------------------ MONEY
def moth(c, x, y, t):
    fl = abs(math.sin(t * 25))
    oval(c, x - 26, y, 26, 18 * fl + 4, "#B8B1A5", 5)
    oval(c, x + 26, y, 26, 18 * fl + 4, "#B8B1A5", 5)
    oval(c, x, y, 9, 20, "#8A8275", 5)


def doener(c, cx, cy, s=1.0):
    p = skia.Path()
    p.moveTo(cx - 90 * s, cy - 60 * s)
    p.lineTo(cx + 90 * s, cy - 60 * s)
    p.lineTo(cx, cy + 110 * s)
    p.close()
    drawpath(c, p, "#E9B872", 7)
    for k, col in enumerate(["#7FBF4D", "#E5484D", "#FFFFFF", "#9C5A2E"]):
        circ(c, cx - 50 * s + k * 33 * s, cy - 62 * s, 20 * s, col, 4)


def s_money(c, t):
    t0 = SC["money"][0]
    clip = iris(c, t, t0, "#FF6B4A", prev="#333333", cy=900)
    background(c, t, "#FF6B4A", "#FF8466")
    title(c, t, t0 + 0.1, "INVENTUR", 170, 150, "#FFD84D")
    rows = [
        ("Kontostand", "3,40 €", wt("a10", 0)),
        ("Pfandbon", "1 Stück (25 Cent)", wt("a10", 6)),
        ("Date-Budget", "½ Döner", wt("a10", 10)),
        ("Job", "keiner", LINES["a10"]["end"] + 0.1),
    ]
    c.save()
    s = back(prog(t, t0 + 0.2, 0.4))
    c.translate(540, 330)
    c.scale(s, s)
    c.translate(-540, -330)
    card(c, 80, 290, 920, 560, "#FFFFFF", 34, 14, 8)
    for k, (lab, val, ts) in enumerate(rows):
        y = 380 + k * 125
        if t < ts:
            continue
        x = prog(t, ts, 0.3)
        c.save()
        c.translate((1 - eo(x)) * -60, 0)
        a = int(255 * clamp(x * 2))
        xmark(c, 150, y, 32)
        text(c, lab, 205, y + 16, "black", 44, INK, "l", a=a)
        text(c, val, 950, y + 16, "semi", 42, "#555555", "r", a=a)
        if k < len(rows) - 1:
            c.drawLine(120, y + 62, 960, y + 62, strokep("#EEEEEE", 4))
        c.restore()
    c.restore()
    st = base_state(t)
    st.update(rarm=-120, larm=10)
    if t > EV["tromb"]:
        st.update(eyes="sad", mshape="sad", sweat=1, bob=0.3, tilt=6)
    ahmed(c, t, 540, 1840, 1.0, st)
    mt = t - (t0 + 0.6)
    if mt > 0:
        moth(c, 700 + mt * 120 + math.sin(mt * 6) * 40, 1450 - mt * 260, t)
    # doener + "1/2" badge
    td = wt("a10", 11)
    if t > td:
        c.save()
        pop(c, t, td, 860, 1380)
        c.translate(860, 1380)
        c.rotate(math.sin(t * 3) * 8)
        doener(c, 0, 0, 1.1)
        circ(c, 85, -85, 48, "#E5484D", 6)
        text(c, "½", 85, -66, "black", 56, "#FFFFFF")
        c.restore()
    if t > wt("a10", 1):
        for k, (lab, col) in enumerate([("2€", "#E9C46A"), ("1€", "#E9C46A"), ("20", "#C98A4B"), ("20", "#C98A4B")]):
            ts = wt("a10", 1) + k * 0.12
            if t < ts:
                continue
            px = 120 + k * 0
            px = 100 + k * 30
            py = 1500 - k * 10
            c.save()
            pop(c, t, ts, px, py)
            circ(c, px, py, 40, col, 6)
            text(c, lab, px, py + 13, "black", 32, INK)
            c.restore()
    draw_caption(c, t, cy=1050)
    if t > EV["tromb"] + 0.2:
        c.save()
        pop(c, t, EV["tromb"] + 0.2, 540, 1060)
        pill(c, "Sonnenuntergang-Date: in Gefahr", 540, 1060, 42, fill=INK, col="#FFD84D", name="black")
        c.restore()
    if clip:
        c.restore()


# ------------------------------------------------------------------ POLL
def briefcase(c, cx, cy, s=1.0):
    rrect(c, cx - 30 * s, cy - 34 * s, 60 * s, 26 * s, 8 * s, None, 7 * s)
    rrect(c, cx - 48 * s, cy - 18 * s, 96 * s, 62 * s, 12 * s, "#8B5A2B", 6 * s)
    c.drawLine(cx - 48 * s, cy + 8 * s, cx + 48 * s, cy + 8 * s, strokep(INK, 5 * s))


def shower(c, cx, cy, s=1.0, t=0):
    p = skia.Path()
    p.moveTo(cx - 40 * s, cy - 40 * s)
    p.quadTo(cx - 40 * s, cy - 60 * s, cx, cy - 55 * s)
    c.drawPath(p, strokep(INK, 7 * s))
    pp = skia.Path()
    pp.moveTo(cx - 30 * s, cy - 10 * s)
    pp.quadTo(cx, cy - 55 * s, cx + 30 * s, cy - 10 * s)
    pp.close()
    drawpath(c, pp, "#BFC7CF", 6 * s)
    for k in range(4):
        dy = ((t * 120 + k * 17) % 50) * s
        c.drawLine(cx - 22 * s + k * 15 * s, cy + dy, cx - 25 * s + k * 15 * s, cy + 14 * s + dy, strokep("#3BA3FF", 6 * s))


def s_poll(c, t):
    t0 = SC["poll"][0]
    clip = iris(c, t, t0, "#7EE0C3", prev="#FF6B4A", cy=900)
    background(c, t, "#7EE0C3", "#93E8CF")
    title(c, t, t0 + 0.1, "IHR", 130, 120, "#FFFFFF")
    title(c, t, t0 + 0.25, "ENTSCHEIDET!", 265, 128, "#FFFFFF")
    c.save()
    s = back(prog(t, t0 + 0.4, 0.45))
    c.translate(540, 650)
    c.scale(s, s)
    c.translate(-540, -650)
    card(c, 80, 380, 920, 560, "#FFFFFF", 34, 14, 8)
    text(c, "Was soll Ahmed machen?", 540, 470, "black", 52, INK)
    tA, tB = wt("a11", 4), wt("a11", 8)
    a12s = LINES["a12"]["start"]
    sw = 0.5
    if t > a12s:
        sw = 0.5 + 0.18 * math.sin((t - a12s) * 5) * clamp(prog(t, a12s, 0.4))
    if t > EV["cta"]:
        sw = 0.5 + 0.03 * math.sin(t * 7)
    for k, (lab, txt, ts) in enumerate([("A", "Arbeit suchen", tA), ("B", "Endlich duschen", tB)]):
        if t < ts:
            continue
        y = 540 + k * 180
        x = back(prog(t, ts, 0.35))
        c.save()
        c.translate(540, y + 65)
        c.scale(x, x)
        c.translate(-540, -(y + 65))
        rrect(c, 130, y, 820, 130, 30, "#F3F1EE", 6)
        frac = sw if k == 0 else 1 - sw
        if t > a12s:
            rrect(c, 130, y, 820 * frac, 130, 30, "#FFD84D" if k == 0 else "#8FD3FF", 0)
            rrect(c, 130, y, 820, 130, 30, None, 6)
            text(c, f"{int(round(frac * 100))}%", 920, y + 82, "black", 44, INK, "r")
        circ(c, 205, y + 65, 42, INK)
        text(c, lab, 205, y + 82, "black", 48, "#FFFFFF")
        text(c, txt, 275, y + 82, "black", 50, INK, "l")
        if k == 0:
            briefcase(c, 760 if t > a12s else 880, y + 60, 0.9)
        else:
            shower(c, 760 if t > a12s else 880, y + 68, 0.9, t)
        c.restore()
    c.restore()
    st = base_state(t)
    st.update(rarm=-150, wave=0)
    a12 = LINES["a12"]
    if a12["start"] < t < a12["end"]:
        st.update(eyes="wide", worried=True, sweat=2)
    if t > EV["cta"]:
        st.update(wave=1, eyes="derp")
        st["hop"] = max(0, math.sin((t - EV["cta"]) * 7) * 45)
    ahmed(c, t, 540, 1840, 1.0, st)
    if t > EV["cta"]:
        c.save()
        pop(c, t, EV["cta"], 540, 1010, kind="el")
        bb = 1 + 0.05 * math.sin(t * 10)
        c.translate(540, 1010)
        c.scale(bb, bb)
        c.translate(-540, -1010)
        pill(c, "JETZT ABSTIMMEN!", 540, 1010, 62, fill="#E0245E", name="black", padx=44, pady=26)
        c.restore()
        if t > wt("a13", 3) - 0.1:
            c.save()
            pop(c, t, wt("a13", 3) - 0.1, 540, 1115)
            pill(c, "TAG 2 – MORGEN", 540, 1115, 46, fill=INK, col="#FFD84D", name="black")
            c.restore()
    else:
        draw_caption(c, t)
    if clip:
        c.restore()


SCENE_FN = {"intro": s_intro, "hook": s_hook, "match": s_match, "english": s_english, "secret": s_secret, "date": s_date, "money": s_money, "poll": s_poll}

# ---------- cinematic post: slow push-in + vignette ----------
_VIG = None


def vignette():
    global _VIG
    if _VIG is None:
        s = skia.Surface(W, H)
        cc = s.getCanvas()
        p = skia.Paint(AntiAlias=True)
        p.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 1150, [C("#000000", 0), C("#000000", 0), C("#000000", 95)], [0.0, 0.55, 1.0]))
        cc.drawRect(skia.Rect.MakeWH(W, H), p)
        _VIG = s.makeImageSnapshot()
    return _VIG


def frame(c, name, t):
    a, b = SC[name]
    k = (t - a) / max(b - a, 1e-3)
    z = 1.0 + 0.03 * k if name != "intro" else 1.0
    c.save()
    c.translate(W / 2, H * 0.55)
    c.scale(z, z)
    c.translate(-W / 2, -H * 0.55)
    SCENE_FN[name](c, t)
    c.restore()
    c.drawImage(vignette(), 0, 0)
