"""Writes every composition of "42 Falten bis zum Mond". Run: python3 tools/build.py"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "compositions")
os.makedirs(C, exist_ok=True)

def write(name, html):
    open(os.path.join(C, name + ".html"), "w").write(html)

# ------------------------------------------------------------------ desk (top-down, the sheet is folded twice)
def desk(cid, folds=True):
    p = cid
    js_folds = f"""
    // fold 1: the top half comes down onto the bottom half
    tl.to(["#{p}-tl", "#{p}-tr"], {{ rotationX: -180, transformOrigin: "50% 100%", duration: 0.55, ease: "power2.inOut" }}, 0.95);
    tl.fromTo(["#{p}-tl .sh", "#{p}-tr .sh"], {{ opacity: 0 }}, {{ opacity: 0.35, duration: 0.28, ease: "power1.in", yoyo: true, repeat: 1 }}, 0.95);
    tl.to("#{p}-shadow", {{ y: 438, height: 438, duration: 0.55, ease: "power2.inOut" }}, 0.95);
    tl.to("#{p}-shadow", {{ width: 310, duration: 0.55, ease: "power2.inOut" }}, 1.95);
    // fold 2: the right half comes over the left
    tl.to("#{p}-r", {{ rotationY: -180, transformOrigin: "0% 50%", duration: 0.55, ease: "power2.inOut" }}, 1.95);
    tl.fromTo("#{p}-r .sh", {{ opacity: 0 }}, {{ opacity: 0.3, duration: 0.28, ease: "power1.in", yoyo: true, repeat: 1 }}, 1.95);
    // the camera tips down to the desk's edge: into the side view
    tl.to("#{p}-cam", {{ rotationX: 62, scale: 2.4, y: 260, transformOrigin: "540px 1000px", transformPerspective: 1400, duration: 0.75, ease: "power3.in" }}, 3.25);
    tl.to("#{p}-cam", {{ filter: "blur(10px)", duration: 0.25, ease: "power2.in" }}, 3.75);
    tl.to("#{p}-hook", {{ opacity: 0, filter: "blur(10px)", duration: 0.2 }}, 3.3);
