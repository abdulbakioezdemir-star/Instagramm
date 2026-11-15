"""Kevin Nsimba – Slate-Referenz eins zu eins (ohne Stimme), mit Kevins echten Beiträgen.
World 1  deep blue: floating 3D phone with Kevin's profile, posts lift off the screen, camera skims the bio,
         the profile picture lifts off as a glowing icon over rings of light, shrinks into a spinning cube, letters orbit.
World 2  grey spotlight: "Jeder / Fußballer / hat Grenzen." (oval spotlight) "Doch nicht jeder wird aufgehalten."
World 3  black neon: Klarheit / Fokus / Leistung / Grenzen sind im Kopf. – bars slam down and break.
End      logo out of focus into focus, M E N T A L  C O A C H.
All cuts sit on the beat grid of tools/beat.py.  Writes index.html."""
import json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BEAT = 2.65 / 6
T0 = 5.85 - 13 * BEAT
def b(n): return round(T0 + n * BEAT, 3)
DUR = 14.4
PERSP = 2000

def center(dx, dy, s, rx, ry, rz):
    """translation that puts local point (dx,dy) (offset from phone centre) at the screen centre"""
    x, y, z = dx * s, dy * s, 0.0
    a = math.radians(rx); y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
    a = math.radians(ry); x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    a = math.radians(rz); x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return round(-x), round(-y)

# phone: 560 x 1140, local centre (280, 570)
AV = (36 + 84, 130 + 84)               # avatar centre in phone coords
def off(p): return (p[0] - 280, p[1] - 570)

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

/* ---------- world 1 ---------- */
#bg1 { background: radial-gradient(70% 50% at 50% 46%, #1d4cf0 0%, #0b2299 36%, #050e48 68%, #010312 100%); }
#rows { left: 0; top: 0; width: 1080px; height: 1920px; opacity: 0; }
.row { position: absolute; left: -400px; width: 1880px; text-align: center; font-size: 230px; font-weight: 900; letter-spacing: -0.03em; line-height: 1;
       color: transparent; -webkit-text-stroke: 2px rgba(150,185,255,.09); white-space: nowrap; }
.dust { width: 6px; height: 6px; border-radius: 50%; background: rgba(170,200,255,.55); filter: blur(1px); }
#cam { perspective: %PERSP%px; perspective-origin: 540px 960px; }
#ph { left: 260px; top: 390px; width: 560px; height: 1140px; transform-style: preserve-3d; }
#pbody { left: -10px; top: -10px; width: 580px; height: 1160px; border-radius: 86px; background: #10131c; border: 3px solid #2c3446;
         box-shadow: 0 50px 140px rgba(0,8,50,.85), 0 0 160px rgba(60,110,255,.35); }
