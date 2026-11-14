"""Four centred cuts of the Kevin Nsimba spot (voice: Chris, continuous).
A = reference 1 (marq: centred kinetic type, cream/navy, motion blur, typing)
B = reference 2 (soft grey, small type rolling with blur, profile card morph)
C = retro 80s (synthwave grid, neon sun, VHS)
D = retro vintage film (sepia, grain, gate weave, light leaks, serif)
python tools/refbuild.py A|B|C|D -> index.html"""
import json, sys, random
from pathlib import Path
from PIL import ImageFont

HERE = Path(__file__).resolve().parent.parent
W = json.load(open(HERE / "tools" / "words.json"))
DUR = 18.0
BLACK = ImageFont.truetype(str(HERE / "fonts" / "InterDisplay-Black.otf"), 100)

def fit(text, size, maxw=940, k=0.955):
    w = BLACK.getlength(text) * size / 100 * k
    return min(size, int(size * maxw / max(w, 1)))

FONTS = """
@font-face { font-family: I; font-weight: 300; src: url(fonts/InterDisplay-Light.otf) format("opentype"); }
@font-face { font-family: I; font-weight: 500; src: url(fonts/InterDisplay-Medium.otf) format("opentype"); }
@font-face { font-family: I; font-weight: 600; src: url(fonts/InterDisplay-SemiBold.otf) format("opentype"); }
@font-face { font-family: I; font-weight: 700; src: url(fonts/InterDisplay-Bold.otf) format("opentype"); }
@font-face { font-family: I; font-weight: 900; src: url(fonts/InterDisplay-Black.otf) format("opentype"); }
@font-face { font-family: Play; font-weight: 400; src: url(fonts/playfair-display-latin-400-normal.woff2) format("woff2"); }
@font-face { font-family: Play; font-weight: 400; font-style: italic; src: url(fonts/playfair-display-latin-400-italic.woff2) format("woff2"); }
@font-face { font-family: Play; font-weight: 700; src: url(fonts/playfair-display-latin-700-normal.woff2) format("woff2"); }
@font-face { font-family: Play; font-weight: 700; font-style: italic; src: url(fonts/playfair-display-latin-700-italic.woff2) format("woff2"); }
@font-face { font-family: Bebas; font-weight: 400; src: url(fonts/bebas-neue-latin-400-normal.woff2) format("woff2"); }
@font-face { font-family: Mono; font-weight: 400; src: url(fonts/space-mono-latin-400-normal.woff2) format("woff2"); }
@font-face { font-family: Mono; font-weight: 700; src: url(fonts/space-mono-latin-700-normal.woff2) format("woff2"); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { position: absolute; inset: 0; } .abs { position: absolute; } .full { position: absolute; inset: 0; }
.ctr { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
"""

def page(css, body, js):
    return ("<!doctype html><html lang='de'><head><meta charset='UTF-8' /><meta name='viewport' content='width=1080, height=1920' />"
            "<script src='ui/gsap.min.js'></script><style>" + FONTS + css + "</style></head><body>"
            f"<div id='root' data-composition-id='main' data-start='0' data-duration='{DUR}' data-fps='30' data-width='1080' data-height='1920'>"
            f"<div id='stage' class='clip' data-start='0' data-duration='{DUR}' data-track-index='1'>" + body + "</div></div>"
            "<script>window.__timelines = window.__timelines || {}; const tl = gsap.timeline({ paused: true });"
            + js + "window.__timelines['main'] = tl;</script></body></html>")

SENT = [(0, 7, 0.00), (7, 9, 2.42), (9, 10, 3.52), (10, 11, 4.38), (11, 12, 5.40), (12, 16, 6.32), (16, 18, 8.20),
        (18, 19, 9.76), (19, 20, 10.70), (20, 21, 11.70)]
LINES = ["In dir steckt mehr,<br>als du denkst.", "Ein Funke.", "Druck.", "Zweifel.", "Angst.", "Doch ein Funke<br>genügt.",
         "Potenzial<br>entfachen.", "Klarheit.", "Fokus.", "Stärke."]
ENDT = 12.55

