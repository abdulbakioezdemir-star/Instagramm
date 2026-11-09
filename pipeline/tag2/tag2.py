import sys, json, math, subprocess, os, random
sys.path.insert(0, "/home/claude")
import numpy as np, skia
from draw import *
from scenes import glow, float_hearts, vignette, doener

FPS, SR = 30, 48000
D = "/home/claude/tag2"
OUT = D + "/out"
os.makedirs(OUT, exist_ok=True)

TEXT = {}
for ln in open(f"{D}/lines.tsv", encoding="utf-8"):
    i, who, txt = ln.rstrip("\n").split("\t")
    TEXT[i] = (who, txt)


def load(i):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f"{D}/{i}.wav", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


AUD = {i: load(i) for i in TEXT}
DUR = {i: len(a) / SR for i, a in AUD.items()}
ST = {}
SC = {}


def put(i, t):
    ST[i] = t
    return t + DUR[i]


s = 0.0
e = put("a01", 0.15)
SC["hook"] = (0.0, e + 0.55)
s = SC["hook"][1]
e = put("a02", s + 0.2)
e = put("a03", e + 0.35)
SC["doener"] = (s, e + 0.6)
s = SC["doener"][1]
e = put("a04", s + 0.2)
e = put("a05", e + 0.3)
SC["shower"] = (s, e + 0.7)
s = SC["shower"][1]
e = put("l01", s + 0.35)
e = put("a06", e + 0.25)
SC["call"] = (s, e + 0.6)
s = SC["call"][1]
e = put("a07", s + 0.25)
SC["poll"] = (s, e + 1.1)
TOTAL = SC["poll"][1]
ORDER = ["hook", "doener", "shower", "call", "poll"]

WT = {}
for i in TEXT:
    w = json.load(open(f"{D}/{i}.mp3.json"))
    o0 = w[0][0]
    WT[i] = [(ST[i] + o - o0, t) for o, d, t in w]


def wt(i, k):
    return WT[i][k][0]


DISP = {
    "a01": ["Einer", "sagt", "A,", "einer", "sagt", "B.", "Okay,", "Bruder…", "dann", "mach", "ich", "halt", "beides."],
    "a02": ["Erst", "Arbeit.", "Bewerbung", "bei", "der", "Dönerbude."],
    "a03": ["Erfahrung?", "Ja,", "sehr", "viel.", "Im", "Döner", "essen."],
    "a04": ["Okay.", "Dann", "wenigstens", "duschen."],
    "a05": ["Warum", "ist", "das", "Wasser", "kalt?!", "…Ah.", "Stromrechnung."],
    "l01": ["Hey", "Ahmed!", "Lass", "uns", "heute", "Abend", "videocallen!"],
    "a06": ["Videocall?!", "Bruder…", "die", "denkt,", "ich", "seh", "aus", "wie", "Emre!"],
    "a07": ["Ihr", "entscheidet.", "A:", "Emre", "geht", "für", "mich", "ran.", "B:", "Ich", "sag,", "meine", "Kamera", "ist", "kaputt.", "Schreibt", "A", "oder", "B!"],
}
CHUNKS = []
for i in TEXT:
    toks = DISP[i]
    assert len(toks) == len(WT[i]), i
    cur = []
    for k, tok in enumerate(toks):
        cur.append((tok, WT[i][k][0]))
        if (tok[-1] in ".!?:…" and len(cur) >= 2) or len(cur) >= 5 or k == len(toks) - 1:
            CHUNKS.append(dict(who=TEXT[i][0], words=cur, start=cur[0][1] - 0.06, line=i))
            cur = []
CHUNKS.sort(key=lambda c: c["start"])
for k, ch in enumerate(CHUNKS):
    nxt = CHUNKS[k + 1]["start"] if k + 1 < len(CHUNKS) else 1e9
    ch["end"] = min(nxt, ST[ch["line"]] + DUR[ch["line"]] + 0.4)

