// LOREBOUND – „Der hundertste Schlag“. Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev, BEAT } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const STONE = { x: W / 2 - 70, y: H * 0.53 };
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const ALL = [...S.strikes, S.finalStrike];

  // ---------- background ----------
  function background(ctx, t) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#06070c'); g.addColorStop(0.55, '#0e0d14'); g.addColorStop(1, '#1b130b');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    const r = U.mulberry32(5);
    for (let i = 0; i < 80; i++) {
      const x = r() * W, y = r() * H * 0.5, a = 0.12 + 0.3 * r() * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
      ctx.fillStyle = `rgba(230,220,200,${a})`; ctx.fillRect(x, y, 2.2, 2.2);
    }
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const lc = ctx.createLinearGradient(0, 0, 0, H * 0.85);
    lc.addColorStop(0, 'rgba(227,176,75,0.09)'); lc.addColorStop(1, 'rgba(227,176,75,0)');
    ctx.fillStyle = lc; ctx.beginPath(); ctx.moveTo(W * 0.38, 0); ctx.lineTo(W * 0.62, 0); ctx.lineTo(W * 0.95, H * 0.85); ctx.lineTo(W * 0.05, H * 0.85); ctx.fill();
    ctx.restore();
    for (let i = 0; i < 3; i++) {
      const y = H * (0.70 + i * 0.06), x = W / 2 + Math.sin(t * 0.25 + i * 1.7) * 220;
      const mg = ctx.createRadialGradient(x, y, 0, x, y, 650);
      mg.addColorStop(0, 'rgba(120,110,130,0.06)'); mg.addColorStop(1, 'rgba(120,110,130,0)');
      ctx.fillStyle = mg; ctx.fillRect(0, y - 650, W, 1300);
    }
    // ground
    ctx.fillStyle = '#08070a';
    ctx.beginPath(); ctx.moveTo(0, H);
    const rr = U.mulberry32(11);
    for (let x = 0; x <= W + 60; x += 60) ctx.lineTo(x, H * 0.77 + Math.sin(x * 0.01) * 14 + rr() * 12);
    ctx.lineTo(W, H); ctx.fill();
  }

  function embers(ctx, t, boost = 0) {
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 40; i++) {
      const sp = 40 + r() * 70, x0 = r() * W, ph = r() * 40, sz = 1.5 + r() * 3;
      const y = H - ((t * sp + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.8 + i) * 30;
      ctx.fillStyle = `rgba(255,200,110,${Math.min(1, (0.2 + 0.35 * r()) * (1 + boost))})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- the stone: a low-poly block ----------
  const NR = 12, RX = 300, RY = 320;
  const OUT = [], INN = [];
  (function build() {
    const r = U.mulberry32(42);
    for (let i = 0; i < NR; i++) {
      const a = (i / NR) * Math.PI * 2 - Math.PI / 2;
      // squarish block: superellipse
      const c = Math.cos(a), s = Math.sin(a);
      const k = 0.35;
      const x = Math.sign(c) * Math.pow(Math.abs(c), k) * RX * (0.93 + 0.1 * r());
      const y = Math.sign(s) * Math.pow(Math.abs(s), k) * RY * (0.93 + 0.1 * r());
      OUT.push([x, y]);
      INN.push([x * (0.5 + 0.12 * r()) + (r() - 0.5) * 30, y * (0.5 + 0.12 * r()) + (r() - 0.5) * 30]);
    }
  })();
  const FACES = [];
  for (let i = 0; i < NR; i++) {
    const j = (i + 1) % NR;
    FACES.push([OUT[i], OUT[j], INN[i]], [OUT[j], INN[j], INN[i]], [INN[i], INN[j], [0, 0]]);
  }
  function faceShade(f) {
    const cx = (f[0][0] + f[1][0] + f[2][0]) / 3, cy = (f[0][1] + f[1][1] + f[2][1]) / 3;
    const L = Math.hypot(cx, cy) || 1;
    const d = (-(cx / L) * 0.6 - (cy / L) * 0.8);
    return 0.55 + 0.32 * d * Math.min(1, L / 200) + 0.1 * (U.hash(Math.round(cx), Math.round(cy)) - 0.5);
  }
  const shadeCol = (s, dim) => { const k = clamp(s) * dim; return `rgb(${Math.round(lerp(12, 92, k))},${Math.round(lerp(12, 86, k))},${Math.round(lerp(16, 92, k))})`; };
  function stonePath(ctx) { ctx.beginPath(); OUT.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]))); ctx.closePath(); }

  // ---------- cracks: grown from the impact point, one batch per strike ----------
  const HIT = [RX * 0.98, -20];
  const CR = [];
  (function grow() {
    const r = U.mulberry32(7);
    const tips = [{ x: HIT[0] - 10, y: HIT[1], a: Math.PI, w: 4 }];
    let guard = 0;
    while (CR.length < 200 && guard++ < 5000) {
      const i = Math.floor(r() * tips.length), tp = tips[i];
      const a = tp.a + (r() - 0.5) * 0.9;
      const len = 26 + r() * 30;
      const nx = tp.x + Math.cos(a) * len, ny = tp.y + Math.sin(a) * len;
      if (Math.abs(nx) / RX + 0.0 > 0.9 || Math.abs(ny) / RY > 0.9) { tp.a += Math.PI * 0.5 * (r() - 0.5); continue; }
      CR.push([tp.x, tp.y, nx, ny, Math.max(1, tp.w)]);
      tips[i] = { x: nx, y: ny, a, w: tp.w * 0.93 };
      if (r() < 0.22) tips.push({ x: nx, y: ny, a: a + (r() < 0.5 ? 1 : -1) * (0.6 + r() * 0.6), w: tp.w * 0.7 });
    }
  })();
  // the split line (top to bottom, jagged) for strike 100
  const SPLIT = [];
  (function () { const r = U.mulberry32(13); for (let i = 0; i <= 10; i++) SPLIT.push([(r() - 0.5) * 70 + 10, -RY * 1.1 + (2.2 * RY * i) / 10]); })();

  function countAt(t) { let n = 0; for (const s of ALL) if (t >= s.t) n = s.n; return n; }
  function lastStrike(t) { let l = null; for (const s of ALL) if (t >= s.t) l = s; return l; }
  function nextStrike(t) { for (const s of ALL) if (s.t > t) return s; return null; }

  function cracks(ctx, t, xray) {
    const n = countAt(t);
    const vis = Math.floor(CR.length * Math.min(1, n / 99));
    if (!vis) return;
    const base = 0.10 + 0.85 * xray;
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
    for (const [lw, a] of [[9, 0.12], [3.5, 0.5], [1.6, 1]]) {
      ctx.strokeStyle = `rgba(255,205,120,${a * base})`;
      for (let i = 0; i < vis; i++) {
        const c = CR[i];
        ctx.lineWidth = lw * (0.5 + c[4] / 4);
        ctx.beginPath(); ctx.moveTo(c[0], c[1]); ctx.lineTo(c[2], c[3]); ctx.stroke();
      }
    }
    // travelling glints along the cracks while x-rayed
    if (xray > 0.3) {
      for (let k = 0; k < 6; k++) {
        const c = CR[Math.floor(((t * 9 + k * 31) % vis))];
        const gr = ctx.createRadialGradient(c[2], c[3], 0, c[2], c[3], 30);
        gr.addColorStop(0, `rgba(255,240,200,${0.8 * xray})`); gr.addColorStop(1, 'rgba(255,240,200,0)');
        ctx.fillStyle = gr; ctx.fillRect(c[2] - 30, c[3] - 30, 60, 60);
      }
    }
    ctx.restore();
  }

  function stoneBody(ctx, t, xray) {
    const dim = 1 - 0.65 * xray;
    for (const f of FACES) {
      ctx.fillStyle = shadeCol(faceShade(f), dim);
      ctx.beginPath(); ctx.moveTo(f[0][0], f[0][1]); ctx.lineTo(f[1][0], f[1][1]); ctx.lineTo(f[2][0], f[2][1]); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(227,176,75,0.08)'; ctx.lineWidth = 1.5; ctx.stroke();
    }
    ctx.save(); stonePath(ctx); ctx.clip(); cracks(ctx, t, xray); ctx.restore();
    stonePath(ctx);
    ctx.shadowColor = 'rgba(227,176,75,0.7)'; ctx.shadowBlur = 16 + 20 * xray;
    ctx.strokeStyle = `rgba(227,176,75,${0.6 + 0.3 * xray})`; ctx.lineWidth = 3.5; ctx.stroke();
    ctx.shadowBlur = 0;
  }

  function halfClip(ctx, side) {
    ctx.beginPath();
    ctx.moveTo(side * 900, -900);
    SPLIT.forEach((p) => ctx.lineTo(p[0], p[1]));
    ctx.lineTo(side * 900, 900);
    ctx.closePath();
  }

  function stone(ctx, t) {
    const xray = sm(ev.reveal - 0.1, ev.reveal + 0.6, t) * (1 - sm(ev.last - 0.4, ev.last + 0.2, t)) + (t >= ev.last ? 0.25 : 0);
    // small knock on every strike
    const ls = lastStrike(t);
    const kick = ls && ls !== S.finalStrike ? 10 * Math.exp(-(t - ls.t) * 14) : 0;
    ctx.save(); ctx.translate(STONE.x - kick, STONE.y);
    // shadow on the ground
    ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.beginPath(); ctx.ellipse(0, RY + 18, RX * 1.15, 34, 0, 0, 7); ctx.fill();
    if (t < ev.drop) {
      stoneBody(ctx, t, xray);
    } else {
      const u = t - ev.drop;
      const open = ease.outCubic(clamp(u / 0.9));
      // light from inside
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const bw = 40 + 180 * open;
      const lg = ctx.createRadialGradient(0, 0, 0, 0, 0, 700);
      lg.addColorStop(0, 'rgba(255,220,150,0.55)'); lg.addColorStop(1, 'rgba(255,220,150,0)');
      ctx.fillStyle = lg; ctx.fillRect(-700, -700, 1400, 1400);
      const beam = ctx.createLinearGradient(-bw, 0, bw, 0);
      beam.addColorStop(0, 'rgba(255,214,140,0)'); beam.addColorStop(0.5, 'rgba(255,236,190,0.4)'); beam.addColorStop(1, 'rgba(255,214,140,0)');
      ctx.fillStyle = beam; ctx.fillRect(-bw, -H, bw * 2, H * 1.2);
      ctx.restore();
      for (const side of [-1, 1]) {
        ctx.save();
        ctx.translate(side * 120 * open, 12 * open);
        ctx.rotate(side * 0.10 * open);
        halfClip(ctx, side); ctx.clip();
        stoneBody(ctx, t, 0.25);
        // glowing broken edge
        ctx.beginPath(); SPLIT.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
        ctx.shadowColor = 'rgba(255,214,140,1)'; ctx.shadowBlur = 30; ctx.strokeStyle = GOLD_HI; ctx.lineWidth = 6; ctx.stroke(); ctx.shadowBlur = 0;
        ctx.restore();
      }
    }
    ctx.restore();
  }

  // ---------- the hammer: held level from the right, pulls back and strikes ----------
  const HITW = [STONE.x + HIT[0] + 4, STONE.y + HIT[1]];
  function hammerPos(t) { // 0 = drawn back, 1 = contact
    const nx = nextStrike(t), ls = lastStrike(t);
    let p = 0;
    if (ls) { const u = t - ls.t; if (u < 0.3) p = 1 - ease.outCubic(clamp(u / 0.3)); }
    if (nx) { const d = nx.t - t, sw = nx === S.finalStrike ? 0.22 : 0.16; if (d < sw) p = Math.max(p, ease.inQuad(1 - d / sw)); }
    return p;
  }
  function hammer(ctx, t) {
    const vis = (1 - sm(ev.reveal, ev.reveal + 0.4, t)) + sm(ev.last - 0.6, ev.last - 0.2, t) * (1 - sm(ev.drop + 0.4, ev.drop + 1.2, t));
    if (vis <= 0.01) return;
    let p = hammerPos(t);
    if (t >= ev.drop) p = 1 - ease.outCubic(clamp((t - ev.drop) / 0.8));
    const back = 170 * (1 - p), tilt = -0.45 * (1 - p);
    ctx.save(); ctx.globalAlpha = clamp(vis);
    ctx.translate(HITW[0] + 62 + back, HITW[1] - 60 * (1 - p)); ctx.rotate(tilt);
    ctx.fillStyle = '#16120d'; ctx.strokeStyle = 'rgba(227,176,75,0.8)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.rect(50, -14, 700, 28); ctx.fill(); ctx.stroke();
    ctx.shadowColor = 'rgba(227,176,75,0.7)'; ctx.shadowBlur = 14;
    ctx.fillStyle = '#25262d'; ctx.beginPath(); ctx.rect(-58, -82, 116, 164); ctx.fill(); ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.fillStyle = 'rgba(255,230,180,0.22)'; ctx.fillRect(-54, -78, 16, 156);
    ctx.fillStyle = 'rgba(227,176,75,0.35)'; ctx.fillRect(-10, -82, 6, 164);
    ctx.restore();
  }

  function sparks(ctx, t, t0, at, n, speed, life = 0.8) {
    const u = t - t0; if (u < 0 || u > life) return;
    const r = U.mulberry32(Math.round(t0 * 100) + 3);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < n; i++) {
      const ang = Math.PI * (0.55 + r() * 0.9) + (r() - 0.5), sp = speed * (0.3 + r());
      const x = at[0] + Math.cos(ang) * sp * u, y = at[1] + Math.sin(ang) * sp * u + 700 * u * u;
      ctx.strokeStyle = `rgba(255,${Math.round(180 + 60 * r())},90,${1 - u / life})`; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - Math.cos(ang) * 18, y - Math.sin(ang) * 18); ctx.stroke();
    }
    ctx.restore();
  }
  function chips(ctx, t) {
    if (t < ev.drop || t > ev.drop + 2) return;
    const u = t - ev.drop, r = U.mulberry32(99);
    ctx.save();
    for (let i = 0; i < 26; i++) {
      const ang = -Math.PI / 2 + (r() - 0.5) * 2.6, sp = 500 + r() * 900, sz = 8 + r() * 18;
      const x = STONE.x + (r() - 0.5) * 60 + Math.cos(ang) * sp * u, y = STONE.y + (r() - 0.5) * 300 + Math.sin(ang) * sp * u + 1400 * u * u;
      ctx.save(); ctx.translate(x, y); ctx.rotate(u * 8 + i);
      ctx.globalAlpha = 1 - u / 2; ctx.fillStyle = shadeCol(0.4 + 0.4 * r(), 1); ctx.strokeStyle = 'rgba(227,176,75,0.6)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(-sz, -sz * 0.4); ctx.lineTo(sz * 0.6, -sz); ctx.lineTo(sz, sz * 0.5); ctx.lineTo(-sz * 0.3, sz); ctx.closePath(); ctx.fill(); ctx.stroke();
      ctx.restore();
    }
    ctx.restore();
  }

  // ---------- text ----------
  function seriesTag(ctx, t) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('GLEICHNISSE IN 30 SEKUNDEN · #1', W / 2, S.SAFE.y + 34);
    ctx.fillStyle = 'rgba(227,176,75,0.5)'; ctx.fillRect(W / 2 - 60, S.SAFE.y + 52, 120, 2);
    ctx.restore();
  }
  function card(ctx, c, t) {
    if (t < c.t - 0.01 || t > c.end + 0.25) return;
    const size = c.small ? 92 : 128, lh = size * 1.02;
    const fadeOut = 1 - clamp((t - c.end) / 0.25);
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
        ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 24;
        ctx.fillStyle = j % 2 ? GOLD : INK;
        ctx.fillText(p, x, y);
        x += ctx.measureText(p).width;
      });
    });
    ctx.restore();
  }
  function counter(ctx, t) {
    if (t >= ev.end) return;
    const n = countAt(t); if (!n) return;
    const ls = lastStrike(t);
    const pop = ls ? Math.exp(-(t - ls.t) * 8) : 0;
    const big = n === 100;
    const a = (1 - sm(ev.reveal, ev.reveal + 0.3, t)) + sm(ev.last - 0.3, ev.last, t);
    if (a <= 0.01 && !big) return;
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = big ? 1 : clamp(a);
    const y = H * 0.755;
    const sz = (big ? 96 : 72) * (1 + 0.15 * pop);
    ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
    ctx.font = `700 ${sz}px "Cinzel"`;
    const label = 'SCHLAG ', lw = (ctx.font = '700 40px "Cinzel"', ctx.measureText(label).width);
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(String(n)).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left';
    ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = 'rgba(242,235,221,0.75)'; ctx.fillText(label, x0, y);
    ctx.font = `700 ${sz}px "Cinzel"`;
    ctx.shadowColor = `rgba(255,200,100,${0.5 + 0.5 * pop})`; ctx.shadowBlur = 20 + 30 * pop;
    ctx.fillStyle = pop > 0.4 || big ? GOLD_HI : GOLD;
    ctx.fillText(String(n), x0 + lw, y);
    ctx.restore();
  }
  function footer(ctx, t) {
    const a = sm(ev.follow, ev.follow + 0.6, t);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center';
    const y = H * 0.735;
    ctx.fillStyle = 'rgba(6,6,10,0.82)'; ctx.fillRect(W / 2 - 330, y - 62, 660, 130);
    ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 2; ctx.strokeRect(W / 2 - 330, y - 62, 660, 130);
    ctx.font = '700 54px "Cinzel"'; ctx.fillStyle = GOLD_HI;
    ctx.fillText('FOLGE FÜR TEIL #2', W / 2, y);
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
      for (const [h, amp] of [[ev.hook, 12], [ev.drop, 36]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      const ls = lastStrike(t);
      if (ls && ls !== S.finalStrike && ls.t > 0) shake += (2 + 6 * ls.n / 99) * Math.exp(-(t - ls.t) * 12);
      // slow push-in during the reveal
      const zoom = 1 + 0.06 * sm(ev.reveal, ev.last, t) - 0.06 * sm(ev.last, ev.last + 0.5, t);
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      ctx.translate(STONE.x, STONE.y); ctx.scale(zoom, zoom); ctx.translate(-STONE.x, -STONE.y);
      background(ctx, t);
      stone(ctx, t);
      hammer(ctx, t);
      if (ls && ls !== S.finalStrike) sparks(ctx, t, ls.t, HITW, 14 + Math.round(16 * ls.n / 99), 520, 0.5);
      if (t >= ev.drop) sparks(ctx, t, ev.drop, [STONE.x, STONE.y], 80, 1000, 1.2);
      chips(ctx, t);
      embers(ctx, t, t >= ev.drop ? 1.5 * Math.exp(-(t - ev.drop)) : 0);
      ctx.restore();
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(0, 0, W, H); }
      const f = t >= ev.drop ? 0.9 * Math.exp(-(t - ev.drop) * 9) : (t < 0.2 ? 0.15 * Math.exp(-t * 14) : 0);
      if (f > 0.01) { ctx.fillStyle = `rgba(255,236,200,${f})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx, t);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