# ======================================================================= A  (reference 1)
def A():
    cards = [
        (0.00, "c", [("in dir", 200)]), (0.34, "n", [("steckt", 330)]), (0.72, "c", [("mehr,", 440)]),
        (1.04, "n", [("als du", 260)]), (1.54, "c", [("denkst.", 360)]), (2.42, "n", [("ein", 260)]),
        (2.60, "c", [("funke.", 400, "acc")]), (3.52, "n", [("druck.", 400)]), (4.38, "c", [("zweifel.", 380)]),
        (5.40, "n", [("angst.", 430)]), (6.32, "c", [("doch ein", 240)]), (6.86, "n", [("funke", 420)]),
        (7.34, "c", [("genügt.", 400, "acc")]), (8.20, "n", [("po", 440)]), (8.36, "n", [("poten", 420)]),
        (8.52, "n", [("potenzi", 380)]), (8.70, "n", [("potenzial", 340, "acc")]), (8.88, "c", [("entfachen.", 330)]),
        (9.76, "n", [("klarheit.", 360)]), (10.70, "c", [("fokus.", 430)]), (11.70, "n", [("stärke.", 420, "acc")]),
        (12.64, "c", [("kevin", 300)]), (13.24, "n", [("nsimba", 330)]), (13.98, "c", [("dein", 260)]),
        (14.24, "n", [("mental", 380)]), (14.66, "c", [("coach.", 420, "acc")]), (15.30, "n", "END")]
    css = """
.card { position: absolute; inset: 0; visibility: hidden; display: flex; align-items: center; justify-content: center; font-family: I; }
.card.c { background: #efeae1; color: #121212; } .card.n { background: #0f1a2b; color: #f4f1ea; }
#k0 { visibility: visible; }
.wd { font-weight: 900; letter-spacing: -0.045em; line-height: .9; white-space: nowrap; padding-bottom: .08em; }
.c .acc { color: #a8742a; } .n .acc { color: #e2b56a; }
#shade { background: radial-gradient(120% 85% at 50% 45%, rgba(0,0,0,0) 50%, rgba(0,0,0,.22) 100%); pointer-events: none; }
#grain { opacity: .06; mix-blend-mode: overlay; background: url(ui/grain.png); background-size: 256px; }
.endw { display: flex; flex-direction: column; align-items: center; }
.endw .nm { font-weight: 900; font-size: 150px; letter-spacing: -0.045em; line-height: .9; }
.endw .sq { display: inline-block; width: .16em; height: .16em; background: #e2b56a; margin-left: .04em; }
.endw .rl { margin-top: 40px; font-weight: 600; font-size: 54px; color: #e2b56a; letter-spacing: -0.02em; }
.endw .cl { margin-top: 60px; font-weight: 500; font-size: 42px; color: #c9c6bf; line-height: 1.3; }
.endw .hd { margin-top: 40px; font-weight: 500; font-size: 32px; color: #8d8a84; }
"""
    body, js = [], []
    for i, (t, bg, ln) in enumerate(cards):
        t1 = cards[i + 1][0] if i + 1 < len(cards) else DUR
        if ln == "END":
            inner = ("<div class='endw' id='kx%d'><div class='nm'>kevin nsimba<span class='sq'></span></div>"
                     "<div class='rl' id='e1'>dein mental coach.</div><div class='cl' id='e2'>train the mind.<br>change the game.</div>"
                     "<div class='hd' id='e3'>@kevnsimba</div></div>") % i
        else:
            txt, size = ln[0][0], ln[0][1]
            acc = len(ln[0]) > 2
            inner = f"<div class='wd{' acc' if acc else ''}' id='kx{i}' style='font-size:{fit(txt, size)}px'>{txt}</div>"
        body.append(f"<div class='card {bg}' id='k{i}'>{inner}</div>")
        js.append(f"tl.set('#k{i}', {{ visibility: 'visible' }}, {t:.3f}); tl.set('#k{i}', {{ visibility: 'hidden' }}, {t1:.3f});")
        d = 1 if i % 2 == 0 else -1
        if ln == "END":
            js.append(f"tl.fromTo('#kx{i} .nm', {{ x: 120, filter: 'blur(14px)' }}, {{ x: 0, filter: 'blur(0px)', duration: 0.16, ease: 'power3.out' }}, {t:.3f});")
            js.append(f"tl.fromTo(['#e1', '#e2', '#e3'], {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: 'power3.out', stagger: 0.35 }}, {t + 0.25:.3f});")
        elif not (8.2 < t < 8.8):          # typing frames don't slide
            js.append(f"tl.fromTo('#kx{i}', {{ x: {110 * d}, filter: 'blur(14px)' }}, {{ x: 0, filter: 'blur(0px)', duration: 0.14, ease: 'power3.out' }}, {t:.3f});")
    body.append("<div id='shade' class='full'></div><div id='grain' class='full'></div>")
    return page(css, "".join(body), "".join(js))

