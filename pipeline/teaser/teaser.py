import sys, json, math, subprocess, os
sys.path.insert(0, "/home/claude")
import numpy as np, skia
from draw import *
from scenes import glow, float_hearts, briefcase, shower, vignette

FPS, SR = 30, 48000
OFF = 0.4
TOTAL = 15.6
W_ = json.load(open("/home/claude/teaser/t01.mp3.json"))
w0 = W_[0][0]
WT = [OFF + (o - w0) for o, d, t in W_]
TOK = [t for o, d, t in W_]


def wt(word, n=0):
    k = [i for i, t in enumerate(TOK) if t == word][n]
    return WT[k]


raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", "/home/claude/teaser/t01.wav", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
v = np.frombuffer(raw, np.float32)
voice = np.zeros(int(TOTAL * SR), np.float32)
s0 = int(OFF * SR)
voice[s0:s0 + len(v)] = v[: len(voice) - s0]
VEND = OFF + len(v) / SR
hop = SR // FPS
nf = int(TOTAL * FPS) + 1
env = np.array([np.sqrt(np.mean(voice[k * hop:(k + 1) * hop] ** 2) + 1e-12) for k in range(nf)])
env = np.clip(env / np.percentile(env[env > 1e-3], 95), 0, 1)
for k in range(1, nf):
    env[k] = max(env[k], env[k - 1] * 0.55)

DISP = ["Yo,", "ich", "bin", "Ahmed.", "27,", "100", "%", "Single…", "noch.", "Lena", "kommt", "in", "30", "Tagen.", "Und", "ihr", "entscheidet,", "was", "ich", "mache.", "Schreibt", "A", "für", "Arbeit,", "oder", "B", "für", "Duschen.", "Wallah,", "ich", "mach,", "was", "ihr", "sagt."]
assert len(DISP) == len(TOK)
DISP[5], DISP[6] = "100%", ""
CH = []
cur = []
for k, (tok, t) in enumerate(zip(DISP, WT)):
    if tok:
        cur.append((tok, t))
    if (tok and tok[-1] in ".…" and len(cur) >= 2) or len(cur) >= 5 or k == len(DISP) - 1:
        if cur:
            CH.append(dict(words=cur, start=cur[0][1] - 0.06))
        cur = []
for k, ch in enumerate(CH):
    ch["end"] = CH[k + 1]["start"] if k + 1 < len(CH) else VEND + 0.4


