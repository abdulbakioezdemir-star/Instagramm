"""Valmora – Tag 2 · Teil 2/2: Bäckerei (Top-Kommentar). ca. 30 s. Rendert Audio + Video (1080x1920, 30 fps).
Basis: tag01.py. Bauten kommen aus bauten.py (bleiben in allen Folgen sichtbar)."""
import numpy as np, json, subprocess, math, os
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import butter, sosfilt, fftconvolve

W, H, FPS = 1080, 1920, 30
SR = 48000
rng = np.random.default_rng(4)
exec(open("synth_body.py").read())
from bauten import lighthouse, bootssteg, baeckerei
FB = "/home/claude/instagramm/pipeline/fonts/Bungee-Regular.ttf"
FL = "/home/claude/instagramm/pipeline/fonts/LilitaOne-Regular.ttf"
OUT = os.environ.get("OUT", "valmora_tag02_teil2.mp4")

TAG = 2
K_MIT, KOSTEN = 66, 60         # 1000 + 16 Likes − 950
K_NEU = K_MIT - KOSTEN         # 6
EW = 7

def eur(v): return f"{v:,} €".replace(",", ".")

# ---------------- timeline ----------------
def dec(path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)

NL = 6
gaps = {"l1": 0.1, "l2": 0.25, "l3": 0.25, "l4": 0.25, "l5": 0.25, "l6": 0.25}
t = 0.0
L = {}
for i in range(1, NL + 1):
    k = f"l{i}"
    a = dec(f"{k}.mp3")
    t += gaps[k]
    words = json.load(open(f"{k}.mp3.json"))
    L[k] = dict(t0=t, t1=t + len(a) / SR, audio=a, words=[(t + o, d, w) for o, d, w in words])
    t = L[k]["t1"]
TOTAL = t + 0.8
N = int(TOTAL * SR) + SR
print("total", TOTAL)

def wt(k, idx):  # Startzeit des idx-ten Worts einer Zeile
    ws = L[k]["words"]; return ws[min(idx, len(ws) - 1)][0]

S = {
    "hook": (0, L["l2"]["t0"] - 0.1),
    "stats": (L["l2"]["t0"] - 0.1, L["l3"]["t0"] - 0.1),
    "build": (L["l3"]["t0"] - 0.1, L["l4"]["t0"] - 0.1),
    "pleite": (L["l4"]["t0"] - 0.1, L["l5"]["t0"] - 0.1),
    "vote": (L["l5"]["t0"] - 0.1, L["l6"]["t0"] - 0.1),
    "end": (L["l6"]["t0"] - 0.1, TOTAL + 1),
}
BUILD0 = wt("l3", 5) - 0.1                  # "Bäckerei"
BUILD1 = wt("l3", 8) - 0.15                 # vor "Sechzig"
print("build", BUILD0, BUILD1)

# ---------------- audio ----------------
voice = np.zeros(N)
for k, v in L.items():
    add(voice, v["t0"], v["audio"].astype(np.float64), 1.0)
sfx = np.zeros(N)
add(sfx, 0.0, braam(36, 2.2), 0.55)
add(sfx, 0.05, taiko(1.0), 0.6)
for j in range(6):
    add(sfx, 0.25 + j * 0.09, coin(), 0.28)          # Geld fliegt raus
for k in ("stats", "build", "pleite", "vote", "end"):
    add(sfx, S[k][0], whoosh(0.5), 0.45)
for j in range(3):
    add(sfx, wt("l2", [0, 2, 4][j]), pop(), 0.5)
add(sfx, wt("l3", 1), pop(500, 1200), 0.5)
tt_ = BUILD0
while tt_ < BUILD1:
    add(sfx, tt_, thud(), 0.35); tt_ += 0.3
add(sfx, BUILD1, bell(mtof(84), 1.4, 0.2), 0.8)
add(sfx, wt("l4", 1), coin(), 0.4)
add(sfx, wt("l4", 10) - 0.05, buzzer(), 0.25)
for w_ in (2, 4, 6):
    add(sfx, wt("l5", w_), pop(500, 1200), 0.5)
add(sfx, L["l6"]["t0"] + 0.2, sparkle(), 0.5)
mus = np.zeros(N)
bar = 2.0
Am, F, C, G = (57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)
t0 = 0.0; k = 0
while t0 < TOTAL:
    ch = [Am, F, C, G][k % 4]
    for m in ch:
        add(mus, t0, strings(mtof(m), bar, att=0.6, rel=0.9, bright=1800), 0.18)
    add(mus, t0, strings(mtof(ch[0] - 24), bar, att=0.4, rel=0.9, bright=600), 0.25)
    if t0 >= S["stats"][0] - 0.5 and t0 < S["end"][0] and not (S["pleite"][0] + 2.5 < t0 < S["pleite"][1]):
        for j in range(4):
            add(mus, t0 + j * bar / 4, taiko(0.5 + 0.2 * (j == 0)), 0.18)
    if t0 >= S["stats"][0]:
        notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24]
        for j in range(8):
            add(mus, t0 + j * bar / 8, piano(mtof(notes[[0, 1, 2, 3, 2, 1, 2, 1][j]]), 1.4, 0.45), 0.10)
    t0 += bar; k += 1