# ======================================================================= B  (reference 2)
def B():
    css = """
#bg { background: radial-gradient(110% 80% at 50% 40%, #f1f1f2 0%, #e4e4e6 70%, #d9d9dc 100%); }
.rw { position: absolute; left: 0; width: 1080px; top: 0; text-align: center; font-family: I; font-weight: 600; color: #141414; letter-spacing: -0.03em; opacity: 0; white-space: nowrap; }
.rw.acc { color: #b07a28; }
#card { left: 140px; top: 690px; width: 800px; height: 540px; border-radius: 46px; background: #0d0d10; opacity: 0; overflow: hidden; }
#av { left: 70px; top: 70px; width: 170px; height: 170px; border-radius: 50%; background: #1d1d22; border: 3px solid #c99a4a; overflow: hidden; }
#av img { width: 150%; margin-left: -25%; margin-top: 18%; }
#nm { left: 280px; top: 92px; font-family: I; font-weight: 700; font-size: 54px; color: #fff; letter-spacing: -0.02em; }
#sub { left: 280px; top: 164px; font-family: I; font-weight: 500; font-size: 36px; color: #a9a9b0; }
#btn { left: 70px; top: 330px; width: 660px; height: 120px; border-radius: 26px; background: #c99a4a; color: #0d0d10; font-family: I; font-weight: 700; font-size: 46px; display: flex; align-items: center; justify-content: center; }
#btn2 { left: 70px; top: 330px; width: 660px; height: 120px; border-radius: 26px; background: #2a2a30; color: #fff; font-family: I; font-weight: 700; font-size: 46px; display: flex; align-items: center; justify-content: center; opacity: 0; }
#fill { background: linear-gradient(160deg, #e9c983 0%, #c99a4a 55%, #9b6c28 100%); opacity: 0; }
#pill { left: 340px; top: 900px; width: 400px; height: 120px; border-radius: 60px; background: #c99a4a; display: flex; align-items: center; gap: 22px; padding-left: 12px; opacity: 0; font-family: I; font-weight: 700; font-size: 40px; color: #120c03; }
#pav { width: 96px; height: 96px; border-radius: 50%; background: #0d0d10; overflow: hidden; flex: none; }
#pav img { width: 150%; margin-left: -25%; margin-top: 18%; }
#handle { font-family: I; font-weight: 700; font-size: 92px; color: #120c03; letter-spacing: -0.02em; opacity: 0; }
#claim { margin-top: 36px; font-family: I; font-weight: 500; font-size: 44px; color: #2a1e0b; line-height: 1.3; opacity: 0; }
#mc { margin-top: 30px; font-family: I; font-weight: 600; font-size: 40px; color: #120c03; opacity: 0; letter-spacing: .25em; }
"""
    body = ["<div id='bg' class='full'></div>"]
    js = []
    disp = {0: "In", 1: "dir", 2: "steckt", 3: "mehr,", 4: "als", 5: "du", 6: "denkst.", 7: "Ein", 8: "Funke.", 9: "Druck.",
            10: "Zweifel.", 11: "Angst.", 12: "Doch", 13: "ein", 14: "Funke", 15: "genügt.", 16: "Potenzial", 17: "entfachen.",
            18: "Klarheit.", 19: "Fokus.", 20: "Stärke."}
    CY = 920; STEP = 104
    for k in range(21):
        acc = W[k].get("accent")
        size = 96 if k not in (16, 17) else 120
        body.append(f"<div class='rw{' acc' if acc else ''}' id='r{k}' style='top:{CY}px;font-size:{size}px'>{disp[k]}</div>")
    # roll: each word arrives from below (blurred), sits sharp in the centre, then moves up and fades as the next arrives
    for k in range(21):
        t = W[k]["t"]
        js.append(f"tl.fromTo('#r{k}', {{ y: {STEP}, opacity: 0, filter: 'blur(10px)' }}, {{ y: 0, opacity: 1, filter: 'blur(0px)', duration: 0.32, ease: 'power3.out' }}, {t - 0.06:.2f});")
        if k < 20:
            t2 = W[k + 1]["t"]
            js.append(f"tl.to('#r{k}', {{ y: {-STEP}, opacity: .28, filter: 'blur(6px)', duration: 0.32, ease: 'power3.out' }}, {t2 - 0.06:.2f});")
            js.append(f"tl.to('#r{k}', {{ y: {-2 * STEP}, opacity: 0, filter: 'blur(12px)', duration: 0.3, ease: 'power2.in' }}, {(W[k + 2]['t'] if k + 2 < 21 else 12.3) - 0.06:.2f});")
    js.append("tl.to('#r20', { y: -104, opacity: 0, filter: 'blur(12px)', duration: 0.3, ease: 'power2.in' }, 12.3);")
    # card
    body.append("<div id='card' class='abs'><div id='av' class='abs'><img src='ui/kn-logo.png' alt='' /></div>"
                "<div id='nm' class='abs'>Kevin Nsimba</div><div id='sub' class='abs'>Mental Coach · @kevnsimba</div>"
                "<div id='btn' class='abs'>Folgen</div><div id='btn2' class='abs'>Gefolgt ✓</div></div>")
    body.append("<div id='pill' class='abs'><div id='pav'><img src='ui/kn-logo.png' alt='' /></div><span>@kevnsimba</span></div>")
    body.append("<div id='fill' class='full'></div><div class='ctr'><div id='handle'>@kevnsimba</div><div id='mc'>DEIN MENTAL COACH</div>"
                "<div id='claim'>Train the mind.<br>Change the game.</div></div>")
    js.append("tl.fromTo('#card', { opacity: 0, scale: 0.2, borderRadius: 300 }, { opacity: 1, scale: 1, borderRadius: 46, duration: 0.6, ease: 'expo.out' }, 12.6);")
    js.append("tl.fromTo(['#av', '#nm', '#sub', '#btn'], { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.35, ease: 'power3.out', stagger: 0.08 }, 12.85);")
    js.append("tl.to('#btn', { scale: 0.94, duration: 0.08, yoyo: true, repeat: 1 }, 14.0);")
    js.append("tl.to('#btn2', { opacity: 1, duration: 0.2 }, 14.16);")
    # card hands over to a pill, then the pill floods the screen
    js.append("tl.to('#card', { scale: 0.55, opacity: 0, duration: 0.4, ease: 'power3.in' }, 14.7);")
    js.append("tl.fromTo('#pill', { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.4, ease: 'back.out(1.6)' }, 14.95);")
    js.append("tl.to('#fill', { opacity: 1, duration: 0.01 }, 15.3); tl.fromTo('#fill', { clipPath: 'inset(46.9% 31.5% 46.9% 31.5% round 60px)' }, { clipPath: 'inset(0% 0% 0% 0% round 0px)', duration: 0.55, ease: 'power3.inOut' }, 15.3);")
    js.append("tl.to('#pill', { opacity: 0, duration: 0.15 }, 15.4);")
    js.append("tl.fromTo('#handle', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: 'power3.out' }, 15.7);")
    js.append("tl.fromTo('#mc', { opacity: 0 }, { opacity: 1, duration: 0.4 }, 16.0); tl.fromTo('#claim', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4 }, 16.3);")
    return page(css, "".join(body), "".join(js))