N = int(TOTAL * SR) + 1
ahm = np.zeros(N, np.float32)
lena = np.zeros(N, np.float32)
for i, a in AUD.items():
    s0 = int(ST[i] * SR)
    (ahm if TEXT[i][0] == "A" else lena)[s0:s0 + len(a)] += a[: N - s0]
hop = SR // FPS
nf = int(TOTAL * FPS) + 2
env = np.array([np.sqrt(np.mean(ahm[k * hop:(k + 1) * hop] ** 2) + 1e-12) if k * hop < N else 0 for k in range(nf)])
env = np.clip(env / np.percentile(env[env > 1e-3], 95), 0, 1)
for k in range(1, nf):
    env[k] = max(env[k], env[k - 1] * 0.55)


def mouth(t):
    return float(env[min(int(t * FPS), nf - 1)])


def base(t, **kw):
    d = dict(mouth=mouth(t), blink=(t % 3.3) < 0.11)
    d.update(kw)
    return d


def caps(c, t, cy=1050):
    for ch in CHUNKS:
        if ch["start"] <= t < ch["end"]:
            caption(c, t, ch["who"], ch["words"], cy, tail_x=(560 if ch["who"] == "A" else None), appear=ch["start"])


def tag_pill(c, t, t0, label="TAG 2"):
    c.save()
    pop(c, t, t0, 540, 110)
    pill(c, label, 540, 110, 44, fill=INK, col="#FFD84D", name="black")
    c.restore()


def stamp(c, t, t0, txt, cx, cy, col="#E5484D", size=88, rot=-12, w=None):
    if t < t0:
        return
    x = prog(t, t0, 0.28)
    c.save()
    c.translate(cx, cy)
    c.rotate(rot)
    ss = 2.4 - 1.4 * eo(x)
    c.scale(ss, ss)
    a = int(255 * clamp(x * 3))
    ww = (w or tw(txt, "black", size) + 80)
    rrect(c, -ww / 2, -size * 0.85, ww, size * 1.7, 20, "#FFFFFF", 0, a=int(a * 0.88))
    rrect(c, -ww / 2, -size * 0.85, ww, size * 1.7, 20, None, 12, ink=col, a=a)
    text(c, txt, 0, size * 0.35, "black", size, col, a=a)
    c.restore()


