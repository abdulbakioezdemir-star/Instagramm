// LOREBOUND – „Das dünne Seil“ (Gleichnis #3). Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const GROUND = H * 0.71;
  const STAKE_X = W * 0.83;
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const lastOf = (list, t) => { let l = null; for (const s of list) if (t >= s.t) l = s; return l; };

  // ---------- state of the elephant over time ----------
  function scaleAt(t) { // adult in hook, calf in flashback, grows during years
    if (t < ev.back - 0.15) return 1.12;
    if (t < ev.years) return 0.46;
    return lerp(0.46, 1.12, ease.inOutCubic(clamp((t - ev.years) / (ev.could - 0.3 - ev.years))));
  }
  function xAt(t, s) { return lerp(W * 0.5, W * 0.44, (s - 0.46) / 0.66); }
  function tugAt(t) { // 0..1 pulse strength of the current tug
    if (t < ev.back || t > ev.stop + 0.2) return 0;
    let v = 0;
    for (const g of S.tugs) { const u = t - g.t; if (u >= -0.12 && u < 0.6) v = Math.max(v, g.s * (u < 0 ? (u + 0.12) / 0.12 : Math.exp(-u * 5))); }
    return v;
  }

  // ---------- sky ----------
  function sky(ctx, t) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#05060b'); g.addColorStop(0.6, '#0c0d13'); g.addColorStop(1, '#16110a');
    ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    const r = U.mulberry32(5);
    for (let i = 0; i < 110; i++) {
      const x = r() * W, y = r() * H * 0.72;
      const a = 0.12 + 0.3 * r() * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
      ctx.fillStyle = `rgba(230,220,200,${a})`; ctx.fillRect(x, y, 2.2, 2.2);
    }
    const mx = W * 0.80, my = H * 0.43;
    const mg = ctx.createRadialGradient(mx, my, 0, mx, my, 320);
    mg.addColorStop(0, 'rgba(255,226,170,0.22)'); mg.addColorStop(1, 'rgba(255,226,170,0)');
    ctx.fillStyle = mg; ctx.fillRect(mx - 340, my - 340, 680, 680);
    ctx.fillStyle = 'rgba(255,232,190,0.88)'; ctx.beginPath(); ctx.arc(mx, my, 38, 0, 7); ctx.fill();
    // distant hills
    ctx.fillStyle = '#0a0a0e';
    ctx.beginPath(); ctx.moveTo(-50, GROUND);
    for (let x = -50; x <= W + 50; x += 30) ctx.lineTo(x, GROUND - 70 - 40 * Math.sin(x * 0.006) - 25 * Math.sin(x * 0.017 + 1));
    ctx.lineTo(W + 50, GROUND); ctx.fill();
  }
  function ground(ctx) {
    const g = ctx.createLinearGradient(0, GROUND, 0, H);
    g.addColorStop(0, '#15100b'); g.addColorStop(1, '#060506');
    ctx.fillStyle = g; ctx.fillRect(-200, GROUND, W + 400, H - GROUND + 200);
    ctx.strokeStyle = 'rgba(227,176,75,0.45)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(-50, GROUND); ctx.lineTo(W + 50, GROUND); ctx.stroke();
    const r = U.mulberry32(31);
    for (let i = 0; i < 50; i++) {
      const px = r() * W, py = GROUND + 20 + r() * 300, s = 3 + r() * 8;
      ctx.fillStyle = `rgba(60,48,38,${0.3 + 0.3 * r()})`; ctx.beginPath(); ctx.ellipse(px, py, s * 1.4, s * 0.6, 0, 0, 7); ctx.fill();
    }
  }

  // ---------- the elephant (faces left), origin = ground under body centre ----------
  function parts(calf) {
    const P = [];
    const hr = calf ? 128 : 110; // calves have bigger heads
    P.push({ k: 'ell', x: 20, y: -360, rx: 235, ry: 160 });                // body
    P.push({ k: 'ell', x: -190, y: -410, rx: hr, ry: hr * 1.0 });            // head
    P.push({ k: 'ell', x: -230, y: -500, rx: hr * 0.62, ry: hr * 0.5 });     // forehead dome
    return P;
  }
  function trunkPts(calf, t, sway) {
    const pts = [];
    const p0 = [-275, -400], p1 = [-345, -250], p2 = [-300 + sway * 30, calf ? -130 : -70];
    for (let i = 0; i <= 70; i++) {
      const u = i / 70;
      const x = (1 - u) * (1 - u) * p0[0] + 2 * u * (1 - u) * p1[0] + u * u * p2[0];
      const y = (1 - u) * (1 - u) * p0[1] + 2 * u * (1 - u) * p1[1] + u * u * p2[1];
      pts.push([x, y, lerp(calf ? 46 : 42, calf ? 20 : 15, u)]);
    }
    return pts;
  }
  const LEGS = [ // x, far?
    [-130, true], [160, true], [-170, false], [120, false],
  ];
  function elephant(ctx, t, x, s, lean, step) {
    const calf = s < 0.7;
    ctx.save();
    ctx.translate(x, GROUND); ctx.scale(s, s);
    ctx.rotate(-0.035 * lean);
    const sway = Math.sin(t * 1.6) * 0.5 + lean * -0.6;
    const legH = calf ? 200 : 235;
    const shapes = (fill, outline) => {
      // far legs first
      for (const [lx, far] of LEGS) {
        const off = far ? 0 : 0;
        const ph = step * (far ? 1 : -1) * (lx > 0 ? 1 : -1);
        ctx.fillStyle = fill(far);
        ctx.beginPath(); G.roundRect ? 0 : 0;
        const w = calf ? 78 : 74;
        const lx2 = lx + ph * 12 + lean * (lx > 0 ? 18 : -10);
        ctx.moveTo(lx - w / 2 + off, -legH - 120);
        ctx.lineTo(lx + w / 2 + off, -legH - 120);
        ctx.lineTo(lx2 + w / 2 + 4, -4);
        ctx.quadraticCurveTo(lx2, 6, lx2 - w / 2 - 4, -4);
        ctx.closePath(); ctx.fill(); if (outline) ctx.stroke();
      }
      ctx.fillStyle = fill(false);
      for (const p of parts(calf)) { ctx.beginPath(); ctx.ellipse(p.x, p.y, p.rx, p.ry, 0, 0, 7); ctx.fill(); if (outline) ctx.stroke(); }
      // tail
      ctx.lineCap = 'round';
      ctx.strokeStyle = outline ? ctx.strokeStyle : fill(false);
      // trunk as tapered dots
      for (const [px, py, r] of trunkPts(calf, t, sway)) { ctx.beginPath(); ctx.arc(px, py, r + (outline ? 3 : 0), 0, 7); ctx.fillStyle = outline ? GOLD_HI : fill(false); ctx.globalAlpha = outline ? 0.55 : 1; ctx.fill(); ctx.globalAlpha = 1; }
    };
    // pass 1: gold rim (wider), pass 2: dark fill on top -> only the silhouette edge glows
    ctx.save();
    ctx.strokeStyle = 'rgba(227,176,75,0.75)'; ctx.lineWidth = 7 / Math.max(0.6, s);
    shapes(() => 'rgba(227,176,75,0.0)', true);
    ctx.restore();
    const body = ctx.createLinearGradient(0, -560, 0, 0);
    body.addColorStop(0, '#3a332b'); body.addColorStop(1, '#14110e');
    shapes((far) => far ? '#0b0a09' : body, false);
    // tail
    ctx.strokeStyle = '#2a2520'; ctx.lineWidth = 9; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(250, -400); ctx.quadraticCurveTo(275 + Math.sin(t * 2) * 8, -320, 262, -250); ctx.stroke();
    // ear
    ctx.fillStyle = '#1c1915'; ctx.strokeStyle = 'rgba(227,176,75,0.55)'; ctx.lineWidth = 3 / s;
    const ef = Math.sin(t * 2.4) * 0.06;
    ctx.save(); ctx.translate(-120, -440); ctx.rotate(ef);
    ctx.beginPath(); ctx.moveTo(0, -60); ctx.bezierCurveTo(80, -90, 110, 20, 60, 90); ctx.bezierCurveTo(30, 130, -10, 90, -10, 40); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.restore();
    // tusk (adult only)
    if (!calf) {
      ctx.strokeStyle = '#d9cdb4'; ctx.lineWidth = 14; ctx.lineCap = 'round';
      ctx.beginPath(); ctx.moveTo(-255, -335); ctx.quadraticCurveTo(-320, -300, -345, -340); ctx.stroke();
    }
    // eye with gold glint
    ctx.fillStyle = '#000'; ctx.beginPath(); ctx.arc(-235, -440, 9, 0, 7); ctx.fill();
    ctx.fillStyle = GOLD_HI; ctx.beginPath(); ctx.arc(-232, -443, 3, 0, 7); ctx.fill();
    ctx.restore();
  }
  // world position of the rear near ankle (rope anchor)
  function ankle(t) {
    const s = scaleAt(t), x = xAt(t, s), lean = leanAt(t);
    return [x + (120 + lean * 18) * s, GROUND - 30 * s];
  }
  function leanAt(t) { return -tugAt(t) * 1.0; }

  // ---------- stake + rope ----------
  function stake(ctx, t) {
    const wob = Math.sin(t * 40) * 0.04 * tugAt(t);
    ctx.save(); ctx.translate(STAKE_X, GROUND + 6); ctx.rotate(-0.12 + wob);
    const g = ctx.createLinearGradient(-12, 0, 12, 0);
    g.addColorStop(0, '#3a2a1a'); g.addColorStop(0.5, '#6b4f30'); g.addColorStop(1, '#2a1e12');
    ctx.fillStyle = g; ctx.fillRect(-12, -78, 24, 84);
    ctx.fillStyle = '#7a5c38'; ctx.beginPath(); ctx.ellipse(0, -78, 12, 5, 0, 0, 7); ctx.fill();
    ctx.strokeStyle = 'rgba(227,176,75,0.6)'; ctx.lineWidth = 2; ctx.strokeRect(-12, -78, 24, 84);
    ctx.restore();
  }
  function ropePts(t) {
    const [ax, ay] = ankle(t);
    const bx = STAKE_X - 4, by = GROUND - 50;
    const taut = Math.max(tugAt(t), t < ev.back - 0.15 ? 0.6 + 0.4 * Math.exp(-t * 3) : 0.15);
    const sag = lerp(60, 4, taut);
    const pts = [];
    for (let i = 0; i <= 30; i++) { const u = i / 30; pts.push([lerp(ax, bx, u), lerp(ay, by, u) + Math.sin(Math.PI * u) * sag]); }
    return pts;
  }
  function rope(ctx, t) {
    if (t >= ev.drop + 0.05) return;
    const pts = ropePts(t);
    const glow = sm(ev.dry, ev.breath, t);
    ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    if (glow > 0) { ctx.shadowColor = `rgba(255,210,120,${glow})`; ctx.shadowBlur = 30 * glow; }
    ctx.strokeStyle = '#b89a6a'; ctx.lineWidth = 6;
    ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = `rgba(255,217,138,${0.35 + 0.6 * glow})`; ctx.lineWidth = 2;
    ctx.beginPath(); pts.forEach(([x, y], i) => (i ? ctx.lineTo(x, y - 1.5) : ctx.moveTo(x, y - 1.5))); ctx.stroke();
    ctx.restore();
  }
  function ropeDust(ctx, t) {
    const u = t - ev.drop; if (u < 0 || u > 3.5) return;
    const pts = ropePts(ev.drop - 0.01), r = U.mulberry32(99);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 160; i++) {
      const p = pts[Math.floor(r() * pts.length)];
      const vx = (r() - 0.5) * 160, vy = -60 - r() * 260, sz = 2 + r() * 4;
      const a = Math.max(0, 1 - u / (1.8 + r() * 1.7));
      ctx.fillStyle = `rgba(255,${200 + Math.floor(r() * 40)},120,${a})`;
      ctx.beginPath(); ctx.arc(p[0] + vx * u, p[1] + vy * u - 30 * u * u, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }
  function dust(ctx, t) { // kicked up by tugs
    ctx.save();
    for (const g of S.tugs) {
      const u = t - g.t; if (u < 0 || u > 0.9) continue;
      const r = U.mulberry32(Math.floor(g.t * 100));
      const [ax] = ankle(g.t);
      for (let i = 0; i < 10; i++) {
        const x = ax - 60 + r() * 60 - u * (40 + r() * 120), y = GROUND - u * (20 + r() * 60);
        ctx.fillStyle = `rgba(150,120,80,${0.35 * g.s * (1 - u / 0.9)})`;
        ctx.beginPath(); ctx.arc(x, y, 6 + u * 18 * r(), 0, 7); ctx.fill();
      }
    }
    ctx.restore();
  }

  function embers(ctx, t, boost = 0) {
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 36; i++) {
      const sp = 40 + r() * 70, x0 = r() * W, ph = r() * 40, sz = 1.5 + r() * 3, ra = r();
      const y = H - ((t * sp + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.8 + i) * 30;
      ctx.fillStyle = `rgba(255,200,110,${Math.min(1, (0.18 + 0.3 * ra) * (1 + boost))})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- text ----------
  function seriesTag(ctx) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('GLEICHNISSE IN 30 SEKUNDEN · #3', W / 2, S.SAFE.y + 34);
    ctx.fillStyle = 'rgba(227,176,75,0.5)'; ctx.fillRect(W / 2 - 60, S.SAFE.y + 52, 120, 2);
    ctx.restore();
  }
  function card(ctx, c, t) {
    if (t < c.t - 0.01 || t > c.end + 0.1) return;
    const size = c.small ? 96 : 128, lh = size * 1.02;
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
    if (t < ev.back || t >= ev.could) return;
    let label, n, l, dead = false;
    if (t < ev.years) { l = lastOf(S.tugs, t); label = 'VERSUCH '; n = l ? l.n.toLocaleString('de-DE') : '0'; dead = t >= ev.stop; }
    else { l = lastOf(S.years, t); label = 'JAHR '; n = l ? String(l.n) : '0'; }
    const pop = l && !dead ? Math.exp(-(t - l.t) * 8) : 0;
    const a = sm(ev.back, ev.back + 0.3, t) * (1 - sm(ev.could - 0.3, ev.could, t));
    ctx.save(); ctx.globalAlpha = clamp(a) * (dead ? 0.55 : 1);
    const y = H * 0.775;
    const sz = 84 * (1 + 0.15 * pop);
    ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(n).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left';
    ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
    ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = 'rgba(242,235,221,0.8)'; ctx.fillText(label, x0, y);
    ctx.font = `700 ${sz}px "Cinzel"`;
    ctx.shadowColor = `rgba(255,200,100,${0.5 + 0.5 * pop})`; ctx.shadowBlur = 20 + 30 * pop;
    ctx.fillStyle = dead ? '#8a8378' : pop > 0.4 ? GOLD_HI : GOLD;
    ctx.fillText(n, x0 + lw, y);
    if (dead) { ctx.strokeStyle = 'rgba(200,190,175,0.7)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(x0 - 10, y - sz * 0.32); ctx.lineTo(x0 + lw + nw + 10, y - sz * 0.32); ctx.stroke(); }
    ctx.restore();
  }
  function footer(ctx, t) {
    const a = sm(ev.follow, ev.follow + 0.6, t);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center';
    const y = H * 0.745;
    ctx.fillStyle = 'rgba(6,6,10,0.85)'; ctx.fillRect(W / 2 - 330, y - 62, 660, 130);
    ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 2; ctx.strokeRect(W / 2 - 330, y - 62, 660, 130);
    ctx.font = '700 54px "Cinzel"'; ctx.fillStyle = GOLD_HI;
    ctx.fillText('FOLGE FÜR TEIL #4', W / 2, y);
    ctx.font = '500 30px "Oswald"'; ctx.fillStyle = 'rgba(242,235,221,0.8)';
    ctx.fillText('LOREBOUND', W / 2, y + 48);
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
      for (const [h, amp] of [[ev.hook, 14], [ev.drop, 36], [ev.could, 10], [ev.could + 1, 10]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      shake += 6 * tugAt(t);
      // camera: push-in on rope in hook, wide in flashback, slow push at the end
      const zoom = 1.0 + 0.07 * sm(0, ev.back, t) * (1 - sm(ev.back - 0.2, ev.back, t)) + 0.06 * sm(ev.drop, ev.follow, t);
      const fx = W * 0.62, fy = GROUND - 100;
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      ctx.translate(fx, fy); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy);
      sky(ctx, t);
      ground(ctx);
      const s = scaleAt(t);
      const step = t >= ev.years && t < ev.could ? Math.sin(t * 6) : 0;
      elephant(ctx, t, xAt(t, s) + leanAt(t) * 14 * s, s, leanAt(t), step);
      dust(ctx, t);
      rope(ctx, t);
      stake(ctx, t);
      ropeDust(ctx, t);
      embers(ctx, t, t >= ev.drop ? 1.5 * Math.exp(-(t - ev.drop)) : 0);
      ctx.restore();
      // flashback: warm sepia veil + flicker
      const fb = sm(ev.back - 0.15, ev.back + 0.1, t) * (1 - sm(ev.years, ev.years + 1.2, t));
      if (fb > 0.01) {
        ctx.save(); ctx.globalCompositeOperation = 'multiply';
        ctx.fillStyle = `rgba(200,150,90,${0.55 * fb})`; ctx.fillRect(0, 0, W, H); ctx.restore();
        ctx.fillStyle = `rgba(255,230,180,${0.03 * fb * (1 + U.noise1(t * 12, 7))})`; ctx.fillRect(0, 0, W, H);
      }
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(0, 0, W, H); }
      const f = t >= ev.drop ? 0.9 * Math.exp(-(t - ev.drop) * 9) : (t < 0.2 ? 0.2 * Math.exp(-t * 14) : 0);
      if (f > 0.01) { ctx.fillStyle = `rgba(255,236,200,${f})`; ctx.fillRect(0, 0, W, H); }
      if (t >= ev.end - 0.5) { ctx.fillStyle = `rgba(4,4,8,${0.5 * sm(ev.end - 0.5, ev.end + 0.5, t)})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
