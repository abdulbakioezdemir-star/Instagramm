// LOREBOUND – „Der Bambus“ (Gleichnis #2). Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const SOIL = H * 0.64;          // ground line in world space
  const SX = W / 2;               // sprout x
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const MAXPX = 3000;             // culm height in px at 20 m

  const lastOf = (list, t) => { let l = null; for (const s of list) if (t >= s.t) l = s; return l; };
  function grow(t) { // 0..1 height progress after the drop
    if (t < ev.drop) return 0;
    return clamp(Math.pow((t - ev.drop) / S.GROW, 1 / 1.6));
  }
  // camera: vertical offset in px (positive = looking down)
  function camY(t) {
    let c = 560 * sm(ev.reveal - 0.2, ev.reveal + 0.9, t) * (1 - sm(ev.last - 0.2, ev.last + 0.7, t));
    if (t >= ev.drop) {
      const tip = SOIL - MAXPX * grow(t);
      c = Math.min(0, tip - H * 0.30);
      c = Math.max(c, -(MAXPX - 300));
    }
    return c;
  }

  // ---------- sky ----------
  function sky(ctx, t, cam) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#05060b'); g.addColorStop(0.6, '#0b0d14'); g.addColorStop(1, '#141009');
    ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    const r = U.mulberry32(5);
    for (let i = 0; i < 110; i++) {
      const x = r() * W, y0 = r() * H * 1.2;
      const y = ((y0 - cam * 0.25) % (H * 1.2) + H * 1.2) % (H * 1.2) - H * 0.1;
      const a = 0.12 + 0.3 * r() * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
      ctx.fillStyle = `rgba(230,220,200,${a})`; ctx.fillRect(x, y, 2.2, 2.2);
    }
    const my = H * 0.40 - cam * 0.12;
    const mg = ctx.createRadialGradient(W * 0.84, my, 0, W * 0.84, my, 300);
    mg.addColorStop(0, 'rgba(255,226,170,0.20)'); mg.addColorStop(1, 'rgba(255,226,170,0)');
    ctx.fillStyle = mg; ctx.fillRect(0, my - 360, W, 720);
    ctx.fillStyle = 'rgba(255,232,190,0.85)'; ctx.beginPath(); ctx.arc(W * 0.84, my, 34, 0, 7); ctx.fill();
  }

  // ---------- roots: branching network grown from the sprout ----------
  const ROOTS = [];
  (function build() {
    const r = U.mulberry32(17);
    const tips = [];
    for (let k = 0; k < 5; k++) tips.push({ x: SX + (k - 2) * 8, y: SOIL + 6, a: Math.PI / 2 + (k - 2) * 0.55, w: 7 });
    let guard = 0;
    while (ROOTS.length < 420 && guard++ < 9000) {
      const i = Math.floor(r() * tips.length), tp = tips[i];
      let a = tp.a + (r() - 0.5) * 0.8;
      a = lerp(a, a > Math.PI / 2 ? Math.PI * 0.92 : Math.PI * 0.08, 0.12); // rhizome spreads sideways
      const len = 22 + r() * 28;
      const nx = tp.x + Math.cos(a) * len, ny = tp.y + Math.sin(a) * len;
      if (nx < 30 || nx > W - 30 || ny < SOIL + 4 || ny > SOIL + 1150) { tp.a = Math.PI / 2 + (r() - 0.5) * 2; continue; }
      ROOTS.push([tp.x, tp.y, nx, ny, Math.max(1, tp.w)]);
      tips[i] = { x: nx, y: ny, a, w: tp.w * 0.95 };
      if (r() < 0.2) tips.push({ x: nx, y: ny, a: a + (r() < 0.5 ? 1 : -1) * (0.5 + r() * 0.7), w: tp.w * 0.72 });
    }
  })();

  function ground(ctx, t, cam) {
    const y = SOIL - cam;
    if (y > H + 300) return;
    const g = ctx.createLinearGradient(0, y, 0, y + 1400);
    g.addColorStop(0, '#120d09'); g.addColorStop(1, '#070506');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(-200, H + 2000); ctx.lineTo(-200, y);
    const rr = U.mulberry32(11);
    for (let x = 0; x <= W + 60; x += 60) ctx.lineTo(x, y + Math.sin(x * 0.01) * 10 + rr() * 8);
    ctx.lineTo(W + 200, y); ctx.lineTo(W + 200, H + 2000); ctx.fill();
    const r = U.mulberry32(31);
    for (let i = 0; i < 70; i++) {
      const px = r() * W, py = y + 30 + r() * 1300, s = 4 + r() * 10;
      ctx.fillStyle = `rgba(60,48,38,${0.35 + 0.3 * r()})`; ctx.beginPath(); ctx.ellipse(px, py, s * 1.3, s, r() * 3, 0, 7); ctx.fill();
    }
    ctx.strokeStyle = 'rgba(227,176,75,0.4)'; ctx.lineWidth = 2;
    ctx.beginPath(); const r2 = U.mulberry32(11);
    for (let x = 0; x <= W + 60; x += 60) { const yy = y + Math.sin(x * 0.01) * 10 + r2() * 8; x ? ctx.lineTo(x, yy) : ctx.moveTo(x, yy); }
    ctx.stroke();
    const snow = sm(ev.seasons + 0.9, ev.seasons + 1.5, t) * (1 - sm(ev.seasons + 2.4, ev.seasons + 2.9, t));
    if (snow > 0.01) { ctx.fillStyle = `rgba(230,236,245,${0.55 * snow})`; ctx.fillRect(0, y - 6, W, 14); }
  }

  function roots(ctx, t, cam) {
    const frac = clamp(0.08 + 0.92 * (t / (ev.roots + 1.2)));
    const vis = Math.max(1, Math.floor(ROOTS.length * frac));
    const look = sm(ev.reveal - 0.1, ev.reveal + 0.8, t);
    const glow = 0.03 + 0.97 * look * (1 - 0.6 * sm(ev.last, ev.last + 0.6, t)) + (t >= ev.drop ? 0.4 * Math.exp(-(t - ev.drop) * 1.5) : 0);
    ctx.save(); ctx.translate(0, -cam); ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
    for (const [lw, a] of [[10, 0.10], [4, 0.45], [1.8, 1]]) {
      ctx.strokeStyle = `rgba(255,200,110,${a * glow})`;
      for (let i = 0; i < vis; i++) {
        const c = ROOTS[i];
        ctx.lineWidth = lw * (0.45 + c[4] / 6);
        ctx.beginPath(); ctx.moveTo(c[0], c[1]); ctx.lineTo(c[2], c[3]); ctx.stroke();
      }
    }
    if (look > 0.3) {
      for (let k = 0; k < 10; k++) {
        const c = ROOTS[Math.floor((t * 11 + k * 41) % vis)];
        const gr = ctx.createRadialGradient(c[2], c[3], 0, c[2], c[3], 34);
        gr.addColorStop(0, `rgba(255,240,200,${0.8 * look})`); gr.addColorStop(1, 'rgba(255,240,200,0)');
        ctx.fillStyle = gr; ctx.fillRect(c[2] - 34, c[3] - 34, 68, 68);
      }
    }
    ctx.restore();
  }

  // ---------- the tiny sprout (before the drop) ----------
  function sprout(ctx, t, cam) {
    if (t >= ev.drop + 0.1) return;
    const y = SOIL - cam;
    const sway = Math.sin(t * 2.1) * 0.06;
    const droop = 0.3 * sm(ev.seasons + 0.9, ev.seasons + 1.5, t) * (1 - sm(ev.seasons + 2.4, ev.seasons + 2.9, t));
    ctx.save(); ctx.translate(SX, y); ctx.rotate(sway);
    ctx.strokeStyle = '#4f7a3e'; ctx.lineWidth = 9; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.quadraticCurveTo(4, -40, 0, -78); ctx.stroke();
    ctx.shadowColor = 'rgba(227,176,75,0.6)'; ctx.shadowBlur = 14;
    for (const s of [-1, 1]) {
      ctx.save(); ctx.translate(0, -70); ctx.rotate(s * (0.9 + droop));
      ctx.fillStyle = '#5f8f47'; ctx.beginPath(); ctx.ellipse(0, -26, 12, 30, 0, 0, 7); ctx.fill();
      ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 2; ctx.stroke();
      ctx.restore();
    }
    ctx.restore();
  }

  // ---------- water drops (one per tick) ----------
  function drops(ctx, t, cam) {
    if (t > ev.reveal) return;
    const y = SOIL - cam;
    for (const tk of S.ticks) {
      const fall = 0.32, u0 = t - (tk.t - fall);
      if (u0 < 0 || u0 > fall + 0.4) continue;
      if (u0 < fall) {
        const yy = y - 92 - 520 * (1 - (u0 / fall) * (u0 / fall));
        ctx.fillStyle = 'rgba(170,215,255,0.9)'; ctx.beginPath(); ctx.ellipse(SX + 30, yy, 9, 15, 0, 0, 7); ctx.fill();
      } else {
        const u = (u0 - fall) / 0.4;
        ctx.strokeStyle = `rgba(190,225,255,${0.8 * (1 - u)})`; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.ellipse(SX + 30, y - 4, 20 + 70 * u, 6 + 10 * u, 0, 0, 7); ctx.stroke();
      }
    }
    if (t < 0.5) { // frame-zero splash (the hook hit)
      const u = t / 0.5;
      ctx.strokeStyle = `rgba(255,220,150,${1 - u})`; ctx.lineWidth = 5;
      ctx.beginPath(); ctx.ellipse(SX + 30, y - 4, 30 + 160 * u, 10 + 22 * u, 0, 0, 7); ctx.stroke();
    }
  }

  // ---------- seasons: leaves, then snow, then leaves ----------
  function seasons(ctx, t) {
    const a = sm(ev.seasons - 0.3, ev.seasons + 0.3, t) * (1 - sm(ev.reveal - 0.4, ev.reveal, t));
    if (a <= 0.01) return;
    const r = U.mulberry32(77);
    const u = t - ev.seasons;
    const snowy = u > 1.0 && u < 2.6;
    ctx.save(); ctx.globalAlpha = a;
    for (let i = 0; i < 60; i++) {
      const x0 = r() * W, sp = 260 + r() * 260, ph = r() * H, rs = r();
      const y = ((ph + u * sp) % (H * 1.05)) - 40;
      const x = x0 + Math.sin(u * 2 + i) * 40;
      if (snowy) { ctx.fillStyle = 'rgba(235,240,250,0.85)'; ctx.beginPath(); ctx.arc(x, y, 3 + rs * 4, 0, 7); ctx.fill(); }
      else { ctx.save(); ctx.translate(x, y); ctx.rotate(u * 3 + i); ctx.fillStyle = i % 3 ? 'rgba(200,130,50,0.8)' : 'rgba(227,176,75,0.85)'; ctx.beginPath(); ctx.ellipse(0, 0, 10, 5, 0, 0, 7); ctx.fill(); ctx.restore(); }
    }
    ctx.restore();
  }

  // ---------- bamboo culms (after the drop) ----------
  const CULMS = [
    { x: SX, w: 58, delay: 0, max: 1.0, hue: 0 },
    { x: SX - 300, w: 40, delay: 0.5, max: 0.82, hue: 1 },
    { x: SX + 290, w: 44, delay: 0.8, max: 0.88, hue: 2 },
    { x: SX - 470, w: 30, delay: 1.3, max: 0.65, hue: 3 },
    { x: SX + 470, w: 32, delay: 1.6, max: 0.7, hue: 4 },
  ];
  function culm(ctx, t, cam, c) {
    const p = grow(t - c.delay);
    if (p <= 0) return;
    const hpx = MAXPX * c.max * p;
    const base = SOIL - cam + 10, top = base - hpx;
    const seg = 190 * (c.w / 58);
    const sway = Math.sin(t * 0.9 + c.hue) * 0.004 * (hpx / 1000);
    ctx.save(); ctx.translate(c.x, base); ctx.rotate(sway); ctx.translate(-c.x, -base);
    const g = ctx.createLinearGradient(c.x - c.w / 2, 0, c.x + c.w / 2, 0);
    g.addColorStop(0, '#1d2a17'); g.addColorStop(0.35, '#4c6b34'); g.addColorStop(0.6, '#36502a'); g.addColorStop(1, '#141c10');
    ctx.fillStyle = g; ctx.fillRect(c.x - c.w / 2, top, c.w, hpx);
    ctx.strokeStyle = 'rgba(227,176,75,0.55)'; ctx.lineWidth = 2; ctx.strokeRect(c.x - c.w / 2, top, c.w, hpx);
    for (let y = base - seg; y > top + 20; y -= seg) {
      ctx.fillStyle = 'rgba(227,176,75,0.75)'; ctx.fillRect(c.x - c.w / 2 - 4, y - 3, c.w + 8, 6);
      ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(c.x - c.w / 2, y + 3, c.w, 5);
    }
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const tg = ctx.createRadialGradient(c.x, top, 0, c.x, top, 130);
    tg.addColorStop(0, `rgba(255,220,150,${0.6 * (1 - p * 0.6)})`); tg.addColorStop(1, 'rgba(255,220,150,0)');
    ctx.fillStyle = tg; ctx.fillRect(c.x - 130, top - 130, 260, 260);
    ctx.restore();
    ctx.fillStyle = '#5a7d3d'; ctx.beginPath(); ctx.moveTo(c.x - c.w / 2, top); ctx.lineTo(c.x, top - c.w * 1.4); ctx.lineTo(c.x + c.w / 2, top); ctx.fill();
    const r = U.mulberry32(50 + c.hue);
    let k = 0;
    for (let y = base - seg * 3; y > top + seg; y -= seg) {
      const born = clamp((p - 0.35) * 3 - k * 0.02); k++;
      const s = r() < 0.5 ? -1 : 1, rr = r();
      if (born <= 0) continue;
      ctx.save(); ctx.translate(c.x + s * c.w / 2, y); ctx.rotate(s * (0.7 + 0.3 * rr) + Math.sin(t * 1.4 + k) * 0.08);
      ctx.fillStyle = '#4e7a38'; ctx.strokeStyle = 'rgba(227,176,75,0.5)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.ellipse(0, -60 * born, 14 * born, 62 * born, 0, 0, 7); ctx.fill(); ctx.stroke();
      ctx.restore();
    }
    ctx.restore();
  }

  function burst(ctx, t, cam) {
    const u = t - ev.drop; if (u < 0 || u > 1.4) return;
    const r = U.mulberry32(99), y = SOIL - cam;
    ctx.save();
    for (let i = 0; i < 40; i++) {
      const ang = -Math.PI / 2 + (r() - 0.5) * 2.4, sp = 400 + r() * 900, sz = 5 + r() * 12;
      const x = SX + Math.cos(ang) * sp * u, yy = y + Math.sin(ang) * sp * u + 1400 * u * u;
      ctx.globalAlpha = 1 - u / 1.4; ctx.fillStyle = i % 3 ? '#3a2a1c' : GOLD;
      ctx.beginPath(); ctx.arc(x, yy, sz, 0, 7); ctx.fill();
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
    ctx.fillText('GLEICHNISSE IN 30 SEKUNDEN · #2', W / 2, S.SAFE.y + 34);
    ctx.fillStyle = 'rgba(227,176,75,0.5)'; ctx.fillRect(W / 2 - 60, S.SAFE.y + 52, 120, 2);
    ctx.restore();
  }
  function card(ctx, c, t) {
    if (t < c.t - 0.01 || t > c.end + 0.1) return;
    const size = c.small ? 92 : 128, lh = size * 1.02;
    const fadeOut = 1 - clamp((t - c.end) / 0.1);
    const y0 = S.SAFE.y + 100 + size * 0.8;
    ctx.save(); ctx.textBaseline = 'alphabetic';
    ctx.font = `400 ${size}px "Bebas Neue"`;
    c.lines.forEach((line, i) => {
      const appear = c.t === ev.hook || c.t === ev.drop ? 1 : ease.outCubic(clamp((t - c.t - i * 0.12) / 0.28));
      const a = appear * fadeOut; if (a <= 0) return;
      const parts = line.split('*');
      const total = parts.reduce((w, p) => w + ctx.measureText(p).width, 0);
      let x = W / 2 - total / 2; const y = y0 + i * lh + (1 - appear) * 30;
      parts.forEach((p, j) => {
        ctx.globalAlpha = a;
        ctx.shadowColor = 'rgba(0,0,0,0.95)'; ctx.shadowBlur = 26;
        ctx.fillStyle = j % 2 ? GOLD : INK;
        ctx.fillText(p, x, y);
        x += ctx.measureText(p).width;
      });
    });
    ctx.restore();
  }
  function counter(ctx, t) {
    if (t >= ev.end) return;
    let label, n, l;
    if (t < ev.drop) { l = lastOf(S.ticks, t); label = 'TAG '; n = l ? l.n.toLocaleString('de-DE') : ''; }
    else { l = lastOf(S.metres, t); label = 'METER '; n = l ? String(l.n) : '0'; }
    const pop = l ? Math.exp(-(t - l.t) * 8) : 0;
    const a = t >= ev.drop ? 1 : (1 - sm(ev.reveal, ev.reveal + 0.3, t));
    if (a <= 0.01) return;
    const big = t >= ev.drop;
    ctx.save(); ctx.globalAlpha = clamp(a);
    const y = H * 0.755;
    const sz = (big ? 96 : 76) * (1 + 0.15 * pop);
    ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(n).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left';
    if (big) { ctx.fillStyle = 'rgba(6,6,10,0.78)'; ctx.fillRect(x0 - 36, y - 92, lw + nw + 72, 124); ctx.strokeStyle = 'rgba(227,176,75,0.5)'; ctx.lineWidth = 2; ctx.strokeRect(x0 - 36, y - 92, lw + nw + 72, 124); }
    ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
    ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = 'rgba(242,235,221,0.8)'; ctx.fillText(label, x0, y);
    ctx.font = `700 ${sz}px "Cinzel"`;
    ctx.shadowColor = `rgba(255,200,100,${0.5 + 0.5 * pop})`; ctx.shadowBlur = 20 + 30 * pop;
    ctx.fillStyle = pop > 0.4 ? GOLD_HI : GOLD;
    ctx.fillText(n, x0 + lw, y);
    ctx.restore();
  }
  function footer(ctx, t) {
    const a = sm(ev.follow, ev.follow + 0.6, t);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center';
    const y = H * 0.735;
    ctx.fillStyle = 'rgba(6,6,10,0.85)'; ctx.fillRect(W / 2 - 330, y - 62, 660, 130);
    ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 2; ctx.strokeRect(W / 2 - 330, y - 62, 660, 130);
    ctx.font = '700 54px "Cinzel"'; ctx.fillStyle = GOLD_HI;
    ctx.fillText('FOLGE FÜR TEIL #3', W / 2, y);
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
      for (const [h, amp] of [[ev.hook, 12], [ev.drop, 38]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      const cam = camY(t);
      const zoom = 1 + 0.08 * sm(0, ev.reveal, t) * (1 - sm(ev.reveal - 0.3, ev.reveal + 0.5, t));
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      ctx.translate(SX, SOIL - cam); ctx.scale(zoom, zoom); ctx.translate(-SX, -(SOIL - cam));
      sky(ctx, t, cam);
      for (let i = CULMS.length - 1; i >= 1; i--) culm(ctx, t, cam, CULMS[i]);
      ground(ctx, t, cam);
      roots(ctx, t, cam);
      culm(ctx, t, cam, CULMS[0]);
      sprout(ctx, t, cam);
      drops(ctx, t, cam);
      burst(ctx, t, cam);
      seasons(ctx, t);
      embers(ctx, t, t >= ev.drop ? 1.5 * Math.exp(-(t - ev.drop)) : 0);
      ctx.restore();
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(0, 0, W, H); }
      const f = t >= ev.drop ? 0.9 * Math.exp(-(t - ev.drop) * 9) : (t < 0.2 ? 0.18 * Math.exp(-t * 14) : 0);
      if (f > 0.01) { ctx.fillStyle = `rgba(255,236,200,${f})`; ctx.fillRect(0, 0, W, H); }
      if (t >= ev.end - 0.5) { ctx.fillStyle = `rgba(4,4,8,${0.55 * sm(ev.end - 0.5, ev.end + 0.5, t)})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