""" if folds else ""
    q = lambda qid, x, y: f'<div id="{p}-{qid}" class="q" style="left:{x}px;top:{y}px"><div class="sh"></div></div>'
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #24170e; }}
    #{p}-cam {{ position: absolute; inset: 0; }}
    #{p}-wood {{ position: absolute; inset: -80px; background:
      repeating-linear-gradient(92deg, rgba(0,0,0,.0) 0 22px, rgba(0,0,0,.08) 22px 24px, rgba(0,0,0,0) 24px 61px, rgba(255,220,170,.05) 61px 63px),
      linear-gradient(170deg, #6b4428 0%, #4a2d18 45%, #3a2212 100%); }}
    #{p}-light {{ position: absolute; inset: 0; background: radial-gradient(70% 45% at 40% 38%, rgba(255,226,180,.22), rgba(0,0,0,0) 70%), radial-gradient(120% 90% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 100%); }}
    #{p}-paper {{ position: absolute; left: 230px; top: 640px; width: 620px; height: 876px; transform-style: preserve-3d; }}
    #{p}-shadow {{ position: absolute; left: 244px; top: 664px; width: 620px; height: 876px; background: rgba(0,0,0,.45); filter: blur(18px); }}
    .{p}-half {{ position: absolute; top: 0; width: 310px; height: 876px; transform-style: preserve-3d; }}
    .q {{ position: absolute; width: 310px; height: 438px; background: linear-gradient(160deg, #fbfaf6, #ecebe5); transform-style: preserve-3d; }}
    .q .sh {{ position: absolute; inset: 0; background: #000; opacity: 0; }}
    #{p}-hook {{ position: absolute; left: 50px; right: 50px; top: 210px; text-align: center; font: 400 190px/0.92 "League Gothic", sans-serif;
      color: #fff; text-transform: uppercase; text-shadow: 0 10px 40px rgba(0,0,0,.6); }}
    #{p}-hook b {{ font-weight: 400; color: #ffc94d; }}
    #{p}-mug {{ position: absolute; left: 820px; top: 420px; width: 230px; height: 230px; }}
    #{p}-pen {{ position: absolute; left: 70px; top: 1560px; width: 520px; height: 26px; border-radius: 13px; background: linear-gradient(180deg, #1f3d73, #10234a); transform: rotate(-14deg); box-shadow: 0 14px 18px rgba(0,0,0,.45); }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-overlap>
    <div id="{p}-cam">
      <div id="{p}-wood"></div>
      <svg id="{p}-mug" viewBox="0 0 230 230"><circle cx="105" cy="115" r="100" fill="rgba(0,0,0,.35)" transform="translate(10 14)"/>
        <rect x="180" y="96" width="44" height="38" rx="16" fill="#8f2f24"/><circle cx="105" cy="115" r="100" fill="#c24a36"/><circle cx="105" cy="115" r="84" fill="#2b140c"/><circle cx="92" cy="100" r="30" fill="#5a3320" opacity=".5"/></svg>
      <div id="{p}-pen"></div>
      <div id="{p}-shadow"></div>
      <div id="{p}-paper">
        <div id="{p}-l" class="{p}-half" style="left:0">{q("tl", 0, 0)}{q("bl", 0, 438)}</div>
        <div id="{p}-r" class="{p}-half" style="left:310px">{q("tr", 0, 0)}{q("br", 0, 438)}</div>
      </div>
      <div id="{p}-light"></div>
    </div>
    <div id="{p}-hook">42× falten<br><b>= Mond?</b></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {js_folds}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""
write("desk", desk("desk"))
write("deskloop", desk("deskloop", folds=False))

# ------------------------------------------------------------------ the ascent: the camera doubles its view with every fold
# n(t) keyframes, local to the scene (scene starts at 4.0 s)
NK = [(0.0, 2.0), (1.6, 3.2), (2.6, 10.0), (3.6, 10.2), (5.2, 23.0), (6.2, 23.2), (8.0, 27.0), (9.6, 27.3), (10.4, 32.0), (12.2, 33.2),
      (14.0, 41.0), (14.4, 42.0), (22.8, 42.4), (25.3, 0.6)]
EASE = ["power2.inOut", "power3.out", "none", "power3.inOut", "none", "power3.inOut", "none", "power3.inOut", "power1.in", "power2.in", "power3.out", "sine.inOut", "power3.inOut"]
REFS = [  # id, img, real height m, aspect w/h, x-left (or "c" for centred at x), label
    ("cup", "cup.svg", 0.10, 1.3, 470, "Tasse · 10 cm"),
    ("house", "house.svg", 13, 14 / 13, 480, "Haus · 13 m"),
    ("burj", "burj.svg", 828, 160 / 828, 560, "Burj Khalifa · 828 m"),
    ("everest", "everest.svg", 8849, 22000 / 8849, "c720", "Mount Everest · 8.849 m"),
]
refs_html = "".join(
    f'<div id="as-{r[0]}" class="ref"><img src="assets/img/{r[1]}"><div class="chip">{r[5]}</div></div>' for r in REFS)
write("ascent", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #000; }}
    .lay {{ position: absolute; inset: 0; }}
    #as-room {{ background: radial-gradient(80% 60% at 60% 30%, #5a3d27 0%, #2a1a10 60%, #140c07 100%); }}
    #as-sky {{ background: linear-gradient(180deg, #2f6fc0 0%, #6aa6e0 55%, #c9e6f7 100%); opacity: 0; }}
    #as-dusk {{ background: linear-gradient(180deg, #02040c 0%, #0b1a3a 55%, #2f5c9c 100%); opacity: 0; }}
    #as-space {{ background: #020309; opacity: 0; }}
    #as-stars {{ opacity: 0; background-image:
      radial-gradient(1.6px 1.6px at 12% 18%, #fff, transparent), radial-gradient(1.2px 1.2px at 32% 64%, #fff, transparent),
      radial-gradient(1.8px 1.8px at 74% 22%, #fff, transparent), radial-gradient(1.1px 1.1px at 86% 70%, #fff, transparent),
      radial-gradient(1.4px 1.4px at 55% 42%, #fff, transparent), radial-gradient(1px 1px at 20% 84%, #fff, transparent),
      radial-gradient(1.5px 1.5px at 66% 88%, #fff, transparent), radial-gradient(1.2px 1.2px at 42% 8%, #fff, transparent);
      background-size: 360px 420px; }}
    #as-desk {{ position: absolute; left: -100px; right: -100px; top: 1560px; height: 500px; background: linear-gradient(180deg, #7a4e2e, #3a2212); }}
    #as-land {{ position: absolute; left: -100px; right: -100px; top: 1560px; height: 500px; background: linear-gradient(180deg, #5d7a3c 0%, #3c5527 40%, #23331a 100%); opacity: 0; }}
    #as-earth {{ position: absolute; border-radius: 50%; opacity: 0;
      background: radial-gradient(circle at 38% 30%, #5fb0ef 0%, #1d5fa8 55%, #082a52 92%, #7fc8ff 99%, rgba(127,200,255,0) 100%); }}
    #as-col {{ position: absolute; left: 255px; top: 560px; width: 150px; height: 1000px;
      background: repeating-linear-gradient(180deg, rgba(0,0,0,.07) 0 1px, rgba(0,0,0,0) 1px 3px),
                  linear-gradient(90deg, #cfccc3 0%, #fbfaf5 28%, #f1efe8 64%, #b8b4aa 100%);
      box-shadow: 18px 0 30px rgba(0,0,0,.35); }}
    #as-coltop {{ position: absolute; left: 0; right: 0; top: -10px; height: 20px; border-radius: 50%; background: #fffefa; }}
    .ref {{ position: absolute; opacity: 0; }}
    .ref img {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
    .chip {{ position: absolute; left: 0; bottom: 100%; margin-bottom: 14px; white-space: nowrap; font: 800 34px "Inter", sans-serif; color: #111;
      background: rgba(255,255,255,.92); padding: 10px 18px; border-radius: 14px; }}
    #as-iss {{ position: absolute; width: 150px; height: 68px; opacity: 0; }}
    #as-iss img {{ width: 100%; height: 100%; }}
    #as-moon {{ position: absolute; opacity: 0; }}
    #as-everest .chip {{ left: 50%; transform: translateX(-50%); }}
    #as-moon img {{ width: 100%; height: 100%; }}
    #as-clouds {{ position: absolute; opacity: 0; }}
    .tag {{ position: absolute; white-space: nowrap; font: 800 34px "Inter", sans-serif; color: #fff; background: rgba(0,0,0,.55); padding: 10px 18px; border-radius: 14px; opacity: 0; }}
    #as-hud {{ position: absolute; left: 60px; top: 190px; }}
    #as-n {{ font: 900 150px/1 "Inter", sans-serif; color: #ffc94d; letter-spacing: -.03em; text-shadow: 0 8px 30px rgba(0,0,0,.5); }}
    #as-h {{ font: 800 58px/1.1 "Inter", sans-serif; color: #fff; text-shadow: 0 6px 24px rgba(0,0,0,.6); }}
  </style>
  <div id="root" data-composition-id="ascent" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-overlap>
    <div id="as-room" class="lay"></div><div id="as-sky" class="lay"></div><div id="as-dusk" class="lay"></div><div id="as-space" class="lay"></div><div id="as-stars" class="lay"></div>
    <img id="as-clouds" src="assets/img/clouds.svg">
    <div id="as-land"></div><div id="as-desk"></div>
    <div id="as-earth"></div>
    {refs_html}
    <div id="as-iss"><img src="assets/img/iss.svg"></div><div id="as-isstag" class="tag">ISS · 420 km</div>
    <div id="as-moon"><img src="assets/img/moon.svg"></div><div id="as-moontag" class="tag">Mond · 384.400 km</div>
    <div id="as-col"><div id="as-coltop"></div></div>
    <div id="as-hud"><div id="as-n">×2</div><div id="as-h">0,4 mm</div></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const G = 1560, PX = 1000, CX = 330;
    const REFS = {json.dumps(REFS)};
    const $ = (s) => document.querySelector(s);
    const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
    const band = (v, a, b, c, d) => clamp((v - a) / (b - a)) * clamp((d - v) / (d - c));
    const fmt = (m) => {{
      const de = (x, d) => x.toLocaleString("de-DE", {{ maximumFractionDigits: d, minimumFractionDigits: d }});
      if (m < 0.01) return de(m * 1000, 1) + " mm";
      if (m < 1) return de(m * 100, 1) + " cm";
      if (m < 1000) return de(m, 0) + " m";
      return de(m / 1000, 0) + " km";
    }};
    const st = {{ n: 2 }};
    function render() {{
      const n = st.n, H = 1e-4 * Math.pow(2, n), k = PX / H;
      // the sky by altitude
      gsap.set("#as-room", {{ opacity: 1 - clamp((n - 13) / 2) }});
      gsap.set("#as-sky", {{ opacity: clamp((n - 13) / 2) * (1 - clamp((n - 26) / 3)) }});
      gsap.set("#as-dusk", {{ opacity: clamp((n - 25) / 2) * (1 - clamp((n - 30) / 2)) }});
      gsap.set("#as-space", {{ opacity: clamp((n - 29) / 2) }});
      gsap.set("#as-stars", {{ opacity: clamp((n - 29) / 3) }});
      gsap.set("#as-desk", {{ opacity: 1 - clamp((n - 12) / 2) }});
      gsap.set("#as-land", {{ opacity: clamp((n - 12) / 2) * (1 - clamp((n - 30) / 1.5)) }});
      // the paper column: always 1000 px tall; thin as a thread once the Earth is in view
      const cw = 150 - 146 * clamp((n - 29) / 6);
      gsap.set("#as-col", {{ width: cw, x: (150 - cw) / 2 }});
      // reference objects, true to scale in height
      REFS.forEach(([id, img, h, asp, xl]) => {{
        const hp = h * k, wp = hp * asp;
        const lg = Math.log2(hp);
        const o = band(lg, Math.log2(30), Math.log2(90), Math.log2(2600), Math.log2(9000));
        const left = typeof xl === "string" ? +xl.slice(1) - wp / 2 : xl;
        gsap.set("#as-" + id, {{ left, top: G - hp, width: wp, height: hp, opacity: o }});
      }});
      // clouds at 2 km
      const cy = G - 2000 * k, cs = 1000 * k / 300;
      gsap.set("#as-clouds", {{ left: -60, top: cy - 300 * cs / 2, width: 1200 * cs, height: 300 * cs, opacity: band(Math.log2(2000 * k), 4, 6, 10, 12) * 0.9 }});
      // the Earth: a flat horizon becomes a ball
      const R = 6.371e6 * k;
      gsap.set("#as-earth", {{ width: 2 * R, height: 2 * R, left: CX - R, top: G - 2, opacity: clamp((n - 27.5) / 2) }});
      // ISS at 420 km (symbol), the Moon at 384,400 km
      const iy = G - 4.2e5 * k;
      const io = band(Math.log2(4.2e5 * k), 6, 7.5, 11, 12.5);
      gsap.set("#as-iss", {{ left: CX + 70, top: iy - 34, opacity: io }}); gsap.set("#as-isstag", {{ left: CX + 230, top: iy - 30, opacity: io }});
      const mr = Math.max(1.737e6 * k, 7), my = G - (3.844e8 + 1.737e6) * k;
      gsap.set("#as-moon", {{ width: 2 * mr, height: 2 * mr, left: CX + 8, top: my - mr, opacity: clamp((n - 37) / 2) }});
      gsap.set("#as-moontag", {{ left: CX + 40, top: my - 30, opacity: clamp((n - 40) / 1.5) }});
      // HUD
      $("#as-n").textContent = "×" + Math.round(n);
      $("#as-h").textContent = fmt(1e-4 * Math.pow(2, Math.round(n)));
    }}
    render();
    const NK = {json.dumps(NK)}, EASE = {json.dumps(EASE)};
    for (let i = 1; i < NK.length; i++) {{
      tl.to(st, {{ n: NK[i][1], duration: NK[i][0] - NK[i - 1][0], ease: EASE[i - 1], onUpdate: render }}, NK[i - 1][0]);
    }}
    // the counter steps aside for the payoff titles, and returns for the rewind
    tl.to("#as-hud", {{ opacity: 0, duration: 0.25 }}, 16.2);
    tl.to("#as-hud", {{ opacity: 1, duration: 0.25 }}, 22.85);
    window.__timelines["ascent"] = tl;
  </script>
</template>
""")