fade = np.ones(N); e = int(TOTAL * SR)
fade[e - SR:e] = np.linspace(1, 0, SR); fade[e:] = 0
mus *= fade

def wav(name, x, norm=None):
    if norm: x = x / (np.abs(x).max() + 1e-9) * norm
    x = np.clip(x, -1, 1).astype(np.float32)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", name],
                   input=x.tobytes(), check=True)
if not os.environ.get("PREVIEW"):
    wav("voice.wav", voice); wav("sfx.wav", sfx, 0.8); wav("music.wav", mus, 0.7)
    subprocess.run(["bash", "-c", """ffmpeg -nostdin -v error -y -i voice.wav -i sfx.wav -i music.wav -filter_complex "
[0:a]highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=1.5,asplit=2[v][key];
[2:a]volume=0.5[m];[m][key]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=350[md];
[1:a]volume=0.75[s];[v][s][md]amix=inputs=3:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=10[out]" -map "[out]" -ar 48000 -ac 2 mix.wav"""], check=True)

# ---------------- visuals ----------------
from world import PW, PH
PAN = Image.open("panorama.jpg").convert("RGB")
LOGO = Image.open("logo_valmora.jpg").convert("RGB")
lm = Image.new("L", LOGO.size, 0)
ImageDraw.Draw(lm).ellipse([LOGO.width * 0.1 - 20, LOGO.height * 0.1 - 20, LOGO.width * 0.9 + 20, LOGO.height * 0.9 + 20], fill=255)
fB = {s: ImageFont.truetype(FB, s) for s in (34, 40, 48, 56, 64, 72, 80, 96, 110, 130, 170, 220)}
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

def kasse(tt):
    return K_MIT if tt < BUILD1 else K_NEU

def hud(d, tt, alpha=1.0):
    if alpha <= 0: return
    geb = 2 if tt < BUILD1 else 3
    y = 110 - (1 - ease(alpha)) * 220
    d.rounded_rectangle([40, y, W - 40, y + 116], radius=34, fill=NAVY, outline=GOLD, width=5)
    d.text((90, y + 58), f"TAG {TAG}", font=fB[48], fill=GOLD, anchor="lm")
    d.text((W / 2 - 40, y + 58), eur(kasse(tt)), font=fB[48], fill=(255, 255, 255), anchor="mm")
    d.text((W - 300, y + 58), f"{EW} EW", font=fB[48], fill=GREEN, anchor="mm")
    d.text((W - 90, y + 58), f"{geb} GEB", font=fB[40], fill=(150, 200, 255), anchor="rm")

_SG = {}
def sub_groups(d, ws):
    """Max. 3 Wörter pro Gruppe, aber nur so viele, wie bei Schriftgröße 64 in die Breite passen."""
    key = id(ws)
    if key in _SG: return _SG[key]
    out, cur = [], []
    for w in ws:
        trial = cur + [w]
        wid = sum(d.textlength(x[2].upper(), font=fB[64]) for x in trial) + 26 * (len(trial) - 1)
        if cur and (len(trial) > 3 or wid > W - 100):
            out.append(cur); cur = [w]
        else:
            cur = trial
    if cur: out.append(cur)
    _SG[key] = out
    return out

def subs(d, tt):
    for k, v in L.items():
        if v["t0"] - 0.05 <= tt <= v["t1"] + 0.15:
            ws = v["words"]
            groups = sub_groups(d, ws)
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
                        d.text((x, 1640), w, font=f, fill=(255, 214, 90) if i == cur else (255, 255, 255),
                               stroke_width=9, stroke_fill=(0, 0, 0), anchor="lm")
                        x += widths[i] + gap
                    return

def board(d, rows, y0, tt):
    h = 150 * len(rows) + 60
    d.rounded_rectangle([70, y0, W - 70, y0 + h], radius=40, fill=(255, 255, 255))
    for i, (a, b, col, st) in enumerate(rows):
        if tt < st: continue
        q = ease((tt - st) / 0.3)
        y = y0 + 40 + i * 150 + (1 - q) * 30
        d.text((120, y + 55), a, font=fB[56], fill=NAVY, anchor="lm")
        d.text((W - 120, y + 55), b, font=fB[64], fill=col, anchor="rm")
        if i < len(rows) - 1:
            d.line([(120, y + 128), (W - 120, y + 128)], fill=(225, 230, 238), width=4)

