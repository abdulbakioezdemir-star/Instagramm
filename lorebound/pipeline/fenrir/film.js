// LOREBOUND – „Die Fessel, die es nicht gibt“. Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev, BEAT } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const HEAD = { x: W / 2, y: H * 0.535 };
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };

  // ---------- background: night, mist, a lamp of light from above ----------
  function background(ctx, t) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#06070c'); g.addColorStop(0.55, '#0e0d14'); g.addColorStop(1, '#1b130b');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    // stars
    const r = U.mulberry32(5);
    for (let i = 0; i < 90; i++) {
      const x = r() * W, y = r() * H * 0.55, a = 0.15 + 0.35 * r() * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
      ctx.fillStyle = `rgba(230,220,200,${a})`; ctx.fillRect(x, y, 2.2, 2.2);
    }
    // light cone
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const lc = ctx.createLinearGradient(0, 0, 0, H * 0.85);
    lc.addColorStop(0, 'rgba(227,176,75,0.10)'); lc.addColorStop(1, 'rgba(227,176,75,0)');
    ctx.fillStyle = lc; ctx.beginPath(); ctx.moveTo(W * 0.38, 0); ctx.lineTo(W * 0.62, 0); ctx.lineTo(W * 0.95, H * 0.85); ctx.lineTo(W * 0.05, H * 0.85); ctx.fill();
    ctx.restore();
    // mist bands
    for (let i = 0; i < 4; i++) {
      const y = H * (0.62 + i * 0.07), x = W / 2 + Math.sin(t * 0.25 + i * 1.7) * 220;
      const mg = ctx.createRadialGradient(x, y, 0, x, y, 700);
      mg.addColorStop(0, 'rgba(120,110,130,0.07)'); mg.addColorStop(1, 'rgba(120,110,130,0)');
      ctx.fillStyle = mg; ctx.fillRect(0, y - 700, W, 1400);
    }
    // rocky horizon
    ctx.fillStyle = '#07070a';
    ctx.beginPath(); ctx.moveTo(0, H);
    const rr = U.mulberry32(11);
    for (let x = 0; x <= W + 60; x += 60) ctx.lineTo(x, H * 0.80 + Math.sin(x * 0.01) * 30 + rr() * 26);
    ctx.lineTo(W, H); ctx.fill();
  }

  function embers(ctx, t, boost = 0) {
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 46; i++) {
      const sp = 40 + r() * 70, x0 = r() * W, ph = r() * 40, sz = 1.5 + r() * 3;
      const y = H - ((t * sp + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.8 + i) * 30;
      const a = (0.25 + 0.4 * r()) * (1 + boost);
      ctx.fillStyle = `rgba(255,200,110,${Math.min(1, a)})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- the wolf: a low-poly heraldic head ----------
  const P = { P0: [0, -150], P1: [90, -175], P2: [200, -360], P3: [290, -110], P4: [330, 20], P5: [390, 180], P6: [260, 200], P7: [310, 320], P8: [150, 290], P9: [115, 400], P10: [55, 470], P11: [0, 485], E: [118, 52], B: [0, 60], N: [0, 395], C: [175, 185], F: [150, -60], EI1: [200, -300], EI2: [245, -135] };
  const FACETS = [
    ['P0', 'P1', 'F', 0.9], ['P1', 'P2', 'P3', 0.75], ['P1', 'EI1', 'EI2', 0.2], ['P1', 'P3', 'F', 0.8], ['F', 'P3', 'P4', 0.68],
    ['P0', 'F', 'B', 0.95], ['F', 'P4', 'E', 0.72], ['F', 'E', 'B', 0.86], ['P4', 'P5', 'P6', 0.58], ['P4', 'P6', 'C', 0.64],
    ['P4', 'C', 'E', 0.7], ['B', 'E', 'C', 0.8], ['B', 'C', 'N', 0.92], ['C', 'P6', 'P8', 0.52], ['P6', 'P7', 'P8', 0.45],
    ['C', 'P8', 'P9', 0.6], ['C', 'P9', 'N', 0.74], ['N', 'P9', 'P10', 0.7], ['N', 'P10', 'P11', 0.82],
  ];
  const OUTLINE = ['P0', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11'];
  const shadeCol = (s, light) => { const k = s * light; return `rgb(${Math.round(lerp(10, 58, k))},${Math.round(lerp(11, 54, k))},${Math.round(lerp(17, 64, k))})`; };

  function wolfScale(t) {
    let s = lerp(0.62, 1.0, ease.inOutQuad(clamp((t - ev.grow) / (ev.chain1 - ev.grow))));
    if (t < ev.grow) s = 0.62 + 0.03 * clamp(t / 1);
    if (t >= ev.drop) s *= 1 + 0.07 * Math.exp(-(t - ev.drop) * 4) * Math.sin(Math.min(Math.PI, (t - ev.drop) * 8));
    return s * 1.0;
  }
  function mouthOpen(t) {
    if (t < ev.pledge) return 0;
    if (t < ev.drop) return 110 * sm(ev.pledge + 0.4, ev.hand + 0.8, t);
    return 0;
  }

  function wolf(ctx, t, alpha) {
    const s = wolfScale(t);
    const open = mouthOpen(t);
    ctx.save(); ctx.globalAlpha = alpha;
    ctx.translate(HEAD.x, HEAD.y); ctx.scale(s, s);
    // open jaws: dark gap + lower jaw (drawn behind the head)
    if (open > 1) {
      ctx.fillStyle = '#160406';
      ctx.beginPath(); ctx.moveTo(-70, 440); ctx.lineTo(70, 440); ctx.lineTo(75, 492 + open); ctx.lineTo(-75, 492 + open); ctx.fill();
      ctx.fillStyle = shadeCol(0.55, 1);
      ctx.beginPath(); ctx.moveTo(-80, 490 + open); ctx.lineTo(80, 490 + open); ctx.lineTo(42, 565 + open); ctx.lineTo(-42, 565 + open); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(227,176,75,0.75)'; ctx.lineWidth = 3.5; ctx.stroke();
      ctx.fillStyle = '#E9E2D2';
      for (let i = -2; i <= 2; i++) { ctx.beginPath(); ctx.moveTo(i * 26 - 9, 492 + open); ctx.lineTo(i * 26 + 9, 492 + open); ctx.lineTo(i * 26, 468 + open); ctx.fill(); }
    }
    // glow behind the head
    const gl = ctx.createRadialGradient(0, 80, 50, 0, 80, 620);
    gl.addColorStop(0, 'rgba(227,176,75,0.10)'); gl.addColorStop(1, 'rgba(227,176,75,0)');
    ctx.fillStyle = gl; ctx.fillRect(-700, -600, 1400, 1400);
    for (const side of [1, -1]) {
      for (const f of FACETS) {
        ctx.fillStyle = shadeCol(f[3], side > 0 ? 1 : 0.72);
        ctx.beginPath();
        for (let i = 0; i < 3; i++) { const p = P[f[i]]; i ? ctx.lineTo(p[0] * side, p[1]) : ctx.moveTo(p[0] * side, p[1]); }
        ctx.closePath(); ctx.fill();
        ctx.strokeStyle = 'rgba(227,176,75,0.10)'; ctx.lineWidth = 1.5; ctx.stroke();
      }
    }
    // gold rim
    ctx.beginPath();
    OUTLINE.forEach((k, i) => (i ? ctx.lineTo(P[k][0], P[k][1]) : ctx.moveTo(P[k][0], P[k][1])));
    [...OUTLINE].reverse().forEach((k) => ctx.lineTo(-P[k][0], P[k][1]));
    ctx.closePath();
    ctx.shadowColor = 'rgba(227,176,75,0.8)'; ctx.shadowBlur = 18;
    ctx.strokeStyle = 'rgba(227,176,75,0.75)'; ctx.lineWidth = 3.5; ctx.stroke();
    ctx.shadowBlur = 0;
    // nose
    ctx.fillStyle = '#040406'; ctx.beginPath(); ctx.moveTo(-42, 392); ctx.lineTo(42, 392); ctx.lineTo(0, 440); ctx.fill();
    if (open > 1) {
      ctx.fillStyle = '#E9E2D2';
      for (let i = -2; i <= 2; i++) { ctx.beginPath(); ctx.moveTo(i * 24 - 9, 478); ctx.lineTo(i * 24 + 9, 478); ctx.lineTo(i * 24, 478 + Math.min(26, open * 0.4)); ctx.fill(); }
    }
    // eyes: open on frame 1, flare at the snaps and the drop
    const opn = t < 0.35 ? 0.15 + 0.85 * ease.outQuad(clamp(t / 0.35)) : 1;
    let glow = 0.8 + 0.2 * Math.sin(t * 3);
    for (const h of [ev.snap1, ev.snap2, ev.drop]) if (t >= h) glow += 1.2 * Math.exp(-(t - h) * 3);
    if (t >= ev.end) glow *= lerp(1, 0.55, sm(ev.end, ev.end + 2, t));
    for (const side of [1, -1]) {
      ctx.save(); ctx.translate(P.E[0] * side, P.E[1]); ctx.scale(side, opn);
      ctx.shadowColor = `rgba(255,190,80,${Math.min(1, 0.6 * glow)})`; ctx.shadowBlur = 30 * glow;
      ctx.fillStyle = GOLD_HI;
      ctx.beginPath(); ctx.moveTo(-48, 12); ctx.lineTo(0, -20); ctx.lineTo(52, -10); ctx.lineTo(6, 20); ctx.closePath(); ctx.fill();
      ctx.shadowBlur = 0;
      ctx.fillStyle = '#1a0d02'; ctx.beginPath(); ctx.ellipse(2, 0, 6, 17, 0, 0, 7); ctx.fill();
      ctx.restore();
    }
    ctx.restore();
    return s;
  }

  // ---------- chains ----------
  function chainLinks(ctx, pts, alpha) {
    const [a, b] = pts; const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy), ang = Math.atan2(dy, dx);
    const n = Math.max(1, Math.floor(L / 52));
    ctx.save(); ctx.globalAlpha *= alpha;
    for (let i = 0; i < n; i++) {
      const u = (i + 0.5) / n, x = a[0] + dx * u, y = a[1] + dy * u;
      ctx.save(); ctx.translate(x, y); ctx.rotate(ang);
      if (i % 2 === 0) {
        ctx.lineWidth = 13; ctx.strokeStyle = '#1b1c22'; ctx.beginPath(); ctx.ellipse(0, 0, 38, 20, 0, 0, 7); ctx.stroke();
        ctx.lineWidth = 7; ctx.strokeStyle = '#8d8f98'; ctx.stroke();
        ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,230,180,0.6)'; ctx.beginPath(); ctx.ellipse(0, -3, 34, 15, 0, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke();
      } else {
        ctx.fillStyle = '#1b1c22'; ctx.fillRect(-36, -7, 72, 14);
        ctx.fillStyle = '#9a9ca5'; ctx.fillRect(-32, -3, 64, 6);
      }
      ctx.restore();
    }
    ctx.restore();
  }
  function chain(ctx, t, on, snap, dir) {
    if (t < on) return;
    const a = [-160, HEAD.y - 360 * dir + 80], b = [W + 160, HEAD.y + 360 * dir + 80];
    const tight = ease.outBack(clamp((t - on) / 0.5), 1.4);
    if (t < snap) {
      const strain = U.noise1(t * 25, dir + 4) * 6 * clamp((t - on) / (snap - on));
      const ox = lerp(dir * 900, 0, tight);
      chainLinks(ctx, [[a[0] + ox, a[1] + strain], [b[0] + ox, b[1] - strain]], 1);
      return;
    }
    const u = t - snap; if (u > 1.4) return;
    const mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    for (const [end, sgn] of [[a, -1], [b, 1]]) {
      ctx.save();
      ctx.translate(mid[0] + sgn * u * 520, mid[1] + 900 * u * u - 120 * u);
      ctx.rotate(sgn * u * 1.6 * dir);
      chainLinks(ctx, [[(end[0] - mid[0]) * 1, (end[1] - mid[1])], [sgn * 30, 0]], 1 - clamp(u / 1.4));
      ctx.restore();
    }
    sparks(ctx, t, snap, mid, 60, 700);
  }
  function sparks(ctx, t, t0, at, n, speed) {
    const u = t - t0; if (u < 0 || u > 1.2) return;
    const r = U.mulberry32(Math.round(t0 * 100));
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < n; i++) {
      const ang = r() * Math.PI * 2, sp = speed * (0.3 + r());
      const x = at[0] + Math.cos(ang) * sp * u, y = at[1] + Math.sin(ang) * sp * u + 600 * u * u;
      const a = 1 - u / 1.2;
      ctx.strokeStyle = `rgba(255,${Math.round(180 + 60 * r())},90,${a})`; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - Math.cos(ang) * 22, y - Math.sin(ang) * 22); ctx.stroke();
    }
    ctx.restore();
  }

  // ---------- Gleipnir: a silk-thin golden ribbon ----------
  function ribbonPath(ctx, k, s, phase, yOff) {
    const cy = HEAD.y + 250 * s + yOff, rx = 430 * s, ry = 70 * s;
    const steps = 120;
    ctx.beginPath();
    for (let i = 0; i <= steps * k; i++) {
      const a = (i / steps) * Math.PI * 2.0 + Math.PI;
      const x = HEAD.x + Math.cos(a) * rx * (1 + 0.05 * Math.sin(a * 3 + phase));
      const y = cy + Math.sin(a) * ry + Math.sin(a * 5 + phase) * 8;
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    }
  }
  function gleipnir(ctx, t, s) {
    if (t < ev.gleipnir) return;
    const k = ease.outCubic(clamp((t - ev.gleipnir) / 1.4));
    let bright = 1 + (t >= ev.drop ? 2.5 * Math.exp(-(t - ev.drop) * 2) : 0);
    const tight = t >= ev.drop ? -18 * clamp((t - ev.drop) / 0.2) : 0;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (const [lw, a, yo] of [[16, 0.10, 0], [6, 0.35, 0], [2.5, 0.95, 0], [2, 0.6, 26]]) {
      ribbonPath(ctx, k, s * (1 + tight / 400), t * 2 + yo, yo);
      ctx.strokeStyle = `rgba(255,214,140,${Math.min(1, a * bright)})`; ctx.lineWidth = lw * (yo ? 1 : 1 + 0.4 * (bright - 1)); ctx.stroke();
    }
    // travelling glints
    for (let i = 0; i < 5; i++) {
      const a = ((t * 0.35 + i / 5) % 1) * Math.PI * 2 * k + Math.PI;
      const x = HEAD.x + Math.cos(a) * 430 * s, y = HEAD.y + 250 * s + Math.sin(a) * 70 * s;
      const gr = ctx.createRadialGradient(x, y, 0, x, y, 26);
      gr.addColorStop(0, 'rgba(255,240,200,0.9)'); gr.addColorStop(1, 'rgba(255,240,200,0)');
      ctx.fillStyle = gr; ctx.fillRect(x - 26, y - 26, 52, 52);
    }
    ctx.restore();
  }

  // ---------- the six impossible things ----------
  function forge(ctx, t) {
    if (t < ev.items[0] - 0.2 || t >= ev.gleipnir + 0.6) return;
    const out = 1 - sm(ev.gleipnir - 0.1, ev.gleipnir + 0.5, t);
    const y0 = H * 0.43, gap = 108;
    ctx.save();
    ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic';
    S.items.forEach((txt, i) => {
      const ti = ev.items[i]; if (t < ti - 0.05) return;
      const a = ease.outCubic(clamp((t - ti + 0.05) / 0.3)) * out;
      const y = y0 + i * gap + (1 - a) * 24;
      const fresh = Math.exp(-(t - ti) * 2.5);
      // rune dot
      ctx.globalAlpha = a;
      ctx.fillStyle = GOLD; ctx.beginPath(); ctx.moveTo(W / 2, y - 92); ctx.lineTo(W / 2 + 7, y - 84); ctx.lineTo(W / 2, y - 76); ctx.lineTo(W / 2 - 7, y - 84); ctx.fill();
      ctx.font = '400 70px "Bebas Neue"';
      ctx.shadowColor = `rgba(255,200,100,${0.9 * fresh})`; ctx.shadowBlur = 30 * fresh;
      ctx.fillStyle = fresh > 0.4 ? GOLD_HI : INK;
      ctx.fillText(txt, W / 2, y);
      ctx.shadowBlur = 0;
    });
    ctx.restore();
  }

  // ---------- the pledge: a hand reaching into the jaws ----------
  function hand(ctx, t, s) {
    if (t < ev.hand || t >= ev.drop) return;
    const u = ease.inOutQuad(clamp((t - ev.hand) / (ev.breath - ev.hand)));
    const x = HEAD.x, y = lerp(H + 300, HEAD.y + 500 * s + 110 + 115, u);
    ctx.save(); ctx.translate(x, y); ctx.scale(1.5, 1.5);
    ctx.fillStyle = '#0c0b0f'; ctx.strokeStyle = GOLD; ctx.lineWidth = 3;
    ctx.shadowColor = 'rgba(227,176,75,0.7)'; ctx.shadowBlur = 14;
    ctx.beginPath();
    ctx.moveTo(-58, 260); ctx.lineTo(-62, 40);
    const fing = [[-50, -95], [-18, -125], [14, -118], [44, -85]];
    ctx.lineTo(-66, 10);
    for (const [fx, fy] of fing) { ctx.lineTo(fx - 13, 0); ctx.lineTo(fx - 13, fy + 12); ctx.quadraticCurveTo(fx, fy - 6, fx + 13, fy + 12); ctx.lineTo(fx + 13, 0); }
    ctx.lineTo(62, 30); ctx.lineTo(108, -20); ctx.quadraticCurveTo(122, -12, 112, 6); ctx.lineTo(66, 90); ctx.lineTo(58, 260);
    ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.restore();
  }

  // ---------- title cards ----------
  function card(ctx, c, t) {
    if (t < c.t - 0.01 || t > c.end + 0.25) return;
    const size = c.small ? 92 : 128, lh = size * 1.02;
    const fadeOut = 1 - clamp((t - c.end) / 0.25);
    const y0 = S.SAFE.y + 40 + size * 0.8;
    ctx.save(); ctx.textBaseline = 'alphabetic';
    ctx.font = `400 ${size}px "Bebas Neue"`;
    c.lines.forEach((line, i) => {
      const appear = c.t === ev.hook ? (i === 0 ? 1 : ease.outCubic(clamp((t - c.t - i * 0.12) / 0.2))) : ease.outCubic(clamp((t - c.t - i * 0.12) / 0.28));
      const a = appear * fadeOut; if (a <= 0) return;
      const parts = line.split('*');
      const total = parts.reduce((w, p) => w + ctx.measureText(p).width, 0);
      let x = W / 2 - total / 2; const y = y0 + i * lh + (1 - appear) * 30;
      parts.forEach((p, j) => {
        ctx.globalAlpha = a;
        ctx.shadowColor = 'rgba(0,0,0,0.85)'; ctx.shadowBlur = 24;
        ctx.fillStyle = j % 2 ? GOLD : INK;
        ctx.fillText(p, x, y);
        x += ctx.measureText(p).width;
      });
    });
    ctx.restore();
  }

  function footer(ctx, t) {
    const a = sm(ev.end + 1.2, ev.end + 2, t);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center';
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('NORDISCHE MYTHOLOGIE · PROSA-EDDA', W / 2, H * 0.755);
    ctx.font = '500 30px "Oswald"'; ctx.fillStyle = 'rgba(242,235,221,0.7)';
    ctx.fillText('LOREBOUND', W / 2, H * 0.755 + 50);
    ctx.restore();
  }

  Studio.film({
    async init() {
      for (const [fam, url, weight] of [['Bebas Neue', 'fonts/bebas-neue-latin-400-normal.woff2', '400'], ['Cinzel', 'fonts/cinzel-latin-700-normal.woff2', '700'], ['Oswald', 'fonts/oswald-latin-500-normal.woff2', '500']]) {
        const f = new FontFace(fam, `url(${url})`, { weight }); document.fonts.add(f); await f.load();
      }
    },
    draw(ctx, t) {
      HEAD.y = H * 0.535 - 150 * (sm(ev.pledge - 0.4, ev.pledge + 0.5, t) - sm(ev.end - 0.5, ev.end + 0.3, t));
      let shake = 0;
      for (const [h, amp] of [[ev.snap1, 22], [ev.snap2, 26], [ev.drop, 34], [ev.hook, 10]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      background(ctx, t);
      const forging = sm(ev.dwarves, ev.dwarves + 0.6, t) * (1 - sm(ev.gleipnir - 0.2, ev.gleipnir + 0.6, t));
      const s = wolf(ctx, t, 1 - 0.8 * forging);
      chain(ctx, t, ev.chain1, ev.snap1, 1);
      chain(ctx, t, ev.chain2, ev.snap2, -1);
      gleipnir(ctx, t, s);
      hand(ctx, t, s);
      if (t >= ev.drop) sparks(ctx, t, ev.drop, [HEAD.x, HEAD.y + 480 * s], 70, 900);
      embers(ctx, t, t >= ev.drop ? 1.5 * Math.exp(-(t - ev.drop)) : 0);
      ctx.restore();
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(0, 0, W, H); }
      // impact flashes
      for (const [h, k] of [[ev.snap1, 0.45], [ev.snap2, 0.5], [ev.drop, 0.85]]) {
        const f = t >= h ? k * Math.exp(-(t - h) * 10) : 0;
        if (f > 0.01) { ctx.fillStyle = `rgba(255,236,200,${f})`; ctx.fillRect(0, 0, W, H); }
      }
      forge(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
