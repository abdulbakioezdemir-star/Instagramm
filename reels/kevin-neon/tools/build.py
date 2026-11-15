"""Kevin Nsimba – Stil-Referenz 3 (Slate-Vorbild): drei Welten.
1 Tiefblau: 3D-Handy mit Kevins Profil, Kamera fliegt über die Bio und taucht ins Profilbild → leuchtendes Icon,
  Buchstaben kreisen in 3D und setzen sich zu „Ein Funke“ zusammen.
2 Hellgrau-Spotlight: Druck / Zweifel / Angst als gekippte 3D-Wörter, Angst im Lichtoval, „Doch ein Funke genügt.“
3 Schwarz-Neon: Potenzial / entfachen / Klarheit / Fokus / Stärke, Stärke hinter Gitterstäben, die aufbrechen → Logo.
Writes index.html."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
T = [w["t"] for w in json.load(open(HERE / "tools" / "words.json"))]
DUR = 18.0
W2, W3, W4 = 3.45, 8.2, 12.52          # world changes (on the beat grid of tools/beat.py)

CSS = """
@font-face { font-family: I; font-weight: 300; src: url(fonts/InterDisplay-Light.otf) format("opentype"); }
@font-face { font-family: I; font-weight: 500; src: url(fonts/InterDisplay-Medium.otf) format("opentype"); }
@font-face { font-family: I; font-weight: 600; src: url(fonts/InterDisplay-SemiBold.otf) format("opentype"); }
@font-face { font-family: I; font-weight: 700; src: url(fonts/InterDisplay-Bold.otf) format("opentype"); }
@font-face { font-family: I; font-weight: 900; src: url(fonts/InterDisplay-Black.otf) format("opentype"); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: I; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { position: absolute; inset: 0; } .abs { position: absolute; } .full { position: absolute; inset: 0; }

/* world 1 – deep blue */
#bg1 { background: radial-gradient(75% 55% at 50% 48%, #1a46e0 0%, #0a1f86 38%, #040c3c 70%, #01030f 100%); }
#ghost { left: 0; top: 700px; width: 1080px; text-align: center; font-size: 250px; font-weight: 900; letter-spacing: -0.03em;
         color: transparent; -webkit-text-stroke: 2px rgba(140,175,255,.10); white-space: nowrap; line-height: 1.1; }
#cam { perspective: 1500px; perspective-origin: 540px 960px; }
#ph { left: 260px; top: 390px; width: 560px; height: 1140px; border-radius: 78px; background: #0a0c13; border: 10px solid #1c2231;
      overflow: hidden; box-shadow: 0 0 0 2px #2c3448, 0 40px 120px rgba(0,10,60,.8), 0 0 160px rgba(60,110,255,.35); }