STEG = (600, 1330, 440)   # x0, y, Länge
BAECK = (150, 1585)       # x, Boden (Strand unter dem Fluss)

def scene_world(tt, baeck_prog):
    img = pan_view(2150, zoom=1.0)
    d = ImageDraw.Draw(img)
    bootssteg(d, STEG[0], STEG[1], STEG[2], 1.0, tt)
    lighthouse(d, 470, 1420, 1.0, tt)
    baeckerei(d, BAECK[0], BAECK[1], baeck_prog, tt, font=fB[34])
    return img

OPTS = [("1", "FISCHERHÜTTE", (90, 170, 230)), ("2", "BRUNNEN", (140, 220, 160)), ("3", "GARTEN", (240, 190, 80))]

def frame(tt):
    sc = next((k for k, (a, b) in S.items() if a <= tt < b), "end")
    a, b = S[sc]; p = (tt - a) / (b - a)
    if sc == "hook":
        img = scene_world(tt, 0)
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.45 - 0.15 * ease(p))
        d = ImageDraw.Draw(img)
        # Münzen fliegen aus dem Bild (Bewegung ab Frame 0)
        for j in range(14):
            ph = (tt * 0.9 + j * 0.071) % 1.0
            cx = W / 2 + math.sin(j * 2.3) * 420 * ph
            cy = 1250 - ph * 1300 + (j % 3) * 40
            r = 26 - 10 * ph
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=(160, 110, 30), width=4)
        hud(d, tt)
        s = back(tt / 0.25)
        ol(d, (W / 2, 470), "1 KOMMENTAR", fB[110] if s > 0.9 else fB[96], fill=GOLD, sw=12)
        ol(d, (W / 2, 620), "HAT MEIN GELD", fB[80], sw=10)
        ol(d, (W / 2, 730), "AUSGEGEBEN", fB[96], sw=10)
        st = wt("l1", 8) - 0.1
        if tt > st:
            q = back((tt - st) / 0.3)
            pulse = 1 + 0.04 * math.sin((tt - st) * 10)
            hw, hh = 380 * pulse, 95 * min(1, q) * pulse
            d.rounded_rectangle([W / 2 - hw, 980 - hh, W / 2 + hw, 980 + hh], radius=34, fill=RED, outline=(255, 255, 255), width=6)
            if q > 0.7:
                d.text((W / 2, 980), f"{eur(K_MIT)} → {eur(K_NEU)}", font=fB[80], fill=(255, 255, 255), anchor="mm")
    elif sc == "stats":
        img = scene_world(tt, 0)
        img = Image.blend(img, Image.new("RGB", (W, H), NAVY), 0.55)
        d = ImageDraw.Draw(img)
        hud(d, tt)
        ol(d, (W / 2, 380), "STAND JETZT", fB[96], fill=GOLD, sw=10)
        rows = [("EINWOHNER", str(EW), (60, 160, 90), wt("l2", 0) - 0.1), ("LIKES", "16", (255, 90, 120), wt("l2", 2) - 0.1),
                ("KASSE", eur(K_MIT), NAVY, wt("l2", 4) - 0.1)]
        board(d, rows, 520, tt)
    elif sc == "build":
        prog = clamp((tt - BUILD0) / (BUILD1 - BUILD0 - 0.2))
        img = scene_world(tt, prog)
        d = ImageDraw.Draw(img)
        hud(d, tt)
        if tt < BUILD0:
            q = back((tt - a) / 0.35)
            d.rounded_rectangle([80, 330, W - 80, 330 + 330 * min(1, q)], radius=36, fill=(255, 255, 255), outline=GOLD, width=6)
            if q > 0.7:
                d.text((W / 2, 400), "TOP-KOMMENTAR", font=fB[56], fill=(120, 130, 150), anchor="mm")
                if tt > wt("l3", 1) - 0.15:
                    d.text((W / 2, 510), '"BAU EINEN', font=fB[80], fill=NAVY, anchor="mm")
                    d.text((W / 2, 600), 'BÄCKER"', font=fB[80], fill=(220, 80, 60), anchor="mm")
            if tt > wt("l3", 4) - 0.1:
                ol(d, (W / 2, 800), "OKAY.", fB[130], fill=GOLD, sw=12)
        else:
            d.rounded_rectangle([110, 340, W - 110, 420], radius=40, fill=NAVY)
            d.rounded_rectangle([120, 350, 120 + (W - 240) * max(0.06, prog), 410], radius=30, fill=GREEN if prog >= 1 else GOLD)
            d.text((W / 2, 380), "FERTIG!" if prog >= 1 else f"BAU {int(prog * 100)} %", font=fB[48], fill=(255, 255, 255),
                   anchor="mm", stroke_width=5, stroke_fill=NAVY)
            ol(d, (W / 2, 530), "BÄCKEREI", fB[110], fill=(255, 255, 255), sw=10)
            if tt > wt("l3", 8) - 0.15:
                ol(d, (W / 2, 670), f"− {eur(KOSTEN)}", fB[110], fill=RED, sw=10)
    elif sc == "pleite":
        img = scene_world(tt, 1.0)
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.5)
        d = ImageDraw.Draw(img)
        hud(d, tt)
        shake = math.sin(tt * 40) * 8 * clamp(1 - (tt - a) / 0.6)
        ol(d, (W / 2 + shake, 560), eur(K_NEU), fB[220], fill=RED, sw=14)
        ol(d, (W / 2, 740), "ÜBRIG", fB[80], fill=(255, 255, 255), sw=10)
        for st, txt, col, y in ((wt("l4", 4) - 0.1, "BROT: FRISCH", GREEN, 900), (wt("l4", 8) - 0.1, "GRÜNDER: PLEITE", RED, 1060)):
            if tt > st:
                q = back((tt - st) / 0.3)
                d.rounded_rectangle([90, y - 70 * min(1, q), W - 90, y + 70 * min(1, q)], radius=34, fill=(255, 255, 255))
                if q > 0.7: d.text((W / 2, y), txt, font=fB[72], fill=tuple(int(c * 0.75) for c in col), anchor="mm")
    elif sc == "vote":
        img = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(img)
        for y in range(0, H, 6):
            g = int(18 + 14 * math.sin(y / 140 + tt))
            d.rectangle([0, y, W, y + 6], fill=(12, g + 12, 52 + g))
        hud(d, tt)
        ol(d, (W / 2, 400), "UND MORGEN?", fB[96], fill=GOLD, sw=10)
        for i, (num, name, col) in enumerate(OPTS):
            st = wt("l5", 2 + 2 * i) - 0.1
            if tt < st: continue
            q = ease((tt - st) / 0.35)
            y = 560 + i * 250; x0 = 80 + (1 - q) * -1000
            d.rounded_rectangle([x0, y, x0 + W - 160, y + 200], radius=36, fill=(255, 255, 255))
            d.ellipse([x0 + 30, y + 25, x0 + 180, y + 175], fill=col)
            d.text((x0 + 105, y + 100), num, font=fB[96], fill=NAVY, anchor="mm")
            d.text((x0 + 220, y + 100), name, font=fB[64], fill=NAVY, anchor="lm")
    else:  # end
        img = scene_world(tt, 1.0)
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
        d = ImageDraw.Draw(img)
        hud(d, tt)
        q = back((tt - a) / 0.4)
        d.rounded_rectangle([80, 330, W - 80, 330 + 330 * min(1, q)], radius=40, fill=(255, 255, 255), outline=GOLD, width=8)
        if q > 0.7:
            d.text((W / 2, 420), "SCHREIB DIE ZAHL", font=fB[72], fill=NAVY, anchor="mm")
            for i, (num, name, col) in enumerate(OPTS):
                cx = W / 2 + (i - 1) * 230
                d.ellipse([cx - 75, 495, cx + 75, 645], fill=col)
                d.text((cx, 570), num, font=fB[96], fill=NAVY, anchor="mm")
        st = wt("l6", 3) - 0.1
        if tt > st:
            q2 = back((tt - st) / 0.35)
            sz = int(260 * min(1, q2)) + 1
            img.paste(LOGO.resize((sz, sz)), (int(W / 2 - sz / 2), int(860 - sz / 2)), lm.resize((sz, sz)))
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([W / 2 - 340, 1030, W / 2 + 340, 1030 + 130 * min(1, q2)], radius=65, fill=(235, 70, 90))
            if q2 > 0.7: d.text((W / 2, 1095), "JETZT FOLGEN", font=fB[72], fill=(255, 255, 255), anchor="mm")
    d = ImageDraw.Draw(img)
    subs(d, tt)
    return img

nf = int(TOTAL * FPS)
if os.environ.get("PREVIEW"):
    ts = [float(x) for x in os.environ["PREVIEW"].split(",")] if os.environ["PREVIEW"] != "auto" else \
        [0.0, 0.5, 1.5, 3.0] + [(S[k][0] + S[k][1]) / 2 for k in S if k != "end"] + [BUILD0 + 0.8, BUILD1 + 0.3, S["vote"][1] - 0.3, S["end"][0] + 1.5, TOTAL - 0.3]
    for t_ in ts:
        frame(t_).resize((360, 640)).save(f"pv_{t_:05.1f}.png")
    raise SystemExit
proc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                         "-r", str(FPS), "-i", "-", "-i", "mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                         "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                         "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(nf):
    proc.stdin.write(frame(i / FPS).tobytes())
proc.stdin.close(); proc.wait()
print("done", TOTAL)