def frame(c, t):
    background(c, t, "#F9D85E", "#FBE07A")
    glow(c, 540, 600, 520, "#FFFFFF", 90)
    float_hearts(c, t, 6, 110, 2)
    vote = t >= wt("Und") - 0.1
    if not vote:
        c.save()
        s = back(prog(t, 0.15, 0.45))
        c.translate(540, 560)
        c.scale(s, s)
        c.translate(-540, -560)
        card(c, 90, 300, 900, 520, "#FFFFFF", 34, 14, 8)
        rows = [("Name", "Ahmed, 27", wt("Ahmed")), ("Status", "100% Single", wt("hundert")), ("Date", "Lena, in 30 Tagen", wt("Lena")), ("Budget", "3,40 €", wt("Tagen") + 0.25)]
        for k, (lab, val, ts) in enumerate(rows):
            y = 390 + k * 115
            if t < ts:
                continue
            x = prog(t, ts, 0.3)
            c.save()
            c.translate((1 - eo(x)) * -60, 0)
            a = int(255 * clamp(x * 2))
            text(c, lab, 150, y + 16, "black", 44, "#E0245E", "l", a=a)
            text(c, val, 940, y + 16, "black", 46, INK, "r", a=a)
            if k == 2:
                heart(c, 940 - tw(val, "black", 46) - 40, y, 22, "#E0245E", 5)
            if k < 3:
                c.drawLine(140, y + 58, 950, y + 58, strokep("#EEEEEE", 4))
            c.restore()
        c.restore()
    else:
        tv = wt("Und") - 0.1
        c.save()
        s = back(prog(t, tv, 0.45))
        c.translate(540, 560)
        c.scale(s, s)
        c.translate(-540, -560)
        card(c, 90, 300, 900, 520, "#FFFFFF", 34, 14, 8)
        text(c, "Was soll Ahmed machen?", 540, 395, "black", 52, INK)
        for k, (lab, txt, ts) in enumerate([("A", "Arbeit suchen", wt("A")), ("B", "Endlich duschen", wt("B"))]):
            if t < ts:
                continue
            y = 450 + k * 175
            x = back(prog(t, ts, 0.35))
            c.save()
            c.translate(540, y + 65)
            c.scale(x, x)
            c.translate(-540, -(y + 65))
            sel = (k == 0 and t < wt("B")) or (k == 1 and wt("B") <= t < wt("Wallah"))
            rrect(c, 140, y, 800, 130, 30, "#FFD84D" if (sel and k == 0) else ("#8FD3FF" if sel else "#F3F1EE"), 6)
            circ(c, 215, y + 65, 42, INK)
            text(c, lab, 215, y + 82, "black", 48, "#FFFFFF")
            text(c, txt, 285, y + 82, "black", 50, INK, "l")
            if k == 0:
                briefcase(c, 870, y + 60, 0.9)
            else:
                shower(c, 870, y + 68, 0.9, t)
            c.restore()
        c.restore()
    st = dict(mouth=float(env[min(int(t * FPS), nf - 1)]), blink=(t % 3.3) < 0.11, rarm=-150, wave=1.0 if t < 1.6 else 0.0)
    if wt("Single…".rstrip("…") if False else "Single") <= t < wt("Lena"):
        st["eyes"] = "smug"
    if wt("Lena") <= t < wt("Und"):
        st["eyes"] = "heart"
    if t >= wt("Wallah"):
        st["wave"] = 1.0
        st["hop"] = max(0, math.sin((t - wt("Wallah")) * 7) * 40)
    ahmed(c, t, 540, 1840, 1.0, st)
    c.save()
    pop(c, t, 0.0, 540, 160)
    pill(c, "WER IST AHMED?", 540, 160, 56, fill=INK, col="#FFD84D", name="black", padx=40, pady=24)
    c.restore()
    if t >= wt("Wallah") - 0.1:
        c.save()
        pop(c, t, wt("Wallah") - 0.1, 540, 1010, kind="el")
        bb = 1 + 0.05 * math.sin(t * 10)
        c.translate(540, 1010)
        c.scale(bb, bb)
        c.translate(-540, -1010)
        pill(c, "KOMMENTIERE A ODER B", 540, 1010, 58, fill="#E0245E", name="black", padx=40, pady=24)
        c.restore()
        ay = 1110 + 12 * math.sin(t * 8)
        p = strokep(INK, 12)
        c.drawLine(540, ay, 540, ay + 50, p)
        c.drawLine(540, ay + 50, 515, ay + 25, p)
        c.drawLine(540, ay + 50, 565, ay + 25, p)
    else:
        for ch in CH:
            if ch["start"] <= t < ch["end"]:
                caption(c, t, "A", ch["words"], 1050, tail_x=560, appear=ch["start"])
    c.drawImage(vignette(), 0, 0)


def render(out):
    tmp = out + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "1080x1920", "-r", "30", "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    s = skia.Surface(1080, 1920)
    c = s.getCanvas()
    for f in range(int(TOTAL * FPS)):
        t = f / FPS
        c.save()
        z = 1 + 0.03 * t / TOTAL
        c.translate(540, 1056)
        c.scale(z, z)
        c.translate(-540, -1056)
        frame(c, t)
        c.restore()
        p.stdin.write(s.makeImageSnapshot().tobytes())
    p.stdin.close()
    assert p.wait() == 0
    os.replace(tmp, out)