# ======================================================================= C  (retro 80s)
def C():
    css = """
#sky { background: linear-gradient(180deg, #0b0221 0%, #2a0a4a 38%, #6a1b6e 52%, #ff4f8b 60%, #1a0630 60.2%, #0b0221 100%); }
#sun { left: 240px; top: 600px; width: 600px; height: 600px; border-radius: 50%;
       background: linear-gradient(180deg, #ffe66d 0%, #ff9a3c 45%, #ff3d7f 100%);
       -webkit-mask-image: linear-gradient(180deg, #000 0 52%, transparent 52% 56%, #000 56% 63%, transparent 63% 67%, #000 67% 73%, transparent 73% 78%, #000 78% 83%, transparent 83% 89%, #000 89% 100%);
       mask-image: linear-gradient(180deg, #000 0 52%, transparent 52% 56%, #000 56% 63%, transparent 63% 67%, #000 67% 73%, transparent 73% 78%, #000 78% 83%, transparent 83% 89%, #000 89% 100%);
       filter: drop-shadow(0 0 60px rgba(255,80,140,.8)); clip-path: inset(0 0 50% 0); }
#grid { left: -540px; width: 2160px; top: 1152px; height: 900px; transform-origin: 50% 0; transform: perspective(500px) rotateX(62deg);
        background-image: linear-gradient(rgba(255,60,200,.9) 3px, transparent 3px), linear-gradient(90deg, rgba(0,230,255,.8) 3px, transparent 3px);
        background-size: 100% 90px, 120px 100%; filter: drop-shadow(0 0 6px rgba(255,60,200,.9)); }
#horizon { left: 0; top: 1148px; width: 1080px; height: 6px; background: #ff4fd8; box-shadow: 0 0 30px 8px rgba(255,79,216,.8); }
.nt { font-family: Bebas; color: #fff; letter-spacing: .04em; line-height: .95; opacity: 0;
      text-shadow: 0 0 8px #fff, 0 0 24px #ff4fd8, 0 0 60px #ff4fd8, 4px 0 0 rgba(0,240,255,.7), -4px 0 0 rgba(255,0,90,.7); }
.chrome { background: linear-gradient(180deg, #e8f7ff 0%, #8fd3ff 45%, #2a1458 50%, #ff8ad8 54%, #fff3fb 100%); -webkit-background-clip: text; background-clip: text; color: transparent;
          text-shadow: none; filter: drop-shadow(0 0 20px rgba(255,80,220,.8)); }
#scan { background: repeating-linear-gradient(180deg, rgba(0,0,0,.25) 0 2px, rgba(0,0,0,0) 2px 5px); pointer-events: none; mix-blend-mode: multiply; }
#osd { left: 60px; top: 90px; font-family: Mono; font-weight: 700; font-size: 34px; color: #fff; text-shadow: 2px 0 rgba(255,0,90,.8), -2px 0 rgba(0,240,255,.8); }
#rec { left: 790px; top: 90px; font-family: Mono; font-weight: 700; font-size: 34px; color: #ff3b5c; }
#flash { background: #ffd1f1; opacity: 0; mix-blend-mode: screen; }
#logo { width: 600px; filter: drop-shadow(0 0 18px rgba(255,79,216,.9)) drop-shadow(0 0 40px rgba(0,230,255,.5)); opacity: 0; }
#e1 { margin-top: 50px; font-size: 92px; } #e2 { margin-top: 30px; font-family: Mono; font-size: 40px; color: #8ff3ff; opacity: 0; letter-spacing: .1em; }
#e3 { margin-top: 30px; font-family: Mono; font-size: 34px; color: #ffd36b; opacity: 0; }
#vhs { background: linear-gradient(90deg, rgba(255,0,90,.12), rgba(0,240,255,.12)); opacity: 0; mix-blend-mode: screen; }
"""
    body = ["<div id='sky' class='full'></div><div id='sun' class='abs'></div><div id='grid' class='abs'></div><div id='horizon' class='abs'></div>"]
    js = []
    sizes = [130, 200, 230, 230, 260, 150, 200, 230, 260, 260]
    for i, ((a, b, t), txt) in enumerate(zip(SENT, LINES)):
        up = txt.upper()
        cls = "nt chrome" if i in (6, 9) else "nt"
        body.append(f"<div class='ctr'><div class='{cls}' id='l{i}' style='font-size:{sizes[i]}px;margin-top:-260px'>{up}</div></div>")
        t1 = SENT[i + 1][2] if i + 1 < len(SENT) else ENDT
        # glitch in: flicker + RGB split jitter
        js.append(f"tl.fromTo('#l{i}', {{ opacity: 0, x: -30, skewX: 12 }}, {{ keyframes: [{{ opacity: 1, x: 18, skewX: -8, duration: .04 }}, {{ opacity: .3, x: -10, duration: .04 }}, {{ opacity: 1, x: 6, skewX: 0, duration: .04 }}, {{ x: 0, duration: .05 }}] }}, {t - 0.04:.2f});")
        js.append(f"tl.to('#l{i}', {{ keyframes: [{{ opacity: .4, x: 14, duration: .04 }}, {{ opacity: 1, x: -8, duration: .04 }}, {{ opacity: 0, x: 0, scaleY: .05, duration: .08 }}] }}, {t1 - 0.18:.2f});")
        js.append(f"tl.fromTo('#vhs', {{ opacity: .9 }}, {{ opacity: 0, duration: .25, immediateRender: false }}, {t - 0.04:.2f});")
    js.append("tl.fromTo('#grid', { backgroundPosition: '0px 0px, 0px 0px' }, { backgroundPosition: '0px 900px, 0px 0px', duration: 8.2, ease: 'none' }, 0);")
    js.append("tl.to('#grid', { backgroundPosition: '0px 3600px, 0px 0px', duration: 9.8, ease: 'none' }, 8.2);")
    js.append("tl.fromTo('#sun', { y: 160, scale: .9 }, { y: 0, scale: 1, duration: 8.2, ease: 'sine.out' }, 0);")
    js.append("tl.fromTo('#flash', { opacity: .85 }, { opacity: 0, duration: .6, immediateRender: false }, 8.2);")
    js.append("tl.to('#sun', { scale: 1.12, filter: 'drop-shadow(0 0 120px rgba(255,80,140,1))', duration: .5, ease: 'expo.out' }, 8.2);")
    body.append("<div id='vhs' class='full'></div><div class='ctr'><img id='logo' src='ui/kn-logo.png' alt='Kevin Nsimba' style='margin-top:-240px' />"
                "<div class='nt' id='e1'>DEIN MENTAL COACH</div><div id='e2'>TRAIN THE MIND. CHANGE THE GAME.</div><div id='e3'>@KEVNSIMBA</div></div>")
    js.append(f"tl.fromTo('#logo', {{ opacity: 0, scale: 1.2 }}, {{ keyframes: [{{ opacity: 1, scale: 1.05, duration: .06 }}, {{ opacity: .2, duration: .05 }}, {{ opacity: 1, scale: 1, duration: .3 }}] }}, {ENDT:.2f});")
    js.append("tl.fromTo('#e1', { opacity: 0 }, { keyframes: [{ opacity: 1, duration: .04 }, { opacity: .2, duration: .04 }, { opacity: 1, duration: .1 }] }, 14.0);")
    js.append("tl.fromTo('#e2', { opacity: 0 }, { opacity: 1, duration: .3 }, 15.4); tl.fromTo('#e3', { opacity: 0 }, { opacity: 1, duration: .3 }, 15.9);")
    body.append("<div id='osd' class='abs'>▶ PLAY</div><div id='rec' class='abs' id2='t'>SP 0:00:00</div><div id='scan' class='full'></div>")
    # running VHS counter
    js.append("const rec = document.getElementById('rec'); const cnt = { v: 0 }; tl.to(cnt, { v: 18, duration: 18, ease: 'none', onUpdate: () => { const s = Math.floor(cnt.v); rec.textContent = 'SP 0:00:' + String(s).padStart(2, '0'); } }, 0);")
    return page(css, "".join(body), "".join(js))

