import json, subprocess, numpy as np
VO = "/home/claude/vo3"
SR = 48000
FPS = 30
TEXT = {}
for ln in open(f"{VO}/lines.tsv", encoding="utf-8"):
    i, who, txt = ln.rstrip("\n").split("\t")
    TEXT[i] = (who, txt)
USE = ["a01", "a03", "l01", "a04", "l02", "a05", "a06", "l03", "a08", "a09", "a10", "a11", "a12", "a13"]


def load(i):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f"{VO}/{i}.wav", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


AUD = {i: load(i) for i in USE}
DUR = {i: len(a) / SR for i, a in AUD.items()}
STARTS, EV, SCENES = {}, {}, []


def put(i, t):
    STARTS[i] = round(t, 3)
    return t + DUR[i]


def scene(name, s, e):
    SCENES.append((name, round(s, 3), round(e, 3)))


T1 = "Hello my sweet lady, you are my sunshine"
# INTRO
scene("intro", 0.0, 2.2)
# HOOK
s = 2.2
e = put("a01", s + 0.25)
EV["notif"] = e + 0.2
scene("hook", s, e + 1.05)
# MATCH
s = SCENES[-1][2]
EV["match"] = s
e = put("a03", s + 0.85)
scene("match", s, e + 0.3)
# CHAT
s = SCENES[-1][2]
EV["chat"] = s
EV["l01msg"] = s + 0.35
e = put("l01", s + 0.45)
e = put("a04", e + 0.25)
EV["type0"] = STARTS["a04"] + 0.4
EV["type1"] = EV["type0"] + 2.4
EV["send"] = max(e + 0.1, EV["type1"] + 0.2)
EV["dots0"], EV["dots1"] = EV["send"] + 0.25, EV["send"] + 0.8
EV["l02msg"] = EV["send"] + 0.8
e = put("l02", EV["send"] + 0.9)
e = put("a05", e + 0.2)
EV["fail"] = STARTS["a05"] + 0.15
scene("english", s, e + 0.4)
# SECRET
s = SCENES[-1][2]
EV["secret"] = s
e = put("a06", s + 0.25)
EV["versions"] = e + 0.15
scene("secret", s, e + 1.3)
# DATE
s = SCENES[-1][2]
EV["date"] = s
EV["l03msg"] = s + 0.25
e = put("l03", s + 0.35)
e = put("a08", e + 0.2)
EV["freeze"] = e + 0.12
e = put("a09", EV["freeze"] + 0.3)
scene("date", s, e + 0.35)
# MONEY
s = SCENES[-1][2]
EV["money"] = s
e = put("a10", s + 0.25)
EV["tromb"] = e + 0.2
scene("money", s, e + 1.75)
# POLL
s = SCENES[-1][2]
EV["poll"] = s
e = put("a11", s + 0.4)
e = put("a12", e + 0.25)
e = put("a13", e + 0.2)
EV["cta"] = STARTS["a13"] - 0.05
scene("poll", s, e + 0.9)
TOTAL = SCENES[-1][2]


def build():
    lines = []
    n = int(TOTAL * SR) + 1
    ahmed = np.zeros(n, np.float32)
    lena = np.zeros(n, np.float32)
    for i, st in STARTS.items():
        a = AUD[i]
        who, txt = TEXT[i]
        w = json.load(open(f"{VO}/{i}.mp3.json"))
        off0 = w[0][0] if w else 0
        words = [[st + max(0, o - off0), d, t] for o, d, t in w]
        lines.append(dict(id=i, who=who, text=txt, start=st, end=st + DUR[i], words=words))
        s0 = int(st * SR)
        tgt = ahmed if who == "A" else lena
        tgt[s0:s0 + len(a)] += a[: n - s0]
    nf = int(TOTAL * FPS) + 1
    hop = SR // FPS
    env = np.array([np.sqrt(np.mean(ahmed[k * hop:(k + 1) * hop] ** 2) + 1e-12) for k in range(nf)])
    env = np.clip(env / np.percentile(env[env > 1e-3], 95), 0, 1)
    sm = env.copy()
    for k in range(1, nf):
        sm[k] = max(env[k], sm[k - 1] * 0.55)
    np.save("/home/claude/ahmed.npy", ahmed)
    np.save("/home/claude/lena.npy", lena)
    json.dump(dict(lines=lines, mouth=sm.tolist(), scenes=SCENES, total=TOTAL, ev=EV, t1=T1), open("/home/claude/timeline.json", "w"), ensure_ascii=False)
    for sc in SCENES:
        print(sc)
    print("TOTAL", TOTAL)


if __name__ == "__main__":
    build()