def audio(out):
    ns = {}
    src = open("/home/claude/audio.py").read()
    src = src[: src.index("# ================= SFX track")]
    exec(src, ns)
    N = int(TOTAL * SR)
    mus = np.zeros(N)
    sfx = np.zeros(N)
    add, pizz, taiko, piano, strings, bell, pop_, harp, braam, heartbeat, riser = (ns[k] for k in ["add", "pizz", "taiko", "piano", "strings", "bell", "pop", "harp_gliss", "braam", "heartbeat", "riser"])
    mtof = ns["mtof"]
    beat = 60 / 104
    seq = [62, 69, 66, 69, 62, 69, 67, 69]
    t, k = 0.0, 0
    while t < TOTAL - 1.2:
        add(mus, t, pizz(mtof(seq[k % 8]), 1.0 if k % 2 == 0 else 0.7))
        if k % 4 == 0:
            add(mus, t, taiko(0.3))
        t += beat / 2
        k += 1
    rom = [[62, 66, 69], [57, 61, 64], [59, 62, 66], [55, 59, 62]]
    for b in range(int(TOTAL / (4 * beat)) + 1):
        for m in rom[b % 4]:
            add(mus, b * 4 * beat, strings(mtof(m - 12), 4 * beat, 0.4, 0.6, 1500), 0.5)
    add(mus, wt("Wallah") - 0.9, riser(0.9), 0.8)
    add(mus, wt("Wallah") - 0.1, taiko(1.2))
    for k, m in enumerate([74, 78, 81, 86]):
        add(mus, wt("Wallah") + k * 0.08, bell(mtof(m), 1.4, 0.12))
    add(sfx, 0.0, pop_(), 0.35)
    add(sfx, 0.15, pop_(300, 700, 0.12), 0.3)
    for w in ["Ahmed", "hundert", "Lena"]:
        add(sfx, wt(w), pop_(), 0.3)
    add(sfx, wt("Lena"), heartbeat(), 0.6)
    add(sfx, wt("Tagen") + 0.25, pop_(), 0.3)
    add(sfx, wt("Und") - 0.1, ns["whoosh"](0.35), 0.4)
    add(sfx, wt("A"), pop_(), 0.35)
    add(sfx, wt("B"), pop_(), 0.35)
    fe = int((TOTAL - 1.0) * SR)
    mus[fe:] *= np.linspace(1, 0, N - fe) ** 2

    def wav(name, x, norm=None):
        if norm:
            x = x / (np.abs(x).max() + 1e-9) * norm
        x = np.clip(x, -1, 1).astype(np.float32)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", f"/home/claude/teaser/{name}.wav"], input=x.tobytes(), check=True)
    wav("voice", voice)
    wav("sfx", sfx, 0.8)
    wav("music", mus, 0.9)
    subprocess.run(["bash", "-c", "cd /home/claude/teaser && sed 's#-y -i voice.wav#-y -i voice.wav#' /home/claude/mix.sh | bash"], check=True)


if __name__ == "__main__":
    if sys.argv[1] == "preview":
        from PIL import Image
        ims = []
        for t in [float(x) for x in sys.argv[2:]]:
            s = skia.Surface(1080, 1920)
            c = s.getCanvas()
            frame(c, t)
            ims.append(Image.frombytes("RGBA", (1080, 1920), s.makeImageSnapshot().tobytes(), "raw", "BGRA").convert("RGB").resize((360, 640)))
        sh = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims):
            sh.paste(im, (i * 360, 0))
        sh.save("/home/claude/teaser/prev.png")
    else:
        audio(None)
        render("/home/claude/teaser/video.mp4")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", "/home/claude/teaser/video.mp4", "-i", "/home/claude/teaser/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", "/home/claude/teaser/teaser_wer_ist_ahmed.mp4"], check=True)
        print("done")