# ======================================================================= D  (vintage film)
def D():
    rng = random.Random(9)
    css = """
#bg { background: radial-gradient(90% 70% at 50% 45%, #3b2a1a 0%, #24180e 60%, #120b05 100%); }
#leak1 { left: -300px; top: 200px; width: 900px; height: 900px; border-radius: 50%; filter: blur(90px); background: radial-gradient(circle, rgba(255,140,40,.55), rgba(255,90,20,0) 65%); opacity: 0; mix-blend-mode: screen; }
#leak2 { left: 500px; top: 1100px; width: 900px; height: 900px; border-radius: 50%; filter: blur(90px); background: radial-gradient(circle, rgba(255,190,90,.5), rgba(255,120,30,0) 65%); opacity: 0; mix-blend-mode: screen; }
#frame { left: 90px; top: 520px; width: 900px; height: 880px; border: 3px solid rgba(232,212,170,.75); outline: 1px solid rgba(232,212,170,.45); outline-offset: 14px; opacity: 0; }
.vt { font-family: Play; color: #efe1c4; line-height: 1.05; opacity: 0; text-shadow: 0 0 2px rgba(255,240,210,.6); }
.vt i { font-style: italic; color: #e3b46a; }
.orn { font-family: Play; font-size: 44px; color: #c99a4a; letter-spacing: .5em; padding-left: .5em; opacity: 0; }
#burn { background: radial-gradient(60% 45% at 50% 50%, rgba(255,250,235,1) 0%, rgba(255,170,60,.9) 25%, rgba(120,40,0,.6) 55%, rgba(0,0,0,0) 75%); opacity: 0; mix-blend-mode: screen; }
#tint { background: #6b4a22; mix-blend-mode: color; opacity: .35; pointer-events: none; }
#vig { background: radial-gradient(85% 65% at 50% 48%, rgba(0,0,0,0) 45%, rgba(0,0,0,.75) 100%); pointer-events: none; }
#grain { opacity: .22; mix-blend-mode: overlay; background: url(ui/grain.png); background-size: 200px; }
.scr { position: absolute; top: 0; width: 2px; height: 1920px; background: rgba(255,245,225,.35); opacity: 0; }
.dst { position: absolute; border-radius: 50%; background: rgba(255,245,225,.6); opacity: 0; }
#logo { width: 560px; filter: sepia(1) saturate(1.6) hue-rotate(-8deg) brightness(.95); opacity: 0; }
#e1 { margin-top: 50px; font-size: 76px; } #e2 { margin-top: 26px; font-size: 44px; } #e3 { margin-top: 28px; font-family: Play; font-size: 34px; color: #c9b08a; opacity: 0; }
"""
    body = ["<div id='bg' class='full'></div><div id='leak1' class='abs'></div><div id='leak2' class='abs'></div><div id='frame' class='abs'></div>"]
    js = []
    lines = ["In dir steckt <i>mehr</i>,<br>als du denkst.", "Ein <i>Funke</i>.", "Druck.", "Zweifel.", "Angst.", "Doch ein Funke<br><i>genügt</i>.",
             "<i>Potenzial</i><br>entfachen.", "Klarheit.", "Fokus.", "<i>Stärke</i>."]
    sizes = [96, 140, 170, 170, 170, 110, 150, 160, 160, 170]
    for i, ((a, b, t), txt) in enumerate(zip(SENT, lines)):
        body.append(f"<div class='ctr'><div class='orn' id='o{i}'>✦</div><div class='vt' id='l{i}' style='font-size:{sizes[i]}px;margin:20px 0'>{txt}</div></div>")
        t1 = SENT[i + 1][2] if i + 1 < len(SENT) else ENDT
        js.append(f"tl.fromTo('#l{i}', {{ opacity: 0, filter: 'blur(6px)' }}, {{ keyframes: [{{ opacity: .6, filter: 'blur(2px)', duration: .08 }}, {{ opacity: .35, duration: .06 }}, {{ opacity: 1, filter: 'blur(0px)', duration: .3 }}] }}, {t - 0.06:.2f});")
        js.append(f"tl.to('#l{i}', {{ opacity: 0, filter: 'blur(4px)', duration: .22, ease: 'power2.in' }}, {t1 - 0.24:.2f});")
        if i in (0, 1, 5, 6):
            js.append(f"tl.fromTo('#o{i}', {{ opacity: 0 }}, {{ opacity: 1, duration: .4 }}, {t + 0.1:.2f}); tl.to('#o{i}', {{ opacity: 0, duration: .2 }}, {t1 - 0.24:.2f});")
    js.append("tl.fromTo('#frame', { opacity: 0 }, { opacity: 1, duration: 1.2 }, 0.2); tl.to('#frame', { opacity: 0, duration: .5 }, 12.2);")
    # film burn on Potenzial, light leaks drift
    js.append("tl.fromTo('#burn', { opacity: 0, scale: .4 }, { opacity: 1, scale: 1.4, duration: .35, ease: 'power2.out' }, 7.95); tl.to('#burn', { opacity: 0, scale: 2, duration: .7, ease: 'power2.in' }, 8.3);")
    js.append("tl.fromTo('#leak1', { opacity: 0, x: 0 }, { opacity: 1, x: 260, duration: 3, ease: 'sine.inOut' }, 2.2); tl.to('#leak1', { opacity: 0, duration: 1.5 }, 5.2);")
    js.append("tl.fromTo('#leak2', { opacity: 0, x: 0 }, { opacity: 1, x: -300, duration: 4, ease: 'sine.inOut' }, 8.3); tl.to('#leak2', { opacity: .4, duration: 2 }, 12.3);")
    # gate weave + exposure flicker (deterministic)
    keys = ", ".join(f"{{ y: {rng.uniform(-3,3):.1f}, x: {rng.uniform(-1.5,1.5):.1f}, duration: .083 }}" for _ in range(216))
    js.append(f"tl.to('#weave', {{ keyframes: [{keys}] }}, 0);")
    fl = ", ".join(f"{{ opacity: {rng.uniform(.0,.12):.2f}, duration: .083 }}" for _ in range(216))
    js.append(f"tl.to('#flick', {{ keyframes: [{fl}] }}, 0);")
    # scratches and dust
    for j in range(6):
        x = rng.uniform(80, 1000); t = rng.uniform(0.5, 16)
        body.append(f"<div class='scr' id='s{j}' style='left:{x:.0f}px'></div>")
        js.append(f"tl.set('#s{j}', {{ opacity: .8 }}, {t:.2f}); tl.set('#s{j}', {{ opacity: 0 }}, {t + 0.12:.2f});")
    for j in range(14):
        x, y, s, t = rng.uniform(40, 1040), rng.uniform(80, 1840), rng.uniform(3, 9), rng.uniform(0.3, 17)
        body.append(f"<div class='dst' id='d{j}' style='left:{x:.0f}px;top:{y:.0f}px;width:{s:.0f}px;height:{s:.0f}px'></div>")
        js.append(f"tl.set('#d{j}', {{ opacity: 1 }}, {t:.2f}); tl.set('#d{j}', {{ opacity: 0 }}, {t + 0.08:.2f});")
    body.append("<div class='ctr'><img id='logo' src='ui/kn-logo.png' alt='Kevin Nsimba' style='margin-top:-160px' />"
                "<div class='vt' id='e1'>Dein <i>Mental Coach</i>.</div><div class='vt' id='e2'>Train the mind. <i>Change the game.</i></div><div id='e3'>@kevnsimba</div></div>")
    js.append(f"tl.fromTo('#logo', {{ opacity: 0 }}, {{ keyframes: [{{ opacity: .7, duration: .1 }}, {{ opacity: .4, duration: .06 }}, {{ opacity: 1, duration: .5 }}] }}, {ENDT:.2f});")
    js.append("tl.fromTo('#e1', { opacity: 0 }, { opacity: 1, duration: .5 }, 14.0); tl.fromTo('#e2', { opacity: 0 }, { opacity: 1, duration: .5 }, 15.4); tl.fromTo('#e3', { opacity: 0 }, { opacity: 1, duration: .5 }, 15.9);")
    html = "".join(body)
    html = "<div id='weave' class='full'>" + html + "</div><div id='tint' class='full'></div><div id='flick' class='full' style='background:#fff3d6;opacity:0;mix-blend-mode:screen'></div><div id='burn' class='full'></div><div id='vig' class='full'></div><div id='grain' class='full'></div>"
    js.append("tl.fromTo('#grain', { backgroundPosition: '0px 0px' }, { keyframes: [" + ", ".join(f"{{ backgroundPosition: '{rng.randint(0,200)}px {rng.randint(0,200)}px', duration: .042 }}" for _ in range(430)) + "] }, 0);")
    return page(css, html, "".join(js))

v = sys.argv[1]
(HERE / "index.html").write_text({"A": A, "B": B, "C": C, "D": D}[v]())
print("built", v)
