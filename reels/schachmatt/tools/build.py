"""Writes every composition of "Schachmatt" from one place, so board, phone and office stay consistent.
Run: python3 tools/build.py   (then npx hyperframes check)"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "compositions")
os.makedirs(C, exist_ok=True)
SCREENS = json.load(open(os.path.join(ROOT, "tools", "screens.json")))["screens"]

SQ, FR = 115, 40
SIZE = {"pawn": (110, 220), "rook": (120, 240), "knight": (126, 252), "bishop": (120, 260),
        "queen": (132, 282), "king": (138, 296), "crown": (150, 150)}

def sq_xy(f, r):
    """centre of square (file f, rank r) in board pixels; rank 0 is the near edge"""
    return FR + f * SQ + SQ / 2, FR + (7 - r) * SQ + SQ / 2

def head(cid):
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #0a0807; }}
    .{cid}-stage {{ position: absolute; inset: 0; perspective: 1500px; perspective-origin: 540px 1290px; }}
    .{cid}-world {{ position: absolute; left: 40px; top: 560px; width: 1000px; height: 1000px; transform-style: preserve-3d; }}
    .{cid}-world > img {{ position: absolute; left: 0; top: 0; width: 1000px; height: 1000px; }}
    .pc {{ position: absolute; width: 0; height: 0; transform-style: preserve-3d; }}
    .up {{ position: absolute; transform-style: preserve-3d; }}
    .tip {{ position: absolute; inset: 0; }}
    .tip > img {{ position: absolute; left: 0; bottom: 0; width: 100%; height: 100%; }}
    .shadow {{ position: absolute; border-radius: 50%; background: radial-gradient(closest-side, rgba(0,0,0,.55), rgba(0,0,0,0)); }}
    .bub {{ position: absolute; left: 50%; bottom: 104%; white-space: nowrap; transform: translateX(-50%);
      font: 800 44px/1 "Inter", sans-serif; color: #111; background: #f4f1ea; padding: 14px 22px; border-radius: 26px; }}
  </style>"""

def backdrop(cid):
    # the room behind the board: warm dark wood, a window's light on the wall
    return f"""<div id="{cid}-back" style="position:absolute;inset:0;background:linear-gradient(180deg,#1a120c 0%,#2a1c12 38%,#120c08 70%,#070504 100%)">
      <div style="position:absolute;left:620px;top:160px;width:300px;height:520px;background:linear-gradient(180deg,rgba(255,226,170,.16),rgba(255,226,170,0));transform:skewX(-8deg)"></div>
    </div>"""

def piece(cid, pid, kind, mat, f, r, blur=0, extra=""):
    x, y = sq_xy(f, r)
    w, h = SIZE[kind]
    src = "assets/pieces/crown.svg" if kind == "crown" else f"assets/pieces/{kind}-{mat}.svg"
    sh = "" if kind == "crown" else f'<div class="shadow" style="left:{-w*0.55}px;top:{-w*0.25}px;width:{w*1.1}px;height:{w*0.5}px"></div>'
    return f"""<div id="{cid}-{pid}" class="pc" style="left:{x}px;top:{y}px">{sh}
        <div id="{cid}-{pid}-up" class="up" style="left:{-w/2}px;top:{-h}px;width:{w}px;height:{h}px">
          <div id="{cid}-{pid}-tip" class="tip"><img id="{cid}-{pid}-img" src="{src}" style="filter:blur({blur}px)">{extra}</div>
        </div>
      </div>"""

