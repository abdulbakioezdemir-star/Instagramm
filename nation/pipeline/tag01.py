"""Valmora – Tag 1: Gründung. Rendert Audio + Video (1080x1920, 30 fps)."""
import numpy as np, json, subprocess, math, os
from scipy.signal import butter, sosfilt, fftconvolve
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SR = 48000
rng = np.random.default_rng(3)
exec(open("synth_body.py").read())
FB = "/home/claude/instagramm/pipeline/fonts/Bungee-Regular.ttf"
FL = "/home/claude/instagramm/pipeline/fonts/LilitaOne-Regular.ttf"

# ---------------- timeline ----------------
def dec(path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)

gaps = {"l1": 0.2, "l2": 0.45, "l3": 0.45, "l4": 0.6, "l5": 0.6, "l6": 0.6, "l7": 1.6, "l8": 0.6, "l9": 0.6}
t = 0.0
L = {}
for i in range(1, 10):
    k = f"l{i}"
    a = dec(f"{k}.mp3")
    t += gaps[k]
    words = json.load(open(f"{k}.mp3.json"))
    L[k] = dict(t0=t, t1=t + len(a) / SR, audio=a, words=[(t + o, d, w) for o, d, w in words])
    t = L[k]["t1"]
TOTAL = t + 1.8
N = int(TOTAL * SR) + SR
print("total", TOTAL)

S = {
    "hook": (0, L["l2"]["t0"] - 0.15),
    "pan": (L["l2"]["t0"] - 0.15, L["l3"]["t0"] - 0.2),
    "map": (L["l3"]["t0"] - 0.2, L["l4"]["t0"] - 0.3),
    "flag": (L["l4"]["t0"] - 0.3, L["l5"]["t0"] - 0.3),
    "stats": (L["l5"]["t0"] - 0.3, L["l6"]["t0"] - 0.3),
    "build": (L["l6"]["t0"] - 0.3, L["l7"]["t0"] - 0.2),
    "budget": (L["l7"]["t0"] - 0.2, L["l8"]["t0"] - 0.3),
    "rules": (L["l8"]["t0"] - 0.3, L["l9"]["t0"] - 0.3),
    "og": (L["l9"]["t0"] - 0.3, TOTAL),
}
BUILD0 = L["l6"]["t0"] + 3.4
BUILD1 = L["l6"]["t1"] + 1.2
# ---------------- audio ----------------
voice = np.zeros(N)
for k, v in L.items():
    add(voice, v["t0"], v["audio"].astype(np.float64), 1.0)
sfx = np.zeros(N)
add(sfx, 0.0, braam(36, 2.2), 0.55)
for k in ("pan", "map", "flag", "stats", "build", "budget", "rules", "og"):
    add(sfx, S[k][0], whoosh(0.5), 0.45)
add(sfx, L["l4"]["t0"] + 0.9, taiko(1.0), 0.8)
add(sfx, L["l4"]["t0"] + 0.9, cymbal_swell(1.4), 0.25)
for j in range(3):
    add(sfx, L["l5"]["t0"] + 0.2 + j * 2.0, pop(), 0.5)
tt_ = BUILD0
while tt_ < BUILD1:
    add(sfx, tt_, thud(), 0.35); tt_ += 0.32
add(sfx, BUILD1, bell(mtof(84), 1.4, 0.2), 0.8)
for j in range(6):
    add(sfx, L["l7"]["t0"] - 1.2 + j * 0.1, coin(), 0.35)
add(sfx, L["l7"]["t0"] - 0.3, buzzer(), 0.25)
for j, k in enumerate(("l8",)):
    pass
for off in (1.6, 3.6, 5.6):
    add(sfx, L["l8"]["t0"] + off, pop(500, 1200), 0.45)