# ------------------------------------------------------------------ the touch: a close-up as the column reaches the Moon
write("touch", """<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #020309; }
    #tc-cam { position: absolute; inset: 0; }
    #tc-stars { position: absolute; inset: 0; background-image:
      radial-gradient(1.6px 1.6px at 12% 18%, #fff, transparent), radial-gradient(1.2px 1.2px at 32% 64%, #fff, transparent),
      radial-gradient(1.8px 1.8px at 74% 22%, #fff, transparent), radial-gradient(1.1px 1.1px at 86% 70%, #fff, transparent),
      radial-gradient(1.4px 1.4px at 55% 42%, #fff, transparent), radial-gradient(1px 1px at 20% 84%, #fff, transparent);
      background-size: 300px 340px; opacity: .8; }
    #tc-moon { position: absolute; left: -110px; top: -260px; width: 1300px; height: 1300px; }
    #tc-earth { position: absolute; left: 640px; top: 1360px; width: 330px; height: 330px; filter: blur(3px); opacity: .9; }
    #tc-col { position: absolute; left: 470px; top: 1010px; width: 110px; height: 1100px;
      background: repeating-linear-gradient(180deg, rgba(0,0,0,.07) 0 1px, rgba(0,0,0,0) 1px 3px), linear-gradient(90deg, #a9a59b 0%, #fbfaf5 30%, #ecebe4 65%, #8f8b82 100%); }
    #tc-dust { position: absolute; left: 380px; top: 960px; width: 290px; height: 110px; border-radius: 50%;
      background: radial-gradient(closest-side, rgba(210,205,195,.85), rgba(210,205,195,0)); opacity: 0; }
    #tc-flash { position: absolute; inset: 0; background: #fff; opacity: 0; }
  </style>
  <div id="root" data-composition-id="touch" data-width="1080" data-height="1920" data-layout-allow-overflow>
    <div id="tc-cam">
      <div id="tc-stars"></div>
      <img id="tc-earth" src="assets/img/earth.svg">
      <img id="tc-moon" src="assets/img/moon.svg">
      <div id="tc-col"></div>
      <div id="tc-dust"></div>
    </div>
    <div id="tc-flash"></div>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#tc-cam", { scale: 1.12, transformOrigin: "540px 900px" }, { scale: 1.0, duration: 1.9, ease: "power2.out" }, 0);
    tl.fromTo("#tc-col", { y: 900 }, { y: 0, duration: 0.42, ease: "power3.in" }, 0);
    tl.fromTo("#tc-flash", { opacity: 0 }, { opacity: 0.55, duration: 0.05 }, 0.42);
    tl.to("#tc-flash", { opacity: 0, duration: 0.4, ease: "power2.out" }, 0.47);
    tl.fromTo("#tc-dust", { opacity: 0, scale: 0.4 }, { opacity: 1, scale: 1.6, duration: 0.5, ease: "expo.out" }, 0.42);
    tl.to("#tc-dust", { opacity: 0, duration: 0.9, ease: "power2.in" }, 0.95);
    tl.fromTo("#tc-cam", { x: 0 }, { x: 10, duration: 0.05, ease: "none", yoyo: true, repeat: 7 }, 0.42);
    window.__timelines["touch"] = tl;
  </script>
</template>
""")