def board_js(cid, rx):
    # keeps every piece standing up toward the lens whatever the camera's tilt
    return f"""
    const W = document.querySelector(".{cid}-world");
    const ups = document.querySelectorAll(".{cid}-world .up");
    const cam = {{ rx: {rx} }};
    const stand = () => {{ gsap.set(W, {{ rotationX: cam.rx }}); ups.forEach((u) => gsap.set(u, {{ rotationX: -cam.rx, transformOrigin: "50% 100%" }})); }};
    stand();
    const tilt = (to, at, dur, ease) => tl.to(cam, {{ rx: to, duration: dur, ease, onUpdate: stand }}, at);
    const blur = (id, px, at, dur) => tl.to("#{cid}-" + id + "-img", {{ filter: `blur(${{px}}px)`, duration: dur, ease: "power2.inOut" }}, at);
    const SQ = {SQ};
    // the lens aims at a square: that square stays on the stage's perspective origin (540, 1150)
    const aimVals = (f, r) => {{ const px = {FR} + f * SQ + SQ / 2, py = {FR} + (7 - r) * SQ + SQ / 2;
      return {{ x: 540 - 40 - px, y: 1290 - 560 - py, transformOrigin: `${{px}}px ${{py}}px` }}; }};
    const aimSet = (f, r, z) => gsap.set(W, {{ ...aimVals(f, r), z }});
    const aim = (f, r, z, at, dur, ease = "power2.inOut") => tl.to(W, {{ ...aimVals(f, r), z, duration: dur, ease }}, at);
    const move = (id, df, dr, at, dur = 0.34) => {{
      tl.to("#{cid}-" + id, {{ x: "+=" + df * SQ, y: "-=" + dr * SQ, duration: dur, ease: "power3.inOut" }}, at);
      tl.fromTo("#{cid}-" + id + "-tip", {{ y: 0 }}, {{ y: -34, duration: dur / 2, ease: "power2.out", yoyo: true, repeat: 1 }}, at);
    }};
    const fall = (id, dir, at) => {{
      tl.to("#{cid}-" + id + "-tip", {{ rotation: 86 * dir, transformOrigin: "50% 100%", duration: 0.42, ease: "power2.in" }}, at);
      tl.to("#{cid}-" + id + "-tip", {{ rotation: 80 * dir, duration: 0.09, ease: "power1.out", yoyo: true, repeat: 1 }}, at + 0.42);
    }};
"""

def scene(cid, body, js, dur, extra_css=""):
    return head(cid) + (f"\n  <style>{extra_css}</style>" if extra_css else "") + f"""
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-overlap>
    {body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""

def write(name, html):
    open(os.path.join(C, name + ".html"), "w").write(html)

# ---------------------------------------------------------------- 1. the king falls (0 - 3.6)
cid = "bking"
pcs = [piece(cid, "r1", "rook", "white", 1, 6, 7), piece(cid, "b1", "bishop", "black", 5, 6, 7), piece(cid, "n1", "knight", "black", 2, 7, 8),
       piece(cid, "r2", "rook", "black", 6, 7, 8), piece(cid, "p1", "pawn", "white", 0, 5, 6), piece(cid, "q1", "queen", "white", 6, 5, 5),
       piece(cid, "king", "king", "gold", 3, 4, 0, '<img id="bking-crown" src="assets/pieces/crown.svg" style="left:-8px;top:-24px;bottom:auto;width:154px;height:154px">'),
       piece(cid, "p2", "pawn", "black", 1, 2, 9), piece(cid, "b2", "bishop", "white", 6, 2, 10)]
body = backdrop(cid) + f"""
    <div class="{cid}-stage"><div id="{cid}-world" class="{cid}-world"><img src="assets/img/board.svg">{''.join(pcs)}</div></div>"""
js = board_js(cid, 74) + f"""
    // camera: low macro on the king, a slow push
    aimSet(3, 4.4, 700);
    aim(3, 4.1, 900, 0, 2.1, "power1.inOut");
    // crown sits on the king's head
    // the fall, in slow motion
    tl.to("#{cid}-king-tip", {{ rotation: 84, transformOrigin: "50% 100%", duration: 0.8, ease: "power2.in" }}, 1.75);
    tl.to("#{cid}-king-tip", {{ rotation: 79, duration: 0.12, ease: "power1.out", yoyo: true, repeat: 1 }}, 2.55);
    // the crown slips off as he lands
    tl.to("#bking-crown", {{ x: 70, y: 40, rotation: 35, duration: 0.35, ease: "power2.out" }}, 2.5);
    // the lens dives onto the fallen king and his crown
    aim(4.6, 4.2, 1160, 2.6, 1.0, "power2.in");
