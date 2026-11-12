"""VINFlow Direct – Werbefilm 9:16, cut to "The silent force" (120 BPM: a beat every 0.5 s, a bar every 2 s).
Every scene change sits on a bar; every transition is caused by something on screen (no dissolves).
Writes index.html and compositions/*.html. Run: python3 tools/build.py"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "compositions")
RED = "#D00024"
RED_LIGHT = "#ff2a4a"
INK = "#F4F4F2"

BASE_CSS = f"""
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #0b0c0e; font-family: "Inter", sans-serif; }}
    .full {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    .line {{ position: absolute; left: 70px; right: 70px; text-align: center; color: {INK}; font-weight: 700; letter-spacing: -.025em; text-shadow: 0 4px 30px rgba(0,0,0,.7); }}
    .line .r {{ color: {RED_LIGHT}; }}
    .w {{ display: inline-block; }}
    .cap {{ position: absolute; left: 70px; right: 70px; top: 1460px; text-align: center; font: 700 60px/1.14 "Inter", sans-serif; color: {INK}; letter-spacing: -.025em; text-shadow: 0 4px 30px rgba(0,0,0,.7); }}
    .cap .r {{ color: {RED_LIGHT}; }}
    .sub {{ position: absolute; left: 80px; right: 80px; top: 1545px; text-align: center; font: 500 34px/1.3 "Inter", sans-serif; color: rgba(244,244,242,.62); }}
    .phone {{ position: absolute; width: 600px; height: 1252px; border-radius: 92px; background: #0a0a0b;
      box-shadow: 0 0 0 3px #2b2d31, 0 50px 120px rgba(0,0,0,.65); }}
    .phone .scr {{ position: absolute; left: 20px; top: 20px; width: 560px; height: 1212px; border-radius: 74px; overflow: hidden; background: #f4f3ef; }}
    .phone .isl {{ position: absolute; left: 50%; top: 34px; width: 170px; height: 48px; margin-left: -85px; border-radius: 26px; background: #000; z-index: 5; }}
    .phone .scr img.page {{ position: absolute; left: 0; top: 0; width: 560px; }}
"""

K = 1.2   # 100 BPM: a bar is 2.4 s instead of 2.0 s, so every move runs 20 % slower

def scene(cid, body, js, k=K):
    return f"""<template>
  <style>{BASE_CSS}</style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-overlap>
    {body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {js}
    // slow the whole scene down evenly, so every beat-locked move stays on the new beat grid
    tl.getChildren(false, true, true).forEach((c) => {{ c.startTime(c.startTime() * {k}); if (c.duration()) c.duration(c.duration() * {k}); }});
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""

def write(name, html):
    open(os.path.join(C, name + ".html"), "w").write(html)

def words(text):
    return " ".join(f'<span class="w">{w}</span>' for w in text.split())

# one entrance for words: crisp, per word, on the beat; one exit: a short blur
def words_in(sel, t, stagger=0.06):
    return f'tl.fromTo("{sel} .w", {{ opacity: 0, filter: "blur(10px)", scale: 1.06 }}, {{ opacity: 1, filter: "blur(0px)", scale: 1, duration: 0.28, stagger: {stagger}, ease: "expo.out" }}, {t});'
def out(sel, t):
    return f'tl.to("{sel}", {{ opacity: 0, filter: "blur(10px)", duration: 0.2, ease: "power2.in" }}, {t});'

DARK = '<div style="position:absolute;inset:0;background:radial-gradient(70% 45% at 50% 42%, rgba(208,0,36,.16), rgba(11,12,14,0) 70%), #0b0c0e"></div>'

# ------------------------------------------------------------------ 1. (0-4 s) the showroom, the question
write("s1", scene("s1", f"""
    <video id="s1-v" class="clip full" src="clips/s1.mp4" muted playsinline data-start="0" data-duration="4.8"></video>
    <div style="position:absolute;left:0;right:0;top:760px;height:820px;background:linear-gradient(180deg,rgba(8,9,11,0),rgba(8,9,11,.62) 35%,rgba(8,9,11,.62) 70%,rgba(8,9,11,0))"></div>
    <div id="s1-l1" class="line" style="top:960px;font-size:92px">{words("Du verkaufst Autos.")}</div>
    <div id="s1-l2" class="line" style="top:920px;font-size:80px;line-height:1.1">{words("Aber wo finden Kunden")}<br><span class="r">{words("deinen Bestand?")}</span></div>
""", f"""
    // frame 0: the line is already there, the music's first hit lands with the camera
    tl.fromTo("#s1-l1", {{ scale: 1.08 }}, {{ scale: 1, duration: 0.9, ease: "expo.out" }}, 0);
    tl.to("#s1-l1", {{ x: -260, opacity: 0, filter: "blur(12px)", duration: 0.16, ease: "power3.in" }}, 1.86);
    {words_in("#s1-l2", 2.1, 0.08)}
    {out("#s1-l2", 3.8)}
"""))

# ------------------------------------------------------------------ 2. (4-8 s) the dealer publishes: through the monitor into VINFlow
write("s2", scene("s2", f"""
    <img id="s2-bg" class="full" src="img/shot3_1.png">
    <div id="s2-ui" style="position:absolute;inset:0;background:#0b0c0e;opacity:0">
      {DARK}
      <div id="s2-win" style="position:absolute;left:40px;top:470px;width:1000px;border-radius:28px;overflow:hidden;background:#18191c;box-shadow:0 40px 120px rgba(0,0,0,.6),0 0 0 2px #26282c">
        <div style="height:66px;background:#202226;position:relative">
          <i style="position:absolute;left:26px;top:25px;width:16px;height:16px;border-radius:50%;background:#3a3c41"></i>
          <i style="position:absolute;left:52px;top:25px;width:16px;height:16px;border-radius:50%;background:#3a3c41"></i>
          <i style="position:absolute;left:78px;top:25px;width:16px;height:16px;border-radius:50%;background:#3a3c41"></i>
          <div style="position:absolute;left:130px;right:30px;top:14px;height:38px;border-radius:19px;background:#121315;color:#8d9097;font:500 22px/38px 'Inter';padding-left:20px">vinflowapp.com</div>
        </div>
        <img src="ui/card_dealer.png" style="display:block;width:1000px">
      </div>
      <div id="s2-direct" style="position:absolute;left:100px;top:860px;width:880px;border-radius:26px;overflow:hidden;box-shadow:0 40px 120px rgba(0,0,0,.55);opacity:0">
        <img src="ui/card_direct.png" style="display:block;width:880px">
      </div>
      <div id="s2-cursor" style="position:absolute;left:0;top:0;width:46px;height:46px;opacity:0">
        <svg viewBox="0 0 24 24" width="46" height="46"><path d="M4 2l15 9-7 1.6L9.5 20z" fill="#fff" stroke="#000" stroke-width="1.2"/></svg>
      </div>
      <div id="s2-ring" style="position:absolute;width:72px;height:72px;border-radius:50%;border:4px solid {RED};opacity:0"></div>
    </div>
    <div id="s2-cap" class="cap">{words("Ein Klick.")}<br><span class="r">{words("Dein Bestand ist online.")}</span></div>
""", f"""
    // push toward his monitor, accelerating ...
    tl.fromTo("#s2-bg", {{ scale: 1.0 }}, {{ scale: 1.6, transformOrigin: "65% 66%", duration: 1.5, ease: "power3.in" }}, 0);
    // ... and fly through it: the screen becomes the frame (no fade between worlds)
    tl.set("#s2-ui", {{ opacity: 1 }}, 1.5);
    tl.set("#s2-bg", {{ opacity: 0 }}, 1.55);
    tl.fromTo("#s2-win", {{ scale: 0.3, x: 162, y: 600, filter: "blur(6px)" }}, {{ scale: 1, x: 0, y: 0, filter: "blur(0px)", duration: 0.55, ease: "expo.out" }}, 1.5);
    // the cursor goes to the Direct channel and clicks on the beat
    tl.fromTo("#s2-cursor", {{ x: 780, y: 1560, opacity: 1 }}, {{ x: 560, y: 1030, opacity: 1, duration: 0.45, ease: "power3.out" }}, 2.0);
    tl.fromTo("#s2-ring", {{ x: 535, y: 1005, scale: 0.4, opacity: 1 }}, {{ scale: 1.6, opacity: 0, duration: 0.4, ease: "power2.out" }}, 2.5);
    tl.fromTo("#s2-direct", {{ opacity: 0, y: 70 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "expo.out" }}, 2.5);
    tl.to("#s2-win", {{ opacity: 0.3, scale: 0.97, duration: 0.5, ease: "power2.out" }}, 2.5);
    tl.to("#s2-cursor", {{ opacity: 0, duration: 0.15 }}, 2.7);
    {words_in("#s2-cap", 3.0)}
    // everything leaves upward: the phone will arrive in the same motion
    tl.to(["#s2-ui", "#s2-cap"], {{ y: -700, filter: "blur(8px)", duration: 0.3, ease: "power3.in" }}, 3.7);
"""))

# ------------------------------------------------------------------ 3. (8-12 s) his own vehicle website
write("s3", scene("s3", f"""
    {DARK}
    <div id="s3-ph" class="phone" style="left:240px;top:150px">
      <div class="isl"></div>
      <div class="scr"><img id="s3-page" class="page" src="ui/m_demo.png"></div>
    </div>
    <div id="s3-cap" class="cap">{words("Deine eigene Fahrzeugseite.")}</div>
    <div id="s3-sub" class="sub">Bestand, Preise, Details – immer aktuell.</div>
""", f"""
    // arrives from below, continuing the upward motion of the cut
    tl.fromTo("#s3-ph", {{ y: 900, filter: "blur(8px)" }}, {{ y: 0, filter: "blur(0px)", duration: 0.6, ease: "expo.out" }}, 0);
    // the page scrolls on the beat: hero, the Audi, the next cars
    tl.to("#s3-page", {{ y: -1290, duration: 0.45, ease: "power3.inOut" }}, 1.0);
    tl.to("#s3-page", {{ y: -2040, duration: 0.45, ease: "power3.inOut" }}, 2.0);
    tl.to("#s3-page", {{ y: -2780, duration: 0.45, ease: "power3.inOut" }}, 3.0);
    {words_in("#s3-cap", 0.5)}
    tl.fromTo("#s3-sub", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.9);
"""))

# ------------------------------------------------------------------ 4. (12-16 s) a QR code on the car
write("s4", scene("s4", f"""
    <img id="s4-bg" class="full" src="img/shot4_1.png">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,9,11,.35),rgba(8,9,11,0) 30%,rgba(8,9,11,0) 60%,rgba(8,9,11,.85))"></div>
    <div id="s4-card" style="position:absolute;left:330px;top:500px;width:420px;height:560px;border-radius:22px;background:#fff;box-shadow:0 30px 60px rgba(0,0,0,.45);transform:rotate(-1.5deg)">
      <img src="ui/vinflow-logo.png" style="position:absolute;left:30px;top:28px;width:64px;height:64px;border-radius:14px">
      <div style="position:absolute;left:110px;top:34px;font:700 28px 'Inter';color:#111">Fahrzeug ansehen</div>
      <div style="position:absolute;left:110px;top:70px;font:500 22px 'Inter';color:#6b6e75">Audi A4 Avant · 28.900 €</div>
      <img src="ui/qr_audi.png" style="position:absolute;left:60px;top:130px;width:300px;height:300px">
      <div style="position:absolute;left:0;right:0;bottom:36px;text-align:center;font:600 24px 'Inter';color:{RED}">Scannen &amp; anfragen</div>
    </div>
    <div id="s4-ph" class="phone" style="left:240px;top:520px">
      <div class="isl"></div>
      <div class="scr" style="background:#111">
        <div id="s4-cam" style="position:absolute;inset:0;overflow:hidden">
          <img src="img/shot4_1.png" style="position:absolute;left:-260px;top:-300px;width:1080px;height:1920px;object-fit:cover;filter:blur(1px)">
          <div style="position:absolute;left:90px;top:280px;width:380px;height:500px;border-radius:20px;background:#fff">
            <img src="ui/qr_audi.png" style="position:absolute;left:50px;top:110px;width:280px;height:280px">
          </div>
          <div style="position:absolute;left:120px;top:370px;width:320px;height:320px;border:6px solid {RED};border-radius:26px"></div>
          <div id="s4-scan" style="position:absolute;left:130px;top:380px;width:300px;height:4px;background:{RED};box-shadow:0 0 18px {RED}"></div>
        </div>
        <img id="s4-page" class="page" src="ui/m_audi.png" style="opacity:0">
      </div>
    </div>
    <div id="s4-cap" class="cap" style="top:1180px">{words("QR scannen.")}<br><span class="r">{words("Direkt zum Fahrzeug.")}</span></div>
""", f"""
    tl.fromTo("#s4-bg", {{ scale: 1.12 }}, {{ scale: 1.0, duration: 4.0, ease: "power1.out" }}, 0);
    tl.fromTo("#s4-card", {{ scale: 1.06 }}, {{ scale: 1, duration: 0.8, ease: "expo.out" }}, 0);
    {words_in("#s4-cap", 0.15)}
    {out("#s4-cap", 0.85)}
    // the phone comes up in front of the card on the beat
    tl.fromTo("#s4-ph", {{ y: 1500 }}, {{ y: 0, duration: 0.5, ease: "expo.out" }}, 1.0);
    tl.fromTo("#s4-scan", {{ y: 0 }}, {{ y: 300, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: 1 }}, 1.55);
    tl.set("#s4-cam", {{ opacity: 0 }}, 2.5);
    tl.fromTo("#s4-page", {{ opacity: 0, scale: 1.05 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "expo.out" }}, 2.5);
"""))

# ------------------------------------------------------------------ 5. (16-19 s) the request lands as a lead with its source
rows = "".join(f'''<div style="height:96px;position:relative;border-bottom:1px solid #e2e1dc">
        <div style="position:absolute;left:36px;top:32px;font:500 24px 'Inter';color:#9a9da4">0{i+1}</div>
        <div style="position:absolute;left:110px;top:28px;font:700 30px 'Inter'">{n}</div>
        <div id="s5-n{i}" style="position:absolute;right:36px;top:28px;font:700 30px 'Inter'">{c} Leads</div></div>''' for i, (n, c) in enumerate([("Google", 31), ("Instagram", 13), ("QR-Code", 9)]))
write("s5", scene("s5", f"""
    {DARK}
    <div id="s5-ph" class="phone" style="left:240px;top:520px">
      <div class="isl"></div>
      <div class="scr">
        <img class="page" src="ui/m_audi.png">
        <div style="position:absolute;left:0;right:0;bottom:0;height:130px;background:#f4f3ef;border-top:1px solid #e3e2dd">
          <div id="s5-btn" style="position:absolute;left:22px;top:26px;width:250px;height:72px;border-radius:14px;background:{RED};color:#fff;font:700 26px/72px 'Inter';text-align:center">Anfrage</div>
          <div style="position:absolute;right:22px;top:26px;width:250px;height:72px;border-radius:14px;background:#fff;border:2px solid #d9d8d3;color:#111;font:600 26px/68px 'Inter';text-align:center">WhatsApp</div>
        </div>
        <div id="s5-tap" style="position:absolute;left:107px;top:1100px;width:80px;height:80px;border-radius:50%;background:rgba(255,255,255,.6);opacity:0"></div>
      </div>
    </div>
    <div id="s5-dash" style="position:absolute;left:90px;top:330px;width:900px;border-radius:26px;background:#f7f6f2;box-shadow:0 40px 120px rgba(0,0,0,.6);opacity:0;color:#16171a">
      <div style="height:96px;border-bottom:1px solid #e2e1dc;position:relative">
        <div style="position:absolute;left:36px;top:30px;font:700 30px 'Inter'">VINFlow Direct</div>
        <div style="position:absolute;right:36px;top:34px;font:500 24px 'Inter';color:#80838a">Beispiel · letzte 30 Tage</div>
      </div>
      <div style="height:250px;position:relative;border-bottom:1px solid #e2e1dc">
        <div id="s5-total" style="position:absolute;left:36px;top:40px;font:800 120px/1 'Inter';letter-spacing:-.03em">70</div>
        <div style="position:absolute;left:36px;top:180px;font:500 28px 'Inter';color:#5f626a">Direct Leads</div>
      </div>
      {rows}
      <div style="height:100px;position:relative">
        <div style="position:absolute;left:36px;top:36px;font:500 24px 'Inter';color:#80838a">vinflowapp.com/direct/autohaus</div>
        <div style="position:absolute;right:36px;top:24px;height:52px;padding:0 22px;border-radius:12px;border:2px solid #9fd9b4;color:#1d8a4a;font:700 24px/48px 'Inter'">Online</div>
      </div>
    </div>
    <div id="s5-toast" style="position:absolute;left:90px;top:1170px;width:900px;height:170px;border-radius:24px;background:#16171a;box-shadow:0 30px 80px rgba(0,0,0,.6),0 0 0 2px {RED};opacity:0;color:#fff">
      <div style="position:absolute;left:156px;top:30px;font:800 34px 'Inter'">Neuer Lead · Probefahrt</div>
      <div style="position:absolute;left:156px;top:82px;font:500 27px 'Inter';color:#b9bcc2">Audi A4 Avant 40 TDI · Quelle: <b style="color:#fff">QR-Code</b></div>
    </div>
    <div id="s5-tile" style="position:absolute;left:120px;top:1204px;width:100px;height:100px;border-radius:22px;background:{RED};color:#fff;font:800 34px/100px 'Inter';text-align:center;opacity:0">+1</div>
    <div id="s5-cap" class="cap" style="top:1440px">{words("Jede Anfrage landet bei dir.")}<br><span class="r">{words("Mit Herkunft.")}</span></div>
""", f"""
    // tap on the downbeat
    tl.fromTo("#s5-tap", {{ opacity: 0.9, scale: 0.3 }}, {{ opacity: 0, scale: 1.8, duration: 0.4, ease: "power2.out" }}, 0.0);
    tl.fromTo("#s5-btn", {{ scale: 1 }}, {{ scale: 0.94, duration: 0.07, yoyo: true, repeat: 1 }}, 0.0);
    // carry across: the phone leaves left, VINFlow comes in from the right in one motion
    tl.to("#s5-ph", {{ x: -900, filter: "blur(8px)", duration: 0.35, ease: "power3.in" }}, 0.3);
    tl.fromTo("#s5-dash", {{ opacity: 1, x: 900, filter: "blur(8px)" }}, {{ opacity: 1, x: 0, filter: "blur(0px)", duration: 0.5, ease: "expo.out" }}, 0.5);
    tl.fromTo(["#s5-toast", "#s5-tile"], {{ opacity: 0, y: 80 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "back.out(1.5)" }}, 1.0);
    tl.set("#s5-total", {{ textContent: "71" }}, 1.0);
    tl.set("#s5-n2", {{ textContent: "10 Leads", color: "{RED}" }}, 1.0);
    tl.fromTo(["#s5-total", "#s5-n2"], {{ scale: 1.18 }}, {{ scale: 1, duration: 0.4, ease: "expo.out", transformOrigin: "100% 50%" }}, 1.0);
    {words_in("#s5-cap", 1.5)}
    // the red +1 tile takes the frame: it becomes the VINFlow tile of the finale
    tl.to(["#s5-dash", "#s5-toast", "#s5-cap"], {{ opacity: 0, filter: "blur(10px)", duration: 0.3, ease: "power2.in" }}, 3.55);
    tl.to("#s5-tile", {{ x: 370, y: -814, scale: 2.2, color: "rgba(255,255,255,0)", duration: 0.45, ease: "power3.inOut" }}, 3.55);
"""))

# ------------------------------------------------------------------ 6. (19-24 s) finale
write("s6", scene("s6", f"""
    <img id="s6-bg" class="full" src="ui/hero-dealership.png" style="opacity:.2;filter:blur(6px)">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,#0b0c0e 0%,rgba(11,12,14,.6) 45%,#0b0c0e 100%)"></div>
    <img id="s6-logo" src="ui/vinflow-logo.png" style="position:absolute;left:430px;top:330px;width:220px;height:220px;border-radius:48px;box-shadow:0 20px 60px rgba(208,0,36,.35)">
    <div id="s6-name" class="line" style="top:600px;font-size:66px">VINFlow <span class="r">Direct</span></div>
    <div id="s6-q" class="line" style="top:770px;font-size:54px">{words("Keine eigene Website?")}</div>
    <div id="s6-a" class="line" style="top:850px;font-size:42px;font-weight:500;line-height:1.3;color:rgba(244,244,242,.82)">{words("Mit VINFlow Direct wird dein Bestand online sichtbar.")}</div>
    <div id="s6-c" class="line" style="top:1040px;font-size:48px;line-height:1.35"><span class="w">Dein Bestand.</span><br><span class="w">Deine Reichweite.</span><br><span class="w r">Deine Leads.</span></div>
    <div id="s6-btn" style="position:absolute;left:290px;top:1300px;width:500px;height:96px;border-radius:18px;background:{RED};color:#fff;font:700 34px/96px 'Inter';text-align:center">30 Tage kostenlos testen</div>
    <div id="s6-url" class="line" style="top:1420px;font-size:32px;font-weight:500;color:rgba(244,244,242,.55)">vinflowapp.com</div>
""", f"""
    // the red tile from the lead lands as the logo
    tl.fromTo("#s6-logo", {{ scale: 1.0 }}, {{ scale: 1, duration: 0.01 }}, 0);
    tl.fromTo("#s6-bg", {{ opacity: 0, scale: 1.1 }}, {{ opacity: 0.2, scale: 1.0, duration: 5, ease: "none" }}, 0);
    tl.fromTo("#s6-name", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "expo.out" }}, 0.5);
    {words_in("#s6-q", 1.0)}
    {words_in("#s6-a", 1.5, 0.04)}
    tl.fromTo("#s6-c .w", {{ opacity: 0, filter: "blur(10px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.3, stagger: 0.5, ease: "expo.out" }}, 2.5);
    tl.fromTo("#s6-btn", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.6)" }}, 4.0);
    tl.fromTo("#s6-url", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 4.2);
""", k=1))

# ------------------------------------------------------------------ root
HOSTS = [("s1", 0, 4.8), ("s2", 4.8, 4.8), ("s3", 9.6, 4.8), ("s4", 14.4, 4.8), ("s5", 19.2, 4.8), ("s6", 24.0, 6.0)]
DUR = 30.0
hosts = "\n".join(f'      <div id="{h}" data-composition-id="{h}" data-composition-src="compositions/{h}.html" data-start="{s}" data-duration="{d}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:1"></div>' for h, s, d in HOSTS)
A = json.load(open(os.path.join(ROOT, "tools", "audio.json")))
audio = "\n".join(f'      <audio id="{a["id"]}" class="clip" src="{a["src"]}" data-start="{a["start"]}" data-duration="{a["dur"]}" data-track-index="{a["track"]}" data-volume="{a.get("vol", 1)}"'
                  + (f' data-media-start="{a["ms"]}"' if a.get("ms") else "") + (f' data-fade-out="{a["fade"]}"' if a.get("fade") else "") + (f' data-fade-in="{a["fadein"]}"' if a.get("fadein") else "") + "></audio>" for a in A)
open(os.path.join(ROOT, "index.html"), "w").write(f"""<!doctype html>
<html lang="de">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="ui/gsap.min.js"></script>
    <style>* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0b0c0e; }} #root {{ position: relative; width: 100%; height: 100%; }}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-fps="30" data-width="1080" data-height="1920">
{hosts}
      <div id="film" data-composition-id="film" data-composition-src="compositions/film.html" data-start="0" data-duration="{DUR}" data-track-index="2" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:5"></div>
{audio}
    </div>
    <script>window.__timelines["main"] = gsap.timeline({{ paused: true }});</script>
  </body>
</html>
""")
print("built")