# ------------------------------------------------------------------ words on screen: captions of the narration + payoff titles
LINES = [  # start, duration, text (highlighted words in *stars*)
    (0.15, 3.82, "Falte dieses Blatt *42×* – und es reicht bis zum *Mond.*"),
    (4.1, 1.7, "Klingt verrückt? Pass auf."),
    (6.0, 2.18, "*10×* gefaltet: so hoch wie eine *Tasse.*"),
    (8.4, 2.9, "*23×*: höher als das höchste *Gebäude* der Welt."),
    (11.5, 2.07, "*27×*: über dem *Mount Everest.*"),
    (13.8, 2.31, "*32×*: vorbei an der *Raumstation.*"),
    (16.4, 1.22, "Und bei *42×* …"),
    (18.4, 1.5, "… erreicht es den *Mond.*"),
    (20.3, 3.89, "Das ist *exponentielles* Wachstum. Dein Gehirn kann es sich nicht vorstellen."),
    (24.4, 2.36, "Der Weltrekord liegt übrigens bei *12×.*"),
    (27.3, 1.95, "Schaffst du *8?* Nimm dir ein Blatt."),
]
TITLES = [
    (20.5, 3.7, "4,4 Billionen<br><b>Lagen Papier</b>"),
    (24.5, 2.3, "Weltrekord:<br><b>12×</b>"),
    (27.35, 1.9, "Schaffst du<br><b>8?</b> 👇"),
]
def words(text):
    out, hl = [], False
    for w in text.split(" "):
        h = w.startswith("*")
        w2 = w.strip("*")
        end_hl = w.endswith("*") or w.endswith("*.") or w.endswith("*,")
        cls = "w hl" if (h or hl) else "w"
        out.append(f'<span class="{cls}">{w2.replace("*", "")}</span>')
        hl = (h or hl) and not end_hl and not (h and w.endswith("*"))
    return " ".join(out)