"""
write(cid, scene(cid, body, js, 3.6))

# ---------------------------------------------------------------- phone helper
PHONE_CSS = """
    .ph { position: absolute; left: 150px; top: 200px; width: 780px; height: 1560px; border-radius: 96px; background: #050506;
      box-shadow: 0 60px 120px rgba(0,0,0,.6), inset 0 0 0 3px #2a2c31; }
    .ph-scr { position: absolute; left: 18px; top: 18px; right: 18px; bottom: 18px; border-radius: 80px; overflow: hidden; background: #0d0f13; }
    .ph-bar { position: absolute; left: 0; right: 0; top: 0; height: 96px; font: 700 30px "Inter", sans-serif; color: #f2f2f2; }
    .ph-bar span { position: absolute; top: 34px; left: 64px; }
    .ph-isl { position: absolute; left: 50%; top: 26px; width: 200px; height: 56px; margin-left: -100px; border-radius: 30px; background: #000; }
    .ph-head { position: absolute; left: 0; right: 0; top: 96px; height: 120px; border-bottom: 1px solid #23262c; }
    .ph-av { position: absolute; left: 40px; top: 22px; width: 76px; height: 76px; border-radius: 50%; background: #3b5bdb; color: #fff;
      font: 800 32px/76px "Inter", sans-serif; text-align: center; }
    .ph-title { position: absolute; left: 136px; top: 26px; font: 800 36px "Inter", sans-serif; color: #f5f5f5; }
    .ph-sub { position: absolute; left: 136px; top: 72px; font: 500 26px "Inter", sans-serif; color: #8b9099; }
    .msg { position: absolute; left: 36px; max-width: 560px; padding: 20px 26px; border-radius: 34px; background: #23272e;
      font: 500 38px/1.25 "Inter", sans-serif; color: #f1f1f1; }
    .msg b { display: block; font: 800 28px "Inter", sans-serif; margin-bottom: 6px; }
    .msg.me { left: auto; right: 36px; background: #1f9d5c; }
    .typing { position: absolute; left: 36px; width: 120px; height: 64px; border-radius: 32px; background: #23272e; }
    .typing i { position: absolute; top: 26px; width: 13px; height: 13px; border-radius: 50%; background: #9aa0a9; }
"""
def phone(cid, title, sub, av, inner):
    return f"""<div id="{cid}-ph" class="ph"><div class="ph-scr">
        <div class="ph-bar"><span>09:41</span><div class="ph-isl"></div></div>
        <div class="ph-head"><div class="ph-av" style="background:{av[1]}">{av[0]}</div><div class="ph-title">{title}</div><div class="ph-sub">{sub}</div></div>
        {inner}
      </div></div>"""

def office_bg(cid, tint, blur, his=True):
    screens = "".join(
        f'<div class="{cid}-scr" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{tint};border-radius:{4*s}px"></div>'
        for (x, y, w, h, s) in SCREENS)
    return f"""<div id="{cid}-office" style="position:absolute;inset:-40px;filter:blur({blur}px)">
      <img src="assets/img/office.svg" style="position:absolute;left:40px;top:40px;width:1080px;height:1920px">
      <div style="position:absolute;left:40px;top:40px;width:1080px;height:1920px">{screens}</div>
    </div>"""

# ---------------------------------------------------------------- 2. the headline (3.6 - 6.6)
cid = "news"
news_inner = f"""
        <div style="position:absolute;left:0;right:0;top:96px;height:110px;font:900 40px/110px 'Inter',sans-serif;color:#fff;padding-left:44px;letter-spacing:-.01em">NEWS<span style="color:#e03131">24</span></div>
        <div id="news-img" style="position:absolute;left:36px;right:36px;top:220px;height:470px;border-radius:30px;overflow:hidden;background:#1a1410">
          <img src="assets/img/board.svg" style="position:absolute;left:-120px;top:-260px;width:1000px;opacity:.55;filter:blur(2px)">
          <img src="assets/pieces/crown.svg" style="position:absolute;left:190px;top:120px;width:300px;transform:rotate(-24deg)">
        </div>
        <div style="position:absolute;left:40px;right:40px;top:716px;font:900 66px/1.04 'Inter',sans-serif;color:#fff;letter-spacing:-.02em">Ex-CEO verliert alles</div>
        <div style="position:absolute;left:40px;right:40px;top:870px;font:500 34px/1.3 'Inter',sans-serif;color:#a5abb4">Firma weg. Vermögen weg.<br>Freunde auch.</div>
        <div id="news-c1" class="msg" style="top:1010px"><b style="color:#ffa94d">mike_88</b>verdient 😂😂</div>
        <div id="news-c2" class="msg" style="top:1160px"><b style="color:#74c0fc">sarah.k</b>Vom Thron in die Gosse</div>
        <div id="news-c3" class="msg" style="top:1310px"><b style="color:#b197fc">jonas</b>Wer stellt den noch ein? 🤣</div>"""
body = office_bg(cid, "#2b3a4f", 16) + f"""
    <div style="position:absolute;inset:0;background:rgba(10,8,6,.45)"></div>
    {phone(cid, "", "", ("", "transparent"), news_inner).replace('<div class="ph-head">', '<div class="ph-head" style="display:none">')}"""
js = f"""
    // carried in from the rolling crown: the picture starts huge and pulls back into the phone
    tl.fromTo("#news-ph", {{ scale: 2.6, x: 40, y: 900, rotation: -4, filter: "blur(10px)" }}, {{ scale: 1, x: 0, y: 0, rotation: -2, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }}, 0);
    tl.to("#news-ph", {{ rotation: 1, y: -14, duration: 2.3, ease: "sine.inOut" }}, 0.7);
    ["#news-c1", "#news-c2", "#news-c3"].forEach((s, i) => tl.fromTo(s, {{ opacity: 0, scale: 0.6, transformOrigin: "0% 100%" }}, {{ opacity: 1, scale: 1, duration: 0.32, ease: "back.out(1.6)" }}, 1.0 + i * 0.45));
"""
write(cid, scene(cid, body, js, 3.0, PHONE_CSS))

# ---------------------------------------------------------------- 3. the team chat (6.6 - 9.8)
cid = "chat"
chat_inner = """
        <div id="chat-sys" style="position:absolute;left:0;right:0;top:250px;text-align:center;font:600 26px 'Inter',sans-serif;color:#8b9099">Daniel (Praktikant) ist beigetreten</div>
        <div id="chat-t1" class="typing" style="top:320px"><i style="left:28px"></i><i style="left:54px"></i><i style="left:80px"></i></div>
        <div id="chat-m1" class="msg" style="top:320px"><b style="color:#ff8787">Lisa</b>Habt ihr den Neuen gesehen? 👀</div>
        <div id="chat-m2" class="msg" style="top:520px"><b style="color:#74c0fc">Tom</b>Das ist echt der Ex-Chef? Krass 😂</div>
        <div id="chat-m3" class="msg" style="top:720px"><b style="color:#ff8787">Lisa</b>Opa, der Drucker ist da drüben 🤣</div>
        <div id="chat-m4" class="msg" style="top:920px"><b style="color:#ffd43b">Kevin</b>😂😂😂</div>"""
body = office_bg(cid, "#c7d6ea", 18) + f"""
    <div style="position:absolute;inset:0;background:rgba(20,24,30,.35)"></div>
    {phone(cid, "Team Vertrieb", "Lisa, Tom, Kevin, Daniel", ("TV", "#3b5bdb"), chat_inner)}"""
js = """
    tl.fromTo("#chat-ph", { y: 30, rotation: 1.5 }, { y: -20, rotation: -1, duration: 3.2, ease: "sine.inOut" }, 0);
    tl.fromTo("#chat-office", { scale: 1.04 }, { scale: 1.0, duration: 3.2, ease: "none" }, 0);
    tl.fromTo("#chat-t1 i", { y: 0 }, { y: -8, duration: 0.16, stagger: 0.07, yoyo: true, repeat: 1, ease: "sine.inOut" }, 0.05);
    tl.set("#chat-t1", { opacity: 0 }, 0.4);
    const pop = (s, at) => tl.fromTo(s, { opacity: 0, scale: 0.7, transformOrigin: "0% 100%" }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.7)" }, at);
    tl.set("#chat-m1", { opacity: 0 }, 0);
    pop("#chat-m1", 0.4); pop("#chat-m2", 0.9); pop("#chat-m3", 2.3); pop("#chat-m4", 2.8);
"""
write(cid, scene(cid, body, js, 3.2, PHONE_CSS))

# ---------------------------------------------------------------- 4. the pieces laugh at the pawn (9.8 - 12.2)
cid = "bmock"
bub = lambda t: f'<div class="bub">{t}</div>'
pcs = [piece(cid, "n1", "knight", "black", 1, 2, 6, bub("😂")), piece(cid, "b1", "bishop", "black", 2, 3, 6),
       piece(cid, "r1", "rook", "black", 3, 3, 6, bub("Ein Nichts.")), piece(cid, "q1", "queen", "black", 4, 3, 6),
       piece(cid, "n2", "knight", "black", 5, 2, 6, bub("🤣")), piece(cid, "k1", "king", "black", 3, 5, 8),
       piece(cid, "pawn", "pawn", "white", 3, 1, 0)]
body = backdrop(cid) + f"""
    <div class="{cid}-stage"><div class="{cid}-world"><img src="assets/img/board.svg">{''.join(pcs)}</div></div>"""
js = board_js(cid, 70) + f"""
    aimSet(3, 1.7, 720);
    aim(3, 2.0, 830, 0, 2.4, "power1.inOut");
    gsap.set(".{cid}-world .bub", {{ opacity: 0 }});
    // rack focus: from the small pawn to the pieces laughing at it
    blur("pawn", 7, 0.8, 0.45);
    ["n1", "b1", "r1", "q1", "n2"].forEach((id) => blur(id, 0, 0.8, 0.45));
    blur("k1", 3, 0.8, 0.45);
    // they lean in and shake with laughter
    [["n1", 9], ["b1", 5], ["r1", 4], ["q1", -5], ["n2", -9]].forEach(([id, a], i) => {{
      tl.to("#{cid}-" + id + "-tip", {{ rotation: a, transformOrigin: "50% 100%", duration: 0.35, ease: "power2.out" }}, 0.9 + i * 0.06);
      tl.to("#{cid}-" + id + "-tip", {{ rotation: a * 0.4, duration: 0.11, ease: "sine.inOut", yoyo: true, repeat: 7 }}, 1.3 + i * 0.05);
    }});
    ["n1", "r1", "n2"].forEach((id, i) => tl.fromTo("#{cid}-" + id + "-tip .bub", {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1, duration: 0.28, ease: "back.out(2)" }}, 1.05 + i * 0.25));
"""
write(cid, scene(cid, body, js, 2.4))

# ---------------------------------------------------------------- 5. the system is down (12.2 - 16.6)
cid = "night"
body = office_bg(cid, "#ff3b30", 0) + f"""
    <div id="night-red" style="position:absolute;inset:0;background:#ff1e1e;mix-blend-mode:multiply;opacity:.35"></div>
    <div id="night-alert" style="position:absolute;left:90px;right:90px;top:230px;text-align:center;font:900 64px/1 'Inter',sans-serif;color:#fff;background:#d90f0f;padding:26px 0;border-radius:18px;letter-spacing:.02em">SYSTEM AUSGEFALLEN</div>
    <div id="night-desk" style="position:absolute;inset:0;filter:blur(12px)">
      <img src="assets/img/his-desk.svg" style="position:absolute;left:0;top:0;width:1080px;height:1920px">
      <div id="night-mon" style="position:absolute;left:78px;top:1078px;width:524px;height:324px;border-radius:6px;background:#06120b;overflow:hidden">
        {''.join(f'<div class="night-code" style="position:absolute;left:{24 + (i % 3) * 30}px;top:{22 + i * 30}px;height:12px;width:{180 + (i * 67) % 260}px;background:{"#51cf66" if i % 4 else "#94d82d"};border-radius:6px"></div>' for i in range(10))}
      </div>
    </div>"""
js = f"""
    tl.fromTo("#night-office", {{ scale: 1.0, transformOrigin: "540px 900px" }}, {{ scale: 1.12, duration: 4.4, ease: "power1.inOut" }}, 0);
    tl.fromTo("#night-red", {{ opacity: 0.22 }}, {{ opacity: 0.42, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: 7 }}, 0);
    tl.fromTo("#night-alert", {{ opacity: 0, scale: 1.2 }}, {{ opacity: 1, scale: 1, duration: 0.2, ease: "expo.out" }}, 0.1);
    tl.to("#night-alert", {{ opacity: 0, filter: "blur(8px)", duration: 0.2 }}, 2.1);
    // rack focus: from the red room to the one man who stays calm
    tl.to("#night-desk", {{ filter: "blur(0px)", duration: 0.6, ease: "power2.inOut" }}, 2.2);
    tl.to("#night-office", {{ filter: "blur(9px)", duration: 0.6, ease: "power2.inOut" }}, 2.2);
    tl.fromTo("#night-desk", {{ y: 60 }}, {{ y: 0, duration: 2.2, ease: "power2.out" }}, 2.2);
    tl.fromTo(".night-code", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.12, stagger: 0.14, ease: "none" }}, 2.7);
"""
write(cid, scene(cid, body, js, 4.4))

# ---------------------------------------------------------------- 6. the run to the last rank (16.6 - 30)
cid = "brun"
pcs = [piece(cid, "n1", "knight", "black", 4, 2, 0), piece(cid, "r1", "rook", "black", 3, 3, 0), piece(cid, "b1", "bishop", "black", 4, 4, 0),
       piece(cid, "q1", "queen", "black", 6, 6, 3), piece(cid, "k1", "king", "black", 2, 7, 4), piece(cid, "p1", "pawn", "black", 1, 5, 3),
       piece(cid, "p2", "pawn", "black", 6, 4, 2), piece(cid, "pawn", "pawn", "white", 3, 0, 0), piece(cid, "queen", "queen", "gold", 4, 7, 0)]
body = backdrop(cid) + f"""
    <div class="{cid}-stage"><div class="{cid}-world"><img src="assets/img/board.svg">{''.join(pcs)}</div></div>
    <div id="brun-shaft" style="position:absolute;left:340px;top:-200px;width:400px;height:1700px;background:linear-gradient(180deg,rgba(255,230,160,.0),rgba(255,226,150,.55) 60%,rgba(255,226,150,0));clip-path:polygon(40% 0,60% 0,100% 100%,0 100%);opacity:0"></div>
    <div id="brun-flash" style="position:absolute;inset:0;background:#fff3d1;opacity:0"></div>
    <div id="brun-shade" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.65) 0%,rgba(0,0,0,.4) 30%,rgba(0,0,0,0) 50%);opacity:0"></div>
    <div id="brun-title" style="position:absolute;left:60px;right:60px;top:250px;text-align:center;font:400 128px/1.02 'League Gothic',sans-serif;color:#f6f1e7;text-transform:uppercase;letter-spacing:.01em">
      <span class="brun-w">Unterschätz</span> <span class="brun-w">nie</span> <span class="brun-w">jemanden,</span><br><span class="brun-w">der</span> <span class="brun-w" style="color:#f2c66d">von</span> <span class="brun-w" style="color:#f2c66d">unten</span> <span class="brun-w">kommt.</span>
    </div>"""
js = board_js(cid, 66) + f"""
    // camera rides behind the pawn; it dollies up the board as the pawn advances
    aimSet(3, 0.7, 640);
    const follow = (dx, rank, at, dur = 0.5) => aim(3 + dx, rank + 0.7, 640, at, dur);
    gsap.set("#{cid}-queen", {{ opacity: 0 }});
    // step 1
    move("pawn", 0, 1, 0.5); follow(0, 1, 0.45);
    // capture the knight
    move("pawn", 1, 1, 1.8); fall("n1", 1, 1.98); tl.to("#{cid}-n1", {{ x: "+=160", y: "+=40", opacity: 0, duration: 0.5, ease: "power2.in" }}, 2.3); follow(1, 2, 1.75);
    // capture the rook
    move("pawn", -1, 1, 4.3); fall("r1", -1, 4.48); tl.to("#{cid}-r1", {{ x: "-=160", y: "+=40", opacity: 0, duration: 0.5, ease: "power2.in" }}, 4.8); follow(0, 3, 4.25);
    // capture the bishop, then run
    move("pawn", 1, 1, 6.9); fall("b1", 1, 7.08); tl.to("#{cid}-b1", {{ x: "+=160", opacity: 0, duration: 0.5, ease: "power2.in" }}, 7.4); follow(1, 4, 6.85);
    move("pawn", 0, 1, 7.45, 0.28); follow(1, 5, 7.4, 0.4);
    move("pawn", 0, 1, 7.85, 0.28); follow(1, 6, 7.8, 0.4);
    move("pawn", 0, 1, 8.25, 0.28); follow(1, 7, 8.2, 0.4);
    // promotion: a shaft of light, the pawn becomes the queen
    tl.fromTo("#brun-shaft", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.25, ease: "power2.out" }}, 8.45);
    tl.to("#brun-shaft", {{ opacity: 0.35, duration: 1.4, ease: "power2.inOut" }}, 8.9);
    tl.fromTo("#brun-flash", {{ opacity: 0 }}, {{ opacity: 0.85, duration: 0.08, ease: "none" }}, 8.62);
    tl.to("#brun-flash", {{ opacity: 0, duration: 0.6, ease: "power2.out" }}, 8.7);
    tl.set("#{cid}-pawn", {{ opacity: 0 }}, 8.7);
    tl.set("#{cid}-queen", {{ opacity: 1 }}, 8.7);
    tl.fromTo("#{cid}-queen-tip", {{ scale: 0.6, transformOrigin: "50% 100%" }}, {{ scale: 1, duration: 0.7, ease: "elastic.out(1, 0.55)" }}, 8.7);
    // hero angle: the camera drops low and pushes in on the queen
    tilt(80, 8.7, 1.6, "power2.inOut");
    aim(4, 7.35, 960, 8.7, 1.8);
    // the others back away
    [["q1", 1], ["k1", -1], ["p1", -1], ["p2", 1]].forEach(([id, d], i) => tl.to("#{cid}-" + id, {{ x: "+=" + d * 140, y: "-=60", duration: 0.8, ease: "power2.out" }}, 9.3 + i * 0.08));
    // the claim
    tl.fromTo("#brun-shade", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, 10.4);
    tl.fromTo(".brun-w", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.16, stagger: 0.09, ease: "power2.out" }}, 10.7);
"""
write(cid, scene(cid, body, js, 13.4))

# ---------------------------------------------------------------- 7. insert: the screens turn green (19.4 - 20.6)
cid = "green"
body = office_bg(cid, "#ff3b30", 0) + """
    <div id="green-wash" style="position:absolute;inset:0;background:#ff1e1e;mix-blend-mode:multiply;opacity:.35"></div>"""
js = """
    tl.fromTo("#green-office", { scale: 1.12, transformOrigin: "540px 900px" }, { scale: 1.18, duration: 1.2, ease: "none" }, 0);
    const scr = Array.from(document.querySelectorAll(".green-scr")).reverse();
    tl.to(scr, { backgroundColor: "#2fd06b", duration: 0.08, stagger: 0.045, ease: "none" }, 0.15);
    tl.to("#green-wash", { backgroundColor: "#1fbf5a", opacity: 0.22, duration: 0.6, ease: "power2.inOut" }, 0.3);
"""
write(cid, scene(cid, body, js, 1.2))

# ---------------------------------------------------------------- 8. insert: who was it? (21.6 - 23.2)
cid = "who"
who_inner = """
        <div class="msg" style="top:250px;opacity:.5"><b style="color:#ff8787">Lisa</b>Opa, der Drucker ist da drüben 🤣</div>
        <div id="who-m1" class="msg" style="top:450px"><b style="color:#74c0fc">Tom</b>System läuft wieder?! 😳</div>
        <div id="who-m2" class="msg" style="top:650px"><b style="color:#ff8787">Lisa</b>Wer… war das?</div>
        <div id="who-m3" class="msg me" style="top:850px;font-weight:800;font-size:52px">Ich.</div>"""
body = office_bg(cid, "#2fd06b", 18) + f"""
    <div style="position:absolute;inset:0;background:rgba(8,20,12,.45)"></div>
    {phone(cid, "Team Vertrieb", "Lisa, Tom, Kevin, Daniel", ("TV", "#3b5bdb"), who_inner)}"""
js = """
    tl.fromTo("#who-ph", { y: 40, scale: 1.03 }, { y: 0, scale: 1, duration: 1.6, ease: "power2.out" }, 0);
    const pop = (s, at, o = "0% 100%") => tl.fromTo(s, { opacity: 0, scale: 0.7, transformOrigin: o }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.7)" }, at);
    pop("#who-m1", 0.15); pop("#who-m2", 0.55); pop("#who-m3", 1.15, "100% 100%");
"""
write(cid, scene(cid, body, js, 1.6, PHONE_CSS))

# ---------------------------------------------------------------- captions (whole film)
CAPS = [("n1", 0.45, 1.9, "Er hatte alles."), ("n2", 3.95, 1.9, "Dann verlor er alles."),
        ("k1", 7.4, 1.6, "Das ist echt der Ex-Chef? Krass."), ("k2", 8.95, 2.1, "Opa, der Drucker ist da drüben."),
        ("k3", 12.4, 2.0, "Nichts geht mehr! Alles ist down!"), ("n3", 14.6, 2.6, "Aber sein Wissen konnte ihm keiner nehmen."),
        ("k4", 22.15, 1.2, "Wer… war das?"), ("c1", 25.2, 1.9, "Ab morgen leitest du das Team.")]
json.dump(CAPS, open(os.path.join(ROOT, "tools", "captions.json"), "w"))
caps = "".join(f'<div id="cap-{i}" class="clip cap" data-start="{s}" data-duration="{d}"><span>{t}</span></div>' for i, s, d, t in CAPS)
write("caps", f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap {{ position: absolute; left: 70px; right: 70px; top: 1170px; text-align: center; }}
    .cap span {{ display: inline-block; font: 800 50px/1.2 "Inter", sans-serif; color: #fff; background: rgba(0,0,0,.62); padding: 14px 26px; border-radius: 18px; }}
  </style>
  <div id="root" data-composition-id="caps" data-width="1080" data-height="1920">{caps}</div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    document.querySelectorAll("#root .cap span").forEach(() => {{}});
    {''.join(f'tl.fromTo("#cap-{i} span", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.14, ease: "power2.out" }}, {s});' for i, s, d, t in CAPS)}
    window.__timelines["caps"] = tl;
  </script>
</template>
""")

# ---------------------------------------------------------------- the film look (whole film): grain, vignette, a touch of gate weave
write("film", """<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
    #film-grain-wrap { position: absolute; inset: 0; opacity: .085; mix-blend-mode: overlay; }
    #film-grain { position: absolute; left: -200px; top: -200px; width: 1480px; height: 2320px;
      background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='1.1' numOctaves='2' seed='11'/><feColorMatrix type='saturate' values='0'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>");
      background-size: 240px 240px; }
    #film-vig { position: absolute; inset: 0; background: radial-gradient(120% 80% at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,.55) 100%); }
  </style>
  <div id="root" data-composition-id="film" data-width="1080" data-height="1920" data-layout-allow-overflow>
    <div id="film-grain-wrap"><div id="film-grain"></div></div>
    <div id="film-vig"></div>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    const g = document.querySelector("#film-grain");
    const n = { t: 0 };
    tl.fromTo(n, { t: 0 }, { t: 30, duration: 30, ease: "none", onUpdate() {
      const f = Math.floor(n.t * 24);
      const h = (k) => { const x = Math.sin((f + 1) * 12.9898 + k * 78.233) * 43758.5453; return x - Math.floor(x); };
      gsap.set(g, { x: Math.round(h(1) * 240), y: Math.round(h(2) * 240) });
    } }, 0);
    window.__timelines["film"] = tl;
  </script>
</template>
""")

# ---------------------------------------------------------------- root
HOSTS = [("bking", 0, 3.6, 1), ("news", 3.6, 3.0, 1), ("chat", 6.6, 3.2, 1), ("bmock", 9.8, 2.4, 1), ("night", 12.2, 4.4, 1),
         ("brun", 16.6, 13.4, 1), ("green", 19.4, 1.2, 2), ("who", 21.6, 1.6, 2), ("caps", 0, 30, 5), ("film", 0, 30, 6)]
hosts = "\n".join(
    f'      <div id="{h}" data-composition-id="{h}" data-composition-src="compositions/{h}.html" data-start="{s}" data-duration="{d}" '
    f'data-track-index="{z}" data-track-kind="{"captions" if h == "caps" else "graphics"}" data-width="1080" data-height="1920" style="z-index:{z}"></div>'
    for h, s, d, z in HOSTS)
AUDIO = json.load(open(os.path.join(ROOT, "tools", "audio.json")))
audio = "\n".join(
    f'      <audio id="{a["id"]}" class="clip" src="{a["src"]}" data-start="{a["start"]}" data-duration="{a["dur"]}" data-track-index="{a["track"]}" data-volume="{a.get("vol", 1)}"'
    + (f' data-fade-out="{a["fade"]}"' if a.get("fade") else "") + "></audio>"
    for a in AUDIO)
open(os.path.join(ROOT, "index.html"), "w").write(f"""<!doctype html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0a0807; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="30" data-fps="24" data-width="1080" data-height="1920">
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
