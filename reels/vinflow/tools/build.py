"""VINFlow Direct – Werbefilm 9:16. Writes index.html and compositions/*.html. Run: python3 tools/build.py"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, "compositions")
RED = "#D00024"
INK = "#F4F4F2"

BASE_CSS = f"""
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #0b0c0e; font-family: "Inter", sans-serif; }}
    .full {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
    .shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8,9,11,.55) 0%, rgba(8,9,11,0) 30%, rgba(8,9,11,0) 55%, rgba(8,9,11,.85) 100%); }}
    .line {{ position: absolute; left: 80px; right: 80px; text-align: center; color: {INK}; font-weight: 600; letter-spacing: -.02em; }}
    .line .r {{ color: {RED}; }}
    .cap {{ position: absolute; left: 80px; right: 80px; top: 1160px; text-align: center; font: 600 58px/1.15 "Inter", sans-serif; color: {INK}; letter-spacing: -.02em; }}
    .sub {{ position: absolute; left: 80px; right: 80px; top: 1250px; text-align: center; font: 500 34px/1.3 "Inter", sans-serif; color: rgba(244,244,242,.62); }}
    .phone {{ position: absolute; width: 600px; height: 1252px; border-radius: 92px; background: #0a0a0b;
      box-shadow: 0 0 0 3px #2b2d31, 0 50px 120px rgba(0,0,0,.65); }}
    .phone .scr {{ position: absolute; left: 20px; top: 20px; width: 560px; height: 1212px; border-radius: 74px; overflow: hidden; background: #f4f3ef; }}
    .phone .isl {{ position: absolute; left: 50%; top: 34px; width: 170px; height: 48px; margin-left: -85px; border-radius: 26px; background: #000; z-index: 5; }}
    .phone .scr img.page {{ position: absolute; left: 0; top: 0; width: 560px; }}
"""

def scene(cid, body, js, css=""):
    return f"""<template>
  <style>{BASE_CSS}{css}</style>
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

def words(text):
    return " ".join(f'<span class="w">{w}</span>' for w in text.split())

WIN_IN = 'tl.fromTo("{s}", {{ opacity: 0, y: 26, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }}, {t});'
OUT = 'tl.to("{s}", {{ opacity: 0, filter: "blur(8px)", duration: 0.35, ease: "power2.in" }}, {t});'

# ------------------------------------------------------------------ 1. the showroom: where do customers find your stock?
write("s1", scene("s1", f"""
    <img id="s1-a" class="full" src="img/shot1_1.png">
    <img id="s1-b" class="full" src="img/shot2_1.png" style="opacity:0">
    <div class="shade"></div>
    <div id="s1-l1" class="line" style="top:1080px;font-size:66px">Du verkaufst Autos.</div>
    <div id="s1-l2" class="line" style="top:1170px;font-size:66px;line-height:1.12">Aber wo finden Kunden<br><span class="r">deinen Bestand?</span></div>
""", f"""
    tl.fromTo("#s1-a", {{ scale: 1.12, x: 30 }}, {{ scale: 1.02, x: -20, duration: 3.2, ease: "none" }}, 0);
    tl.fromTo("#s1-b", {{ opacity: 0, scale: 1.1 }}, {{ opacity: 1, scale: 1.03, duration: 0.9, ease: "power2.inOut" }}, 2.3);
    tl.to("#s1-b", {{ scale: 1.0, duration: 1.6, ease: "none" }}, 3.2);
    {WIN_IN.format(s="#s1-l1", t=0.35)}
    {OUT.format(s="#s1-l1", t=1.95)}
    {WIN_IN.format(s="#s1-l2", t=2.2)}
    {OUT.format(s="#s1-l2", t=4.2)}
"""))

# ------------------------------------------------------------------ 2. the dealer publishes his stock with VINFlow Direct
write("s2", scene("s2", f"""
    <img id="s2-bg" class="full" src="img/shot3_0.png">
    <div class="shade"></div>
    <div id="s2-ui" style="position:absolute;inset:0;background:#0b0c0e;opacity:0">
      <div id="s2-win" style="position:absolute;left:60px;top:420px;width:960px;border-radius:26px;overflow:hidden;background:#18191c;box-shadow:0 40px 120px rgba(0,0,0,.6),0 0 0 2px #26282c">
        <div style="height:64px;background:#202226;position:relative">
          <i style="position:absolute;left:26px;top:24px;width:16px;height:16px;border-radius:50%;background:#3a3c41"></i>
          <i style="position:absolute;left:52px;top:24px;width:16px;height:16px;border-radius:50%;background:#3a3c41"></i>
          <i style="position:absolute;left:78px;top:24px;width:16px;height:16px;border-radius:50%;background:#3a3c41"></i>
          <div style="position:absolute;left:130px;right:30px;top:13px;height:38px;border-radius:19px;background:#121315;color:#8d9097;font:500 22px/38px 'Inter';padding-left:20px">vinflowapp.com</div>
        </div>
        <img src="ui/card_dealer.png" style="display:block;width:960px">
      </div>
      <div id="s2-direct" style="position:absolute;left:120px;top:820px;width:840px;border-radius:26px;overflow:hidden;box-shadow:0 40px 120px rgba(0,0,0,.55);opacity:0">
        <img src="ui/card_direct.png" style="display:block;width:840px">
      </div>
      <div id="s2-cursor" style="position:absolute;left:0;top:0;width:44px;height:44px">
        <svg viewBox="0 0 24 24" width="44" height="44"><path d="M4 2l15 9-7 1.6L9.5 20z" fill="#fff" stroke="#000" stroke-width="1.2"/></svg>
      </div>
      <div id="s2-ring" style="position:absolute;width:70px;height:70px;border-radius:50%;border:4px solid {RED};opacity:0"></div>
    </div>
    <div id="s2-cap" class="cap">Ein Klick.<br><span style="color:{RED}">Dein Bestand ist online.</span></div>
""", f"""
    tl.fromTo("#s2-bg", {{ scale: 1.0 }}, {{ scale: 1.35, transformOrigin: "52% 42%", duration: 1.8, ease: "power2.in" }}, 0);
    tl.fromTo("#s2-ui", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.35, ease: "power2.out" }}, 1.55);
    tl.fromTo("#s2-win", {{ scale: 1.08, filter: "blur(10px)" }}, {{ scale: 1, filter: "blur(0px)", duration: 0.7, ease: "expo.out" }}, 1.55);
    // the cursor goes to the Direct channel and clicks
    tl.fromTo("#s2-cursor", {{ x: 760, y: 1500 }}, {{ x: 560, y: 1000, duration: 0.8, ease: "power3.inOut" }}, 2.0);
    tl.fromTo("#s2-ring", {{ x: 535, y: 975, scale: 0.4, opacity: 1 }}, {{ scale: 1.6, opacity: 0, duration: 0.45, ease: "power2.out" }}, 2.85);
    tl.fromTo("#s2-direct", {{ opacity: 0, y: 60, scale: 0.97 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "expo.out" }}, 2.95);
    tl.to("#s2-win", {{ opacity: 0.35, scale: 0.97, duration: 0.6, ease: "power2.out" }}, 2.95);
    tl.to("#s2-cursor", {{ opacity: 0, duration: 0.2 }}, 3.3);
    {WIN_IN.format(s="#s2-cap", t=3.2)}
"""))

# ------------------------------------------------------------------ 3. his own vehicle website on a phone
write("s3", scene("s3", f"""
    <div style="position:absolute;inset:0;background:radial-gradient(60% 40% at 50% 46%, rgba(208,0,36,.22), rgba(11,12,14,0) 70%), #0b0c0e"></div>
    <div id="s3-ph" class="phone" style="left:240px;top:150px">
      <div class="isl"></div>
      <div class="scr"><img id="s3-page" class="page" src="ui/m_demo.png"></div>
    </div>
    <div id="s3-cap" class="cap" style="top:1460px">Deine eigene Fahrzeugseite.</div>
    <div id="s3-sub" class="sub" style="top:1545px">Bestand, Preise, Details – immer aktuell.</div>
""", f"""
    tl.fromTo("#s3-ph", {{ y: 520, rotation: 6, opacity: 0 }}, {{ y: 0, rotation: 0, opacity: 1, duration: 1.0, ease: "expo.out" }}, 0);
    tl.to("#s3-ph", {{ y: -14, duration: 3.6, ease: "sine.inOut" }}, 1.0);
    // the page scrolls: hero, then the first cars with their prices
    tl.fromTo("#s3-page", {{ y: 0 }}, {{ y: -1280, duration: 1.4, ease: "power3.inOut" }}, 1.3);
    tl.to("#s3-page", {{ y: -2050, duration: 1.2, ease: "power3.inOut" }}, 3.0);
    {WIN_IN.format(s="#s3-cap", t=0.6)}
    {WIN_IN.format(s="#s3-sub", t=0.9)}
"""))

# ------------------------------------------------------------------ 4. a QR code on the car: scan, land on the vehicle page
write("s4", scene("s4", f"""
    <img id="s4-bg" class="full" src="img/shot4_0.png">
    <div class="shade"></div>
    <div id="s4-card" style="position:absolute;left:330px;top:520px;width:420px;height:560px;border-radius:22px;background:#fff;box-shadow:0 30px 60px rgba(0,0,0,.45)">
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
          <img src="img/shot4_0.png" style="position:absolute;left:-260px;top:-300px;width:1080px;height:1920px;object-fit:cover;filter:blur(1px)">
          <div style="position:absolute;left:90px;top:280px;width:380px;height:500px;border-radius:20px;background:#fff">
            <img src="ui/qr_audi.png" style="position:absolute;left:50px;top:110px;width:280px;height:280px">
          </div>
          <div style="position:absolute;left:120px;top:370px;width:320px;height:320px;border:6px solid {RED};border-radius:26px"></div>
          <div id="s4-scan" style="position:absolute;left:130px;top:380px;width:300px;height:4px;background:{RED};box-shadow:0 0 18px {RED}"></div>
        </div>
        <img id="s4-page" class="page" src="ui/m_audi.png" style="opacity:0">
      </div>
    </div>
    <div id="s4-cap" class="cap" style="top:1500px">QR scannen.<br><span style="color:{RED}">Direkt zum Fahrzeug.</span></div>
""", f"""
    tl.fromTo("#s4-bg", {{ scale: 1.08 }}, {{ scale: 1.0, duration: 4.6, ease: "none" }}, 0);
    tl.fromTo("#s4-card", {{ opacity: 0, y: 30, rotation: -1.5 }}, {{ opacity: 1, y: 0, rotation: -1.5, duration: 0.8, ease: "expo.out" }}, 0.2);
    // the phone comes up in front of the card
    tl.fromTo("#s4-ph", {{ y: 1500 }}, {{ y: 0, duration: 0.9, ease: "expo.out" }}, 1.4);
    tl.fromTo("#s4-scan", {{ y: 0 }}, {{ y: 300, duration: 0.55, ease: "sine.inOut", yoyo: true, repeat: 1 }}, 2.1);
    tl.to("#s4-cam", {{ opacity: 0, duration: 0.25 }}, 3.25);
    tl.fromTo("#s4-page", {{ opacity: 0, scale: 1.04 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "expo.out" }}, 3.25);
    {WIN_IN.format(s="#s4-cap", t=0.5)}
    {OUT.format(s="#s4-cap", t=1.3)}
"""))

# ------------------------------------------------------------------ 5. the customer asks; a lead lands in VINFlow with its source
write("s5", scene("s5", f"""
    <div style="position:absolute;inset:0;background:radial-gradient(70% 45% at 50% 40%, rgba(208,0,36,.14), rgba(11,12,14,0) 70%), #0b0c0e"></div>
    <div id="s5-ph" class="phone" style="left:240px;top:150px">
      <div class="isl"></div>
      <div class="scr">
        <img class="page" src="ui/m_audi.png">
        <div style="position:absolute;left:0;right:0;bottom:0;height:130px;background:#f4f3ef;border-top:1px solid #e3e2dd">
          <div id="s5-btn" style="position:absolute;left:22px;top:26px;width:250px;height:72px;border-radius:14px;background:{RED};color:#fff;font:700 26px/72px 'Inter';text-align:center">Anfrage</div>
          <div style="position:absolute;right:22px;top:26px;width:250px;height:72px;border-radius:14px;background:#fff;border:2px solid #d9d8d3;color:#111;font:600 26px/68px 'Inter';text-align:center">WhatsApp</div>
        </div>
        <div id="s5-tap" style="position:absolute;left:107px;top:1100px;width:80px;height:80px;border-radius:50%;background:rgba(255,255,255,.55);opacity:0"></div>
      </div>
    </div>
    <div id="s5-dash" style="position:absolute;left:90px;top:300px;width:900px;border-radius:26px;background:#f7f6f2;box-shadow:0 40px 120px rgba(0,0,0,.6);opacity:0;color:#16171a">
      <div style="height:96px;border-bottom:1px solid #e2e1dc;position:relative">
        <div style="position:absolute;left:36px;top:30px;font:700 30px 'Inter'">VINFlow Direct</div>
        <div style="position:absolute;right:36px;top:34px;font:500 24px 'Inter';color:#80838a">Beispiel · letzte 30 Tage</div>
      </div>
      <div style="height:250px;position:relative;border-bottom:1px solid #e2e1dc">
        <div id="s5-total" style="position:absolute;left:36px;top:40px;font:800 120px/1 'Inter';letter-spacing:-.03em">70</div>
        <div style="position:absolute;left:36px;top:180px;font:500 28px 'Inter';color:#5f626a">Direct Leads</div>
      </div>
      {''.join(f'''<div style="height:96px;position:relative;border-bottom:1px solid #e2e1dc">
        <div style="position:absolute;left:36px;top:32px;font:500 24px 'Inter';color:#9a9da4">0{i+1}</div>
        <div style="position:absolute;left:110px;top:28px;font:700 30px 'Inter'">{n}</div>
        <div id="s5-n{i}" style="position:absolute;right:36px;top:28px;font:700 30px 'Inter'">{c} Leads</div></div>''' for i,(n,c) in enumerate([("Google",31),("Instagram",13),("QR-Code",9)]))}
      <div style="height:100px;position:relative">
        <div style="position:absolute;left:36px;top:36px;font:500 24px 'Inter';color:#80838a">vinflowapp.com/direct/autohaus</div>
        <div style="position:absolute;right:36px;top:24px;height:52px;padding:0 22px;border-radius:12px;border:2px solid #9fd9b4;color:#1d8a4a;font:700 24px/48px 'Inter'">Online</div>
      </div>
    </div>
    <div id="s5-toast" style="position:absolute;left:90px;top:1130px;width:900px;height:170px;border-radius:24px;background:#16171a;box-shadow:0 30px 80px rgba(0,0,0,.6),0 0 0 2px {RED};opacity:0;color:#fff">
      <div style="position:absolute;left:30px;top:34px;width:100px;height:100px;border-radius:22px;background:{RED};font:800 34px/100px 'Inter';text-align:center">+1</div>
      <div style="position:absolute;left:156px;top:30px;font:800 34px 'Inter'">Neuer Lead · Probefahrt</div>
      <div style="position:absolute;left:156px;top:82px;font:500 27px 'Inter';color:#b9bcc2">Audi A4 Avant 40 TDI · Quelle: <b style="color:#fff">QR-Code</b></div>
    </div>
    <div id="s5-cap" class="cap" style="top:1440px">Jede Anfrage landet bei dir.<br><span style="color:{RED}">Mit Herkunft.</span></div>
""", f"""
    tl.fromTo("#s5-ph", {{ opacity: 1 }}, {{ opacity: 1, duration: 0.01 }}, 0);
    tl.fromTo("#s5-tap", {{ opacity: 0.9, scale: 0.3 }}, {{ opacity: 0, scale: 1.8, duration: 0.45, ease: "power2.out" }}, 0.55);
    tl.fromTo("#s5-btn", {{ scale: 1 }}, {{ scale: 0.94, duration: 0.08, yoyo: true, repeat: 1 }}, 0.55);
    // the phone steps back, the dashboard comes forward
    tl.to("#s5-ph", {{ x: -420, scale: 0.8, opacity: 0, duration: 0.6, ease: "power3.in" }}, 1.0);
    tl.fromTo("#s5-dash", {{ opacity: 0, x: 300, scale: 0.96 }}, {{ opacity: 1, x: 0, scale: 1, duration: 0.7, ease: "expo.out" }}, 1.25);
    tl.fromTo("#s5-toast", {{ opacity: 0, y: 60 }}, {{ opacity: 1, y: 0, duration: 0.55, ease: "back.out(1.4)" }}, 1.9);
    tl.set("#s5-total", {{ textContent: "71" }}, 2.15);
    tl.set("#s5-n2", {{ textContent: "10 Leads", color: "{RED}" }}, 2.15);
    tl.fromTo(["#s5-total", "#s5-n2"], {{ scale: 1.15 }}, {{ scale: 1, duration: 0.4, ease: "expo.out", transformOrigin: "100% 50%" }}, 2.15);
    {WIN_IN.format(s="#s5-cap", t=2.4)}
"""))

# ------------------------------------------------------------------ 6. finale
write("s6", scene("s6", f"""
    <img id="s6-bg" class="full" src="ui/hero-dealership.png" style="opacity:.22;filter:blur(6px)">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,#0b0c0e 0%,rgba(11,12,14,.6) 45%,#0b0c0e 100%)"></div>
    <img id="s6-logo" src="ui/vinflow-logo.png" style="position:absolute;left:430px;top:330px;width:220px;height:220px;border-radius:48px;box-shadow:0 20px 60px rgba(208,0,36,.35)">
    <div id="s6-name" class="line" style="top:600px;font-size:64px;font-weight:700">VINFlow <span class="r">Direct</span></div>
    <div id="s6-q" class="line" style="top:770px;font-size:52px;font-weight:600">Keine eigene Website?</div>
    <div id="s6-a" class="line" style="top:850px;font-size:42px;font-weight:500;line-height:1.3;color:rgba(244,244,242,.8)">Mit VINFlow Direct wird dein Bestand online sichtbar.</div>
    <div id="s6-c" class="line" style="top:1040px;font-size:46px;font-weight:700;line-height:1.35">Dein Bestand.<br>Deine Reichweite.<br><span class="r">Deine Leads.</span></div>
    <div id="s6-btn" style="position:absolute;left:290px;top:1290px;width:500px;height:96px;border-radius:18px;background:{RED};color:#fff;font:700 34px/96px 'Inter';text-align:center">30 Tage kostenlos testen</div>
    <div id="s6-url" class="line" style="top:1410px;font-size:32px;font-weight:500;color:rgba(244,244,242,.55)">vinflowapp.com</div>
""", f"""
    tl.fromTo("#s6-bg", {{ scale: 1.1 }}, {{ scale: 1.0, duration: 5, ease: "none" }}, 0);
    tl.fromTo("#s6-logo", {{ opacity: 0, scale: 0.6, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.8, ease: "expo.out" }}, 0.1);
    {WIN_IN.format(s="#s6-name", t=0.45)}
    {WIN_IN.format(s="#s6-q", t=0.9)}
    {WIN_IN.format(s="#s6-a", t=1.25)}
    {WIN_IN.format(s="#s6-c", t=2.1)}
    tl.fromTo("#s6-btn", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.6)" }}, 2.7);
    {WIN_IN.format(s="#s6-url", t=2.9)}
"""))

# ------------------------------------------------------------------ root
HOSTS = [("s1", 0, 4.6), ("s2", 4.6, 4.6), ("s3", 9.2, 4.6), ("s4", 13.8, 4.6), ("s5", 18.4, 4.0), ("s6", 22.4, 4.8)]
DUR = 27.2
hosts = "\n".join(f'      <div id="{h}" data-composition-id="{h}" data-composition-src="compositions/{h}.html" data-start="{s}" data-duration="{d}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920" style="z-index:1"></div>' for h, s, d in HOSTS)
A = json.load(open(os.path.join(ROOT, "tools", "audio.json")))
audio = "\n".join(f'      <audio id="{a["id"]}" class="clip" src="{a["src"]}" data-start="{a["start"]}" data-duration="{a["dur"]}" data-track-index="{a["track"]}" data-volume="{a.get("vol", 1)}"'
                  + (f' data-fade-out="{a["fade"]}"' if a.get("fade") else "") + (f' data-fade-in="{a["fadein"]}"' if a.get("fadein") else "") + "></audio>" for a in A)
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