caps = "".join(f'<div id="cap-{i}" class="clip cap" data-start="{s}" data-duration="{d}"><div class="capin">{words(t)}</div></div>' for i, (s, d, t) in enumerate(LINES))
ttl = "".join(f'<div id="ttl-{i}" class="clip ttl" data-start="{s}" data-duration="{d}">{t}</div>' for i, (s, d, t) in enumerate(TITLES))
cap_js = "".join(
    f'tl.fromTo("#cap-{i} .w", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.12, stagger: {max(0.05, min(0.32, d * 0.82 / max(1, len(t.split())))):.3f}, ease: "power2.out" }}, {s});\n    '
    for i, (s, d, t) in enumerate(LINES))
ttl_js = "".join(
    f'tl.fromTo("#ttl-{i}", {{ opacity: 0, scale: 1.25, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.22, ease: "expo.out" }}, {s});\n    '
    for i, (s, d, t) in enumerate(TITLES))
write("words", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap {{ position: absolute; left: 60px; right: 60px; top: 1120px; text-align: center; }}
    .capin {{ display: inline-block; font: 900 60px/1.2 "Inter", sans-serif; color: #fff; letter-spacing: -.01em;
      background: rgba(8,8,10,.72); padding: 16px 28px; border-radius: 22px; }}
    .w {{ display: inline-block; }}
    .hl {{ color: #ffc94d; }}
    .ttl {{ position: absolute; left: 50px; right: 50px; top: 250px; text-align: center; font: 400 180px/0.92 "League Gothic", sans-serif; color: #fff;
      text-transform: uppercase; text-shadow: 0 10px 40px rgba(0,0,0,.65); }}
    .ttl b {{ font-weight: 400; color: #ffc94d; }}
  </style>
  <div id="root" data-composition-id="words" data-width="1080" data-height="1920" data-layout-allow-overlap>{caps}{ttl}</div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {cap_js}{ttl_js}
    window.__timelines["words"] = tl;
  </script>
</template>
""")

# ------------------------------------------------------------------ film look
write("film", open(os.path.join(ROOT, "..", "schachmatt", "compositions", "film.html")).read())

# ------------------------------------------------------------------ root
HOSTS = [("desk", 0, 4.0, 1), ("ascent", 4.0, 25.3, 1), ("touch", 18.4, 1.9, 2), ("deskloop", 29.3, 0.7, 3), ("words", 0, 30, 6), ("film", 0, 30, 7)]
hosts = "\n".join(
    f'      <div id="{h}" data-composition-id="{h}" data-composition-src="compositions/{h}.html" data-start="{s}" data-duration="{d}" '
    f'data-track-index="{z}" data-track-kind="{"captions" if h == "words" else "graphics"}" data-width="1080" data-height="1920" style="z-index:{z}"></div>'
    for h, s, d, z in HOSTS)
A = json.load(open(os.path.join(ROOT, "tools", "audio.json")))
audio = "\n".join(
    f'      <audio id="{a["id"]}" class="clip" src="{a["src"]}" data-start="{a["start"]}" data-duration="{a["dur"]}" data-track-index="{a["track"]}" data-volume="{a.get("vol", 1)}"'
    + (f' data-fade-in="{a["fadein"]}"' if a.get("fadein") else "") + (f' data-fade-out="{a["fade"]}"' if a.get("fade") else "")
    + (f' data-media-start="{a["ms"]}"' if a.get("ms") else "")
    + (" data-automation='" + json.dumps(a["auto"], separators=(",", ":")) + "'" if a.get("auto") else "") + "></audio>" for a in A)
open(os.path.join(ROOT, "index.html"), "w").write(f"""<!doctype html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="30" data-fps="30" data-width="1080" data-height="1920">
{hosts}
{audio}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
print("built")