add(sfx, L["l9"]["t0"] + 0.2, sparkle(), 0.5)
mus = np.zeros(N)
exec(open("/home/claude/nwork/arr.py").read()) if os.path.exists("/home/claude/nwork/arr.py") else None
bar = 2.0
Am, F, C, G = (57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)
t0 = 0.0
k = 0
while t0 < TOTAL:
    ch = [Am, F, C, G][k % 4]
    for m in ch:
        add(mus, t0, strings(mtof(m), bar, att=0.6, rel=0.9, bright=1800), 0.18)
    add(mus, t0, strings(mtof(ch[0] - 24), bar, att=0.4, rel=0.9, bright=600), 0.25)
    if t0 >= S["stats"][0] - 0.5 and t0 < S["og"][0]:
        for j in range(4):
            add(mus, t0 + j * bar / 4, taiko(0.5 + 0.2 * (j == 0)), 0.18)
    if t0 >= S["flag"][0] - 1:
        notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24]
        for j in range(8):
            add(mus, t0 + j * bar / 8, piano(mtof(notes[[0, 1, 2, 3, 2, 1, 2, 1][j]]), 1.4, 0.45), 0.10)
    t0 += bar
    k += 1
fade = np.ones(N)
e = int(TOTAL * SR)
fade[e - SR:e] = np.linspace(1, 0, SR)
fade[e:] = 0
mus *= fade

def wav(name, x, norm=None):
    if norm:
        x = x / (np.abs(x).max() + 1e-9) * norm
    x = np.clip(x, -1, 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", name],
                   input=x.tobytes(), check=True)
wav("voice.wav", voice)
wav("sfx.wav", sfx, 0.8)
wav("music.wav", mus, 0.7)
subprocess.run(["bash", "-c", """ffmpeg -nostdin -v error -y -i voice.wav -i sfx.wav -i music.wav -filter_complex "
[0:a]highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=1.5,asplit=2[v][key];
[2:a]volume=0.5[m];[m][key]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=350[md];
[1:a]volume=0.75[s];[v][s][md]amix=inputs=3:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=10[out]" -map "[out]" -ar 48000 -ac 2 mix.wav"""], check=True)

# ---------------- visuals ----------------
from world import PW, PH, HZ
PAN = Image.open("panorama.jpg").convert("RGB")
MAP = Image.open("karte.jpg").convert("RGB")
LOGO = Image.open("logo_valmora.jpg").convert("RGB")
lm = Image.new("L", LOGO.size, 0)
ImageDraw.Draw(lm).ellipse([LOGO.width * 0.1 - 20, LOGO.height * 0.1 - 20, LOGO.width * 0.9 + 20, LOGO.height * 0.9 + 20], fill=255)
fB = {s: ImageFont.truetype(FB, s) for s in (40, 48, 56, 64, 72, 80, 96, 110, 130, 170)}
fL = {s: ImageFont.truetype(FL, s) for s in (40, 48, 56, 64, 76)}
NAVY, GOLD, GREEN, RED = (12, 30, 52), (240, 190, 80), (140, 220, 160), (235, 80, 80)
ease = lambda x: 1 - (1 - max(0, min(1, x))) ** 3
def clamp(x): return max(0.0, min(1.0, x))
def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def pan_view(x, zoom=1.0):
    w = int(1080 / zoom); h = int(1920 / zoom)
    x = max(0, min(PW - w, x)); y = PH - h
    return PAN.crop((int(x), y, int(x) + w, y + h)).resize((W, H))