# ---------------- scenes ----------------
def s_hook(c, t):
    background(c, t, "#F9D85E", "#FBE07A")
    glow(c, 540, 560, 520, "#FFFFFF", 90)
    # scoreboard
    c.save()
    s = back(prog(t, 0.0, 0.35))
    c.translate(540, 560)
    c.scale(s, s)
    c.translate(-540, -560)
    card(c, 90, 330, 900, 460, "#FFFFFF", 34, 14, 8)
    text(c, "Eure Abstimmung", 540, 420, "black", 50, INK)
    for k, (lab, txt, col, ts) in enumerate([("A", "Arbeit", "#FFD84D", wt("a01", 2)), ("B", "Duschen", "#8FD3FF", wt("a01", 5))]):
        x0 = 150 + k * 420
        rrect(c, x0, 470, 360, 260, 30, col if t >= ts else "#F3F1EE", 6)
        circ(c, x0 + 180, 545, 44, INK)
        text(c, lab, x0 + 180, 563, "black", 52, "#FFFFFF")
        text(c, txt, x0 + 180, 640, "black", 44, INK)
        if t >= ts:
            c.save()
            pop(c, t, ts, x0 + 180, 695)
            text(c, "1 Stimme", x0 + 180, 708, "xbold", 34, "#555555")
            c.restore()
    text(c, ":", 540, 610, "black", 90, INK)
    c.restore()
    if wt("a01", 6) - 0.1 < t < wt("a01", 12):
        stamp(c, t, wt("a01", 6) - 0.1, "UNENTSCHIEDEN", 540, 560, "#1F4BD8", 74, -8)
    stamp(c, t, wt("a01", 12) - 0.05, "BEIDES!", 540, 560, "#E0245E", 120, -10)
    st = base(t, rarm=-150, wave=0)
    if t < wt("a01", 6):
        st.update(eyes="derp", look=(-20 if t < wt("a01", 3) else 20, 0))
    elif t < wt("a01", 12):
        st.update(eyes="sad", worried=True, larm=-40, rarm=-170)  # shrug
    else:
        st.update(eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin", hop=max(0, math.sin((t - wt("a01", 12)) * 8) * 50))
    ahmed(c, t, 540, 1840, 1.0, st)
    tag_pill(c, t, 0.0)
    caps(c, t)


def shopfront(c, t):
    # Doenerbude storefront
    card(c, 110, 290, 860, 560, "#FFF4E0", 26, 14, 8)
    for k in range(8):
        col = "#E5484D" if k % 2 == 0 else "#FFFFFF"
        p = skia.Path()
        x0 = 110 + k * 107.5
        p.moveTo(x0, 290)
        p.lineTo(x0 + 107.5, 290)
        p.lineTo(x0 + 107.5, 400)
        p.quadTo(x0 + 53.75, 440, x0, 400)
        p.close()
        drawpath(c, p, col, 6)
    text(c, "DÖNERBUDE 24/7", 540, 500, "lilita", 84, "#E5484D", stroke=10, stroke_col=INK)
    text(c, "DÖNERBUDE 24/7", 540, 500, "lilita", 84, "#FFD84D")
    # spit
    rrect(c, 520, 540, 40, 280, 8, "#9A9A9A", 6)
    sp = skia.Path()
    sp.moveTo(470, 570)
    sp.lineTo(610, 570)
    sp.lineTo(590, 800)
    sp.lineTo(490, 800)
    sp.close()
    c.save()
    c.translate(540, 0)
    c.scale(1 + 0.03 * math.sin(t * 6), 1)
    c.translate(-540, 0)
    drawpath(c, sp, "#B5652B", 7)
    for k in range(5):
        c.drawLine(480 + k * 4, 600 + k * 45, 600 - k * 4, 600 + k * 45, strokep("#7A3E14", 6))
    c.restore()
    doener(c, 260, 690, 0.9)
    doener(c, 820, 690, 0.9)


def s_doener(c, t):
    t0 = SC["doener"][0]
    clip = iris(c, t, t0, "#FFB86B", prev="#F9D85E", cy=600, d=0.35)
    background(c, t, "#FFB86B", "#FFC88A")
    form_t = wt("a03", 0) - 0.15
    if t < form_t:
        c.save()
        s = back(prog(t, t0 + 0.05, 0.4))
        c.translate(540, 570)
        c.scale(s, s)
        c.translate(-540, -570)
        shopfront(c, t)
        c.restore()
    else:
        c.save()
        s = back(prog(t, form_t, 0.35))
        c.translate(540, 570)
        c.scale(s, s)
        c.translate(-540, -570)
        card(c, 110, 300, 860, 540, "#FFFFFF", 26, 14, 8)
        text(c, "BEWERBUNG", 540, 385, "black", 60, INK)
        rows = [("Name", "Ahmed, 27", form_t + 0.1), ("Erfahrung?", "", form_t + 0.1), ("", "Döner essen", wt("a03", 5)), ("", "(sehr viel)", wt("a03", 5) + 0.2)]
        for k, (lab, val, ts) in enumerate(rows):
            if t < ts:
                continue
            y = 470 + k * 85
            if lab:
                text(c, lab, 170, y, "black", 44, "#E0245E", "l")
            if val:
                text(c, val, 910, y, "xbold" if k < 3 else "semi", 44, INK, "r")
        c.restore()
        stamp(c, t, wt("a03", 6) + 0.25, "ABGELEHNT", 560, 600, "#E5484D", 96, -14)
    st = base(t, rarm=-30)
    if t >= form_t:
        st.update(eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin")
    if t >= wt("a03", 6) + 0.25:
        st.update(eyes="sad", mshape="sad", sweat=2)
    ahmed(c, t, 540, 1840, 1.0, st)
    tag_pill(c, t, t0 + 0.05)
    caps(c, t)
    if clip:
        c.restore()


def tiles(c, col1, col2):
    c.clear(C(col1))
    p = strokep(col2, 5)
    for x in range(0, W + 1, 120):
        c.drawLine(x, 0, x, H, p)
    for y in range(0, H + 1, 120):
        c.drawLine(0, y, W, y, p)


def s_shower(c, t):
    t0 = SC["shower"][0]
    cold_t = wt("a05", 4) - 0.1
    cold = t >= cold_t
    clip = iris(c, t, t0, "#9ED8F0", prev="#FFB86B", cy=900, d=0.35)
    tiles(c, "#9ED8F0" if not cold else "#BFE6FF", "#7FC3E0" if not cold else "#9FD4F5")
    # steam (warm) or frost (cold)
    if not cold:
        for k in range(6):
            yy = 900 - ((t * 60 + k * 120) % 700)
            oval(c, 300 + k * 90 + 30 * math.sin(t + k), yy, 90, 50, "#FFFFFF", 0, a=70)
    # shower head + pipe
    c.drawLine(760, 0, 760, 420, strokep("#8E9AA6", 26))
    c.drawLine(760, 420, 640, 520, strokep("#8E9AA6", 26))
    sh = skia.Path()
    sh.moveTo(560, 560)
    sh.quadTo(640, 450, 720, 560)
    sh.close()
    drawpath(c, sh, "#BFC7CF", 9)
    # water
    r = random.Random(int(t * 30))
    wcol = "#3BA3FF" if not cold else "#BDEBFF"
    for k in range(26):
        x = r.uniform(420, 860)
        y = 600 + ((t * 900 + k * 97) % 900)
        c.drawLine(x, y, x - 6, y + 34, strokep(wcol, 7))
    # curtain
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
        stamp(c, t, cold_t + 0.05, "BRRRR!", 540, 420, "#1F4BD8", 110, -8)
    bill_t = wt("a05", 6) - 0.1
    if t >= bill_t:
        c.save()
        pop(c, t, bill_t, 790, 640)
        c.translate(790, 640)
        c.rotate(8)
        card(c, -200, -150, 400, 300, "#FFFFFF", 18, 10, 6)
        text(c, "STROMRECHNUNG", 0, -85, "black", 40, INK)
        text(c, "offen: 89,90 €", 0, -20, "xbold", 38, "#555555")
        rrect(c, -150, 30, 300, 80, 14, None, 8, ink="#E5484D")
        text(c, "MAHNUNG", 0, 88, "black", 52, "#E5484D")
        c.restore()
    shiver = math.sin(t * 70) * 7 if cold else 0
    st = base(t, cap=True, rarm=-150, sweat=0)
    if not cold:
        st.update(eyes="smug", mshape="smile" if mouth(t) > 0.12 else "grin")
    else:
        st.update(eyes="wide", mshape="grimace", worried=True)
    c.save()
    c.translate(shiver, 0)
    ahmed(c, t, 540, 1840, 1.0, st)
    c.restore()
    tag_pill(c, t, t0 + 0.05)
    caps(c, t)
    if clip:
        c.restore()


def s_call(c, t):
    t0 = SC["call"][0]
    clip = iris(c, t, t0, "#FF9EC0", prev="#9ED8F0", cy=600, d=0.35)
    background(c, t, "#FF9EC0", "#FFB5CF")
    float_hearts(c, t, 7, 120, 4)
    ring_t = ST["a06"] - 0.15
    if t < ring_t:
        # notification
        c.save()
        pop(c, t, t0 + 0.3, 540, 520)
        card(c, 110, 400, 860, 240, "#FFFFFF", 36, 12, 7)
        lena_avatar(c, 220, 520, 70)
        text(c, "Lena", 320, 480, "black", 46, INK, "l")
        for k, L in enumerate(wrap("Hey Ahmed! Lass uns heute Abend videocallen!", "semi", 36, 600)):
            text(c, L, 320, 535 + k * 46, "semi", 36, "#444444", "l")
        c.restore()
    else:
        # incoming video call screen
        sh = math.sin(t * 40) * 6 * (1 if (t - ring_t) % 1.0 < 0.5 else 0)
        c.save()
        c.translate(sh, 0)
        s = back(prog(t, ring_t, 0.35))
        c.translate(540, 600)
        c.scale(s, s)
        c.translate(-540, -600)
        rrect(c, 250 + 14, 220 + 14, 580, 680, 60, INK)
        rrect(c, 250, 220, 580, 680, 60, "#1C1C2B", 9)
        lena_avatar(c, 540, 420, 110)
        text(c, "Lena", 540, 600, "black", 56, "#FFFFFF")
        text(c, "Videoanruf…", 540, 650, "semi", 36, "#BBBBBB")
        for k, (col, x) in enumerate([("#E5484D", 420), ("#2FBF71", 660)]):
            pul = 1 + 0.1 * math.sin(t * 10 + k)
            circ(c, x, 790, 52 * pul, col, 6)
        c.drawLine(395, 790, 445, 790, strokep("#FFFFFF", 10))
        c.drawLine(640, 780, 680, 800, strokep("#FFFFFF", 10))
        c.restore()
        # thought bubble with Emre
        if t > wt("a06", 4):
            c.save()
            pop(c, t, wt("a06", 4), 870, 1180)
            for (bx, by, br) in [(700, 1310, 16), (750, 1260, 24)]:
                circ(c, bx, by, br, "#FFFFFF", 6)
            emre_avatar(c, 870, 1170, 110, t)
            c.restore()
    st = base(t, rarm=-150, phone_r=True)
    if t < ring_t:
        st.update(eyes="heart")
    else:
        st.update(eyes="wide", mshape="grimace" if mouth(t) < 0.15 else "o", sweat=4, worried=True, buzz=0.6)
    ahmed(c, t, 540, 1840, 1.0, st)
    tag_pill(c, t, t0 + 0.05)
    caps(c, t)
    if clip:
        c.restore()


def broken_cam(c, cx, cy, s=1.0):
    rrect(c, cx - 50 * s, cy - 32 * s, 100 * s, 66 * s, 12 * s, "#555555", 6 * s)
    circ(c, cx, cy, 22 * s, "#9ED8F0", 6 * s)
    p = strokep(INK, 5 * s)
    c.drawLine(cx - 12 * s, cy - 18 * s, cx + 4 * s, cy, p)
    c.drawLine(cx + 4 * s, cy, cx - 6 * s, cy + 16 * s, p)


def s_poll(c, t):
    t0 = SC["poll"][0]
    clip = iris(c, t, t0, "#7EE0C3", prev="#FF9EC0", cy=900, d=0.35)
    background(c, t, "#7EE0C3", "#93E8CF")
    title(c, t, t0 + 0.05, "IHR ENTSCHEIDET!", 220, 112, "#FFFFFF")
    c.save()
    s = back(prog(t, t0 + 0.25, 0.4))
    c.translate(540, 640)
    c.scale(s, s)
    c.translate(-540, -640)
    card(c, 80, 360, 920, 560, "#FFFFFF", 34, 14, 8)
    text(c, "Lena will videocallen…", 540, 450, "black", 50, INK)
    for k, (lab, txt, ts) in enumerate([("A", "Emre geht ran", wt("a07", 2)), ("B", "Kamera \"kaputt\"", wt("a07", 8))]):
        if t < ts:
            continue
        y = 510 + k * 180
        x = back(prog(t, ts, 0.35))
        c.save()
        c.translate(540, y + 65)
        c.scale(x, x)
        c.translate(-540, -(y + 65))
        sel = (k == 0 and t < wt("a07", 8)) or (k == 1 and wt("a07", 8) <= t < wt("a07", 15))
        rrect(c, 130, y, 820, 130, 30, ("#FFD84D" if k == 0 else "#8FD3FF") if sel else "#F3F1EE", 6)
        circ(c, 205, y + 65, 42, INK)
        text(c, lab, 205, y + 82, "black", 48, "#FFFFFF")
        text(c, txt, 275, y + 82, "black", 48, INK, "l")
        if k == 0:
            emre_avatar(c, 870, y + 65, 48, t)
        else:
            broken_cam(c, 870, y + 65, 0.9)
        c.restore()
    c.restore()
    cta = wt("a07", 15) - 0.1
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
            pill(c, "TAG 3 – MORGEN", 540, 1115, 44, fill=INK, col="#FFD84D", name="black")
            c.restore()
    else:
        caps(c, t)
    if clip:
        c.restore()


FN = {"hook": s_hook, "doener": s_doener, "shower": s_shower, "call": s_call, "poll": s_poll}


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


# ---------------- audio ----------------
def build_audio():
    ns = {}
    src = open("/home/claude/audio.py").read()
    src = src[: src.index("# ================= SFX track")]
    exec(src, ns)
    g = lambda k: ns[k]
    add, pizz, taiko, piano, strings, bell, pop_, harp, braam, heartbeat, riser, whoosh, thud, buzzer, scratch, mtof, tt = (g(k) for k in ["add", "pizz", "taiko", "piano", "strings", "bell", "pop", "harp_gliss", "braam", "heartbeat", "riser", "whoosh", "thud", "buzzer", "scratch", "mtof", "tt"])
    bp, lp, hp = g("bp"), g("lp"), g("hp")
    rng = np.random.default_rng(5)
    Nn = int(TOTAL * SR)
    mus = np.zeros(Nn)
    sfx = np.zeros(Nn)
    beat = 60 / 108
    # hook: bouncy pizz
    a, b = SC["hook"]
    seq = [62, 69, 66, 69, 62, 69, 67, 69]
    t, k = a, 0
    while t < b:
        add(mus, t, pizz(mtof(seq[k % 8]), 1.0 if k % 2 == 0 else 0.7))
        if k % 4 == 0:
            add(mus, t, taiko(0.3))
        t += beat / 2
        k += 1
    # doener: oriental-flavoured pizz (D phrygian dominant) + darbuka-ish hits
    a, b = SC["doener"]
    sc = [62, 63, 66, 67, 69, 70, 72, 74]
    pat = [0, 1, 2, 1, 3, 2, 1, 0, 4, 5, 4, 3, 2, 1, 2, 0]
    t, k = a + 0.05, 0
    while t < b:
        add(mus, t, pizz(mtof(sc[pat[k % 16]] + 12), 0.9))
        if k % 4 == 0:
            add(mus, t, taiko(0.45))
        elif k % 4 == 2:
            add(mus, t, taiko(0.25, low=False))
        t += beat / 2
        k += 1
    # shower: warm pad until cold, then nothing but wind
    a, b = SC["shower"]
    cold_t = wt("a05", 4) - 0.1
    for m in [62, 66, 69]:
        add(mus, a, strings(mtof(m), cold_t - a, 0.4, 0.2, 2200), 0.6)
    t = a
    while t < cold_t:
        add(mus, t, piano(mtof(74 + [0, 4, 7, 12][int((t - a) / (beat / 2)) % 4]), 1.2, 0.5))
        t += beat / 2
    # call: tense pulsing
    a, b = SC["call"]
    ring_t = ST["a06"] - 0.15
    rom = [[62, 66, 69], [57, 61, 64]]
    for kk, ch in enumerate(rom):
        for m in ch:
            add(mus, a + kk * 1.8, strings(mtof(m - 12), 1.8, 0.3, 0.4, 1600), 0.5)
    t = ring_t
    k = 0
    while t < b:
        add(mus, t, pizz(mtof([50, 50, 53, 50][k % 4]), 1.0))
        if k % 2 == 0:
            add(mus, t, taiko(0.35))
        t += beat / 2
        k += 1
    # poll: epic build + hit
    a, b = SC["poll"]
    cta = wt("a07", 15) - 0.1
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
    # ---- SFX
    add(sfx, wt("a01", 2), pop_(), 0.35)
    add(sfx, wt("a01", 5), pop_(), 0.35)
    add(sfx, wt("a01", 6) - 0.1, thud(), 0.6)
    add(sfx, wt("a01", 12) - 0.05, thud(), 0.8)
    add(sfx, wt("a01", 12), bell(1318.5, 0.6, 0.15))
    for n in ORDER[1:]:
        add(sfx, SC[n][0] - 0.1, whoosh(0.35), 0.4)
    add(sfx, wt("a03", 0) - 0.15, pop_(), 0.3)
    add(sfx, wt("a03", 5), pop_(), 0.3)
    add(sfx, wt("a03", 6) + 0.25, thud(), 0.8)
    add(sfx, wt("a03", 6) + 0.3, buzzer(), 0.7)
    # shower water noise
    a, b = SC["shower"]
    n = rng.standard_normal(int((b - a) * SR))
    water = bp(n, 1500, 7000) * 0.12
    water *= np.minimum(1, tt(b - a) / 0.3)
    ci = int((cold_t - a) * SR)
    water[ci:] *= 1.4
    add(sfx, a, water)
    add(sfx, cold_t, scratch(), 0.7)
    add(sfx, cold_t + 0.05, thud(), 0.6)
    add(sfx, wt("a05", 6) - 0.1, pop_(), 0.3)
    add(sfx, wt("a05", 6) - 0.05, buzzer(), 0.4)
    # call
    add(sfx, SC["call"][0] + 0.3, bell(1568, 0.5, 0.15))
    add(sfx, SC["call"][0] + 0.42, bell(2093, 0.6, 0.15))
    t = ring_t
    while t < SC["call"][1] - 0.2:
        for kk, m in enumerate([76, 79, 84, 79, 76, 79]):
            add(sfx, t + kk * 0.11, bell(mtof(m), 0.3, 0.09))
        t += 1.3
    add(sfx, wt("a06", 4), pop_(300, 800, 0.12), 0.3)
    add(sfx, wt("a07", 2), pop_(), 0.35)
    add(sfx, wt("a07", 8), pop_(), 0.35)

    def wav(name, x, norm=None):
        if norm:
            x = x / (np.abs(x).max() + 1e-9) * norm
        x = np.clip(x, -1, 1).astype(np.float32)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", f"{D}/{name}.wav"], input=x.tobytes(), check=True)
    wav("voice", (ahm + lena)[:Nn])
    wav("sfx", sfx, 0.8)
    wav("music", mus, 0.9)
    subprocess.run(["bash", "-c", f"cd {D} && bash /home/claude/mix.sh"], check=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "info":
        print({k: (round(a, 2), round(b, 2)) for k, (a, b) in SC.items()}, "TOTAL", round(TOTAL, 2))
    elif cmd == "preview":
        from PIL import Image
        ts = [float(x) for x in sys.argv[2:]]
        ims = []
        for t in ts:
            s = skia.Surface(1080, 1920)
            c = s.getCanvas()
            frame(c, scene_at(t), t)
            ims.append(Image.frombytes("RGBA", (1080, 1920), s.makeImageSnapshot().tobytes(), "raw", "BGRA").convert("RGB").resize((360, 640)))
        sh = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims):
            sh.paste(im, (i * 360, 0))
        sh.save(f"{D}/prev.png")
    elif cmd == "scene":
        for n in sys.argv[2:]:
            render_scene(n)
            print("ok", n, flush=True)
    elif cmd == "audio":
        build_audio()
        print("audio ok")
