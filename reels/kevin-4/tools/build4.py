"""Four structurally different cuts of the Kevin Nsimba spot. Same voice (Chris, continuous).
python tools/build4.py v1|v2|v3|v4  -> index.html"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
W = json.load(open(HERE / "tools" / "words.json"))
WJ = json.dumps(W, ensure_ascii=False)
DUR = 18.0

HEAD = """<!doctype html><html lang="de"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
<script src="ui/gsap.min.js"></script><style>
@font-face { font-family: D; font-weight: 300; src: url(fonts/InterDisplay-Light.otf) format("opentype"); }
@font-face { font-family: D; font-weight: 500; src: url(fonts/InterDisplay-Medium.otf) format("opentype"); }
@font-face { font-family: D; font-weight: 600; src: url(fonts/InterDisplay-SemiBold.otf) format("opentype"); }
@font-face { font-family: D; font-weight: 700; src: url(fonts/InterDisplay-Bold.otf) format("opentype"); }
@font-face { font-family: D; font-weight: 900; src: url(fonts/InterDisplay-Black.otf) format("opentype"); }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: D; }
#root { position: relative; width: 100%; height: 100%; overflow: hidden; }
.clip { position: absolute; inset: 0; } .abs { position: absolute; } .full { position: absolute; inset: 0; }
.gold { background: linear-gradient(100deg, #b8862f 0%, #f7e2ad 40%, #d6a24a 70%, #fff0c8 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
#grain { opacity: .06; mix-blend-mode: overlay; background-size: 256px 256px; background-image: url(ui/grain.png); }
/* shared end card */
#end { background: #070707; opacity: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #f5f5f5; }
#end img { width: 560px; display: block; margin-top: -80px; }
#end .r { margin-top: 70px; font-weight: 700; font-size: 66px; letter-spacing: -0.03em; }
#end .c { margin-top: 44px; font-weight: 500; font-size: 46px; line-height: 1.25; text-align: center; color: #d8d8d8; }
#end .h { margin-top: 46px; font-weight: 500; font-size: 32px; color: #8e8e8e; }
"""

END_HTML = """<div id="end" class="full"><img id="endlogo" src="ui/kn-logo.png" alt="Kevin Nsimba" />
<div class="r" id="endr">dein <span class="gold">Mental Coach.</span></div>
<div class="c" id="endc">Train the mind.<br><span class="gold">Change the game.</span></div>
<div class="h" id="endh">@kevnsimba</div></div>"""

END_JS = """
tl.fromTo("#end", { opacity: 0 }, { opacity: 1, duration: 0.35, ease: "power2.out" }, END);
tl.fromTo("#endlogo", { scale: 1.12, filter: "blur(12px)" }, { scale: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, END);
tl.fromTo(["#endr", "#endc", "#endh"], { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out", stagger: 0.4 }, END + 0.4);
"""

def page(css, body, js, end=12.55):
    return (HEAD + css + "</style></head><body>"
            f'<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-fps="30" data-width="1080" data-height="1920">'
            + body.replace("{END}", END_HTML) +
            "</div><script>window.__timelines = window.__timelines || {};const tl = gsap.timeline({ paused: true });"
            f"const WORDS = {WJ}; const T = (w) => WORDS.find((x) => x.w === w).t; const END = " + str(end) + ";"
            + js + END_JS + 'window.__timelines["main"] = tl;</script></body></html>')

# ---------------------------------------------------------------- V1  Lese-Fluss
V1_CSS = """
#bg { background: radial-gradient(90% 60% at 50% 40%, #1a1408 0%, #0a0806 60%, #050403 100%); }
#glow { left: 90px; top: 500px; width: 900px; height: 900px; border-radius: 50%; filter: blur(80px); background: radial-gradient(circle, rgba(214,160,74,.45), rgba(214,160,74,0) 65%); opacity: .35; }
.sent { position: absolute; left: 90px; right: 90px; top: 760px; font-weight: 700; font-size: 112px; line-height: 1.08; letter-spacing: -0.035em; color: #fff; opacity: 0; }
.sent .w { opacity: .18; display: inline-block; margin-right: .22em; }
.sent .w.acc { }
#flash { background: radial-gradient(70% 45% at 50% 50%, rgba(255,215,140,.6), rgba(0,0,0,0) 70%); opacity: 0; mix-blend-mode: screen; }
"""
SENTS = [["in", "dir", "steckt", "mehr,", "als", "du", "denkst."], ["ein", "funke."], ["druck.", "zweifel.", "angst."],
         ["doch", "ein", "funke", "genügt."], ["potenzial", "entfachen."], ["klarheit.", "fokus.", "stärke."],
         ["kevin", "nsimba", "dein", "mental", "coach."]]
DISPLAY = {"nsimba": "Nsimba.", "kevin": "Kevin", "mental": "Mental", "coach.": "Coach."}

def v1():
    body = ['<div id="bg" class="full"></div><div id="glow" class="abs"></div><div id="flash" class="full"></div>']
    k = 0; js = []
    for si, sent in enumerate(SENTS):
        spans = []
        for w in sent:
            acc = W[k].get("accent")
            NOUN = {"funke.", "funke", "druck.", "zweifel.", "angst.", "potenzial", "klarheit.", "fokus.", "stärke."}
            first = (w == sent[0] and sent.index(w) == 0 and spans == [])
            txt = DISPLAY.get(w, w[0].upper() + w[1:] if (first or w in NOUN) else w)
            spans.append(f'<span class="w{" gold" if acc else ""}" id="w{k}">{txt}</span>')
            js.append(f'tl.to("#w{k}", {{ opacity: 1, duration: 0.18, ease: "power2.out" }}, {W[k]["t"]:.2f});')
            k += 1
        body.append(f'<div class="sent" id="s{si}">{"".join(spans)}</div>')
        t0 = W[k - len(sent)]["t"] - 0.12
        t1 = W[k]["t"] - 0.14 if k < len(W) else 15.1
        js.append(f'tl.fromTo("#s{si}", {{ opacity: 0, y: 120 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {max(0, t0):.2f});')
        js.append(f'tl.to("#s{si}", {{ opacity: 0, y: -160, duration: 0.3, ease: "power2.in" }}, {t1 - 0.18:.2f});')
    js.append('tl.fromTo("#glow", { x: -120, y: 80 }, { x: 140, y: -120, duration: 18, ease: "sine.inOut" }, 0);')
    js.append('tl.to("#glow", { opacity: .9, scale: 1.3, duration: 0.5, ease: "power2.out" }, 8.2); tl.to("#glow", { opacity: .55, duration: 2, ease: "sine.inOut" }, 8.7);')
    js.append('tl.fromTo("#flash", { opacity: .9 }, { opacity: 0, duration: 0.8, ease: "power2.out", immediateRender: false }, 8.2);')
    body.append('{END}<div id="grain" class="full"></div>')
    return page(V1_CSS, "".join(body), "".join(js), 15.3)

# ---------------------------------------------------------------- V2  Zwei Hälften
V2_CSS = """
#gold { background: linear-gradient(160deg, #f6dfa3 0%, #d4a24a 50%, #9c6a22 100%); }
.half { position: absolute; left: 0; width: 1080px; height: 960px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
#top { top: 0; background: #080808; color: #fafafa; } #bot { top: 960px; background: #f7f7f7; color: #0a0a0a; }
.tw { position: absolute; left: 0; width: 1080px; text-align: center; font-weight: 900; letter-spacing: -0.045em; line-height: .9; opacity: 0; }
#top .tw { bottom: 70px; } #bot .tw { top: 70px; }
#seam { left: 0; top: 958px; width: 1080px; height: 4px; background: #d4a24a; }
#big { top: 760px; font-weight: 900; font-size: 230px; letter-spacing: -0.05em; color: #120c03; width: 1080px; text-align: center; opacity: 0; }
#big2 { top: 1010px; font-weight: 300; font-size: 120px; letter-spacing: -0.02em; color: #120c03; width: 1080px; text-align: center; opacity: 0; }
.band { position: absolute; left: 0; width: 1080px; height: 640px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 230px; letter-spacing: -0.05em; }
#b1 { top: 0; background: #080808; color: #fff; } #b2 { top: 640px; background: #f7f7f7; color: #0a0a0a; } #b3 { top: 1280px; background: #080808; }
"""
def v2():
    tops = [("in dir steckt", 120, "in"), ("ein", 200, "ein"), ("druck.", 250, "druck."), ("angst.", 270, "angst."), ("doch ein funke", 112, "doch")]
    bots = [("mehr, als du denkst.", 104, "mehr,"), ("funke.", 260, "funke."), ("zweifel.", 230, "zweifel."), ("genügt.", 250, "genügt.")]
    body = ['<div id="gold" class="full"></div><div id="big" class="abs">potenzial</div><div id="big2" class="abs">entfachen.</div>',
            '<div id="top" class="half">']
    for i, (t, s, _) in enumerate(tops):
        body.append(f'<div class="tw" id="t{i}" style="font-size:{s}px">{t}</div>')
    body.append('</div><div id="bot" class="half">')
    for i, (t, s, _) in enumerate(bots):
        g = ' gold' if t == "genügt." else ''
        body.append(f'<div class="tw{g}" id="u{i}" style="font-size:{s}px">{t}</div>')
    body.append('</div><div id="seam" class="abs"></div>')
    body.append('<div id="b1" class="band">klarheit.</div><div id="b2" class="band">fokus.</div><div id="b3" class="band"><span class="gold">stärke.</span></div>')
    body.append('{END}<div id="grain" class="full"></div>')
    js = []
    # the halves talk to each other: top line, then its answer below
    seq = [("t0", 0.0, 2.3, -1), ("u0", 0.72, 2.3, 1), ("t1", 2.42, 3.45, -1), ("u1", 2.60, 3.45, 1),
           ("t2", 3.52, 6.2, -1), ("u2", 4.38, 6.2, 1), ("t3", 5.40, 6.2, -1), ("t4", 6.32, 8.1, -1), ("u3", 7.34, 8.1, 1)]
    for el, a, b, d in seq:
        js.append(f'tl.fromTo("#{el}", {{ opacity: 0, y: {60 * d} }}, {{ opacity: 1, y: 0, duration: 0.28, ease: "power3.out" }}, {a:.2f});')
        js.append(f'tl.to("#{el}", {{ opacity: 0, y: {-50 * d}, duration: 0.18, ease: "power2.in" }}, {b - 0.18:.2f});')
    js.append('tl.set("#t2", { opacity: 0 }, 5.38);')        # angst replaces druck
    js.append('tl.fromTo("#seam", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power3.out" }, 0.05);')
    # Potenzial: the halves tear apart, gold behind
    js.append('tl.to("#top", { y: -960, duration: 0.5, ease: "power4.in" }, 7.92); tl.to("#bot", { y: 960, duration: 0.5, ease: "power4.in" }, 7.92); tl.to("#seam", { opacity: 0, duration: 0.2 }, 8.1);')
    js.append('tl.fromTo("#big", { opacity: 0, scale: 1.6, filter: "blur(16px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }, 8.2);')
    js.append('tl.fromTo("#big2", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, 8.88);')
    # three bands slide in from alternating sides
    for i, (b, t) in enumerate([("b1", 9.76), ("b2", 10.70), ("b3", 11.70)]):
        d = -1 if i % 2 == 0 else 1
        js.append(f'tl.fromTo("#{b}", {{ x: {1080 * d} }}, {{ x: 0, duration: 0.35, ease: "expo.out" }}, {t - 0.1:.2f});')
    js.append('tl.to(["#b1", "#b2", "#b3"], { x: (i) => (i % 2 ? 1080 : -1080), duration: 0.4, ease: "power4.in", stagger: 0.06 }, 12.2);')
    return page(V2_CSS, "".join(body), "".join(js))

# ---------------------------------------------------------------- V3  Typo-Poster
V3_CSS = """
#bg { background: #0a0a0a; }
.pw { position: absolute; font-weight: 900; letter-spacing: -0.045em; color: #f4f4f4; white-space: nowrap; transform-origin: 50% 50%; opacity: 0; line-height: .9; }
#vert { left: 540px; top: 960px; font-weight: 900; font-size: 300px; letter-spacing: -0.05em; white-space: nowrap; opacity: 0; transform: translate(-50%, -50%) rotate(-90deg); }
#entf { left: 0; width: 1080px; text-align: right; padding-right: 70px; top: 1650px; font-weight: 300; font-size: 96px; color: #fff; opacity: 0; }
"""
# word -> (x, y, size, rotation)
POS = {0: (70, 260, 150, 0), 1: (300, 380, 260, -6), 2: (80, 640, 200, 0), 3: (420, 820, 300, 4), 4: (90, 1120, 150, 0),
       5: (380, 1110, 150, 0), 6: (130, 1250, 250, -3), 7: (640, 1560, 140, 0), 8: (220, 1640, 230, 0),
       9: (60, 420, 270, -8), 10: (200, 900, 280, 5), 11: (300, 1380, 320, -4),
       12: (80, 300, 160, 0), 13: (520, 300, 160, 0), 14: (90, 470, 300, 0), 15: (160, 1150, 300, -5),
       18: (70, 360, 250, 0), 19: (330, 860, 330, -6), 20: (150, 1380, 320, 3)}
def v3():
    body = ['<div id="bg" class="full"></div>']
    js = []
    groups = [range(0, 9), range(9, 12), range(12, 16), range(18, 21)]
    ends = [3.45, 6.2, 8.12, 12.45]
    for gi, g in enumerate(groups):
        for k in g:
            x, y, s, r = POS[k]
            from PIL import ImageFont
            _f = ImageFont.truetype(str(HERE / "fonts" / "InterDisplay-Black.otf"), 100)
            wpx = _f.getlength(W[k]["w"]) * s / 100 * 0.955 * 1.05
            if wpx > 980: s = int(s * 980 / wpx); wpx = 980
            x = max(40, min(x, int(1040 - wpx)))
            acc = W[k].get("accent")
            body.append(f'<div class="pw{" gold" if acc else ""}" id="p{k}" style="left:{x}px;top:{y}px;font-size:{s}px">{W[k]["w"]}</div>')
            js.append(f'tl.fromTo("#p{k}", {{ opacity: 0, scale: 1.5, rotation: {r - 8}, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, rotation: {r}, filter: "blur(0px)", duration: 0.22, ease: "expo.out" }}, {W[k]["t"] - 0.03:.2f});')
            nxt = [kk for kk in g if kk > k]
            if nxt:
                js.append(f'tl.to("#p{k}", {{ opacity: .32, duration: 0.2 }}, {W[nxt[0]]["t"]:.2f});')
        ids = ", ".join(f'"#p{k}"' for k in g)
        js.append(f'tl.to([{ids}], {{ x: (i) => (i % 2 ? 1400 : -1400), y: (i) => (i % 3 - 1) * 400, rotation: (i) => (i % 2 ? 25 : -25), opacity: 0, duration: 0.35, ease: "power4.in", stagger: 0.01 }}, {ends[gi] - 0.25:.2f});')
    body.append('<div id="vert" class="abs gold">potenzial</div><div id="entf" class="abs">entfachen.</div>')
    js.append('tl.fromTo("#vert", { opacity: 0, scale: 1.4 }, { opacity: 1, scale: 1, duration: 0.45, ease: "expo.out" }, 8.18);')
    js.append('tl.fromTo("#entf", { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: 0.3, ease: "power3.out" }, 8.86);')
    js.append('tl.to(["#vert", "#entf"], { opacity: 0, scale: 0.9, duration: 0.25, ease: "power2.in" }, 9.5);')
    body.append('{END}<div id="grain" class="full"></div>')
    return page(V3_CSS, "".join(body), "".join(js))

# ---------------------------------------------------------------- V4  Filmtrailer
V4_CSS = """
#bgv { width: 1080px; height: 1920px; object-fit: cover; }
.bar { position: absolute; left: 0; width: 1080px; height: 250px; background: #000; z-index: 5; }
#bt { top: 0; } #bb { bottom: 0; }
.cap { position: absolute; left: 0; width: 1080px; text-align: center; font-weight: 600; font-size: 64px; letter-spacing: .22em; padding-left: .22em; color: #f2efe8; text-transform: uppercase; opacity: 0; text-shadow: 0 2px 20px rgba(0,0,0,.8); }
.cardk { background: #000; opacity: 0; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 150px; letter-spacing: .14em; padding-left: .14em; color: #f2efe8; text-transform: uppercase; z-index: 4; }
#potz { top: 830px; font-weight: 900; font-size: 140px; letter-spacing: .04em; padding-left: .04em; z-index: 3; }
.cap.gold { color: transparent; text-shadow: none; filter: drop-shadow(0 2px 16px rgba(0,0,0,.7)); }
#entz { top: 1020px; font-weight: 300; font-size: 70px; letter-spacing: .5em; padding-left: .5em; z-index: 3; }
#spark { left: 533px; top: 1093px; width: 14px; height: 14px; border-radius: 50%; background: #fff6e2; box-shadow: 0 0 18px 6px rgba(255,214,140,.95), 0 0 60px 22px rgba(227,170,90,.55); opacity: 0; z-index: 2; }
#tac { left: 0; top: 0; width: 1080px; height: 1920px; z-index: 2; }
#tac .ln { fill: none; stroke: rgba(255,255,255,.85); stroke-width: 5; stroke-linecap: round; }
#tac .gd { fill: none; stroke: #f3d9a0; stroke-width: 7; stroke-linecap: round; }
#tac circle { fill: none; stroke: rgba(255,255,255,.9); stroke-width: 5; }
#end { z-index: 6; }
"""
def v4():
    caps = [("c1", "in dir steckt mehr,", 780, 0.0, 1.0), ("c2", "als du denkst.", 880, 1.04, 2.3), ("c3", "ein funke.", 820, 2.42, 3.45),
            ("c4", "doch ein funke", 780, 6.32, 8.05), ("c5", "genügt.", 880, 7.34, 8.05), ("c6", "klarheit.", 820, 9.76, 10.62),
            ("c7", "fokus.", 820, 10.70, 11.62), ("c8", "stärke.", 820, 11.70, 12.5)]
    body = ['<video id="bgv" class="clip" src="clips/stadium.mp4" muted playsinline data-start="0" data-duration="18" data-track-index="0"></video>',
            '<div id="stage" class="clip" data-start="0" data-duration="18" data-track-index="1">',
            '<svg id="tac" class="abs" viewBox="0 0 1080 1920"><circle id="o1" cx="250" cy="1560" r="30"/><circle id="o2" cx="560" cy="1620" r="30"/><circle id="o3" cx="830" cy="1530" r="30"/>'
            '<path id="a1" class="ln" d="M280,1550 C380,1500 460,1570 530,1610"/><path id="a2" class="ln" d="M590,1605 C680,1570 740,1550 800,1540"/><path id="a3" class="gd" d="M830,1500 C760,1420 640,1380 545,1350"/></svg>',
            '<div id="spark" class="abs"></div>']
    for cid, txt, top, a, b in caps:
        g = ' gold' if cid in ("c5", "c8") else ''
        body.append(f'<div class="cap{g}" id="{cid}" style="top:{top}px">{txt}</div>')
    body.append('<div class="cap gold" id="potz">potenzial</div><div class="cap" id="entz">entfachen.</div>')
    for i, w in enumerate(["druck.", "zweifel.", "angst."]):
        body.append(f'<div class="full cardk" id="k{i}">{w}</div>')
    body.append('<div id="bt" class="bar"></div><div id="bb" class="bar"></div>{END}<div id="grain" class="full"></div></div>')
    js = []
    for cid, txt, top, a, b in caps:
        js.append(f'tl.fromTo("#{cid}", {{ opacity: 0, filter: "blur(10px)", y: 14 }}, {{ opacity: 1, filter: "blur(0px)", y: 0, duration: 0.35, ease: "power2.out" }}, {a:.2f});')
        js.append(f'tl.to("#{cid}", {{ opacity: 0, filter: "blur(8px)", duration: 0.25, ease: "power2.in" }}, {b - 0.25:.2f});')
    # hard black title cards, cut on the word
    for i, (a, b) in enumerate([(3.52, 4.30), (4.38, 5.32), (5.40, 6.20)]):
        js.append(f'tl.set("#k{i}", {{ opacity: 1 }}, {a - 0.03:.2f}); tl.set("#k{i}", {{ opacity: 0 }}, {b:.2f});')
        js.append(f'tl.fromTo("#k{i}", {{ scale: 1.08 }}, {{ scale: 1, duration: 0.8, ease: "power2.out" }}, {a - 0.03:.2f});')
    js.append('tl.fromTo("#spark", { opacity: 0, scale: 0 }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }, 2.6);')
    js.append('tl.to("#spark", { scale: 2.2, duration: 1.2, ease: "sine.inOut" }, 6.6); tl.to("#spark", { scale: 9, opacity: 0, duration: 0.7, ease: "expo.out" }, 8.2);')
    js.append('tl.fromTo("#potz", { opacity: 0, scale: 1.3, filter: "blur(14px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }, 8.2);')
    js.append('tl.fromTo("#entz", { opacity: 0 }, { opacity: 1, duration: 0.5 }, 8.88); tl.to(["#potz", "#entz"], { opacity: 0, duration: 0.3 }, 9.45);')
    js.append('gsap.set(["#a1", "#a2", "#a3"], { strokeDasharray: 1200, strokeDashoffset: 1200 });')
    js.append('tl.fromTo(["#o1", "#o2", "#o3"], { opacity: 0, scale: 0, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)", stagger: 0.08 }, 9.76);')
    js.append('tl.to("#a1", { strokeDashoffset: 0, duration: 0.5 }, 10.7); tl.to("#a2", { strokeDashoffset: 0, duration: 0.5 }, 10.9); tl.to("#a3", { strokeDashoffset: 0, duration: 0.7 }, 11.7);')
    js.append('tl.to("#tac", { opacity: 0, duration: 0.4 }, 12.4);')
    js.append('tl.fromTo(["#bt", "#bb"], { height: 250 }, { height: 0, duration: 0.6, ease: "power3.inOut" }, 12.3);')
    return page(V4_CSS, "".join(body), "".join(js))

v = sys.argv[1]
html = {"v1": v1, "v2": v2, "v3": v3, "v4": v4}[v]()
if v != "v4":   # timed wrapper for v1-v3
    html = html.replace('data-height="1920">', 'data-height="1920"><div id="stage" class="clip" data-start="0" data-duration="18" data-track-index="1">', 1)
    html = html.replace("</div><script>", "</div></div><script>", 1)
(HERE / "index.html").write_text(html)
print("built", v)