def ol(d, xy, text, f, fill=(255, 255, 255), sw=9, anchor="mm", stroke=(0, 0, 0)):
    d.text(xy, text, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

def hud(d, tt, alpha=1.0):
    if alpha <= 0: return
    kasse = 1000 if tt < BUILD1 else 200
    geb = 0 if tt < BUILD1 else 1
    y = 110 - (1 - ease(alpha)) * 220
    d.rounded_rectangle([40, y, W - 40, y + 116], radius=34, fill=NAVY, outline=GOLD, width=5)
    d.text((90, y + 58), "TAG 1", font=fB[48], fill=GOLD, anchor="lm")
    d.text((W / 2 - 40, y + 58), f"{kasse:,} €".replace(",", "."), font=fB[48], fill=(255, 255, 255), anchor="mm")
    d.text((W - 300, y + 58), "1 EW", font=fB[48], fill=GREEN, anchor="mm")
    d.text((W - 90, y + 58), f"{geb} 🏠" if False else f"{geb} GEB", font=fB[40], fill=(150, 200, 255), anchor="rm")

def subs(d, tt):
    for k, v in L.items():
        if v["t0"] - 0.05 <= tt <= v["t1"] + 0.15:
            ws = v["words"]
            groups = [ws[i:i + 3] for i in range(0, len(ws), 3)]
            for gi, g in enumerate(groups):
                gs = g[0][0]
                ge = groups[gi + 1][0][0] if gi + 1 < len(groups) else v["t1"] + 0.15
                if gs - 0.05 <= tt < ge:
                    cur = max([i for i, w in enumerate(g) if w[0] <= tt] or [0])
                    words = [w[2].upper() for w in g]
                    f = fB[80]; gap = 26
                    widths = [d.textlength(w, font=f) for w in words]
                    while sum(widths) + gap * (len(words) - 1) > W - 100 and f.size > 48:
                        f = fB[{80: 64, 64: 56, 56: 48}[f.size]]; widths = [d.textlength(w, font=f) for w in words]
                    x = (W - sum(widths) - gap * (len(words) - 1)) / 2
                    for i, w in enumerate(words):
                        d.text((x, 1560), w, font=f, fill=(255, 214, 90) if i == cur else (255, 255, 255),
                               stroke_width=9, stroke_fill=(0, 0, 0), anchor="lm")
                        x += widths[i] + gap
                    return

def flag(d, x, y, s, wt):
    d.rectangle([x, y, x + 12 * s, y + 420 * s], fill=(70, 50, 30))
    fw, fh = 300 * s, 200 * s
    top = [(x + 12 * s + u / 20 * fw, y + math.sin(wt * 5 + u / 20 * 6) * 14 * s * u / 20) for u in range(21)]
    bot = [(px, py + fh) for px, py in top]
    d.polygon(top + bot[::-1], fill=(30, 120, 180))
    mid = [(px, py + fh * 0.55) for px, py in top]
    d.polygon(top + mid[::-1], fill=(255, 196, 110))
    m = [top[i] for i in (2, 8, 13, 20)]
    d.polygon([(m[0][0], m[0][1] + fh * 0.7), (m[1][0], m[1][1] + fh * 0.15), (m[2][0] - 10 * s, m[2][1] + fh * 0.5),
               (m[2][0] + 20 * s, m[2][1] + fh * 0.25), (m[3][0], m[3][1] + fh * 0.7)], fill=(60, 90, 100))
    d.rectangle([x + 12 * s, y, x + 26 * s, y + fh], fill=GOLD)

def board(d, rows, y0, p):
    h = 150 * len(rows) + 60
    d.rounded_rectangle([70, y0, W - 70, y0 + h], radius=40, fill=(255, 255, 255))
    for i, (a, b, col, st) in enumerate(rows):
        if p < st: continue
        q = ease((p - st) / 0.3)
        y = y0 + 40 + i * 150 + (1 - q) * 30
        d.text((120, y + 55), a, font=fB[56], fill=NAVY, anchor="lm")
        d.text((W - 120, y + 55), b, font=fB[64], fill=col, anchor="rm")
        if i < len(rows) - 1:
            d.line([(120, y + 128), (W - 120, y + 128)], fill=(225, 230, 238), width=4)

def lighthouse(d, x, base, prog, t):
    # Haus + Turm, wird von unten nach oben gebaut
    hh = 820
    top = base - hh * prog
    tw = 150
    def clipbox(y0, y1):
        return max(y0, top), y1
    # Haus
    y0, y1 = clipbox(base - 220, base)
    if y1 > y0:
        d.rectangle([x - 260, y0, x - 40, y1], fill=(245, 240, 230))
        if top < base - 220:
            d.polygon([(x - 290, base - 220), (x - 150, base - 330), (x - 10, base - 220)], fill=(200, 70, 60)) if top < base - 330 else None
            d.rectangle([x - 200, base - 150, x - 140, base - 80], fill=(120, 180, 230))
            d.rectangle([x - 110, base - 120, x - 60, base], fill=(130, 90, 60))
    # Turm (rot-weiß gestreift)
    for k in range(6):
        sy1 = base - k * 110; sy0 = sy1 - 110
        a, b = clipbox(sy0, sy1)
        if b > a:
            sh = 1 - k * 0.06
            d.polygon([(x - tw / 2 * sh, b), (x + tw / 2 * sh, b), (x + tw / 2 * (sh - 0.06), a), (x - tw / 2 * (sh - 0.06), a)],
                      fill=(235, 70, 70) if k % 2 == 0 else (250, 250, 250))
    if prog >= 0.82:
        d.rectangle([x - 60, base - 760, x + 60, base - 680], fill=(255, 240, 150))
        d.polygon([(x - 80, base - 760), (x, base - 820), (x + 80, base - 760)], fill=(200, 70, 60))
        if prog >= 1:
            for a in (-0.25, 0.25):
                ang = math.sin(t * 2) * 0.6 + a
                d.polygon([(x, base - 720), (x + 600 * math.cos(ang - 0.1), base - 720 + 600 * math.sin(ang - 0.1)),
                           (x + 600 * math.cos(ang + 0.1), base - 720 + 600 * math.sin(ang + 0.1))], fill=(255, 250, 200))
    # Gerüst während Bau
    if 0 < prog < 1:
        for yy in range(int(top), base, 60):
            d.line([(x - 110, yy), (x + 110, yy)], fill=(150, 110, 70), width=6)
        d.line([(x - 110, top), (x - 110, base)], fill=(150, 110, 70), width=6)
        d.line([(x + 110, top), (x + 110, base)], fill=(150, 110, 70), width=6)

def frame(tt):
    sc = next(k for k, (a, b) in S.items() if a <= tt < b) if tt < TOTAL else "og"
    a, b = S[sc]; p = (tt - a) / (b - a)
    if sc == "hook":
        img = pan_view(450 + 120 * p, zoom=1.15 - 0.1 * p)
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.55 * (1 - ease(p * 1.3)))
        d = ImageDraw.Draw(img)
        s = back((tt) / 0.35)
        ol(d, (W / 2, 560), "ICH HABE MEIN", fB[96], sw=10)
        ol(d, (W / 2, 690), "EIGENES LAND", fB[110], sw=10)
        ol(d, (W / 2, 830), "GEGRÜNDET", fB[110], fill=(255, 214, 90), sw=10)
        if tt > L["l1"]["t0"] + 2.0:
            q = back((tt - L["l1"]["t0"] - 2.0) / 0.3)
            d.rounded_rectangle([W / 2 - 330, 940, W / 2 + 330, 940 + 150 * q], radius=30, fill=GOLD)
            if q > 0.7: d.text((W / 2, 1015), "MIT 1.000 €", font=fB[96], fill=NAVY, anchor="mm")
    elif sc == "pan":
        img = pan_view(ease(p) * (PW - 1080), zoom=1.0)
        d = ImageDraw.Draw(img)
        lab = [("BERGE", 0.0, 0.3), ("WÄLDER", 0.3, 0.5), ("EIGENER FLUSS", 0.5, 0.72), ("MEER", 0.72, 1.01)]
        for txt, s0, s1 in lab:
            if s0 <= p < s1:
                q = back((p - s0) / 0.06)
                ol(d, (W / 2, 470), txt, fB[int(110 * min(1, q) + 1)] if False else fB[110], fill=(255, 255, 255), sw=11)
    elif sc == "map":
        img = Image.new("RGB", (W, H), (30, 120, 180))
        z = 0.75 + 0.25 * ease(p * 1.4)
        sz = int(1000 * z)
        img.paste(MAP.resize((sz, sz)), (int(W / 2 - sz / 2), int(860 - sz / 2)))
        d = ImageDraw.Draw(img)
        if tt > L["l3"]["t0"] + 0.1:
            q = back((tt - L["l3"]["t0"] - 0.1) / 0.3)
            d.rounded_rectangle([W / 2 - 280, 300, W / 2 + 280, 300 + 140 * min(1, q)], radius=30, fill=NAVY, outline=GOLD, width=5)
            if q > 0.7: d.text((W / 2, 370), "12 KM²", font=fB[96], fill=GOLD, anchor="mm")
        if tt > L["l3"]["t0"] + 2.2:
            q = back((tt - L["l3"]["t0"] - 2.2) / 0.3)
            ol(d, (W / 2, 1420), "100 % LEER", fB[110], fill=(255, 255, 255), sw=12)
    elif sc == "flag":
        img = pan_view(2150, zoom=1.0)
        d = ImageDraw.Draw(img)
        rise = ease((tt - a) / 1.2)
        flag(d, 330, 1350 - 420 * rise, 1.3, tt)
        if tt > L["l4"]["t0"] + 0.8:
            q = back((tt - L["l4"]["t0"] - 0.8) / 0.35)
            sz = max(10, int(470 * q))
            img.paste(LOGO.resize((sz, sz)), (int(W / 2 - sz / 2), int(520 - sz / 2)), lm.resize((sz, sz)))
            d = ImageDraw.Draw(img)
        hud(d, tt, clamp((tt - L["l4"]["t0"] - 2.0) / 0.4))
    elif sc == "stats":
        img = pan_view(1500, zoom=1.05)
        img = Image.blend(img, Image.new("RGB", (W, H), NAVY), 0.55)
        d = ImageDraw.Draw(img)
        hud(d, tt)
        ol(d, (W / 2, 380), "STARTWERTE", fB[96], fill=GOLD, sw=10)
        st = [L["l5"]["t0"] + o for o in (0.0, 2.0, 4.7)]
        rows = [("KAPITAL", "1.000 €", (200, 140, 30), st[0]), ("EINWOHNER", "1 (ICH)", (60, 160, 90), st[1]),
                ("GEBÄUDE", "0", RED, st[2])]
        board(d, rows, 520, tt)
    elif sc == "build":
        img = pan_view(2150, zoom=1.0)
        d = ImageDraw.Draw(img)
        prog = clamp((tt - BUILD0) / (BUILD1 - BUILD0 - 0.2))
        flag(d, 600, 1000, 0.8, tt)
        lighthouse(d, 470, 1420, prog, tt)
        hud(d, tt)
        if tt < BUILD0:
            q = back((tt - a) / 0.35)
            d.rounded_rectangle([80, 330, W - 80, 330 + 260 * min(1, q)], radius=36, fill=(255, 255, 255))
            if q > 0.7:
                d.text((W / 2, 400), "ERSTE ENTSCHEIDUNG", font=fB[56], fill=NAVY, anchor="mm")
                d.text((W / 2, 500), "LEUCHTTURM-HAUS", font=fB[72], fill=(220, 80, 60), anchor="mm")
        else:
            d.rounded_rectangle([110, 340, W - 110, 420], radius=40, fill=NAVY)
            d.rounded_rectangle([120, 350, 120 + (W - 240) * prog, 410], radius=30, fill=GREEN if prog >= 1 else GOLD)
            d.text((W / 2, 380), "FERTIG!" if prog >= 1 else f"BAU {int(prog * 100)} %", font=fB[48], fill=(255, 255, 255),
                   anchor="mm", stroke_width=5, stroke_fill=NAVY)
            ol(d, (W / 2, 520), "− 800 €", fB[110], fill=RED, sw=10)
    elif sc == "budget":
        img = pan_view(2150, zoom=1.0)
        d = ImageDraw.Draw(img)
        lighthouse(d, 470, 1420, 1.0, tt)
        img = Image.blend(img, Image.new("RGB", (W, H), NAVY), 0.5)
        d = ImageDraw.Draw(img)
        hud(d, tt)
        d.rounded_rectangle([90, 420, W - 90, 1060], radius=40, fill=(255, 255, 255))
        d.text((W - 160, 530), "1.000 €", font=fB[80], fill=NAVY, anchor="rm")
        d.text((W - 160, 660), "− 800 €", font=fB[80], fill=RED, anchor="rm")
        d.text((160, 660), "HAUS", font=fB[56], fill=(120, 130, 150), anchor="lm")
        d.line([(160, 740), (W - 160, 740)], fill=NAVY, width=8)
        q = back((tt - a - 0.4) / 0.35)
        if q > 0:
            d.text((W - 160, 880), "200 €", font=ImageFont.truetype(FB, int(80 + 50 * min(1, q))), fill=(60, 160, 90), anchor="rm")
            d.text((160, 880), "ÜBRIG", font=fB[56], fill=(120, 130, 150), anchor="lm")
    elif sc == "rules":
        img = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(img)
        for y in range(0, H, 6):
            g = int(18 + 14 * math.sin(y / 140 + tt))
            d.rectangle([0, y, W, y + 6], fill=(12, g + 12, 52 + g))
        hud(d, tt)
        ol(d, (W / 2, 360), "AB JETZT", fB[80], fill=(255, 255, 255), sw=9)
        ol(d, (W / 2, 470), "ENTSCHEIDET IHR", fB[96], fill=GOLD, sw=10)
        cards = [(1.4, "1 LIKE", "= 1 €", (255, 120, 140)), (3.4, "1 FOLLOWER", "= 1 EINWOHNER", GREEN),
                 (5.4, "TOP-KOMMENTAR", "= NÄCHSTER BAU", (130, 190, 255))]
        for i, (off, l1_, r1_, col) in enumerate(cards):
            st = L["l8"]["t0"] + off
            if tt < st: continue
            q = ease((tt - st) / 0.35)
            y = 620 + i * 210; x0 = 80 + (1 - q) * -1000
            d.rounded_rectangle([x0, y, x0 + W - 160, y + 180], radius=34, fill=(255, 255, 255))
            d.rounded_rectangle([x0, y, x0 + 30, y + 180], radius=14, fill=col)
            d.text((x0 + 70, y + 58), l1_, font=fB[56], fill=NAVY, anchor="lm")
            d.text((x0 + W - 200, y + 128), r1_, font=fL[64], fill=tuple(int(c * 0.65) for c in col), anchor="rm")
    else:  # og
        img = pan_view(2150, zoom=1.0)
        d = ImageDraw.Draw(img)
        lighthouse(d, 470, 1420, 1.0, tt)
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
        d = ImageDraw.Draw(img)
        hud(d, tt)
        q = back((tt - a) / 0.45)
        cx, cy = W / 2, 760
        w2, h2 = 440 * min(1.05, q), 280 * min(1.05, q)
        rot = math.sin(tt * 2) * 0.0
        d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], radius=40, fill=GOLD, outline=(255, 245, 200), width=8)
        if q > 0.8:
            sx = cx - w2 + ((tt * 700) % (2 * w2 + 400)) - 200
            if cx - w2 + 60 < sx < cx + w2 - 20:
                d.polygon([(sx, cy - h2 + 8), (sx + 60, cy - h2 + 8), (sx - 40, cy + h2 - 8), (sx - 100, cy + h2 - 8)], fill=(250, 215, 120))
            sz = 300
            img.paste(LOGO.resize((sz, sz)), (int(cx - w2 + 40), int(cy - sz / 2)), lm.resize((sz, sz)))
            d = ImageDraw.Draw(img)
            d.text((cx + 150, cy - 160), "OG-PASS", font=fB[96], fill=NAVY, anchor="mm")
            d.text((cx + 150, cy - 50), "BÜRGER VON", font=fB[48], fill=NAVY, anchor="mm")
            d.text((cx + 150, cy + 20), "VALMORA", font=fB[72], fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=NAVY)
            d.text((cx + 150, cy + 150), "NR. 0001 – 0100", font=fB[48], fill=NAVY, anchor="mm")
        if tt > L["l9"]["t0"] + 3.0:
            q2 = back((tt - L["l9"]["t0"] - 3.0) / 0.35)
            d.rounded_rectangle([W / 2 - 340, 1150, W / 2 + 340, 1150 + 130 * min(1, q2)], radius=65, fill=(235, 70, 90))
            if q2 > 0.7: d.text((W / 2, 1215), "JETZT FOLGEN", font=fB[72], fill=(255, 255, 255), anchor="mm")
    d = ImageDraw.Draw(img)
    subs(d, tt)
    return img

nf = int(TOTAL * FPS)
if os.environ.get("PREVIEW"):
    for t_ in [float(x) for x in os.environ["PREVIEW"].split(",")]:
        frame(t_).resize((360, 640)).save(f"pv_{t_:05.1f}.png")
    raise SystemExit
proc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", str(FPS), "-i", "-", "-i", "mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                         "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                         "-shortest", "-movflags", "+faststart", "valmora_tag01.mp4"], stdin=subprocess.PIPE)
for i in range(nf):
    proc.stdin.write(frame(i / FPS).tobytes())
proc.stdin.close(); proc.wait()
print("done", TOTAL)
