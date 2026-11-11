// LOREBOUND – „Ein Tag länger als ein Jahr“ (Venus). Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev, BEAT, YEAR, ROT } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const SUN = { x: W / 2, y: H * 0.47 }, ORB = 250, VR = 56;
  const CLOSE = { x: W / 2, y: H * 0.57, r: 360 };
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const ALL = [...S.ticks, S.finalTick];

  function countAt(t) { let n = 0; for (const s of ALL) if (t >= s.t) n = s.n; return n; }
  function lastTick(t) { let l = null; for (const s of ALL) if (t >= s.t) l = s; return l; }
  function daysAt(t) {
    if (t < ALL[0].t) return 0;
    if (t >= S.finalTick.t) return 243 + (t - S.finalTick.t) * 2.5;
    for (let i = 0; i < ALL.length - 1; i++) {
      const a = ALL[i], b = ALL[i + 1];
      if (t >= a.t && t < b.t) {
        if (b === S.finalTick) { // hold during the breath, then snap on the drop
          const u = clamp((t - a.t) / (ev.breath - a.t));
          return lerp(a.n, 242.6, ease.outCubic(u));
        }
        return lerp(a.n, b.n, (t - a.t) / (b.t - a.t));
      }
    }
    return 243;
  }

  // ---------- background ----------
  function background(ctx, t) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#05060b'); g.addColorStop(0.55, '#0b0b14'); g.addColorStop(1, '#140f0a');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    const r = U.mulberry32(5);
    for (let i = 0; i < 170; i++) {
      const x = r() * W, y = r() * H, s = 1 + r() * 2.2, a = 0.15 + 0.45 * r() * (0.6 + 0.4 * Math.sin(t * (0.8 + r()) + i));
      ctx.fillStyle = `rgba(235,228,210,${a})`; ctx.fillRect(x, y, s, s);
    }
    const ng = ctx.createRadialGradient(W * 0.25, H * 0.3, 0, W * 0.25, H * 0.3, 700);
    ng.addColorStop(0, 'rgba(90,70,130,0.10)'); ng.addColorStop(1, 'rgba(90,70,130,0)');
    ctx.fillStyle = ng; ctx.fillRect(0, 0, W, H);
  }

  function dust(ctx, t, boost = 0) {
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 36; i++) {
      const sp = 20 + r() * 40, x0 = r() * W, ph = r() * 40, sz = 1.2 + r() * 2.5;
      const y = H - ((t * sp + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.5 + i) * 30;
      ctx.fillStyle = `rgba(255,210,130,${Math.min(1, (0.15 + 0.3 * r()) * (1 + boost))})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- sun ----------
  function sun(ctx, t, a) {
    if (a <= 0.01) return;
    ctx.save(); ctx.globalAlpha = a;
    ctx.globalCompositeOperation = 'lighter';
    const pulse = 1 + 0.03 * Math.sin(t * 3);
    const g = ctx.createRadialGradient(SUN.x, SUN.y, 0, SUN.x, SUN.y, 260 * pulse);
    g.addColorStop(0, 'rgba(255,230,160,0.95)'); g.addColorStop(0.25, 'rgba(255,190,90,0.55)'); g.addColorStop(1, 'rgba(255,150,60,0)');
    ctx.fillStyle = g; ctx.fillRect(SUN.x - 300, SUN.y - 300, 600, 600);
    ctx.restore();
    ctx.save(); ctx.globalAlpha = a;
    ctx.fillStyle = '#FFE7A8'; ctx.shadowColor = 'rgba(255,200,100,1)'; ctx.shadowBlur = 40;
    ctx.beginPath(); ctx.arc(SUN.x, SUN.y, 44, 0, 7); ctx.fill();
    ctx.restore();
  }

  // ---------- venus ----------
  function venus(ctx, x, y, R, t, light) {
    ctx.save(); ctx.translate(x, y);
    // atmosphere glow
    const ag = ctx.createRadialGradient(0, 0, R * 0.9, 0, 0, R * 1.35);
    ag.addColorStop(0, 'rgba(240,200,120,0.35)'); ag.addColorStop(1, 'rgba(240,200,120,0)');
    ctx.fillStyle = ag; ctx.beginPath(); ctx.arc(0, 0, R * 1.35, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.arc(0, 0, R, 0, 7); ctx.save(); ctx.clip();
    const base = ctx.createRadialGradient(-R * 0.3, -R * 0.3, R * 0.1, 0, 0, R * 1.05);
    base.addColorStop(0, '#f3dca0'); base.addColorStop(0.6, '#d7ac62'); base.addColorStop(1, '#8a6232');
    ctx.fillStyle = base; ctx.fillRect(-R, -R, 2 * R, 2 * R);
    // drifting cloud bands (Venus' clouds race around the planet)
    const r = U.mulberry32(77);
    for (let i = 0; i < 14; i++) {
      const by = -R + (2 * R * (i + r() * 0.6)) / 14, th = R * (0.05 + 0.08 * r());
      const sp = 0.06 + 0.05 * r(), ph = r() * 10;
      ctx.beginPath();
      for (let k = 0; k <= 40; k++) {
        const xx = -R + (2 * R * k) / 40;
        const yy = by + Math.sin(xx / R * 3 + ph + t * sp * 6) * th * 0.8;
        k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy);
      }
      ctx.lineWidth = th; ctx.strokeStyle = i % 2 ? 'rgba(255,240,205,0.22)' : 'rgba(150,100,45,0.22)'; ctx.stroke();
    }
    // night side
    const lx = Math.cos(light), ly = Math.sin(light);
    const sh = ctx.createLinearGradient(lx * R, ly * R, -lx * R, -ly * R);
    sh.addColorStop(0, 'rgba(0,0,0,0)'); sh.addColorStop(0.5, 'rgba(5,4,10,0.15)'); sh.addColorStop(1, 'rgba(5,4,10,0.85)');
    ctx.fillStyle = sh; ctx.fillRect(-R, -R, 2 * R, 2 * R);
    ctx.restore();
    ctx.beginPath(); ctx.arc(0, 0, R, 0, 7);
    ctx.strokeStyle = 'rgba(255,217,138,0.75)'; ctx.lineWidth = Math.max(2, R * 0.012); ctx.shadowColor = 'rgba(227,176,75,0.8)'; ctx.shadowBlur = 18; ctx.stroke();
    ctx.restore();
  }

  function arrowHead(ctx, x, y, ang, s) {
    ctx.beginPath(); ctx.moveTo(x + Math.cos(ang) * s, y + Math.sin(ang) * s);
    ctx.lineTo(x + Math.cos(ang + 2.5) * s, y + Math.sin(ang + 2.5) * s);
    ctx.lineTo(x + Math.cos(ang - 2.5) * s, y + Math.sin(ang - 2.5) * s); ctx.closePath(); ctx.fill();
  }

  // ---------- the orbit scene ----------
  function orbitScene(ctx, t, k) {
    const d = daysAt(t);
    const th = -(2 * Math.PI * d) / YEAR; // counter-clockwise orbit
    const vx = SUN.x + ORB * Math.cos(th), vy = SUN.y + ORB * Math.sin(th);
    const yearDone = d >= YEAR;
    ctx.save(); ctx.globalAlpha = k;
    // orbit path
    ctx.setLineDash([6, 12]); ctx.strokeStyle = 'rgba(242,235,221,0.22)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(SUN.x, SUN.y, ORB, 0, 7); ctx.stroke(); ctx.setLineDash([]);
    // orbit progress arc (the year)
    const yp = Math.min(1, d / YEAR);
    if (yp > 0) {
      const flash = t >= ev.year ? Math.exp(-(t - ev.year) * 3) : 0;
      ctx.strokeStyle = yearDone ? GOLD_HI : GOLD; ctx.lineWidth = 6 + 6 * flash;
      ctx.shadowColor = 'rgba(255,200,100,0.9)'; ctx.shadowBlur = 14 + 30 * flash;
      ctx.beginPath(); ctx.arc(SUN.x, SUN.y, ORB, -2 * Math.PI * yp, 0); ctx.stroke(); ctx.shadowBlur = 0;
      if (flash > 0.01) {
        ctx.strokeStyle = `rgba(255,217,138,${flash})`; ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(SUN.x, SUN.y, ORB + 60 * (1 - flash), 0, 7); ctx.stroke();
      }
    }
    // start marker
    ctx.fillStyle = 'rgba(242,235,221,0.6)'; ctx.fillRect(SUN.x + ORB - 2, SUN.y - 18, 4, 36);
    sun(ctx, t, 1);
    ctx.restore();
    return { vx, vy, th, d };
  }

  function rotationRing(ctx, t, x, y, d, a) {
    const rp = Math.min(1, d / ROT);
    const R = VR + 26;
    ctx.save(); ctx.globalAlpha = a;
    ctx.strokeStyle = 'rgba(242,235,221,0.18)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(x, y, R, 0, 7); ctx.stroke();
    if (rp > 0) {
      const done = d >= ROT;
      const fl = t >= ev.drop ? Math.exp(-(t - ev.drop) * 2.5) : 0;
      ctx.strokeStyle = done ? GOLD_HI : '#d9a24a'; ctx.lineWidth = 7 + 5 * fl;
      ctx.shadowColor = 'rgba(255,200,100,0.9)'; ctx.shadowBlur = 12 + 30 * fl;
      const a0 = -Math.PI / 2; // clockwise = backwards
      ctx.beginPath(); ctx.arc(x, y, R, a0, a0 + 2 * Math.PI * rp); ctx.stroke();
      const ea = a0 + 2 * Math.PI * rp;
      ctx.fillStyle = GOLD_HI; ctx.beginPath(); ctx.arc(x + R * Math.cos(ea), y + R * Math.sin(ea), 8, 0, 7); ctx.fill();
      ctx.shadowBlur = 0;
    }
    ctx.restore();
  }

  function retroArrows(ctx, t, x, y) {
    const a = sm(ev.retro, ev.retro + 0.5, t) * (1 - sm(ev.end - 0.3, ev.end + 0.3, t));
    if (a <= 0.01) return;
    ctx.save(); ctx.globalAlpha = a; ctx.lineWidth = 6; ctx.lineCap = 'round';
    // spin arrow (clockwise) around venus
    const R = VR + 54, spin = (t - ev.retro) * 1.4;
    ctx.strokeStyle = GOLD_HI; ctx.fillStyle = GOLD_HI; ctx.shadowColor = 'rgba(255,200,100,0.9)'; ctx.shadowBlur = 16;
    ctx.beginPath(); ctx.arc(x, y, R, spin, spin + 4.2); ctx.stroke();
    const e = spin + 4.2; arrowHead(ctx, x + R * Math.cos(e), y + R * Math.sin(e), e + Math.PI / 2, 18);
    ctx.restore();
  }

  function bars(ctx, t, d, a) {
    if (a <= 0.01) return;
    const rows = [['EIN JAHR', d / YEAR, ev.year], ['EIN TAG', d / ROT, ev.drop]];
    ctx.save(); ctx.globalAlpha = a;
    rows.forEach(([label, p, tDone], i) => {
      const y = H * 0.655 + i * 78, x0 = 360, x1 = 900, pp = clamp(p);
      const done = p >= 1, fl = t >= tDone ? Math.exp(-(t - tDone) * 3) : 0;
      ctx.font = '700 40px "Cinzel"'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      ctx.fillStyle = done ? GOLD_HI : 'rgba(242,235,221,0.85)'; ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 10;
      ctx.fillText(label, x0 - 24, y);
      ctx.shadowBlur = 0;
      ctx.fillStyle = 'rgba(242,235,221,0.12)'; ctx.fillRect(x0, y - 14, x1 - x0, 28);
      ctx.fillStyle = done ? GOLD_HI : GOLD; ctx.shadowColor = 'rgba(255,200,100,0.9)'; ctx.shadowBlur = 8 + 30 * fl;
      ctx.fillRect(x0, y - 14, (x1 - x0) * pp, 28); ctx.shadowBlur = 0;
      ctx.strokeStyle = 'rgba(227,176,75,0.6)'; ctx.lineWidth = 2; ctx.strokeRect(x0, y - 14, x1 - x0, 28);
      if (done) { // check mark
        ctx.strokeStyle = GOLD_HI; ctx.lineWidth = 6; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(x1 + 22, y); ctx.lineTo(x1 + 34, y + 12); ctx.lineTo(x1 + 56, y - 14); ctx.stroke();
      }
    });
    ctx.restore();
  }

  function burst(ctx, t, t0, x, y, n, speed, life) {
    const u = t - t0; if (u < 0 || u > life) return;
    const r = U.mulberry32(Math.round(t0 * 100) + 3);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < n; i++) {
      const ang = r() * Math.PI * 2, sp = speed * (0.3 + r());
      const px = x + Math.cos(ang) * sp * u, py = y + Math.sin(ang) * sp * u;
      ctx.strokeStyle = `rgba(255,${Math.round(190 + 50 * r())},110,${1 - u / life})`; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px - Math.cos(ang) * 22, py - Math.sin(ang) * 22); ctx.stroke();
    }
    const rr = 40 + u * speed * 0.9;
    ctx.strokeStyle = `rgba(255,217,138,${0.8 * (1 - u / life)})`; ctx.lineWidth = 5;
    ctx.beginPath(); ctx.arc(x, y, rr, 0, 7); ctx.stroke();
    ctx.restore();
  }

  // ---------- text ----------
  function seriesTag(ctx) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('WISSEN IN 30 SEKUNDEN · #1', W / 2, S.SAFE.y + 34);
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
    if (t < ev.zoom || t >= ev.follow) return;
    const n = countAt(t); if (!n) return;
    const ls = lastTick(t);
    const pop = ls ? Math.exp(-(t - ls.t) * 8) : 0;
    const big = n === 243;
    const a = sm(ev.zoom, ev.zoom + 0.3, t);
    ctx.save(); ctx.globalAlpha = a;
    const y = H * 0.765;
    const sz = (big ? 92 : 72) * (1 + 0.12 * pop);
    const label = 'ERDTAG ';
    ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(String(n)).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left'; ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
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
    ctx.fillStyle = 'rgba(6,6,10,0.85)'; ctx.fillRect(W / 2 - 330, y - 62, 660, 130);
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
      for (const [h, amp] of [[ev.hook, 14], [ev.year, 8], [ev.drop, 34]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      const ls = lastTick(t);
      if (ls && ls !== S.finalTick && t > ev.zoom) shake += 2.5 * Math.exp(-(t - ls.t) * 14);
      const z = ease.inOutCubic(sm(ev.zoom, ev.zoom + 0.9, t)); // close-up -> orbit
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      background(ctx, t);
      let vx = CLOSE.x, vy = CLOSE.y, vr = CLOSE.r * (1 + 0.12 * Math.exp(-t * 5)) * (1 + 0.04 * sm(0, ev.zoom, t));
      let light = Math.PI * 1.25, d = 0;
      if (z > 0) {
        const o = orbitScene(ctx, t, z);
        vx = lerp(CLOSE.x, o.vx, z); vy = lerp(CLOSE.y, o.vy, z); vr = lerp(vr, VR, z); d = o.d;
        light = lerp(Math.PI * 1.25, o.th + Math.PI, z);
      }
      venus(ctx, vx, vy, vr, t, light);
      if (z > 0.5) {
        rotationRing(ctx, t, vx, vy, d, sm(ev.zoom + 0.5, ev.zoom + 1.0, t));
        retroArrows(ctx, t, vx, vy);
        if (t >= ev.year) burst(ctx, t, ev.year, vx, vy, 30, 500, 0.8);
        if (t >= ev.drop) burst(ctx, t, ev.drop, vx, vy, 90, 1100, 1.3);
      }
      dust(ctx, t, t >= ev.drop ? 1.5 * Math.exp(-(t - ev.drop)) : 0);
      bars(ctx, t, d, sm(ev.zoom + 0.6, ev.zoom + 1.1, t) * (1 - sm(ev.follow - 0.3, ev.follow + 0.2, t)));
      ctx.restore();
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(0, 0, W, H); }
      const f = t >= ev.drop ? 0.9 * Math.exp(-(t - ev.drop) * 9) : (t < 0.25 ? 0.35 * Math.exp(-t * 12) : 0);
      if (f > 0.01) { ctx.fillStyle = `rgba(255,236,200,${f})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
