// LOREBOUND – „Der Riese, der auf Feuer wartet“ (Wissen #2). Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const GROUND = H * 0.74;
  const CX = W * 0.40, CY0 = H * 0.435, CL = 430, CW = 210; // cone: top centre, length, width
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const lastOf = (list, t) => { let l = null; for (const s of list) if (t >= s.t) l = s; return l; };

  // ---------- fire intensity over time ----------
  function fire(t) {
    if (t < ev.giant) return 0.55 * (1 - sm(1.2, 2.3, t));               // a glimpse in the hook
    if (t < ev.fire) return 0;
    if (t < ev.breath) return sm(ev.fire, ev.fire + 1.4, t) * (0.85 + 0.35 * sm(ev.burn, ev.breath, t));
    if (t < ev.drop) return 0.55;
    return 0.8 * Math.exp(-(t - ev.drop) * 1.8);
  }
  function heat(t) { // how hot the cone is (0..1)
    if (t < ev.fire) return 0;
    if (t < ev.drop) return sm(ev.fire + 0.5, ev.breath, t);
    return Math.exp(-(t - ev.drop) * 1.5);
  }
  function opened(t) { return t < ev.drop ? 0 : ease.outCubic(clamp((t - ev.drop) / 0.5)); }
  function ash(t) { return sm(ev.drop, ev.drop + 2.0, t); }
  function dawn(t) { return sm(ev.seeds, ev.end, t); }

  // ---------- sky + forest ----------
  function sky(ctx, t) {
    const d = dawn(t), f = fire(t);
    const g = ctx.createLinearGradient(0, 0, 0, GROUND);
    g.addColorStop(0, `rgb(${lerp(5, 30, d)},${lerp(6, 22, d)},${lerp(14, 22, d)})`);
    g.addColorStop(0.7, `rgb(${lerp(9, 70, d)},${lerp(11, 44, d)},${lerp(20, 30, d)})`);
    g.addColorStop(1, `rgb(${lerp(14, 120, d) + 70 * f},${lerp(14, 70, d) + 25 * f},${lerp(22, 40, d)})`);
    ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, GROUND + 300);
    // stars fade with dawn and fire
    const r = U.mulberry32(3);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 90; i++) {
      const x = r() * W * 1.2 - W * 0.1, y = r() * GROUND * 0.6, tw = 0.5 + 0.5 * Math.sin(t * (1 + r() * 2) + i);
      ctx.fillStyle = `rgba(255,240,210,${(0.15 + 0.35 * tw) * (1 - d) * (1 - 0.7 * clamp(f))})`;
      ctx.fillRect(x, y, 2.2, 2.2);
    }
    ctx.restore();
    // far forest silhouettes (two layers)
    for (const [k, base, col, hgt] of [[0, GROUND - 40, '#0c1018', 380], [1, GROUND, '#07090e', 260]]) {
      const rr = U.mulberry32(11 + k);
      ctx.fillStyle = col;
      ctx.beginPath(); ctx.moveTo(-200, base + 60);
      for (let x = -200; x < W + 220; x += 70 + rr() * 50) {
        const h = hgt * (0.5 + rr() * 0.6);
        ctx.lineTo(x, base); ctx.lineTo(x + 30, base - h); ctx.lineTo(x + 60, base);
      }
      ctx.lineTo(W + 220, base + 60); ctx.closePath(); ctx.fill();
    }
  }
  function ground(ctx, t) {
    const a = ash(t), f = fire(t);
    const g = ctx.createLinearGradient(0, GROUND, 0, H);
    g.addColorStop(0, `rgb(${lerp(26, 52, a) + 40 * f},${lerp(20, 46, a) + 12 * f},${lerp(14, 44, a)})`);
    g.addColorStop(1, '#050404');
    ctx.fillStyle = g; ctx.fillRect(-300, GROUND, W + 600, H - GROUND + 300);
    ctx.strokeStyle = `rgba(227,176,75,${0.45 - 0.2 * a})`; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(-100, GROUND); ctx.lineTo(W + 100, GROUND); ctx.stroke();
    // glowing ash dots after the fire
    if (a > 0) {
      const r = U.mulberry32(41);
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 70; i++) {
        const x = r() * W, y = GROUND + 8 + r() * 170, ph = r() * 6;
        const glow = (0.25 + 0.5 * (0.5 + 0.5 * Math.sin(t * 3 + ph))) * a * (1 - 0.8 * dawn(t));
        ctx.fillStyle = `rgba(255,${120 + 60 * r()},40,${glow})`; ctx.beginPath(); ctx.arc(x, y, 2 + r() * 2.5, 0, 7); ctx.fill();
      }
      ctx.restore();
    }
  }

  // ---------- the giant trunk (right) + branch ----------
  function trunk(ctx, t) {
    const f = fire(t);
    const x0 = W * 0.66, x1 = W * 1.2;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x0 + 40, -300); ctx.bezierCurveTo(x0 + 10, H * 0.3, x0, H * 0.6, x0 - 70, GROUND + 30);
    ctx.lineTo(x1, GROUND + 30); ctx.lineTo(x1, -300); ctx.closePath();
    const g = ctx.createLinearGradient(x0, 0, x1, 0);
    g.addColorStop(0, `rgb(${74 + 90 * f},${36 + 30 * f},${22})`); g.addColorStop(0.35, '#3a1c12'); g.addColorStop(1, '#140806');
    ctx.fillStyle = g; ctx.fill();
    ctx.strokeStyle = `rgba(${227 + 28 * f},${176 - 60 * f},${75 - 40 * f},0.85)`; ctx.lineWidth = 5; ctx.stroke();
    ctx.clip();
    // bark furrows
    const r = U.mulberry32(7);
    for (let i = 0; i < 16; i++) {
      const fx = x0 + 30 + i * 32 + r() * 14;
      ctx.strokeStyle = `rgba(10,4,2,${0.45 + 0.3 * r()})`; ctx.lineWidth = 5 + r() * 6;
      ctx.beginPath(); ctx.moveTo(fx + 20, -300);
      for (let y = -300; y <= GROUND + 40; y += 120) ctx.lineTo(fx + Math.sin(y * 0.01 + i) * 8 - (y / H) * 40, y);
      ctx.stroke();
    }
    // fire light licking the bark
    if (f > 0.02) {
      ctx.globalCompositeOperation = 'lighter';
      const fg = ctx.createLinearGradient(0, GROUND, 0, GROUND - 900);
      fg.addColorStop(0, `rgba(255,110,30,${0.55 * f})`); fg.addColorStop(1, 'rgba(255,110,30,0)');
      ctx.fillStyle = fg; ctx.fillRect(x0 - 100, GROUND - 900, x1 - x0 + 200, 940);
    }
    ctx.restore();
  }
  function branch(ctx, t) {
    const sway = Math.sin(t * 0.9) * 4;
    const bx0 = W * 0.70, by0 = H * 0.395, bx1 = CX + 6, by1 = CY0 + sway;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(bx0, by0 - 30); ctx.quadraticCurveTo(W * 0.55, by0 - 26, bx1 + 10, by1 - 10);
    ctx.lineTo(bx1 - 6, by1 + 6); ctx.quadraticCurveTo(W * 0.55, by0 + 22, bx0, by0 + 34); ctx.closePath();
    ctx.fillStyle = '#2b140c'; ctx.fill();
    ctx.strokeStyle = 'rgba(227,176,75,0.75)'; ctx.lineWidth = 3; ctx.stroke();
    // a few needle sprays
    const r = U.mulberry32(17);
    ctx.strokeStyle = 'rgba(70,95,60,0.8)'; ctx.lineWidth = 3;
    for (let i = 0; i < 7; i++) {
      const u = 0.15 + i * 0.12, px = lerp(bx0, bx1, u), py = lerp(by0, by1, u) - 6;
      for (let k = 0; k < 6; k++) { const a = -Math.PI / 2 + (k - 2.5) * 0.35 + (r() - 0.5) * 0.2; ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px + Math.cos(a) * 46, py + Math.sin(a) * 46); ctx.stroke(); }
    }
    ctx.restore();
    return sway;
  }

  // ---------- the cone ----------
  function coneShape(u) { return Math.pow(Math.sin(Math.PI * clamp(u * 0.92 + 0.06)), 0.75); } // egg profile 0..1
  function cone(ctx, t, sway) {
    const op = opened(t), h = heat(t);
    const wob = (t < ev.giant ? 0.06 * Math.sin(t * 8) * Math.exp(-t * 1.5) : 0) + Math.sin(t * 1.1) * 0.02 + (t >= ev.fire && t < ev.drop ? U.noise1(t * 14, 4) * 0.03 * h : 0);
    ctx.save(); ctx.translate(CX, CY0 + sway); ctx.rotate(wob);
    ctx.scale(1 + 0.12 * op, 1 + 0.05 * op);
    // stalk
    ctx.strokeStyle = '#3a1d10'; ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(0, -12); ctx.lineTo(0, 22); ctx.stroke();
    // inner glow (seeds inside) when opening
    if (op > 0 || h > 0.3) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const ig = ctx.createRadialGradient(0, CL * 0.5, 0, 0, CL * 0.5, CW * 0.9);
      ig.addColorStop(0, `rgba(255,215,130,${0.5 * op + 0.25 * h})`); ig.addColorStop(1, 'rgba(255,180,80,0)');
      ctx.fillStyle = ig; ctx.fillRect(-CW, 0, CW * 2, CL);
      ctx.restore();
    }
    // core
    ctx.fillStyle = '#1e0e07';
    ctx.beginPath(); ctx.ellipse(0, CL * 0.52, CW * 0.36, CL * 0.47, 0, 0, 7); ctx.fill();
    // scales row by row (top to bottom)
    const rows = 10;
    for (let r = 0; r < rows; r++) {
      const u = (r + 0.5) / rows, y = 24 + u * (CL - 30), w = CW * 0.5 * coneShape(u);
      const n = r % 2 ? 4 : 5;
      for (let k = 0; k < n; k++) {
        const s = n === 1 ? 0 : (k / (n - 1)) * 2 - 1; // -1..1 across the visible face
        const x = s * w * 0.82;
        const sw = Math.max(26, w * 0.62 * (1 - 0.35 * Math.abs(s))), sh = 46 * (0.75 + 0.5 * coneShape(u));
        const ang = s * op * 0.9 + (s === 0 ? 0 : 0) , push = op * 26;
        ctx.save();
        ctx.translate(x + s * push, y + op * 10 * (u - 0.5));
        ctx.rotate(ang);
        ctx.beginPath();
        ctx.moveTo(0, -sh * 0.5); ctx.quadraticCurveTo(sw * 0.55, -sh * 0.1, 0, sh * 0.55); ctx.quadraticCurveTo(-sw * 0.55, -sh * 0.1, 0, -sh * 0.5);
        const sg = ctx.createLinearGradient(0, -sh / 2, 0, sh / 2);
        sg.addColorStop(0, '#2f160b'); sg.addColorStop(1, `rgb(${92 + 120 * h},${52 + 20 * h},${28})`);
        ctx.fillStyle = sg; ctx.fill();
        ctx.strokeStyle = h > 0.25 ? `rgba(255,${190 - 110 * h},${80 - 50 * h},0.95)` : 'rgba(227,176,75,0.85)';
        ctx.lineWidth = 2.5; ctx.stroke();
        ctx.restore();
      }
    }
    // heat halo
    if (h > 0.05) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const hg = ctx.createRadialGradient(0, CL * 0.5, CW * 0.2, 0, CL * 0.5, CW * 1.3);
      hg.addColorStop(0, `rgba(255,90,20,${0.35 * h})`); hg.addColorStop(1, 'rgba(255,90,20,0)');
      ctx.fillStyle = hg; ctx.fillRect(-CW * 1.4, -CW * 0.6, CW * 2.8, CL + CW);
      ctx.restore();
    }
    // glint in the hook and at "closed"
    for (const tg of [0.15, ev.closed + 0.1]) {
      const u = t - tg; if (u < 0 || u > 0.8) continue;
      const a = Math.sin(Math.PI * u / 0.8);
      ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.translate(-CW * 0.2, CL * 0.3);
      ctx.fillStyle = `rgba(255,230,170,${0.8 * a})`;
      ctx.beginPath(); ctx.moveTo(0, -40 * a); ctx.lineTo(6, 0); ctx.lineTo(0, 40 * a); ctx.lineTo(-6, 0); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.moveTo(-40 * a, 0); ctx.lineTo(0, 6); ctx.lineTo(40 * a, 0); ctx.lineTo(0, -6); ctx.closePath(); ctx.fill();
      ctx.restore();
    }
    ctx.restore();
  }

  // ---------- seeds (burst at the drop, land, sprout) ----------
  const SEEDS = (() => {
    const r = U.mulberry32(77), list = [];
    for (let i = 0; i < 46; i++) {
      const a = -Math.PI * (0.05 + 0.9 * r()), sp = 260 + r() * 520;
      list.push({ x0: CX + (r() - 0.5) * CW * 0.6, y0: CY0 + CL * (0.3 + 0.4 * r()), vx: Math.cos(a) * sp * (r() < 0.5 ? -1 : 1), vy: Math.sin(a) * sp * 0.8, land: GROUND + 14 + r() * 120, ph: r() * 6, spin: 3 + r() * 6, sprout: i % 5 === 0 });
    }
    return list;
  })();
  function seedPos(s, t) {
    const u = t - ev.drop; if (u < 0) return null;
    // fast burst, then fluttering descent (winged seeds)
    const drag = 2.2, k = (1 - Math.exp(-drag * u)) / drag;
    let x = s.x0 + s.vx * k + Math.sin(u * 3 + s.ph) * 26 * clamp(u);
    let y = s.y0 + s.vy * k + 95 * u * u * 0.5 + 60 * u;
    const landed = y >= s.land; if (landed) y = s.land;
    x = clamp(x, 30, W - 30);
    return { x, y, landed, u };
  }
  function seeds(ctx, t) {
    if (t < ev.drop) return;
    ctx.save();
    for (const s of SEEDS) {
      const p = seedPos(s, t); if (!p) continue;
      const rot = p.landed ? s.ph : p.u * s.spin + s.ph;
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(rot);
      ctx.shadowColor = 'rgba(255,200,110,0.9)'; ctx.shadowBlur = p.landed ? 6 : 16;
      ctx.fillStyle = p.landed ? '#c9a061' : GOLD_HI;
      ctx.beginPath(); ctx.ellipse(0, 0, 11, 6.5, 0, 0, 7); ctx.fill();
      ctx.fillStyle = '#5a3a1c'; ctx.beginPath(); ctx.ellipse(0, 0, 3.5, 2.5, 0, 0, 7); ctx.fill();
      ctx.restore();
    }
    ctx.restore();
  }
  function sprouts(ctx, t) {
    const g0 = ev.seeds + 0.8; if (t < g0) return;
    SEEDS.filter((s) => s.sprout).forEach((s, i) => {
      const p = seedPos(s, t); if (!p || !p.landed) return;
      const gr = ease.outCubic(clamp((t - g0 - i * 0.25) / 2.2)); if (gr <= 0) return;
      const hgt = (55 + (i % 3) * 22) * gr;
      ctx.save(); ctx.translate(p.x, p.y);
      ctx.strokeStyle = '#8fbf5a'; ctx.lineWidth = 4; ctx.lineCap = 'round';
      ctx.shadowColor = 'rgba(200,230,120,0.7)'; ctx.shadowBlur = 12;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.quadraticCurveTo(6, -hgt * 0.5, 0, -hgt); ctx.stroke();
      ctx.fillStyle = '#a9d36a';
      for (const sd of [-1, 1]) { ctx.beginPath(); ctx.ellipse(sd * 12 * gr, -hgt, 13 * gr, 5 * gr, sd * -0.5, 0, 7); ctx.fill(); }
      ctx.restore();
    });
  }

  // ---------- fire ----------
  function flames(ctx, t) {
    const f = fire(t); if (f <= 0.01) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    // ground glow
    const gg = ctx.createLinearGradient(0, GROUND + 80, 0, GROUND - 700);
    gg.addColorStop(0, `rgba(255,110,30,${0.4 * Math.min(1, f)})`); gg.addColorStop(1, 'rgba(255,80,20,0)');
    ctx.fillStyle = gg; ctx.fillRect(-200, GROUND - 700, W + 400, 800);
    const n = 26;
    for (let i = 0; i < n; i++) {
      const bx = -40 + i * (W + 80) / (n - 1) + U.noise1(i * 3.1, 9) * 20;
      const hgt = (240 + 280 * (0.5 + 0.5 * U.noise1(t * 2.3 + i * 1.7, 2))) * f * (i % 3 === 0 ? 1.25 : 1);
      const wdt = 70 + (i % 4) * 14;
      const sway = U.noise1(t * 3 + i, 5) * 40 * f;
      for (const [sc, col] of [[1, [255, 80, 20, 0.42]], [0.65, [255, 150, 40, 0.32]], [0.35, [255, 220, 140, 0.22]]]) {
        const h2 = hgt * sc, w2 = wdt * (0.5 + 0.5 * sc);
        const yb = GROUND + 50;
        const fg = ctx.createLinearGradient(0, yb, 0, yb - h2);
        fg.addColorStop(0, `rgba(${col[0]},${col[1]},${col[2]},${col[3] * Math.min(1, f)})`); fg.addColorStop(1, `rgba(${col[0]},${col[1] - 40},${col[2]},0)`);
        ctx.fillStyle = fg;
        ctx.beginPath(); ctx.moveTo(bx - w2, yb);
        ctx.quadraticCurveTo(bx - w2 * 0.8, yb - h2 * 0.5, bx + sway, yb - h2);
        ctx.quadraticCurveTo(bx + w2 * 0.8, yb - h2 * 0.5, bx + w2, yb); ctx.closePath(); ctx.fill();
      }
    }
    ctx.restore();
    // smoke
    if (t >= ev.fire) {
      const r = U.mulberry32(51);
      ctx.save();
      for (let i = 0; i < 16; i++) {
        const x0 = r() * W, sp = 50 + r() * 60, ph = r() * 20;
        const y = GROUND - ((t - ev.fire + ph) * sp) % (GROUND * 0.9);
        const rad = 80 + r() * 120;
        const a = 0.16 * clamp(f) * clamp((t - ev.fire) / 1.5);
        const sg = ctx.createRadialGradient(x0 + Math.sin(t + i) * 30, y, 0, x0, y, rad);
        sg.addColorStop(0, `rgba(30,24,22,${a})`); sg.addColorStop(1, 'rgba(30,24,22,0)');
        ctx.fillStyle = sg; ctx.fillRect(x0 - rad, y - rad, rad * 2, rad * 2);
      }
      ctx.restore();
    }
  }
  function embers(ctx, t) {
    const boost = 0.4 + 1.6 * fire(t);
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 45; i++) {
      const sp = 60 + r() * 110, x0 = r() * W, ph = r() * 40, sz = 1.5 + r() * 3, ra = r();
      if (i > 22 && boost < 1) continue;
      const y = H - ((t * sp * (0.6 + 0.4 * boost) + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.8 + i) * 30;
      ctx.fillStyle = `rgba(255,${170 + 50 * ra},90,${Math.min(1, (0.12 + 0.22 * ra) * boost)})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }
  // snow + rain while the years pass
  function seasons(ctx, t) {
    if (t < ev.closed || t > ev.fire + 0.3) return;
    const a = sm(ev.closed, ev.closed + 0.6, t) * (1 - sm(ev.fire - 0.3, ev.fire + 0.3, t));
    const r = U.mulberry32(61);
    ctx.save();
    for (let i = 0; i < 70; i++) {
      const x0 = r() * W, sp = 90 + r() * 90, ph = r() * H, sz = 2 + r() * 3;
      const y = (ph + t * sp) % GROUND, x = x0 + Math.sin(t * 1.3 + i) * 20;
      const winter = 0.5 + 0.5 * Math.sin((t - ev.closed) * 2.2 + 1.0); // seasons cycle
      ctx.fillStyle = `rgba(235,240,255,${0.55 * a * winter})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- text ----------
  function seriesTag(ctx) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('WISSEN IN 30 SEKUNDEN · #2', W / 2, S.SAFE.y + 34);
    ctx.fillStyle = 'rgba(227,176,75,0.5)'; ctx.fillRect(W / 2 - 60, S.SAFE.y + 52, 120, 2);
    ctx.restore();
  }
  function card(ctx, c, t) {
    if (t < c.t - 0.01 || t > c.end + 0.1) return;
    const size = c.small ? 96 : 120, lh = size * 1.02;
    const fadeOut = 1 - clamp((t - c.end) / 0.1);
    const y0 = S.SAFE.y + 100 + size * 0.8;
    ctx.save(); ctx.textBaseline = 'alphabetic';
    ctx.font = `400 ${size}px "Bebas Neue"`;
    let carry = false;
    c.lines.forEach((line, i) => {
      const startGold = carry;
      if ((line.split('*').length - 1) % 2 === 1) carry = !carry;
      const appear = c.t === ev.hook || c.t === ev.drop ? 1 : ease.outCubic(clamp((t - c.t - i * 0.12) / 0.28));
      const a = appear * fadeOut; if (a <= 0) return;
      const parts = line.split('*');
      const total = parts.reduce((w, p) => w + ctx.measureText(p).width, 0);
      let x = W / 2 - total / 2; const y = y0 + i * lh + (1 - appear) * 30;
      let gold = startGold;
      parts.forEach((p, j) => {
        if (j > 0) gold = !gold;
        ctx.globalAlpha = a;
        ctx.shadowColor = 'rgba(0,0,0,0.95)'; ctx.shadowBlur = 26;
        ctx.fillStyle = gold ? GOLD : INK;
        ctx.fillText(p, x, y);
        x += ctx.measureText(p).width;
      });
    });
    ctx.restore();
  }
  function counter(ctx, t) {
    if (t < ev.closed || t >= ev.breath) return;
    const y = H * 0.80;
    ctx.save();
    { const ba = clamp(sm(ev.closed, ev.closed + 0.3, t) * (1 - sm(ev.breath - 0.2, ev.breath, t))); ctx.fillStyle = `rgba(6,5,6,${0.78 * ba})`; ctx.fillRect(W / 2 - 330, y - 92, 660, 160); ctx.strokeStyle = `rgba(227,176,75,${0.5 * ba})`; ctx.lineWidth = 2; ctx.strokeRect(W / 2 - 330, y - 92, 660, 160); }
    if (t < ev.fire) {
      const l = lastOf(S.years, t), n = l ? String(l.n) : '0', label = 'JAHR ';
      const pop = l ? Math.exp(-(t - l.t) * 8) : 0;
      ctx.globalAlpha = clamp(sm(ev.closed, ev.closed + 0.3, t) * (1 - sm(ev.fire - 0.25, ev.fire, t)));
      const sz = 84 * (1 + 0.15 * pop);
      ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
      ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(n).width;
      const x0 = W / 2 - (lw + nw) / 2;
      ctx.textAlign = 'left'; ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
      ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = 'rgba(242,235,221,0.85)'; ctx.fillText(label, x0, y);
      ctx.font = `700 ${sz}px "Cinzel"`; ctx.shadowColor = `rgba(255,200,100,${0.5 + 0.5 * pop})`; ctx.shadowBlur = 20 + 30 * pop;
      ctx.fillStyle = pop > 0.4 ? GOLD_HI : GOLD; ctx.fillText(n, x0 + lw, y);
      ctx.font = '500 30px "Oswald"'; ctx.textAlign = 'center'; ctx.shadowBlur = 10; ctx.fillStyle = 'rgba(242,235,221,0.7)';
      ctx.fillText('ZAPFEN: GESCHLOSSEN', W / 2, y + 46);
    } else {
      // heat meter
      const v = sm(ev.fire, ev.breath - 0.2, t);
      ctx.globalAlpha = clamp(sm(ev.fire, ev.fire + 0.3, t) * (1 - sm(ev.breath - 0.2, ev.breath, t)));
      const bw = 560, bh = 26, bx = W / 2 - bw / 2;
      ctx.textAlign = 'center'; ctx.font = '700 40px "Cinzel"'; ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
      ctx.fillStyle = '#FFB07A'; ctx.fillText('HITZE', W / 2, y - 18);
      ctx.shadowBlur = 0; ctx.fillStyle = 'rgba(10,6,4,0.8)'; ctx.fillRect(bx, y, bw, bh);
      const hg = ctx.createLinearGradient(bx, 0, bx + bw, 0); hg.addColorStop(0, '#E3B04B'); hg.addColorStop(1, '#FF4A1C');
      ctx.fillStyle = hg; ctx.fillRect(bx, y, bw * v, bh);
      ctx.strokeStyle = 'rgba(227,176,75,0.8)'; ctx.lineWidth = 2; ctx.strokeRect(bx, y, bw, bh);
    }
    ctx.restore();
  }
  function footer(ctx, t) {
    const a = sm(ev.end + 0.4, ev.end + 1.0, t);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center';
    const y = H * 0.745;
    ctx.fillStyle = 'rgba(6,6,10,0.85)'; ctx.fillRect(W / 2 - 330, y - 62, 660, 130);
    ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 2; ctx.strokeRect(W / 2 - 330, y - 62, 660, 130);
    ctx.font = '700 54px "Cinzel"'; ctx.fillStyle = GOLD_HI;
    ctx.fillText('FOLGE FÜR TEIL #3', W / 2, y);
    ctx.font = '500 30px "Oswald"'; ctx.fillStyle = 'rgba(242,235,221,0.85)';
    ctx.fillText('SPEICHERN FÜR EINEN SCHWEREN TAG', W / 2, y + 48);
    ctx.restore();
  }

  Studio.film({
    async init() {
      for (const [fam, url, weight] of [['Bebas Neue', 'fonts/bebas-neue-latin-400-normal.woff2', '400'], ['Cinzel', 'fonts/cinzel-latin-700-normal.woff2', '700'], ['Oswald', 'fonts/oswald-latin-500-normal.woff2', '500']]) {
        const f = new FontFace(fam, `url(${url})`, { weight }); document.fonts.add(f); await f.load();
      }
    },
    draw(ctx, t) {
      let shake = 0;
      for (const [h, amp] of [[ev.hook, 14], [ev.fire, 10], [ev.drop, 30]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      if (t >= ev.fire && t < ev.breath) shake += 3 * fire(t);
      // camera: pull back in the hook, push towards the cone with the fire, drift down with the seeds
      const zoom = 1.14 - 0.12 * sm(0, ev.closed, t) + 0.12 * sm(ev.closed, ev.breath, t) - 0.08 * sm(ev.drop, ev.seeds + 1, t);
      const fx = CX + 60, fy = lerp(H * 0.55, H * 0.6, sm(ev.drop, ev.seeds + 1, t));
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      ctx.translate(fx, fy); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy);
      sky(ctx, t);
      ground(ctx, t);
      trunk(ctx, t);
      const sway = branch(ctx, t);
      cone(ctx, t, sway);
      seasons(ctx, t);
      flames(ctx, t);
      sprouts(ctx, t);
      seeds(ctx, t);
      embers(ctx, t);
      ctx.restore();
      // heat vignette
      const f = fire(t);
      if (f > 0.05 && t < ev.drop) {
        const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75);
        v.addColorStop(0, 'rgba(120,30,0,0)'); v.addColorStop(1, `rgba(150,40,5,${0.4 * clamp(f)})`);
        ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
      }
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(0, 0, W, H); }
      const fl = t >= ev.drop ? 0.85 * Math.exp(-(t - ev.drop) * 9) : (t < 0.2 ? 0.3 * Math.exp(-t * 14) : 0);
      if (fl > 0.01) { ctx.fillStyle = `rgba(255,236,200,${fl})`; ctx.fillRect(0, 0, W, H); }
      if (t >= ev.lesson - 0.4) { ctx.fillStyle = `rgba(4,4,8,${0.4 * sm(ev.lesson - 0.4, ev.lesson + 0.4, t)})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