#scr { left: 0; top: 0; width: 560px; height: 1140px; border-radius: 76px; background: #0b0d13; overflow: hidden; }
#scr .abs { position: absolute; }
.stt { left: 48px; top: 26px; font-size: 22px; font-weight: 600; color: #eef1f7; }
.isl { left: 205px; top: 20px; width: 150px; height: 40px; border-radius: 20px; background: #000; }
.hdl { left: 36px; top: 76px; font-size: 34px; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
.hdl i { display: inline-block; width: 22px; height: 22px; margin-left: 8px; border-radius: 50%; background: #3897f0; vertical-align: 2px; }
.ico { top: 80px; width: 30px; height: 30px; border: 3px solid #fff; border-radius: 8px; }
#sock { left: 36px; top: 130px; width: 168px; height: 168px; border-radius: 50%; background: radial-gradient(circle, #05070c 55%, #0e1424 100%); box-shadow: inset 0 0 0 3px #1b2236; }
.sn { top: 168px; width: 100px; text-align: center; color: #fff; font-size: 30px; font-weight: 700; line-height: 1.15; }
.sn small { display: block; font-size: 18px; font-weight: 500; color: #b5bccb; }
.nm { left: 36px; top: 318px; font-size: 27px; font-weight: 700; color: #fff; }
.cat { left: 36px; top: 354px; font-size: 22px; font-weight: 500; color: #8d96aa; }
.bio { left: 36px; font-size: 24px; font-weight: 500; color: #e4e8f1; white-space: nowrap; }
.lnk { left: 36px; top: 456px; font-size: 22px; font-weight: 600; color: #a9c4ff; }
.btn { top: 500px; height: 56px; border-radius: 14px; font-size: 22px; font-weight: 600; color: #fff; display: flex; align-items: center; justify-content: center; background: #252c3d; }
.hl { top: 580px; width: 96px; text-align: center; font-size: 16px; font-weight: 500; color: #cfd5e2; }
.hl img { display: block; width: 92px; height: 92px; border-radius: 50%; object-fit: cover; margin: 0 auto 8px; border: 3px solid #0b0d13; box-shadow: 0 0 0 2px #39415a; }
.tab { top: 712px; height: 40px; width: 186px; display: flex; justify-content: center; }
.tab b { width: 30px; height: 30px; border: 3px solid #fff; border-radius: 4px; }
.tabl { left: 0; top: 750px; width: 186px; height: 3px; background: #fff; }
#spec { left: -300px; top: -200px; width: 260px; height: 1600px; background: linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,.12), rgba(255,255,255,0)); }
.tile { width: 184px; height: 182px; overflow: hidden; background: #111; box-shadow: 0 20px 40px rgba(0,0,0,.55); }
.tile img { width: 100%; height: 100%; object-fit: cover; display: block; }
#avd { left: 36px; top: 130px; width: 168px; height: 168px; border-radius: 84px; background: radial-gradient(circle at 40% 30%, #1a1d26, #040507 70%);
       box-shadow: 0 0 0 4px #d6ad62, 0 0 30px rgba(214,173,98,.45); display: flex; align-items: center; justify-content: center; }
#avd img { width: 128px; }
.ring { border-radius: 50%; border: 4px solid rgba(110,165,255,.95); box-shadow: 0 0 22px rgba(80,140,255,.95), inset 0 0 22px rgba(80,140,255,.7); opacity: 0; }
#cubew { left: 540px; top: 960px; width: 0; height: 0; perspective: 1100px; }
#cube { left: -110px; top: -110px; width: 220px; height: 220px; transform-style: preserve-3d; opacity: 0; }
.face { position: absolute; width: 220px; height: 220px; border-radius: 30px; background: linear-gradient(150deg, #1b2440, #070a14 70%);
        box-shadow: inset 0 0 0 3px rgba(120,170,255,.8), 0 0 40px rgba(60,120,255,.6); display: flex; align-items: center; justify-content: center; }
.face img { width: 160px; }
#orbit { perspective: 1100px; perspective-origin: 540px 960px; }
.lt { left: 540px; top: 960px; font-size: 130px; font-weight: 900; color: #fff; line-height: 1; text-shadow: 0 0 26px rgba(120,170,255,.9); opacity: 0; }
#sliver { left: 538px; top: 760px; width: 4px; height: 400px; background: #dbe7ff; box-shadow: 0 0 30px 8px rgba(120,170,255,.9); opacity: 0; }

/* ---------- world 2 ---------- */
#bg2 { background: radial-gradient(68% 48% at 50% 50%, #f4f6f8 0%, #d6dade 45%, #9da3aa 80%, #6e747b 100%); opacity: 0; }
#w2 { perspective: 1300px; perspective-origin: 540px 960px; }
.k { left: 0; width: 1080px; text-align: center; font-weight: 900; color: #2a2f36; letter-spacing: -0.045em; line-height: 1.05; white-space: nowrap; opacity: 0; }
.k .c { display: inline-block; }
.box { display: inline-block; background: #0d0f12; color: #f2f3f5; padding: 4px 34px 22px; }
.gold { background: linear-gradient(100deg, #8a5a14 0%, #e2b867 35%, #f6dca2 50%, #b8862f 75%, #7a4f10 100%); -webkit-background-clip: text; background-clip: text; color: transparent; padding: 0 24px .12em; }
#oval { background: radial-gradient(48% 10% at 50% 50.5%, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 90%, #000 100%); opacity: 0; }

/* ---------- world 3 ---------- */
#w3 { opacity: 0; }
#col { left: 0; top: 0; width: 1080px; }
.n { position: absolute; left: 0; width: 1080px; text-align: center; font-weight: 900; letter-spacing: -0.04em; line-height: 1; white-space: nowrap; opacity: 0; }
.nb { color: #dceeff; text-shadow: 0 0 4px #8fd0ff, 0 0 18px #2f8cff, 0 0 46px rgba(30,110,255,.85), 0 0 110px rgba(20,80,255,.45); }
.ny { color: #fff6bd; text-shadow: 0 0 4px #ffef6a, 0 0 18px #ffd400, 0 0 46px rgba(255,200,0,.75), 0 0 110px rgba(255,180,0,.4); }
.ng { color: #ffe9b0; text-shadow: 0 0 4px #ffd36a, 0 0 18px #ffb21f, 0 0 46px rgba(255,150,10,.75), 0 0 110px rgba(255,120,0,.45); }
.nr { color: #ffd4ce; text-shadow: 0 0 4px #ff6a5a, 0 0 18px #ff2a1a, 0 0 46px rgba(255,30,10,.85), 0 0 110px rgba(255,0,0,.45); }
.gl { color: transparent; text-shadow: none; }
#g1 { color: rgba(0,230,255,.75); } #g2 { color: rgba(255,40,120,.75); }
.bar { top: -100px; height: 2120px;
       background: linear-gradient(90deg, #020304 0%, #161a20 20%, #4f5762 40%, #a3acb7 47%, #39404a 58%, #0d0f13 80%, #020304 100%); box-shadow: 0 0 50px rgba(0,0,0,.95); }

/* ---------- end ---------- */
#logo { left: 250px; top: 610px; width: 580px; opacity: 0; }
#logo img { width: 100%; display: block; filter: drop-shadow(0 0 26px rgba(255,255,255,.22)); }
.tc { position: absolute; left: 0; width: 1080px; text-align: center; white-space: nowrap; }
#mc { top: 1170px; font-size: 54px; font-weight: 500; color: #e3c27a; }
#mc .c { display: inline-block; opacity: 0; margin: 0 .2em; }
#mc .sp { display: inline-block; width: .6em; }
#hd { top: 1290px; font-size: 32px; font-weight: 500; color: #8a857c; opacity: 0; }
#black { background: #000; opacity: 0; }
#vig { background: radial-gradient(120% 85% at 50% 50%, rgba(0,0,0,0) 54%, rgba(0,0,0,.55) 100%); pointer-events: none; }
#grain { opacity: .06; mix-blend-mode: overlay; background: url(ui/grain.png); background-size: 256px; pointer-events: none; }
""".replace("%PERSP%", str(PERSP))

TILES = ["suit", "restaurant", "mentale", "player", "sp", "amator"]
HL = [("player", "Coaching"), ("mentale", "Mindset"), ("sp", "Partner"), ("wedding", "Familie")]
ORB = list("MINDSET")
DUST = [((i * 397) % 1040 + 20, (i * 613) % 1880 + 20, 0.4 + (i * 37 % 60) / 100) for i in range(22)]

def phone():
    s = ["<div id='ph' class='abs'><div id='pbody' class='abs'></div><div id='scr' class='abs'>",
         "<div class='abs isl'></div><div class='abs stt'>9:41</div>",
         "<div class='abs hdl'>kevnsimba<i></i></div>",
         "<div class='abs ico' style='left:430px'></div><div class='abs ico' style='left:482px;border-radius:50%'></div>",
         "<div id='sock' class='abs'></div>"]
    for i, (n, l) in enumerate([("214", "Beiträge"), ("4.812", "Follower"), ("512", "Gefolgt")]):
        s.append(f"<div class='abs sn' style='left:{226 + i * 108}px'>{n}<small>{l}</small></div>")
    s += ["<div class='abs nm'>Kevin Nsimba</div><div class='abs cat'>Mental Coach · München</div>",
          "<div class='abs bio' style='top:388px'>Mentale Stärke im Fußball ⚽</div>",
          "<div class='abs bio' style='top:420px'>Klarheit · Fokus · Leistung</div>",
          "<div class='abs lnk'>S&amp;P Football Group</div>",
          "<div class='abs btn' style='left:36px;width:200px;background:#2f6bff'>Folgen</div>",
          "<div class='abs btn' style='left:246px;width:200px'>Nachricht</div>",
          "<div class='abs btn' style='left:456px;width:68px'>+</div>"]
    for i, (img, l) in enumerate(HL):
        s.append(f"<div class='abs hl' style='left:{30 + i * 118}px'><img src='ui/posts/{img}.jpg' alt='' />{l}</div>")
    for i in range(3):
        s.append(f"<div class='abs tab' style='left:{i * 187}px'><b style='{'' if i == 0 else 'opacity:.5;'}{'border-radius:50%;' if i == 2 else ''}'></b></div>")
    s.append("<div class='abs tabl'></div><div id='spec' class='abs'></div></div>")
    for i, n in enumerate(TILES):
        x, y = (i % 3) * 188, 758 + (i // 3) * 186
        s.append(f"<div class='abs tile' id='t{i}' style='left:{x}px;top:{y}px'><img src='ui/posts/{n}.jpg' alt='' /></div>")
    for i, d in enumerate((220, 310, 400)):
        s.append(f"<div class='abs ring' id='r{i}' style='left:{AV[0] - d // 2}px;top:{AV[1] - d // 2}px;width:{d}px;height:{d}px'></div>")
    s.append("<div id='avd' class='abs'><img src='ui/kn-gold.png' alt='' /></div></div>")
    return "".join(s)

def body():
    o = ["<div id='bg1' class='full'></div><div id='rows' class='abs'>"]
    for i in range(7):
        o.append(f"<div class='row' style='top:{120 + i * 250}px'>MINDSET MINDSET</div>")
    o.append("</div>")
    for i, (x, y, sc) in enumerate(DUST):
        o.append(f"<div class='abs dust' id='d{i}' style='left:{x}px;top:{y}px;opacity:{sc:.2f}'></div>")
    o.append("<div id='cam' class='full'>" + phone() + "</div>")
    faces = [("0", "0"), ("90", "0"), ("180", "0"), ("-90", "0")]
    cube = "".join(f"<div class='face' style='transform:rotateY({ry}deg) translateZ(110px)'><img src='ui/kn-gold.png' alt='' /></div>" for ry, _ in faces)
    cube += "<div class='face' style='transform:rotateX(90deg) translateZ(110px)'></div><div class='face' style='transform:rotateX(-90deg) translateZ(110px)'></div>"
    o.append(f"<div id='cubew' class='abs'><div id='cube' class='abs'>{cube}</div></div>")
    o.append("<div id='orbit' class='full'>" + "".join(f"<div class='abs lt' id='lt{i}'>{c}</div>" for i, c in enumerate(ORB)) + "</div>")
    o.append("<div id='sliver' class='abs'></div>")
    # world 2
    o.append("<div id='bg2' class='full'></div><div id='w2' class='full'>")
    o.append("<div class='abs k' id='k0' style='top:780px;font-size:250px'>" + "".join(f"<span class='c'>{c}</span>" for c in "Jeder") + "</div>")
    o.append("<div class='abs k' id='k1' style='top:1010px;font-size:150px'><span class='box'>Fußballer</span></div>")
    o.append("<div class='abs k' id='k2' style='top:700px;font-size:150px'>hat</div>")
    o.append("<div class='abs k' id='k3' style='top:860px;font-size:230px'><span class='gold'>Grenzen.</span></div>")
    o.append("<div id='oval' class='full'></div>")
    o.append("<div class='abs k' id='k4' style='top:720px;font-size:150px'>Doch nicht</div>")
    o.append("<div class='abs k' id='k5' style='top:870px;font-size:240px'>jeder</div>")
    o.append("<div class='abs k' id='k6' style='top:1130px;font-size:100px'>wird aufgehalten.</div>")
    o.append("</div>")
    # world 3
    o.append("<div id='w3' class='full'><div id='col' class='abs'>")
    for i, (w, cls, top, fs) in enumerate([("Klarheit.", "nb", 860, 175), ("Fokus.", "ny", 1070, 185), ("Leistung.", "ng", 1280, 175),
                                           ("Grenzen sind", "nr", 1520, 150), ("im Kopf.", "nr", 1700, 200)]):
        o.append(f"<div class='n {cls}' id='n{i}' style='top:{top}px;font-size:{fs}px'>{w}</div>")
    o.append("<div class='n gl' id='g1' style='top:1520px;font-size:150px'>Grenzen sind</div>")
    o.append("<div class='n gl' id='g2' style='top:1520px;font-size:150px'>Grenzen sind</div>")
    o.append("</div>")
    for i, (x, w, bl) in enumerate([(-60, 190, 10), (150, 120, 5), (330, 92, 2), (494, 92, 0), (658, 92, 2), (810, 120, 5), (950, 190, 10)]):
        o.append(f"<div class='abs bar' id='bar{i}' style='left:{x}px;width:{w}px;border-radius:{w // 2}px;filter:blur({bl}px)'></div>")
    o.append("</div>")
    # end
    o.append("<div id='black' class='full'></div>")
    o.append("<div id='logo' class='abs'><img src='ui/kn-logo.png' alt='Kevin Nsimba' /></div>")
    mc = "".join("<span class='sp'></span>" if c == " " else f"<span class='c'>{c}</span>" for c in "MENTAL COACH")
    o.append(f"<div id='mc' class='tc'>{mc}</div><div id='hd' class='tc'>@kevnsimba</div>")
    o.append("<div id='vig' class='full'></div><div id='grain' class='full'></div>")
    return "".join(o)

# ------------------------------------------------------------------ camera keyframes
def cam(s, rx, ry, rz, focus=(0, 0), extra=(0, 0)):
    x, y = center(focus[0], focus[1], s, rx, ry, rz)
    return f"scale: {s}, rotationX: {rx}, rotationY: {ry}, rotationZ: {rz}, x: {x + extra[0]}, y: {y + extra[1]}"

AVO = off(AV)
K0 = cam(0.5, 16, -30, 7, (0, 0), (0, 40))
K1 = cam(0.64, 14, -14, 4, (0, 0), (0, 20))
K2 = cam(1.15, 50, -18, -10, (-30, 260))
K3a = cam(2.3, 40, 0, -18, (180, -150))
K3b = cam(2.45, 38, 2, -16, (-150, -130))
K4 = cam(3.0, 34, 0, -14, AVO)
K5 = cam(2.2, 62, 0, -8, AVO, (120, 160))
K6 = cam(0.14, 62, 0, -8, AVO, (0, 0))

JS = f"""
const tl = gsap.timeline({{ paused: true }});
gsap.set('#ph', {{ transformOrigin: '50% 50%', {K0} }});
gsap.set('#cam', {{ filter: 'blur(14px)' }});
gsap.set('.ring', {{ scale: 0.3 }});
gsap.set('.lt', {{ xPercent: -50, yPercent: -50 }});
gsap.set('#spec', {{ rotation: 18 }});
/* floating dust, drifting upward the whole time */
gsap.utils.toArray('.dust').forEach((d, i) => {{ tl.fromTo(d, {{ y: 0 }}, {{ y: -260 - (i % 5) * 60, duration: {DUR}, ease: 'none' }}, 0); }});

/* ---- world 1: the floating phone ---- */
tl.to('#ph', {{ {K1}, duration: {b(1):.3f}, ease: 'power3.out' }}, 0);
tl.to('#cam', {{ filter: 'blur(0px)', duration: 0.45, ease: 'power2.out' }}, 0);
tl.fromTo('#spec', {{ x: 0 }}, {{ x: 900, duration: 1.0, ease: 'power2.inOut' }}, 0.1);
tl.to('#ph', {{ {K2}, duration: {b(3) - b(1):.3f}, ease: 'power2.inOut' }}, {b(1)});
"""
for i in range(6):
    z = 150 + (i * 53) % 120
    JS += f"tl.fromTo('#t{i}', {{ z: 0, rotationX: 0 }}, {{ z: {z}, rotationX: {-8 + (i % 3) * 6}, duration: 0.42, ease: 'back.out(1.6)' }}, {b(1) + 0.05 + i * 0.045:.3f});\n"
    JS += f"tl.to('#t{i}', {{ z: {z + 30}, duration: 0.2, ease: 'sine.inOut' }}, {b(1) + 0.5 + i * 0.045:.3f});\n"
    JS += f"tl.to('#t{i}', {{ z: 0, rotationX: 0, duration: 0.3, ease: 'power3.in' }}, {b(3) - 0.12 + i * 0.045:.3f});\n"
JS += f"""
/* camera skims over the bio */
tl.fromTo('#ph', {{ {K3a} }}, {{ {K3b}, duration: {b(4.5) - b(3):.3f}, ease: 'power2.out', immediateRender: false }}, {b(3)});
tl.fromTo('#cam', {{ filter: 'blur(8px)' }}, {{ filter: 'blur(0px)', duration: 0.3, ease: 'power2.out', immediateRender: false }}, {b(3)});
/* the profile picture */
tl.to('#ph', {{ {K4}, duration: {b(6) - b(4.5):.3f}, ease: 'power2.inOut' }}, {b(4.5)});
tl.to('#ph', {{ {K5}, duration: {b(8) - b(6):.3f}, ease: 'power2.inOut' }}, {b(6)});
tl.to('#avd', {{ z: 230, rotationX: -62, borderRadius: 46, duration: 0.6, ease: 'power3.out' }}, {b(6)});
tl.to('.ring', {{ opacity: 1, scale: 1, duration: 0.5, ease: 'expo.out', stagger: 0.07 }}, {b(6) + 0.05:.3f});
tl.to('#avd', {{ z: 260, duration: 0.5, ease: 'sine.inOut' }}, {b(6) + 0.6:.3f});
/* everything falls away, only the icon stays → becomes the cube */
tl.to('#ph', {{ {K6}, duration: {b(9) - b(8):.3f}, ease: 'power3.in' }}, {b(8)});
tl.to(['#pbody', '#scr', '.tile', '.ring'], {{ opacity: 0, duration: 0.3 }}, {b(8) + 0.05:.3f});
tl.set('#ph', {{ opacity: 0 }}, {b(9)});
tl.fromTo('#cube', {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: 'expo.out' }}, {b(9) - 0.05:.3f});
tl.fromTo('#cube', {{ rotationY: -30, rotationX: -14 }}, {{ rotationY: 330, rotationX: -14, duration: {b(12.5) - b(9):.3f}, ease: 'none' }}, {b(9) - 0.05:.3f});
tl.fromTo('#rows', {{ opacity: 0, x: 0 }}, {{ opacity: 1, x: -260, duration: {b(13) - b(9):.3f}, ease: 'none' }}, {b(9) - 0.05:.3f});
const O = {{ a: 0, m: 0, s: 0 }};
const LT = gsap.utils.toArray('.lt');
function orbit() {{
  LT.forEach((el, i) => {{
    const th = O.a + i / LT.length * Math.PI * 2, r = 330 * (1 - O.m);
    const oz = r * Math.cos(th);
    gsap.set(el, {{ x: r * Math.sin(th), y: 60 * Math.cos(th) * (1 - O.m), z: oz, rotationY: th * 180 / Math.PI,
                    scale: O.s * (1 - 0.9 * O.m), opacity: Math.min(1, O.s * 2) * (1 - O.m) * (0.4 + 0.6 * (Math.cos(th) + 1) / 2) }});
  }});
}}
tl.to(O, {{ s: 1, duration: 0.3, ease: 'power2.out', onUpdate: orbit }}, {b(9) + 0.1:.3f});
tl.to(O, {{ a: Math.PI * 3, duration: {b(12) - b(9):.3f}, ease: 'none', onUpdate: orbit }}, {b(9) + 0.1:.3f});
tl.to(O, {{ m: 1, duration: 0.35, ease: 'power3.in', onUpdate: orbit }}, {b(12):.3f});
tl.to('#cube', {{ scaleX: 0.02, scaleY: 1.2, duration: 0.25, ease: 'power3.in' }}, {b(12.5) - 0.02:.3f});
tl.fromTo('#sliver', {{ opacity: 0, scaleY: 0.4 }}, {{ opacity: 1, scaleY: 1.4, duration: 0.15 }}, {b(12.5) + 0.2:.3f});
tl.set(['#bg1', '#rows', '.dust', '#sliver', '#cube', '#cubew'], {{ opacity: 0 }}, {b(13)});

/* ---- world 2: grey spotlight ---- */
tl.set('#bg2', {{ opacity: 1 }}, {b(13)});
tl.set('#k0', {{ opacity: 1, rotationY: -24, rotationZ: -9 }}, {b(13)});
tl.fromTo('#k0 .c', {{ y: -280, rotationX: -95, opacity: 0, filter: 'blur(12px)' }}, {{ y: 0, rotationX: 0, opacity: 1, filter: 'blur(0px)', duration: 0.3, ease: 'back.out(1.5)', stagger: 0.04 }}, {b(13) - 0.04:.3f});
tl.to('#k0', {{ y: -240, x: -60, filter: 'blur(2px)', duration: 0.3, ease: 'power3.out' }}, {b(14) - 0.08:.3f});
tl.fromTo('#k1', {{ opacity: 0, x: 760, rotationY: 45, rotationZ: -5, filter: 'blur(16px)' }}, {{ opacity: 1, x: 0, rotationY: 14, rotationZ: -5, filter: 'blur(0px)', duration: 0.3, ease: 'power3.out' }}, {b(14) - 0.08:.3f});
tl.to(['#k0', '#k1'], {{ y: '-=760', opacity: 0, filter: 'blur(16px)', duration: 0.24, ease: 'power3.in' }}, {b(15) - 0.2:.3f});
tl.fromTo('#k2', {{ opacity: 0, y: 140, rotationX: -60, filter: 'blur(10px)' }}, {{ opacity: 1, y: 0, rotationX: 0, filter: 'blur(0px)', duration: 0.24, ease: 'power3.out' }}, {b(15) - 0.04:.3f});
tl.fromTo('#k3', {{ opacity: 0, x: -950, rotationY: -40, filter: 'blur(20px)' }}, {{ opacity: 1, x: 0, rotationY: -10, filter: 'blur(0px)', duration: 0.3, ease: 'power3.out' }}, {b(15.5) - 0.06:.3f});
tl.to('#k2', {{ opacity: 0, y: -80, filter: 'blur(10px)', duration: 0.18 }}, {b(16) - 0.1:.3f});
tl.set('#oval', {{ opacity: 1 }}, {b(16)});
tl.to('#k3', {{ rotationY: 8, duration: {b(17) - b(15.5):.3f}, ease: 'none' }}, {b(15.5) + 0.24:.3f});
tl.set('#oval', {{ opacity: 0 }}, {b(17) - 0.02:.3f});
tl.to('#k3', {{ opacity: 0, x: 950, filter: 'blur(20px)', duration: 0.2, ease: 'power3.in' }}, {b(17) - 0.16:.3f});
tl.fromTo('#k4', {{ opacity: 0, x: -640, rotationY: -32, rotationZ: 5, filter: 'blur(16px)' }}, {{ opacity: 1, x: 0, rotationY: -14, rotationZ: 5, filter: 'blur(0px)', duration: 0.26, ease: 'power3.out' }}, {b(17) - 0.04:.3f});
tl.fromTo('#k5', {{ opacity: 0, x: 640, rotationY: 32, rotationZ: -4, filter: 'blur(16px)' }}, {{ opacity: 1, x: 0, rotationY: 12, rotationZ: -4, filter: 'blur(0px)', duration: 0.26, ease: 'power3.out' }}, {b(17.5) - 0.04:.3f});
tl.fromTo('#k6', {{ opacity: 0, y: 150, rotationX: -55, filter: 'blur(14px)' }}, {{ opacity: 1, y: 0, rotationX: 0, filter: 'blur(0px)', duration: 0.26, ease: 'power3.out' }}, {b(18) - 0.04:.3f});
tl.to(['#k4', '#k5', '#k6'], {{ scale: 1.08, duration: 0.35, ease: 'none' }}, {b(18) + 0.1:.3f});

/* ---- world 3: neon ---- */
tl.set(['#bg2', '#w2'], {{ opacity: 0 }}, {b(19)});
tl.set('#w3', {{ opacity: 1 }}, {b(19)});
tl.fromTo('#n0', {{ opacity: 0, scale: 0.6, filter: 'blur(26px)' }}, {{ opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.4, ease: 'expo.out' }}, {b(19)});
tl.to('#n0', {{ keyframes: [{{ opacity: 0.35, duration: 0.04 }}, {{ opacity: 1, duration: 0.05 }}, {{ opacity: 0.6, duration: 0.03 }}, {{ opacity: 1, duration: 0.05 }}] }}, {b(19) + 0.42:.3f});
"""
STEPS = [(20.5, -110, 1), (22, -320, 2), (23.5, -560, 3), (25, -650, 4)]
for n, y, i in STEPS:
    t = b(n)
    JS += f"tl.to('#col', {{ y: {y}, duration: 0.26, ease: 'power3.inOut' }}, {t - 0.14:.3f});\n"
    JS += f"tl.fromTo('#n{i}', {{ opacity: 0, filter: 'blur(20px)', scale: 0.85 }}, {{ opacity: 1, filter: 'blur(0px)', scale: 1, duration: 0.3, ease: 'expo.out' }}, {t - 0.04:.3f});\n"
    if i >= 2:
        JS += f"tl.to('#n{i - 2}', {{ opacity: 0, filter: 'blur(10px)', duration: 0.25 }}, {t - 0.14:.3f});\n"
    if i >= 1 and i != 4:
        JS += f"tl.to('#n{i - 1}', {{ opacity: 0.32, filter: 'blur(4px)', duration: 0.25 }}, {t - 0.14:.3f});\n"
JS += f"""
/* glitch on "Grenzen sind" */
tl.fromTo('#g1', {{ opacity: 0, x: 0 }}, {{ keyframes: [{{ opacity: 1, x: -14, duration: 0.04 }}, {{ x: 10, duration: 0.05 }}, {{ x: -6, duration: 0.04 }}, {{ opacity: 0, x: 0, duration: 0.05 }}] }}, {b(23.5) + 0.02:.3f});
tl.fromTo('#g2', {{ opacity: 0, x: 0 }}, {{ keyframes: [{{ opacity: 1, x: 14, duration: 0.04 }}, {{ x: -10, duration: 0.05 }}, {{ x: 6, duration: 0.04 }}, {{ opacity: 0, x: 0, duration: 0.05 }}] }}, {b(23.5) + 0.02:.3f});
"""
BX = [-60, 150, 330, 494, 658, 810, 950]
for i in range(7):
    JS += f"tl.fromTo('#bar{i}', {{ y: -2300 }}, {{ y: 0, duration: 0.2, ease: 'power4.in' }}, {b(26) - 0.2 + abs(i - 3) * 0.02:.3f});\n"
for i in range(7):
    d = i - 3
    JS += f"tl.to('#bar{i}', {{ x: {d * 300}, rotation: {d * 6}, opacity: 0, duration: 0.34, ease: 'power3.in' }}, {b(27.3):.3f});\n"
JS += f"""
tl.to(['#n3', '#n4'], {{ scale: 1.2, opacity: 0, filter: 'blur(22px)', duration: 0.34, ease: 'power3.in' }}, {b(27.3):.3f});

/* ---- end: logo into focus ---- */
tl.set('#w3', {{ opacity: 0 }}, {b(28)});
tl.fromTo('#logo', {{ opacity: 0, scale: 1.1, filter: 'blur(34px)' }}, {{ opacity: 1, scale: 1, filter: 'blur(0px)', duration: 0.7, ease: 'expo.out' }}, {b(28) - 0.04:.3f});
tl.fromTo('#mc .c', {{ opacity: 0, filter: 'blur(10px)', y: 14 }}, {{ opacity: 1, filter: 'blur(0px)', y: 0, duration: 0.3, ease: 'power3.out', stagger: 0.04 }}, {b(29):.3f});
tl.fromTo('#hd', {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {b(30):.3f});
tl.to(['#logo', '#mc', '#hd'], {{ opacity: 0, filter: 'blur(14px)', duration: 0.4, ease: 'power2.in' }}, {DUR - 0.5:.2f});
window.__timelines = window.__timelines || {{}}; window.__timelines['main'] = tl;
"""

html = ("<!doctype html><html lang='de'><head><meta charset='UTF-8' /><meta name='viewport' content='width=1080, height=1920' />"
        "<script src='ui/gsap.min.js'></script><style>" + CSS + "</style></head><body>"
        f"<div id='root' data-composition-id='main' data-start='0' data-duration='{DUR}' data-fps='30' data-width='1080' data-height='1920'>"
        f"<div id='stage' class='clip' data-start='0' data-duration='{DUR}' data-track-index='1'>" + body() + "</div></div>"
        "<script>" + JS + "</script></body></html>")
(HERE / "index.html").write_text(html)
print("ok", [b(n) for n in (13, 19, 26, 28)])