#ph .abs { position: absolute; }
.stt { left: 44px; top: 26px; font-size: 22px; font-weight: 600; color: #e8ecf5; }
.hdl { left: 40px; top: 76px; font-size: 36px; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
#av { left: 36px; top: 150px; width: 180px; height: 180px; border-radius: 50%; background: #05060a;
      box-shadow: 0 0 0 5px #0a0c13, 0 0 0 9px #d9b26a; display: flex; align-items: center; justify-content: center; }
#av img { width: 138px; }
.sn { top: 196px; width: 100px; text-align: center; color: #fff; font-size: 34px; font-weight: 700; line-height: 1.1; }
.sn small { display: block; font-size: 19px; font-weight: 500; color: #b8bfcf; }
.nm { left: 40px; top: 352px; font-size: 30px; font-weight: 700; color: #fff; }
.rl { left: 40px; top: 392px; font-size: 24px; font-weight: 500; color: #8f98ad; }
.bio { left: 40px; font-size: 46px; font-weight: 700; letter-spacing: -0.02em; white-space: nowrap; line-height: 1.1; }
.bio span { color: #4b5368; }
.btn { top: 588px; height: 64px; border-radius: 16px; font-size: 24px; font-weight: 600; color: #fff; display: flex; align-items: center; justify-content: center; }
.hl { top: 684px; width: 96px; text-align: center; font-size: 17px; font-weight: 500; color: #c9cfdc; }
.hl i { display: block; width: 96px; height: 96px; border-radius: 50%; margin-bottom: 8px; border: 3px solid #2d354a;
        background: radial-gradient(circle at 40% 35%, #2a3550, #0c1020); }
.tile { width: 178px; height: 178px; border-radius: 6px; display: flex; align-items: flex-end; padding: 14px; font-size: 30px; font-weight: 800; color: #fff; letter-spacing: -0.02em; }
#flash { background: #cfe0ff; opacity: 0; }
#icon { left: 390px; top: 760px; width: 300px; height: 300px; border-radius: 74px; background: linear-gradient(150deg, #4a82ff 0%, #1f54f0 45%, #0c2fc4 100%);
        box-shadow: inset 0 3px 0 rgba(255,255,255,.35), 0 0 60px rgba(70,130,255,.9), 0 0 160px rgba(40,90,255,.6);
        display: flex; align-items: center; justify-content: center; opacity: 0; }
#icon img { width: 230px; }
.ring { left: 50%; border-radius: 50%; border: 3px solid rgba(110,160,255,.95); box-shadow: 0 0 18px rgba(80,140,255,.9), inset 0 0 18px rgba(80,140,255,.6); opacity: 0; }
#orbit { perspective: 1100px; perspective-origin: 540px 960px; }
.lt { left: 540px; top: 960px; font-size: 140px; font-weight: 900; color: #fff; line-height: 1; letter-spacing: -0.02em;
      text-shadow: 0 0 30px rgba(120,170,255,.8); opacity: 0; }
.lt.gd { color: #ffd98a; text-shadow: 0 0 30px rgba(255,190,90,.8); }

/* world 2 – light grey spotlight */
#bg2 { background: radial-gradient(70% 50% at 50% 50%, #f3f5f7 0%, #d4d8dc 45%, #9aa0a7 80%, #6c7279 100%); opacity: 0; }
#w2 { perspective: 1300px; perspective-origin: 540px 960px; }
.k { left: 0; width: 1080px; text-align: center; font-weight: 900; color: #2b3037; letter-spacing: -0.045em; line-height: 1; white-space: nowrap; opacity: 0; }
.k .c { display: inline-block; }
.box { display: inline-block; background: #0d0f12; color: #f2f3f5; padding: 6px 34px 22px; }
.pur { background: linear-gradient(100deg, #4c1d95 0%, #8b5cf6 45%, #c084fc 70%, #5b21b6 100%); -webkit-background-clip: text; background-clip: text; color: transparent; padding: 0 20px .1em; }
.gold { background: linear-gradient(100deg, #9a6a1c 0%, #e9c27a 40%, #b8862f 70%, #f3d79a 100%); -webkit-background-clip: text; background-clip: text; color: transparent; padding: 0 20px .1em; }
#oval { background: radial-gradient(46% 11% at 50% 50%, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 92%, #000 100%); opacity: 0; }

/* world 3 – black neon */
#w3 { opacity: 0; }
#col { left: 0; top: 0; width: 1080px; }
.n { position: absolute; left: 0; width: 1080px; text-align: center; font-weight: 900; letter-spacing: -0.04em; line-height: 1; white-space: nowrap; opacity: 0; }
.ng { color: #ffe9b0; text-shadow: 0 0 4px #ffd36a, 0 0 18px #ffb21f, 0 0 46px rgba(255,150,10,.75), 0 0 110px rgba(255,120,0,.45); }
.nb { color: #d6ecff; text-shadow: 0 0 4px #8fd0ff, 0 0 18px #2f8cff, 0 0 46px rgba(30,110,255,.8), 0 0 110px rgba(20,80,255,.45); }
.nw { color: #ffffff; text-shadow: 0 0 4px #e9f1ff, 0 0 18px #9ec2ff, 0 0 46px rgba(120,160,255,.6); }
.ny { color: #fff6b8; text-shadow: 0 0 4px #ffef6a, 0 0 18px #ffd400, 0 0 46px rgba(255,200,0,.7), 0 0 110px rgba(255,180,0,.4); }
.nr { color: #ffd2cc; text-shadow: 0 0 4px #ff6a5a, 0 0 18px #ff2a1a, 0 0 46px rgba(255,30,10,.8), 0 0 110px rgba(255,0,0,.45); }
.bar { top: -100px; width: 86px; height: 2120px; border-radius: 43px;
       background: linear-gradient(90deg, #030405 0%, #1b1f25 22%, #5d6570 42%, #9aa3ae 48%, #3a4049 60%, #0e1014 82%, #030405 100%);
       box-shadow: 0 0 40px rgba(0,0,0,.9); filter: blur(2px); }

/* end – logo */
#logo { left: 240px; top: 600px; width: 600px; opacity: 0; }
#logo img { width: 100%; display: block; filter: drop-shadow(0 0 24px rgba(255,255,255,.25)); }
#dn { top: 1190px; font-size: 54px; font-weight: 300; color: #e9e6df; letter-spacing: 0; }
#mc { top: 1270px; font-size: 58px; font-weight: 500; color: #e3c27a; letter-spacing: 0; }
#mc .c { display: inline-block; opacity: 0; margin: 0 .18em; }
#mc .sp { display: inline-block; width: .6em; }
#cl { top: 1430px; font-size: 40px; font-weight: 500; line-height: 1.35; color: #bdb8ae; opacity: 0; letter-spacing: -0.01em; }
#hd { top: 1550px; font-size: 32px; font-weight: 500; color: #7f7a72; opacity: 0; letter-spacing: 0; }
.tc { position: absolute; left: 0; width: 1080px; text-align: center; white-space: nowrap; }
#black { background: #000; opacity: 0; }
#vig { background: radial-gradient(120% 85% at 50% 50%, rgba(0,0,0,0) 52%, rgba(0,0,0,.6) 100%); pointer-events: none; }
#grain { opacity: .06; mix-blend-mode: overlay; background: url(ui/grain.png); background-size: 256px; pointer-events: none; }
"""

BIO1 = ["In", "dir", "steckt", "mehr,"]
BIO2 = ["als", "du", "denkst."]
TILES = [("Mehr.", "#1d3fb8,#0a1650"), ("Fokus", "#2a2a2e,#0d0d10"), ("Mut", "#9a6a1c,#3a2408"),
         ("Glaube", "#0d0d10,#26324f"), ("Ziel", "#1f54f0,#0c1d6a"), ("Kraft", "#3a3a40,#121216"),
         ("Mindset", "#121216,#1d3fb8"), ("Team", "#5a4010,#151008"), ("Sieg", "#0b2a8e,#050a20")]
LETTERS = list("EinFunke")
ADV = {"E": .60, "i": .27, "n": .62, "F": .57, "u": .62, "k": .59, "e": .60}   # Inter Display Black, em


def phone():
    p = ["<div id='ph' class='abs'>",
         "<div class='abs stt'>9:41</div><div class='abs hdl'>kevin.nsimba</div>",
         "<div id='av' class='abs'><img src='ui/kn-logo.png' alt='' /></div>"]
    for i, (n, l) in enumerate([("214", "Beiträge"), ("52K", "Follower"), ("180", "Gefolgt")]):
        p.append(f"<div class='abs sn' style='left:{238 + i * 100}px'>{n}<small>{l}</small></div>")
    p.append("<div class='abs nm'>Kevin Nsimba</div><div class='abs rl'>Mental Coach · Fußball</div>")
    p.append("<div class='abs bio' style='top:440px'>" + " ".join(f"<span id='b{i}'>{w}</span>" for i, w in enumerate(BIO1)) + "</div>")
    p.append("<div class='abs bio' style='top:496px'>" + " ".join(f"<span id='b{i + 4}'>{w}</span>" for i, w in enumerate(BIO2)) + "</div>")
    p.append("<div class='abs btn' style='left:40px;width:228px;background:#2f6bff'>Folgen</div>")
    p.append("<div class='abs btn' style='left:280px;width:220px;background:#232a3b'>Nachricht</div>")
    for i, h in enumerate(["Mindset", "Fokus", "Training", "Erfolge"]):
        p.append(f"<div class='abs hl' style='left:{40 + i * 124}px'><i></i>{h}</div>")
    for i, (w, g) in enumerate(TILES):
        x, y = 4 + (i % 3) * 182, 846 + (i // 3) * 182
        p.append(f"<div class='abs tile' style='left:{x}px;top:{y}px;background:linear-gradient(150deg,{g})'>{w}</div>")
    p.append("</div>")
    return "".join(p)


def body():
    b = ["<div id='bg1' class='full'></div><div id='ghost' class='abs'>KEVIN<br>NSIMBA</div>",
         "<div id='cam' class='full'>" + phone() + "</div>"]
    for i, (w, h, y) in enumerate([(620, 150, 1150), (470, 112, 1170), (330, 80, 1186)]):
        b.append(f"<div class='abs ring' id='r{i}' style='top:{y}px;width:{w}px;height:{h}px;margin-left:-{w // 2}px'></div>")
    b.append("<div id='icon' class='abs'><img src='ui/kn-logo.png' alt='' /></div>")
    b.append("<div id='orbit' class='full'>" + "".join(
        f"<div class='abs lt{' gd' if i >= 3 else ''}' id='lt{i}'>{c}</div>" for i, c in enumerate(LETTERS)) + "</div>")
    b.append("<div id='flash' class='full'></div>")
    # world 2
    b.append("<div id='bg2' class='full'></div><div id='w2' class='full'>")
    b.append("<div class='abs k' id='k0' style='top:830px;font-size:230px'>" + "".join(f"<span class='c'>{c}</span>" for c in "Druck.") + "</div>")
    b.append("<div class='abs k' id='k1' style='top:1010px;font-size:170px'><span class='box'>Zweifel.</span></div>")
    b.append("<div class='abs k' id='k2' style='top:850px;font-size:280px'><span class='pur'>Angst.</span></div>")
    b.append("<div id='oval' class='full'></div>")
    b.append("<div class='abs k' id='k3' style='top:740px;font-size:170px'>Doch ein</div>")
    b.append("<div class='abs k' id='k4' style='top:900px;font-size:230px'><span class='gold'>Funke</span></div>")
    b.append("<div class='abs k' id='k5' style='top:1120px;font-size:170px'>genügt.</div>")
    b.append("</div>")
    # world 3
    b.append("<div id='w3' class='full'><div id='col' class='abs'>")
    for i, (w, cls, top, fs) in enumerate([("Potenzial", "ng", 860, 190), ("entfachen.", "nb", 1070, 130), ("Klarheit.", "nw", 1280, 160),
                                           ("Fokus.", "ny", 1480, 170), ("Stärke.", "nr", 1700, 200)]):
        b.append(f"<div class='n {cls}' id='n{i}' style='top:{top}px;font-size:{fs}px'>{w}</div>")
    b.append("</div>")
    for i in range(7):
        b.append(f"<div class='abs bar' id='bar{i}' style='left:{38 + i * 160}px'></div>")
    b.append("</div>")
    # end
    b.append("<div id='black' class='full'></div>")
    b.append("<div id='logo' class='abs'><img src='ui/kn-logo.png' alt='Kevin Nsimba' /></div>")
    b.append("<div id='dn' class='tc' style='opacity:0'>dein</div>")
    mc = "".join("<span class='sp'></span>" if c == " " else f"<span class='c'>{c}</span>" for c in "MENTAL COACH")
    b.append(f"<div id='mc' class='tc'>{mc}</div>")
    b.append("<div id='cl' class='tc'>Train the mind. <span style='color:#e3c27a'>Change the game.</span></div>")
    b.append("<div id='hd' class='tc'>@kevnsimba</div>")
    b.append("<div id='vig' class='full'></div><div id='grain' class='full'></div>")
    return "".join(b)


# flat target x for the orbit letters ("Ein Funke", centred)
FS = 140
adv = [ADV[c] * FS for c in LETTERS]
gap = 0.26 * FS
total = sum(adv) + gap
xs, x = [], -total / 2
for i, a in enumerate(adv):
    xs.append(x + a / 2); x += a + (gap if i == 2 else 0)

JS = f"""
const tl = gsap.timeline({{ paused: true }});
const FX = {json.dumps([round(v, 1) for v in xs])};
/* ---------- world 1: the camera flies over Kevin's profile ---------- */
gsap.set('#ph', {{ transformOrigin: '50% 50%', scale: 0.35, rotationY: -34, rotationX: 22, rotationZ: 8, y: 120, filter: 'blur(14px)' }});
gsap.set('.ring', {{ scale: 0.4 }});
gsap.set('.lt', {{ xPercent: -50, yPercent: -50 }});
tl.to('#ph', {{ scale: 0.66, rotationY: -22, rotationX: 16, rotationZ: 5, y: 40, filter: 'blur(0px)', duration: 0.5, ease: 'power3.out' }}, 0);
tl.to('#ph', {{ scale: 2.15, x: 150, y: 330, rotationY: -14, rotationX: 30, rotationZ: -7, duration: 0.5, ease: 'power2.inOut' }}, 0.5);
tl.to('#ph', {{ x: -40, y: 230, rotationY: 10, rotationX: 26, rotationZ: 5, scale: 2.35, duration: 1.05, ease: 'power1.inOut' }}, 1.02);
tl.to('#ph', {{ x: 480, y: 980, scale: 6.5, rotationY: 0, rotationX: 0, rotationZ: 0, filter: 'blur(8px)', duration: 0.3, ease: 'power3.in' }}, 2.08);
"""
for i, t in enumerate(T[:7]):
    JS += f"tl.to('#b{i}', {{ color: '{'#ffd98a' if i == 3 else '#ffffff'}', duration: 0.12 }}, {t:.2f});\n"
JS += f"""
tl.fromTo('#flash', {{ opacity: 0 }}, {{ opacity: 0.9, duration: 0.06 }}, 2.32);
tl.set(['#ph', '#cam'], {{ opacity: 0 }}, 2.38);
tl.to('#flash', {{ opacity: 0, duration: 0.3, ease: 'power2.out' }}, 2.38);
/* the profile picture becomes a glowing icon on rings of light */
tl.fromTo('#icon', {{ opacity: 0, scale: 2.4, filter: 'blur(16px)' }}, {{ opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.35, ease: 'expo.out' }}, 2.36);
tl.to('.ring', {{ opacity: 1, scale: 1, duration: 0.5, ease: 'expo.out', stagger: 0.06 }}, 2.4);
/* letters circle the icon in 3D, then line up as "Ein Funke" */
const O = {{ a: 0, m: 0, r: 330, s: 0 }};
const LT = gsap.utils.toArray('.lt');
function orbit() {{
  LT.forEach((el, i) => {{
    const th = O.a + i / LT.length * Math.PI * 2;
    const ox = O.r * Math.sin(th), oz = O.r * Math.cos(th), oy = 70 * Math.cos(th) - 40;
    const m = O.m;
    gsap.set(el, {{ x: ox * (1 - m) + FX[i] * m, y: oy * (1 - m) + 0 * m, z: oz * (1 - m),
                    rotationY: (th * 180 / Math.PI) * (1 - m), scale: O.s,
                    opacity: Math.min(1, O.s * 2) * ((1 - m) * (0.45 + 0.55 * (oz / O.r + 1) / 2) + m) }});
  }});
}}
tl.to(O, {{ a: Math.PI * 2.4, duration: 0.9, ease: 'power1.inOut', onUpdate: orbit }}, 2.42);
tl.to(O, {{ s: 1, duration: 0.3, ease: 'power2.out', onUpdate: orbit }}, 2.42);
tl.to('#icon', {{ rotationY: 360, duration: 0.55, ease: 'power2.inOut' }}, 2.42);
tl.to('#icon', {{ scale: 0.5, duration: 0.25, ease: 'power2.inOut' }}, 2.72);
tl.to(O, {{ m: 1, duration: 0.3, ease: 'power3.inOut', onUpdate: orbit }}, 2.95);
tl.to(['#icon', '.ring'], {{ opacity: 0, scale: 0.2, duration: 0.25, ease: 'power3.in' }}, 2.98);
tl.to(['#orbit', '#bg1', '#ghost'], {{ scale: 0.15, opacity: 0, filter: 'blur(10px)', duration: 0.2, ease: 'power3.in' }}, {W2 - 0.2:.2f});

/* ---------- world 2: grey spotlight, words tilted in 3D ---------- */
tl.set('#bg2', {{ opacity: 1 }}, {W2:.2f});
tl.set('#k0', {{ opacity: 1, rotationY: -26, rotationZ: -7 }}, {W2:.2f});
tl.fromTo('#k0 .c', {{ y: -260, rotationX: -90, opacity: 0, filter: 'blur(10px)' }}, {{ y: 0, rotationX: 0, opacity: 1, filter: 'blur(0px)', duration: 0.32, ease: 'back.out(1.6)', stagger: 0.035 }}, {T[9] - 0.1:.2f});
tl.fromTo('#k1', {{ opacity: 0, x: 700, rotationY: 40, rotationZ: -4, filter: 'blur(14px)' }}, {{ opacity: 1, x: 0, rotationY: 16, rotationZ: -4, filter: 'blur(0px)', duration: 0.32, ease: 'power3.out' }}, {T[10] - 0.12:.2f});
tl.to('#k0', {{ y: -230, rotationY: -18, filter: 'blur(2px)', opacity: 0.8, duration: 0.32, ease: 'power3.out' }}, {T[10] - 0.12:.2f});
tl.to(['#k0', '#k1'], {{ y: '-=700', opacity: 0, filter: 'blur(14px)', duration: 0.28, ease: 'power3.in' }}, {T[11] - 0.26:.2f});
tl.fromTo('#k2', {{ opacity: 0, x: -900, rotationY: -35, filter: 'blur(18px)' }}, {{ opacity: 1, x: 0, rotationY: -8, filter: 'blur(0px)', duration: 0.34, ease: 'power3.out' }}, {T[11] - 0.1:.2f});
tl.to('#oval', {{ opacity: 1, duration: 0.25, ease: 'power2.out' }}, {T[11] + 0.38:.2f});
tl.to('#k2', {{ rotationY: 6, duration: 0.9, ease: 'none' }}, {T[11] + 0.24:.2f});
tl.to('#k2', {{ opacity: 0, x: 900, filter: 'blur(18px)', duration: 0.25, ease: 'power3.in' }}, {T[12] - 0.22:.2f});
tl.to('#oval', {{ opacity: 0, duration: 0.25 }}, {T[12] - 0.15:.2f});
tl.fromTo('#k3', {{ opacity: 0, x: -600, rotationY: -30, rotationZ: 4, filter: 'blur(14px)' }}, {{ opacity: 1, x: 0, rotationY: -14, rotationZ: 4, filter: 'blur(0px)', duration: 0.3, ease: 'power3.out' }}, {T[12] - 0.06:.2f});
tl.fromTo('#k4', {{ opacity: 0, x: 600, rotationY: 30, rotationZ: -3, filter: 'blur(14px)' }}, {{ opacity: 1, x: 0, rotationY: 10, rotationZ: -3, filter: 'blur(0px)', duration: 0.3, ease: 'power3.out' }}, {T[14] - 0.08:.2f});
tl.fromTo('#k5', {{ opacity: 0, y: 160, rotationX: -50, filter: 'blur(14px)' }}, {{ opacity: 1, y: 0, rotationX: 0, filter: 'blur(0px)', duration: 0.3, ease: 'power3.out' }}, {T[15] - 0.08:.2f});
/* dramatic pause */
tl.set('#black', {{ opacity: 1 }}, 7.88);

/* ---------- world 3: neon on black ---------- */
tl.set(['#bg2', '#w2'], {{ opacity: 0 }}, {W3:.2f});
tl.set('#w3', {{ opacity: 1 }}, {W3:.2f});
tl.set('#black', {{ opacity: 0 }}, {W3:.2f});
tl.fromTo('#n0', {{ opacity: 0, scale: 0.6, filter: 'blur(24px)' }}, {{ opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.45, ease: 'expo.out' }}, {W3:.2f});
tl.to('#n0', {{ keyframes: [{{ opacity: 0.35, duration: 0.04 }}, {{ opacity: 1, duration: 0.05 }}, {{ opacity: 0.55, duration: 0.04 }}, {{ opacity: 1, duration: 0.06 }}] }}, {W3 + 0.45:.2f});
tl.fromTo('#n1', {{ opacity: 0, y: 120, filter: 'blur(16px)' }}, {{ opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.32, ease: 'power3.out' }}, {T[17] - 0.06:.2f});
"""
for i, (t, y) in enumerate([(T[18], -330), (T[19], -530), (T[20], -760)]):
    JS += f"tl.to('#col', {{ y: {y}, duration: 0.32, ease: 'power3.inOut' }}, {t - 0.2:.2f});\n"
    JS += f"tl.to('#n{i}', {{ opacity: 0.25, filter: 'blur(4px)', duration: 0.3 }}, {t - 0.2:.2f});\n"
    if i > 0:
        JS += f"tl.to('#n{i + 1}', {{ opacity: 0.3, filter: 'blur(3px)', duration: 0.3 }}, {t - 0.2:.2f});\n"
    JS += f"tl.fromTo('#n{i + 2}', {{ opacity: 0, filter: 'blur(18px)', scale: 0.85 }}, {{ opacity: 1, filter: 'blur(0px)', scale: 1, duration: 0.3, ease: 'expo.out' }}, {t - 0.06:.2f});\n"
    JS += f"tl.to('#n{i + 2}', {{ keyframes: [{{ opacity: 0.4, duration: 0.03 }}, {{ opacity: 1, duration: 0.05 }}] }}, {t + 0.26:.2f});\n"
JS += f"tl.to(['#n0', '#n1'], {{ opacity: 0, duration: 0.3 }}, {T[20] - 0.2:.2f});\n"
for i in range(7):
    JS += f"tl.fromTo('#bar{i}', {{ y: -2200 }}, {{ y: 0, duration: 0.22, ease: 'power4.in' }}, {11.86 + abs(i - 3) * 0.025:.3f});\n"
for i in range(7):
    d = i - 3
    JS += (f"tl.to('#bar{i}', {{ x: {d * 260 if d else 0}, rotation: {d * 7}, scaleY: {1.0 if d else 1.0}, opacity: 0, "
           f"filter: 'blur(14px)', duration: 0.35, ease: 'power3.in' }}, {W4 - 0.32:.2f});\n")
JS += f"""
tl.to('#n4', {{ scale: 1.25, opacity: 0, filter: 'blur(20px)', duration: 0.32, ease: 'power3.in' }}, {W4 - 0.32:.2f});
tl.to(['#n2', '#n3'], {{ opacity: 0, duration: 0.25 }}, {W4 - 0.32:.2f});

/* ---------- end: the logo comes into focus ---------- */
tl.set('#w3', {{ opacity: 0 }}, {W4:.2f});
tl.fromTo('#logo', {{ opacity: 0, scale: 1.12, filter: 'blur(30px)' }}, {{ opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.9, ease: 'expo.out' }}, {T[21] - 0.1:.2f});
tl.fromTo('#dn', {{ opacity: 0, y: 20, filter: 'blur(8px)' }}, {{ opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.35, ease: 'power3.out' }}, {T[23] - 0.05:.2f});
tl.fromTo('#mc .c', {{ opacity: 0, filter: 'blur(10px)', y: 14 }}, {{ opacity: 1, filter: 'blur(0px)', y: 0, duration: 0.3, ease: 'power3.out', stagger: 0.055 }}, {T[24] - 0.05:.2f});
tl.fromTo('#cl', {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: 'power3.out' }}, 15.3);
tl.fromTo('#hd', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.45 }}, 15.8);
tl.to(['#logo', '#dn', '#mc', '#cl', '#hd'], {{ opacity: 0, filter: 'blur(14px)', duration: 0.5, ease: 'power2.in' }}, 17.2);
tl.to(['#bg1', '#ghost'], {{ opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.5, ease: 'power2.out' }}, 17.5);
window.__timelines = window.__timelines || {{}}; window.__timelines['main'] = tl;
"""

html = ("<!doctype html><html lang='de'><head><meta charset='UTF-8' /><meta name='viewport' content='width=1080, height=1920' />"
        "<script src='ui/gsap.min.js'></script><style>" + CSS + "</style></head><body>"
        f"<div id='root' data-composition-id='main' data-start='0' data-duration='{DUR}' data-fps='30' data-width='1080' data-height='1920'>"
        f"<div id='stage' class='clip' data-start='0' data-duration='{DUR}' data-track-index='1'>" + body() + "</div></div>"
        "<script>" + JS + "</script></body></html>")
(HERE / "index.html").write_text(html)
print("ok")
