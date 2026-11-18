// LOREBOUND – „Das Tor, das niemand öffnete“ (Fantasy #2). Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const GROUND = H * 0.74;
  const GX = W / 2, DW = 360, GT = 770, DH = GROUND - GT; // gate: centre, door width, door top, door height
  const RING_Y = GROUND - 135;
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const lastOf = (list, t) => { let l = null; for (const s of list) if (t >= s.t) l = s; return l; };
  let doorTex = null;

  function openA(t) { return t < ev.drop ? 0 : 1.2 * ease.outCubic(clamp((t - ev.drop) / 1.1)); }
  function glow(t) { return t < ev.drop ? 0 : clamp(0.6 + 0.4 * sm(ev.drop, ev.drop + 1.5, t)); }
  function shudder(t) { // door shake from hits
    let s = 0;
    for (const h of S.hits) if (t >= h.t) s += (8 + h.k * 0.5) * Math.exp(-(t - h.t) * 14);
    if (t >= 0) s += 18 * Math.exp(-t * 7);
    for (const sp of S.spells) if (t >= sp.t) s += 12 * Math.exp(-(t - sp.t) * 8);
    return s;
  }

  // ---------- door texture (built once, deterministic) ----------
  function buildDoor() {
    const c = document.createElement('canvas'); c.width = DW; c.height = Math.ceil(DH);
    const x = c.getContext('2d');
    const g = x.createLinearGradient(0, 0, DW, 0); g.addColorStop(0, '#2a170d'); g.addColorStop(0.5, '#3b2113'); g.addColorStop(1, '#22130a');
    x.fillStyle = g; x.fillRect(0, 0, DW, DH);
    const r = U.mulberry32(5);
    for (let i = 0; i <= 6; i++) { const px = i * DW / 6; x.fillStyle = 'rgba(0,0,0,0.55)'; x.fillRect(px - 3, 0, 6, DH); }
    for (let i = 0; i < 40; i++) { x.strokeStyle = `rgba(0,0,0,${0.2 + 0.2 * r()})`; x.lineWidth = 1.5; const px = r() * DW; x.beginPath(); x.moveTo(px, r() * DH); x.lineTo(px + (r() - 0.5) * 6, r() * DH); x.stroke(); }
    for (const by of [DH * 0.16, DH * 0.5, DH * 0.84]) {
      x.fillStyle = '#15161a'; x.fillRect(0, by - 20, DW, 40);
      x.strokeStyle = 'rgba(227,176,75,0.35)'; x.lineWidth = 2; x.strokeRect(0, by - 20, DW, 40);
      for (let k = 0; k < 7; k++) { x.fillStyle = 'rgba(200,170,110,0.6)'; x.beginPath(); x.arc(20 + k * (DW - 40) / 6, by, 5, 0, 7); x.fill(); }
    }
    x.strokeStyle = 'rgba(227,176,75,0.55)'; x.lineWidth = 4; x.strokeRect(2, 2, DW - 4, DH - 4);
    return c;
  }
  // draw one door leaf: dir -1 = left leaf (hinge left), +1 = right leaf (hinge right)
  function door(ctx, dir, a, dx) {
    const n = 36, sw = DW / n, ca = Math.cos(a), k = 0.28 * Math.sin(a);
    const xh = GX + dir * DW;
    for (let i = 0; i < n; i++) {
      const u = (i + 0.5) / n; // 0 at hinge
      const src = dir < 0 ? i * sw : DW - (i + 1) * sw;
      const sc = 1 + k * u, hgt = DH * sc, y0 = GT - (hgt - DH) * 0.55;
      const x0 = dir < 0 ? xh + i * sw * ca : xh - (i + 1) * sw * ca;
      ctx.drawImage(doorTex, src, 0, sw, DH, x0 + dx, y0, sw * ca + 0.8, hgt);
      if (a > 0) { ctx.fillStyle = `rgba(0,0,0,${0.5 * Math.sin(a) * u})`; ctx.fillRect(x0 + dx, y0, sw * ca + 0.8, hgt); }
    }
    // ring handle near the free edge, child height
    const u = (DW - 70) / DW, sc = 1 + k * u;
    const rx = xh - dir * (DW - 70) * ca + dx * 1, ry = GT + (RING_Y - GT) * sc - (DH * sc - DH) * 0.55;
    ctx.save(); ctx.strokeStyle = GOLD; ctx.lineWidth = 7; ctx.shadowColor = 'rgba(255,200,100,0.6)'; ctx.shadowBlur = 12;
    ctx.beginPath(); ctx.ellipse(rx, ry + 22 * sc, 26 * sc * Math.max(0.3, ca), 30 * sc, 0, 0, 7); ctx.stroke();
    ctx.fillStyle = '#6b5426'; ctx.beginPath(); ctx.arc(rx, ry - 6 * sc, 10 * sc, 0, 7); ctx.fill();
    ctx.restore();
  }

  // ---------- sky, wall, gate ----------
  function sky(ctx, t) {
    const d = sm(ev.drop, ev.end, t);
    const g = ctx.createLinearGradient(0, 0, 0, GROUND);
    g.addColorStop(0, `rgb(${lerp(5, 24, d)},${lerp(7, 18, d)},${lerp(16, 26, d)})`);
    g.addColorStop(1, `rgb(${lerp(14, 60, d)},${lerp(16, 40, d)},${lerp(28, 34, d)})`);
    ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, GROUND + 300);
    const r = U.mulberry32(3);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 90; i++) {
      const x = r() * W * 1.2 - W * 0.1, y = r() * 620, tw = 0.5 + 0.5 * Math.sin(t * (1 + r() * 2) + i);
      ctx.fillStyle = `rgba(255,240,210,${(0.15 + 0.35 * tw) * (1 - 0.6 * d)})`; ctx.fillRect(x, y, 2.2, 2.2);
    }
    ctx.restore();
    // moon
    ctx.save(); ctx.fillStyle = 'rgba(242,235,221,0.85)'; ctx.shadowColor = 'rgba(242,235,221,0.6)'; ctx.shadowBlur = 40;
    ctx.beginPath(); ctx.arc(W * 0.82, 300, 46, 0, 7); ctx.fill(); ctx.restore();
  }
  function inside(ctx, t) { // what is behind the gate (only visible when open)
    const gl = glow(t);
    ctx.save();
    ctx.beginPath(); ctx.rect(GX - DW, GT, DW * 2, DH); ctx.clip();
    ctx.fillStyle = '#07070b'; ctx.fillRect(GX - DW, GT, DW * 2, DH);
    if (gl > 0) {
      const g = ctx.createRadialGradient(GX, GROUND - 120, 20, GX, GROUND - 120, 700);
      g.addColorStop(0, `rgba(255,236,180,${gl})`); g.addColorStop(0.35, `rgba(240,180,80,${0.85 * gl})`); g.addColorStop(1, `rgba(90,50,20,${0.6 * gl})`);
      ctx.fillStyle = g; ctx.fillRect(GX - DW, GT, DW * 2, DH);
      // far hills + a road of light
      ctx.fillStyle = `rgba(120,70,30,${0.7 * gl})`;
      ctx.beginPath(); ctx.moveTo(GX - DW, GROUND - 150); ctx.quadraticCurveTo(GX - 120, GROUND - 260, GX + 40, GROUND - 170); ctx.quadraticCurveTo(GX + 200, GROUND - 230, GX + DW, GROUND - 160); ctx.lineTo(GX + DW, GROUND); ctx.lineTo(GX - DW, GROUND); ctx.fill();
      ctx.fillStyle = `rgba(255,225,150,${0.8 * gl})`;
      ctx.beginPath(); ctx.moveTo(GX - 20, GROUND - 165); ctx.lineTo(GX + 20, GROUND - 165); ctx.lineTo(GX + 160, GROUND); ctx.lineTo(GX - 160, GROUND); ctx.fill();
    }
    ctx.restore();
  }
  function wall(ctx, t) {
    const top = 640;
    ctx.save();
    // wall with the gate hole
    ctx.beginPath(); ctx.rect(-300, top, W + 600, GROUND - top + 2);
    ctx.moveTo(GX - DW, GROUND); ctx.lineTo(GX - DW, GT); ctx.lineTo(GX + DW, GT); ctx.lineTo(GX + DW, GROUND); ctx.closePath();
    const g = ctx.createLinearGradient(0, top, 0, GROUND); g.addColorStop(0, '#2a2d36'); g.addColorStop(1, '#16181e');
    ctx.fillStyle = g; ctx.fill('evenodd');
    // stone blocks
    ctx.clip('evenodd');
    ctx.strokeStyle = 'rgba(0,0,0,0.55)'; ctx.lineWidth = 3;
    for (let row = 0, y = top; y < GROUND; row++, y += 62) {
      ctx.beginPath(); ctx.moveTo(-300, y); ctx.lineTo(W + 300, y); ctx.stroke();
      for (let x = (row % 2) * 70 - 300; x < W + 300; x += 140) { ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + 62); ctx.stroke(); }
    }
    ctx.restore();
    // battlements
    ctx.fillStyle = '#2a2d36';
    for (let x = -40; x < W + 40; x += 120) ctx.fillRect(x, top - 50, 70, 52);
    ctx.strokeStyle = 'rgba(227,176,75,0.35)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(-10, top); ctx.lineTo(W + 10, top); ctx.stroke();
    // gate frame + lintel with the inscription
    ctx.fillStyle = '#1d1f26'; ctx.fillRect(GX - DW - 34, GT - 96, DW * 2 + 68, 96);
    ctx.fillRect(GX - DW - 34, GT, 34, DH); ctx.fillRect(GX + DW, GT, 34, DH);
    ctx.strokeStyle = 'rgba(227,176,75,0.6)'; ctx.lineWidth = 3; ctx.strokeRect(GX - DW - 34, GT - 96, DW * 2 + 68, 96);
    inscription(ctx, t);
  }
  function inscription(ctx, t) {
    const lit = sm(ev.read + 0.2, ev.read + 1.2, t);
    const y = GT - 30;
    ctx.save(); ctx.textAlign = 'center'; ctx.font = '700 60px "Cinzel"';
    ctx.fillStyle = `rgba(${lerp(120, 255, lit)},${lerp(112, 217, lit)},${lerp(96, 138, lit)},${lerp(0.55, 1, lit)})`;
    ctx.shadowColor = `rgba(255,200,100,${0.9 * lit})`; ctx.shadowBlur = 30 * lit;
    ctx.fillText('ZIEHEN', GX, y);
    ctx.restore();
    // moss over it, falls away when the child reads
    const r = U.mulberry32(23);
    for (let i = 0; i < 26; i++) {
      const x = GX - 200 + r() * 400, yy = y - 40 + r() * 46, rad = 10 + r() * 16, ph = r();
      const fall = sm(ev.read + 0.1 + ph * 0.4, ev.read + 1.0 + ph * 0.4, t);
      if (fall >= 1) continue;
      ctx.fillStyle = `rgba(${40 + r() * 20},${62 + r() * 20},${36},${0.75 * (1 - fall)})`;
      ctx.beginPath(); ctx.arc(x + fall * (r() - 0.5) * 40, yy + fall * 380, rad * (1 - 0.4 * fall), 0, 7); ctx.fill();
    }
  }
  function ground(ctx, t) {
    const gl = glow(t);
    const g = ctx.createLinearGradient(0, GROUND, 0, H);
    g.addColorStop(0, `rgb(${26 + 60 * gl},${22 + 40 * gl},${20 + 14 * gl})`); g.addColorStop(1, '#050404');
    ctx.fillStyle = g; ctx.fillRect(-300, GROUND, W + 600, H - GROUND + 300);
    if (gl > 0) { // light spilling out of the gate
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const lg = ctx.createLinearGradient(0, GROUND, 0, GROUND + 380);
      lg.addColorStop(0, `rgba(255,200,110,${0.45 * gl})`); lg.addColorStop(1, 'rgba(255,200,110,0)');
      ctx.fillStyle = lg; ctx.beginPath(); ctx.moveTo(GX - DW, GROUND); ctx.lineTo(GX + DW, GROUND); ctx.lineTo(GX + DW + 260, GROUND + 380); ctx.lineTo(GX - DW - 260, GROUND + 380); ctx.fill();
      ctx.restore();
    }
    ctx.strokeStyle = 'rgba(227,176,75,0.4)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(-100, GROUND); ctx.lineTo(W + 100, GROUND); ctx.stroke();
  }
  function rays(ctx, t) {
    const gl = glow(t); if (gl <= 0) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 9; i++) {
      const a = -Math.PI / 2 + (i - 4) * 0.2 + Math.sin(t * 0.6 + i) * 0.03, len = 900;
      const ox = GX, oy = GROUND - 140;
      ctx.fillStyle = `rgba(255,215,140,${0.07 * gl})`;
      ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(ox + Math.cos(a - 0.05) * len, oy + Math.sin(a - 0.05) * len); ctx.lineTo(ox + Math.cos(a + 0.05) * len, oy + Math.sin(a + 0.05) * len); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- knights ----------
  function knight(ctx, x, dir, s, run, alpha) {
    ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, GROUND); ctx.scale(dir * s, s);
    ctx.fillStyle = '#0a0b10'; ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 2.5;
    const l1 = Math.sin(run) * 22, l2 = -l1;
    ctx.fillRect(-14 + l1 * 0.5, -70, 14, 70); ctx.fillRect(2 + l2 * 0.5, -70, 14, 70);
    ctx.beginPath(); ctx.moveTo(-26, -70); ctx.lineTo(26, -70); ctx.lineTo(20, -150); ctx.lineTo(-20, -150); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.roundRect(-17, -192, 34, 42, 8); ctx.fill(); ctx.stroke();
    ctx.fillStyle = 'rgba(227,176,75,0.8)'; ctx.fillRect(2, -176, 14, 4);
    ctx.fillStyle = '#7a2a1e'; ctx.beginPath(); ctx.moveTo(-4, -192); ctx.quadraticCurveTo(-30, -220, -40, -196); ctx.quadraticCurveTo(-20, -205, -4, -186); ctx.fill();
    // shield in front + lance
    ctx.fillStyle = '#141720'; ctx.beginPath(); ctx.moveTo(22, -140); ctx.lineTo(58, -140); ctx.lineTo(58, -100); ctx.quadraticCurveTo(58, -78, 40, -68); ctx.quadraticCurveTo(22, -78, 22, -100); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.strokeStyle = 'rgba(227,176,75,0.85)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-40, -118); ctx.lineTo(120, -112); ctx.stroke();
    ctx.restore();
  }
  function knights(ctx, t) {
    if (t < 1.4) { // hook: three knights bounce off the gate on frame one
      for (const [side, off, sc] of [[1, 150, 0.95], [-1, 170, 0.9], [1, 330, 0.75]]) {
        const x = GX + side * (off + 200 * ease.outCubic(clamp(t / 0.7)));
        knight(ctx, x, -side, sc, t * 10 + off, 1 - sm(0.8, 1.4, t));
      }
    }
    if (t < ev.charge - 1 || t > ev.child + 0.6) return;
    const fade = 1 - sm(ev.child - 0.3, ev.child + 0.6, t);
    // the waiting army grows at the sides
    const done = S.hits.filter((h) => t >= h.t).length;
    for (let i = 0; i < Math.min(16, Math.ceil(done * 0.75)); i++) {
      const side = i % 2 ? 1 : -1, row = Math.floor(i / 2);
      const x = GX + side * (DW + 40 + (row % 4) * 34) + (row >= 4 ? side * 18 : 0);
      knight(ctx, x, -side, 0.55 - (row >= 4 ? 0.08 : 0), 0, 0.85 * fade);
    }
    for (const h of S.hits) {
      const dt = t - h.t; if (dt < -0.65 || dt > 0.7) continue;
      const xs = GX + h.side * (W * 0.62), xe = GX + h.side * 150;
      let x, a = 1;
      if (dt < 0) x = lerp(xs, xe, ease.inQuad(clamp((dt + 0.65) / 0.65)));
      else { x = xe + h.side * 160 * ease.outCubic(clamp(dt / 0.5)); a = 1 - clamp((dt - 0.2) / 0.5); }
      knight(ctx, x, -h.side, 0.95, (t + h.k) * 16, a * fade);
    }
  }
  function dust(ctx, t) {
    ctx.save();
    for (const h of [...S.hits, { t: 0, k: 30, side: 1 }]) {
      const dt = t - h.t; if (dt < 0 || dt > 1.0) continue;
      const r = U.mulberry32(100 + h.k);
      for (let i = 0; i < 10; i++) {
        const vx = (r() - 0.5) * 420, vy = -60 - r() * 160, px = GX + (r() - 0.5) * 200 + vx * dt, py = GROUND - 10 + vy * dt + 90 * dt * dt;
        ctx.fillStyle = `rgba(170,150,120,${0.35 * (1 - dt)})`; ctx.beginPath(); ctx.arc(px, py, 10 + 30 * dt, 0, 7); ctx.fill();
      }
    }
    ctx.restore();
  }
  function spells(ctx, t) {
    for (const sp of S.spells) {
      const dt = t - sp.t; if (dt < -0.12 || dt > 0.9) continue;
      if (sp.kind === 'zap') {
        const a = dt < 0 ? 0.5 : Math.exp(-dt * 5);
        ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.strokeStyle = `rgba(150,190,255,${a})`; ctx.lineWidth = 9; ctx.shadowColor = 'rgba(120,170,255,1)'; ctx.shadowBlur = 40;
        const r = U.mulberry32(77); ctx.beginPath(); let x = 80, y = 620; ctx.moveTo(x, y);
        for (let i = 1; i <= 8; i++) { x = lerp(80, GX - 60, i / 8) + (r() - 0.5) * 60; y = lerp(620, GT + DH * 0.45, i / 8) + (r() - 0.5) * 40; ctx.lineTo(x, y); }
        ctx.stroke(); ctx.fillStyle = `rgba(150,190,255,${0.25 * a})`; ctx.fillRect(GX - DW, GT, DW * 2, DH); ctx.restore();
      } else {
        const a = clamp(dt < 0 ? 0.3 : Math.exp(-dt * 2.5));
        ctx.save(); ctx.globalCompositeOperation = 'lighter';
        const g = ctx.createRadialGradient(GX, GT + DH * 0.5, 40, GX, GT + DH * 0.5, 520);
        g.addColorStop(0, `rgba(255,180,80,${0.75 * a})`); g.addColorStop(0.5, `rgba(255,90,20,${0.45 * a})`); g.addColorStop(1, 'rgba(255,60,10,0)');
        ctx.fillStyle = g; ctx.fillRect(GX - 560, GT - 300, 1120, DH + 400); ctx.restore();
      }
    }
  }

  // ---------- the child ----------
  function childX(t) {
    if (t < ev.child) return -100;
    const target = GX + 120;
    let x = lerp(-80, target, ease.outQuad(clamp((t - ev.child) / 2.0)));
    if (t >= ev.drop) x = target + 70 * ease.outCubic(clamp((t - ev.drop) / 0.8));
    return x;
  }
  function child(ctx, t) {
    if (t < ev.child) return;
    const x = childX(t), walking = t < ev.child + 2.0;
    const look = sm(ev.read, ev.read + 0.5, t) * (1 - sm(ev.breath - 0.2, ev.breath, t));
    const reach = sm(ev.breath - 0.5, ev.breath, t) * (1 - sm(ev.drop + 0.4, ev.drop + 0.9, t));
    const bob = walking ? Math.abs(Math.sin((t - ev.child) * 12)) * 5 : 0;
    ctx.save(); ctx.translate(x, GROUND - bob);
    const s = 1.05; ctx.scale(s, s);
    // lantern glow
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const lg = ctx.createRadialGradient(26, -60, 2, 26, -60, 120); lg.addColorStop(0, 'rgba(255,200,110,0.55)'); lg.addColorStop(1, 'rgba(255,200,110,0)');
    ctx.fillStyle = lg; ctx.fillRect(-120, -200, 260, 220); ctx.restore();
    const lstep = walking ? Math.sin((t - ev.child) * 12) * 10 : 0;
    ctx.fillStyle = '#120c0a'; ctx.fillRect(-12 + lstep * 0.4, -34, 9, 34); ctx.fillRect(3 - lstep * 0.4, -34, 9, 34);
    ctx.fillStyle = '#7a2a1e'; ctx.strokeStyle = 'rgba(227,176,75,0.8)'; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.moveTo(-28, -30); ctx.lineTo(28, -30); ctx.lineTo(14, -96); ctx.lineTo(-14, -96); ctx.closePath(); ctx.fill(); ctx.stroke();
    // arm towards the ring (left), lantern hand (right)
    const ringDX = -50, ringDY = -(RING_Y - (GROUND - 135)) - 113;
    const hx = lerp(-16, ringDX, reach), hy = lerp(-58, ringDY, reach);
    ctx.strokeStyle = '#5c1f16'; ctx.lineWidth = 9; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-10, -88); ctx.lineTo(hx, hy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(10, -88); ctx.lineTo(24, -64); ctx.stroke();
    ctx.fillStyle = '#FFD98A'; ctx.fillRect(18, -64, 16, 20);
    // head (tilts up when reading)
    ctx.save(); ctx.translate(0, -112); ctx.rotate(-0.35 * look);
    ctx.fillStyle = '#d9a77a'; ctx.beginPath(); ctx.arc(0, 0, 17, 0, 7); ctx.fill();
    ctx.fillStyle = '#2a170d'; ctx.beginPath(); ctx.arc(0, -5, 18, Math.PI, 0); ctx.fill();
    ctx.fillStyle = '#111'; ctx.beginPath(); ctx.arc(-6, 2 - 3 * look, 2.2, 0, 7); ctx.fill();
    ctx.restore();
    ctx.restore();
  }

  // ---------- text ----------
  function seriesTag(ctx) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('FANTASY IN 30 SEKUNDEN · #2', W / 2, S.SAFE.y + 34);
    ctx.fillStyle = 'rgba(227,176,75,0.5)'; ctx.fillRect(W / 2 - 60, S.SAFE.y + 52, 120, 2);
    ctx.restore();
  }
  function card(ctx, c, t) {
    if (t < c.t - 0.01 || t > c.end + 0.1) return;
    const size = c.big ? 230 : c.small ? 92 : 120, lh = size * 1.02;
    const fadeOut = 1 - clamp((t - c.end) / 0.1);
    const y0 = S.SAFE.y + 100 + (c.big ? 150 : size * 0.8);
    ctx.save(); ctx.textBaseline = 'alphabetic';
    ctx.font = `400 ${size}px "Bebas Neue"`;
    let carry = false;
    c.lines.forEach((line, i) => {
      const startGold = carry;
      if ((line.split('*').length - 1) % 2 === 1) carry = !carry;
      const appear = c.t === ev.hook || c.t === ev.drop ? 1 : ease.outCubic(clamp((t - c.t - i * 0.12) / 0.28));
      const a = appear * fadeOut; if (a <= 0) return;
      const pop = c.big ? 1 + 0.25 * Math.exp(-(t - c.t) * 8) : 1;
      const parts = line.split('*');
      const total = parts.reduce((w, p) => w + ctx.measureText(p).width, 0);
      let x = W / 2 - total / 2; const y = y0 + i * lh + (1 - appear) * 30;
      ctx.save(); ctx.translate(W / 2, y); ctx.scale(pop, pop); ctx.translate(-W / 2, -y);
      let gold = startGold;
      parts.forEach((p, j) => {
        if (j > 0) gold = !gold;
        ctx.globalAlpha = a;
        ctx.shadowColor = c.big ? 'rgba(255,190,90,0.9)' : 'rgba(0,0,0,0.95)'; ctx.shadowBlur = c.big ? 50 : 26;
        ctx.fillStyle = gold ? (c.big ? GOLD_HI : GOLD) : INK;
        ctx.fillText(p, x, y);
        x += ctx.measureText(p).width;
      });
      ctx.restore();
    });
    ctx.restore();
  }
  function counter(ctx, t) {
    if (t < ev.charge || t >= ev.child + 0.4) return;
    const y = H * 0.80;
    const ba = clamp(sm(ev.charge, ev.charge + 0.3, t) * (1 - sm(ev.child, ev.child + 0.4, t)));
    ctx.save(); ctx.globalAlpha = ba;
    ctx.fillStyle = 'rgba(6,5,6,0.8)'; ctx.fillRect(W / 2 - 330, y - 92, 660, 160);
    ctx.strokeStyle = 'rgba(227,176,75,0.5)'; ctx.lineWidth = 2; ctx.strokeRect(W / 2 - 330, y - 92, 660, 160);
    const l = lastOf(S.hits, t), n = l ? l.n.toLocaleString('de-DE') : '0', label = 'RITTER ';
    const pop = l ? Math.exp(-(t - l.t) * 8) : 0;
    const sz = 84 * (1 + 0.15 * pop);
    ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(n).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left'; ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
    ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = 'rgba(242,235,221,0.85)'; ctx.fillText(label, x0, y);
    ctx.font = `700 ${sz}px "Cinzel"`; ctx.shadowColor = `rgba(255,200,100,${0.5 + 0.5 * pop})`; ctx.shadowBlur = 20 + 30 * pop;
    ctx.fillStyle = pop > 0.4 ? GOLD_HI : GOLD; ctx.fillText(n, x0 + lw, y);
    ctx.font = '500 30px "Oswald"'; ctx.textAlign = 'center'; ctx.shadowBlur = 10;
    ctx.fillStyle = t >= ev.still ? '#FF8A6A' : 'rgba(242,235,221,0.7)';
    ctx.fillText('TOR: ZU', W / 2, y + 46);
    ctx.restore();
  }
  function footer(ctx, t) {
    const a = sm(ev.end + 0.4, ev.end + 1.0, t);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center';
    const y = H * 0.745;
    ctx.fillStyle = 'rgba(6,6,10,0.85)'; ctx.fillRect(W / 2 - 360, y - 62, 720, 130);
    ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 2; ctx.strokeRect(W / 2 - 360, y - 62, 720, 130);
    ctx.font = '700 54px "Cinzel"'; ctx.fillStyle = GOLD_HI;
    ctx.fillText('FOLGE FÜR TEIL #3', W / 2, y);
    ctx.font = '500 30px "Oswald"'; ctx.fillStyle = 'rgba(242,235,221,0.85)';
    ctx.fillText('SCHICK ES JEMANDEM, DER IMMER DRÜCKT', W / 2, y + 48);
    ctx.restore();
  }

  Studio.film({
    async init() {
      for (const [fam, url, weight] of [['Bebas Neue', 'fonts/bebas-neue-latin-400-normal.woff2', '400'], ['Cinzel', 'fonts/cinzel-latin-700-normal.woff2', '700'], ['Oswald', 'fonts/oswald-latin-500-normal.woff2', '500']]) {
        const f = new FontFace(fam, `url(${url})`, { weight }); document.fonts.add(f); await f.load();
      }
      doorTex = buildDoor();
    },
    draw(ctx, t) {
      if (!doorTex) doorTex = buildDoor();
      let shake = 0;
      for (const [h, amp] of [[ev.hook, 16], [ev.still, 8], [ev.drop, 26]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      for (const h of S.hits) if (t >= h.t) shake += (3 + h.k * 0.3) * Math.exp(-(t - h.t) * 12);
      const zoom = 1.12 - 0.12 * sm(0, ev.gate + 0.5, t) + 0.05 * sm(ev.charge, ev.still, t) - 0.05 * sm(ev.still, ev.child, t)
        + 0.16 * sm(ev.read, ev.breath, t) - 0.16 * sm(ev.drop, ev.drop + 1.6, t);
      const fx = GX, fy = lerp(H * 0.58, GT, sm(ev.read - 0.5, ev.read + 0.5, t) * (1 - sm(ev.drop, ev.drop + 1.6, t)));
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      ctx.translate(fx, fy); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy);
      sky(ctx, t);
      inside(ctx, t);
      const a = openA(t), dx = U.noise1(t * 40, 5) * shudder(t);
      door(ctx, -1, a * 0.92, dx); door(ctx, 1, a, dx);
      wall(ctx, t);
      ground(ctx, t);
      rays(ctx, t);
      dust(ctx, t);
      knights(ctx, t);
      spells(ctx, t);
      child(ctx, t);
      ctx.restore();
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(0, 0, W, H); }
      let fl = t >= ev.drop ? 0.85 * Math.exp(-(t - ev.drop) * 9) : (t < 0.2 ? 0.35 * Math.exp(-t * 14) : 0);
      for (const h of S.hits) if (t >= h.t && t < h.t + 0.3) fl += 0.12 * Math.exp(-(t - h.t) * 16);
      if (fl > 0.01) { ctx.fillStyle = `rgba(255,236,200,${clamp(fl)})`; ctx.fillRect(0, 0, W, H); }
      if (t >= ev.lesson - 0.4) { ctx.fillStyle = `rgba(4,4,8,${0.45 * sm(ev.lesson - 0.4, ev.lesson + 0.4, t)})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
