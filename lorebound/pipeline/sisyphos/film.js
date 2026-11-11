// LOREBOUND – „Sisyphos“. Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev, BEAT } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const fmt = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, '.');

  // frozen time: while death is chained nothing moves
  const tf = (t) => (t < ev.frozen ? t : t < ev.escape ? ev.frozen + (t - ev.frozen) * 0.03 : t - (ev.escape - ev.frozen) * 0.97);

  // ---------- sky ----------
  function sky(ctx, t, warm) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#05060b'); g.addColorStop(0.55, '#0d0c14'); g.addColorStop(1, '#1a120b');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    const r = U.mulberry32(5);
    for (let i = 0; i < 90; i++) {
      const x = r() * W, y = r() * H * 0.55, a = 0.12 + 0.3 * r() * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
      ctx.fillStyle = `rgba(230,220,200,${a})`; ctx.fillRect(x, y, 2.2, 2.2);
    }
    if (warm > 0) {
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const x = W * 0.82, y = H * 0.47;
      const sg = ctx.createRadialGradient(x, y, 0, x, y, 1100);
      sg.addColorStop(0, `rgba(255,214,140,${0.65 * warm})`); sg.addColorStop(0.35, `rgba(227,150,60,${0.25 * warm})`); sg.addColorStop(1, 'rgba(227,150,60,0)');
      ctx.fillStyle = sg; ctx.fillRect(0, 0, W, H);
      // rays
      for (let i = 0; i < 14; i++) {
        const a = -Math.PI + (i / 13) * Math.PI + Math.sin(t * 0.3 + i) * 0.03;
        ctx.fillStyle = `rgba(255,220,150,${0.06 * warm})`;
        ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(a - 0.04) * 2200, y + Math.sin(a - 0.04) * 2200); ctx.lineTo(x + Math.cos(a + 0.04) * 2200, y + Math.sin(a + 0.04) * 2200); ctx.fill();
      }
      ctx.restore();
    }
  }

  function embers(ctx, t, boost = 0) {
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 44; i++) {
      const sp = 40 + r() * 70, x0 = r() * W, ph = r() * 40, sz = 1.5 + r() * 3;
      const y = H - ((t * sp + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.8 + i) * 30;
      ctx.fillStyle = `rgba(255,200,110,${Math.min(1, (0.2 + 0.35 * r()) * (1 + boost))})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- ACT 1: death in chains ----------
  const DX = W / 2, DY = H * 0.60;
  function link(ctx, x, y, a, s) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(a);
    ctx.beginPath(); ctx.ellipse(0, 0, 26 * s, 13 * s, 0, 0, 7); ctx.stroke();
    ctx.restore();
  }
  function chainLine(ctx, x0, y0, x1, y1, tight, t) {
    const n = 18, a = Math.atan2(y1 - y0, x1 - x0);
    for (let i = 0; i <= n; i++) {
      const u = i / n;
      const sag = (1 - tight) * Math.sin(u * Math.PI) * 120;
      const x = lerp(x0, x1, u), y = lerp(y0, y1, u) + sag;
      link(ctx, x, y, a + (i % 2 ? Math.PI / 2 : 0) * 0 + (i % 2 ? 0.0 : 0), 1);
      if (i % 2) { ctx.save(); ctx.translate(x, y); ctx.rotate(a); ctx.beginPath(); ctx.moveTo(-10, 0); ctx.lineTo(10, 0); ctx.stroke(); ctx.restore(); }
    }
  }
  function death(ctx, t) {
    const vis = 1 - sm(ev.escape + 0.6, ev.punish, t);
    if (vis <= 0.01) return;
    const T0 = tf(t);
    const breathe = Math.sin(T0 * 2.2) * 6;
    ctx.save(); ctx.globalAlpha = vis;
    // shadow
    ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.beginPath(); ctx.ellipse(DX, DY + 420, 360, 40, 0, 0, 7); ctx.fill();
    // cloak
    ctx.save(); ctx.translate(DX, DY + breathe);
    const cg = ctx.createLinearGradient(0, -380, 0, 420);
    cg.addColorStop(0, '#1d1a24'); cg.addColorStop(1, '#09080c');
    ctx.fillStyle = cg;
    ctx.beginPath();
    ctx.moveTo(0, -400);
    ctx.bezierCurveTo(150, -390, 180, -250, 170, -150);
    ctx.bezierCurveTo(260, 0, 330, 250, 340, 420);
    for (let i = 0; i <= 8; i++) ctx.lineTo(340 - i * 85, 420 + (i % 2 ? -30 : 0) + Math.sin(T0 * 3 + i) * 8);
    ctx.bezierCurveTo(-330, 250, -260, 0, -170, -150);
    ctx.bezierCurveTo(-180, -250, -150, -390, 0, -400);
    ctx.fill();
    ctx.strokeStyle = 'rgba(227,176,75,0.55)'; ctx.lineWidth = 3; ctx.shadowColor = 'rgba(227,176,75,0.6)'; ctx.shadowBlur = 18; ctx.stroke(); ctx.shadowBlur = 0;
    // hood void
    ctx.fillStyle = '#020203';
    ctx.beginPath(); ctx.ellipse(0, -250, 95, 120, 0, 0, 7); ctx.fill();
    // eyes
    const eye = 0.6 + 0.4 * Math.sin(T0 * 4);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (const ex of [-34, 34]) {
      const eg = ctx.createRadialGradient(ex, -255, 0, ex, -255, 26);
      eg.addColorStop(0, `rgba(255,220,150,${0.9 * eye})`); eg.addColorStop(1, 'rgba(255,220,150,0)');
      ctx.fillStyle = eg; ctx.fillRect(ex - 26, -281, 52, 52);
    }
    ctx.restore();
    ctx.restore();
    // chains: snap tight on frame 0 (they whip in from slack)
    const tight = ease.outBack(clamp(t / 0.25));
    const jit = Math.exp(-t * 10) * 8;
    ctx.strokeStyle = GOLD; ctx.lineWidth = 7; ctx.shadowColor = 'rgba(255,200,100,0.8)'; ctx.shadowBlur = 16;
    chainLine(ctx, -60, DY - 330 + jit, W + 60, DY + 120, tight, t);
    chainLine(ctx, W + 60, DY - 330 - jit, -60, DY + 120, tight, t);
    chainLine(ctx, -60, DY + 260, W + 60, DY + 260 + jit, tight, t);
    ctx.shadowBlur = 0;
    ctx.restore();
  }
  // frozen hourglass (act 1b) – sand stops
  function hourglass(ctx, t) {
    const a = sm(ev.frozen - 0.05, ev.frozen + 0.25, t) * (1 - sm(ev.escape - 0.2, ev.escape + 0.2, t));
    if (a <= 0.01) return;
    const x = W * 0.83, y = H * 0.70, w = 70, h = 120;
    ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = GOLD; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(x - w, y - h); ctx.lineTo(x + w, y - h); ctx.lineTo(x + 8, y); ctx.lineTo(x + w, y + h); ctx.lineTo(x - w, y + h); ctx.lineTo(x - 8, y); ctx.closePath(); ctx.stroke();
    ctx.fillStyle = 'rgba(227,176,75,0.55)';
    ctx.beginPath(); ctx.moveTo(x - 40, y - 50); ctx.lineTo(x + 40, y - 50); ctx.lineTo(x + 6, y - 6); ctx.lineTo(x - 6, y - 6); ctx.fill();
    // a single grain hanging in the air
    ctx.fillStyle = GOLD_HI; ctx.beginPath(); ctx.arc(x, y + 30, 4, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.moveTo(x - 50, y + h - 4); ctx.lineTo(x + 50, y + h - 4); ctx.lineTo(x + 14, y + 70); ctx.lineTo(x - 14, y + 70); ctx.fill();
    ctx.restore();
  }
  // escape: a door of light tears open behind death
  function door(ctx, t) {
    const o = sm(ev.escape, ev.punish - 0.2, t);
    if (o <= 0.01 || t >= ev.punish) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const w = 20 + 360 * o;
    const g = ctx.createLinearGradient(DX - w, 0, DX + w, 0);
    g.addColorStop(0, 'rgba(255,214,140,0)'); g.addColorStop(0.5, `rgba(255,236,190,${0.7 * o})`); g.addColorStop(1, 'rgba(255,214,140,0)');
    ctx.fillStyle = g; ctx.fillRect(DX - w, H * 0.18, w * 2, H * 0.65);
    ctx.restore();
    // a small figure walking into the light
    const fx = DX - 260 + 260 * o, fy = H * 0.78;
    ctx.save(); ctx.globalAlpha = 1 - sm(ev.punish - 0.5, ev.punish - 0.1, t);
    figure(ctx, fx, fy, -Math.PI / 2, 0.7, Math.sin(t * 9) , 0);
    ctx.restore();
  }

  // ---------- ACT 2: the mountain ----------
  const A = [60, H * 0.75], B = [W * 0.80, H * 0.47];
  const L = Math.hypot(B[0] - A[0], B[1] - A[1]);
  const D = [(B[0] - A[0]) / L, (B[1] - A[1]) / L];
  const N = [D[1], -D[0]]; // up-left normal
  const P = (s) => [A[0] + D[0] * L * s, A[1] + D[1] * L * s];
  const R = 112;
  function mountain(ctx, t, rim) {
    ctx.save();
    const mg = ctx.createLinearGradient(0, H * 0.4, 0, H);
    mg.addColorStop(0, '#121017'); mg.addColorStop(1, '#060508');
    ctx.fillStyle = mg;
    ctx.beginPath();
    ctx.moveTo(-50, H); ctx.lineTo(-50, A[1] + 30); ctx.lineTo(A[0], A[1]);
    const rr = U.mulberry32(17);
    for (let s = 0.05; s <= 1.0001; s += 0.05) { const p = P(s); ctx.lineTo(p[0], p[1] + (rr() - 0.5) * 6); }
    ctx.lineTo(B[0] + 70, B[1] - 6); ctx.lineTo(W + 50, H * 0.60); ctx.lineTo(W + 50, H);
    ctx.closePath(); ctx.fill();
    // rim light along the slope
    ctx.strokeStyle = `rgba(227,176,75,${0.5 + 0.4 * rim})`; ctx.lineWidth = 3; ctx.shadowColor = 'rgba(227,176,75,0.8)'; ctx.shadowBlur = 14;
    ctx.beginPath(); ctx.moveTo(A[0], A[1]); ctx.lineTo(B[0], B[1]); ctx.lineTo(B[0] + 70, B[1] - 6); ctx.stroke();
    ctx.shadowBlur = 0;
    // worn path marks: grooves where the stone always rolled
    ctx.strokeStyle = 'rgba(227,176,75,0.12)'; ctx.lineWidth = 2;
    for (let k = 1; k <= 3; k++) { ctx.beginPath(); ctx.moveTo(A[0] + N[0] * -12 * k, A[1] + N[1] * -12 * k); ctx.lineTo(B[0] + N[0] * -12 * k, B[1] + N[1] * -12 * k); ctx.stroke(); }
    ctx.restore();
  }

  // low-poly boulder
  const NR = 11, OUT = [], INN = [];
  (function build() {
    const r = U.mulberry32(42);
    for (let i = 0; i < NR; i++) {
      const a = (i / NR) * Math.PI * 2;
      OUT.push([Math.cos(a) * R * (0.92 + 0.12 * r()), Math.sin(a) * R * (0.92 + 0.12 * r())]);
      INN.push([Math.cos(a + 0.3) * R * (0.5 + 0.1 * r()), Math.sin(a + 0.3) * R * (0.5 + 0.1 * r())]);
    }
  })();
  const FACES = [];
  for (let i = 0; i < NR; i++) { const j = (i + 1) % NR; FACES.push([OUT[i], OUT[j], INN[i]], [OUT[j], INN[j], INN[i]], [INN[i], INN[j], [0, 0]]); }
  const shadeCol = (k) => `rgb(${Math.round(lerp(14, 98, k))},${Math.round(lerp(13, 90, k))},${Math.round(lerp(18, 96, k))})`;
  function boulder(ctx, s, rot, glow) {
    const p = P(s), cx = p[0] + N[0] * R, cy = p[1] + N[1] * R;
    ctx.save(); ctx.translate(cx, cy);
    ctx.save(); ctx.rotate(rot);
    for (const f of FACES) {
      const mx = (f[0][0] + f[1][0] + f[2][0]) / 3, my = (f[0][1] + f[1][1] + f[2][1]) / 3;
      // light from the upper right (fixed in world space)
      const wa = Math.atan2(my, mx) + rot, l = Math.hypot(mx, my) / R;
      const k = clamp(0.45 + 0.38 * l * (Math.cos(wa) * 0.6 - Math.sin(wa) * 0.8) + 0.1 * (U.hash(Math.round(mx), Math.round(my)) - 0.5));
      ctx.fillStyle = shadeCol(k);
      ctx.beginPath(); ctx.moveTo(f[0][0], f[0][1]); ctx.lineTo(f[1][0], f[1][1]); ctx.lineTo(f[2][0], f[2][1]); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = 'rgba(227,176,75,0.08)'; ctx.lineWidth = 1.5; ctx.stroke();
    }
    ctx.restore();
    ctx.beginPath(); OUT.forEach((q, i) => { const a = Math.atan2(q[1], q[0]) + rot, d = Math.hypot(q[0], q[1]); const x = Math.cos(a) * d, y = Math.sin(a) * d; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }); ctx.closePath();
    ctx.shadowColor = 'rgba(227,176,75,0.8)'; ctx.shadowBlur = 16 + 24 * glow;
    ctx.strokeStyle = `rgba(227,176,75,${0.65 + 0.3 * glow})`; ctx.lineWidth = 3.5; ctx.stroke();
    ctx.restore();
    return [cx, cy];
  }

  // silhouette man. (x,y)=feet, dir = body angle, k = lean 0..1, ph = stride phase, push = arms forward 0..1
  function figure(ctx, x, y, dir, scale, ph, push, armTo) {
    const bx = Math.cos(dir), by = Math.sin(dir);
    const sc = scale || 1;
    const hip = [x + bx * 100 * sc, y + by * 100 * sc];
    const sh = [hip[0] + bx * 92 * sc, hip[1] + by * 92 * sc];
    const hd = [sh[0] + bx * 40 * sc, sh[1] + by * 40 * sc];
    const st = 28 * sc * (ph || 0);
    ctx.save();
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    const body = (w, col) => {
      ctx.strokeStyle = col; ctx.lineWidth = w * sc;
      // legs
      for (const sg of [1, -1]) {
        const foot = [x + D[0] * st * sg - 0, y + D[1] * st * sg];
        const knee = [(hip[0] + foot[0]) / 2 - by * 14 * sc, (hip[1] + foot[1]) / 2 + bx * 14 * sc];
        ctx.beginPath(); ctx.moveTo(hip[0], hip[1]); ctx.lineTo(knee[0], knee[1]); ctx.lineTo(foot[0], foot[1]); ctx.stroke();
      }
      ctx.lineWidth = (w + 12) * sc;
      ctx.beginPath(); ctx.moveTo(hip[0], hip[1]); ctx.lineTo(sh[0], sh[1]); ctx.stroke();
      ctx.lineWidth = w * 0.85 * sc;
      const tgt = armTo || [sh[0] - bx * 125 * sc + 14 * sc, sh[1] - by * 125 * sc];
      const elb = [(sh[0] + tgt[0]) / 2 + bx * 18 * sc, (sh[1] + tgt[1]) / 2 + by * 18 * sc];
      for (const o of [0, 10]) { ctx.beginPath(); ctx.moveTo(sh[0], sh[1]); ctx.lineTo(elb[0] + o, elb[1] + o * 0.3); ctx.lineTo(tgt[0] + o * 0.5, tgt[1] + o); ctx.stroke(); }
    };
    ctx.shadowColor = 'rgba(227,176,75,0.9)'; ctx.shadowBlur = 10;
    body(26, 'rgba(227,176,75,0.85)');
    ctx.shadowBlur = 0;
    body(20, '#0a090d');
    ctx.fillStyle = '#0a090d'; ctx.strokeStyle = 'rgba(227,176,75,0.85)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(hd[0], hd[1], 30 * sc, 0, 7); ctx.fill(); ctx.stroke();
    ctx.restore();
  }

  // state of the mountain at time t
  const S0 = 0.36, SMAX = 0.88;
  function climb(t) {
    // returns {s, man: {s, vis, push, upright}, rot}
    let s = S0, man = { s: S0, vis: 1, push: 1, upright: 0, walk: 0 }, glow = 0;
    if (t < ev.punish) return { s, man, glow };
    const cyc = S.cycles.find((c) => t >= c.t0 && t < c.t1);
    if (cyc) {
      if (t < cyc.tp) {
        const u = (t - cyc.t0) / (cyc.tp - cyc.t0);
        s = lerp(S0, SMAX, ease.inOutQuad(u));
        man = { s, vis: 1, push: 1, upright: 0, walk: (t - cyc.t0) * 4 };
      } else {
        const u = (t - cyc.tp) / (cyc.t1 - cyc.tp);
        s = lerp(SMAX, S0, ease.inQuad(u));
        man = { s: SMAX, vis: 1 - clamp(u * 1.6), push: 0, upright: 0.5, walk: 0 };
      }
    } else if (t < ev.drop) {
      // after the last cycle: he starts again, slowly
      const u = clamp((t - ev.last) / (ev.drop - ev.last));
      s = lerp(S0, 0.55, ease.outQuad(u));
      man = { s, vis: 1, push: 1, upright: 0, walk: (t - ev.last) * 2.5 };
    } else {
      // drop: the stone at the brink, it rolls down once more; he stands and looks into the light
      const u = clamp((t - ev.drop - 0.35) / 2.2);
      s = lerp(SMAX, -0.2, ease.inQuad(u));
      man = { s: SMAX, vis: 1, push: 0, upright: 1, walk: 0 };
      glow = 1;
    }
    return { s, man, glow };
  }
  function scene2(ctx, t) {
    if (t < ev.punish - 0.01) return;
    const st = climb(t);
    const warm = t >= ev.drop ? 0.4 + 0.6 * sm(ev.drop, ev.drop + 0.6, t) : 0.12;
    sky(ctx, t, warm);
    mountain(ctx, t, t >= ev.drop ? 1 : 0);
    // man first (he is downhill, behind the stone)
    const m = st.man;
    if (m.vis > 0.01) {
      const fs = m.upright >= 1 ? 0.985 : m.s - 380 / L;
      const f = P(fs);
      const lean = Math.atan2(-0.82, 0.57);
      const up = Math.atan2(N[1], N[0]) * 0 + -Math.PI / 2;
      const dir = lerp(lean, up, m.upright);
      const ph = m.push ? Math.sin(m.walk * Math.PI) : 0;
      const p = P(m.s), cx = p[0] + N[0] * R, cy = p[1] + N[1] * R;
      const arm = m.push ? [cx - D[0] * R * 0.92 + N[0] * 10, cy - D[1] * R * 0.92 + N[1] * 10] : null;
      ctx.save(); ctx.globalAlpha = m.vis;
      figure(ctx, f[0], f[1], dir, m.upright >= 1 ? 0.9 : 1.12, ph, m.push, arm);
      ctx.restore();
    }
    const rot = (st.s * L) / R;
    boulder(ctx, st.s, rot, st.glow);
    // dust where the stone slips back
    const lr = lastRoll(t);
    if (lr && t - lr.t < 0.6 && t < ev.drop) dust(ctx, t, lr.t, P(SMAX));
  }
  function dust(ctx, t, t0, at) {
    const u = t - t0, r = U.mulberry32(Math.round(t0 * 100));
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 20; i++) {
      const a = -Math.PI * (0.2 + 0.7 * r()), sp = 120 + 260 * r();
      const x = at[0] + Math.cos(a) * sp * u, y = at[1] + Math.sin(a) * sp * u + 200 * u * u;
      ctx.fillStyle = `rgba(255,200,120,${0.5 * (1 - u / 0.6)})`; ctx.beginPath(); ctx.arc(x, y, 3 + 3 * r(), 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  function lastRoll(t) { let l = null; for (const r of S.rolls) if (t >= r.t) l = r; return l; }

  // ---------- text ----------
  function seriesTag(ctx, t) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('MYTHEN IN 30 SEKUNDEN · #1', W / 2, S.SAFE.y + 34);
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
    if (c.by) {
      const a = sm(c.t + 0.6, c.t + 1.0, t) * fadeOut;
      ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = GOLD;
      ctx.fillText(c.by, W / 2, y0 + c.lines.length * lh + 10);
    }
    ctx.restore();
  }
  function counter(ctx, t) {
    if (t < ev.punish || t >= ev.end) return;
    const lr = lastRoll(t);
    const inf = t >= ev.drop;
    const n = inf ? '∞' : lr ? fmt(lr.n) : '0';
    const pop = inf ? Math.exp(-(t - ev.drop) * 6) : lr ? Math.exp(-(t - lr.t) * 8) : 0;
    ctx.save(); ctx.globalAlpha = sm(ev.punish, ev.punish + 0.3, t);
    const y = H * 0.765;
    const sz = (inf ? 110 : 72) * (1 + 0.15 * pop);
    ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
    const label = 'VERSUCH ';
    ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(n).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left';
    ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = 'rgba(242,235,221,0.8)'; ctx.fillText(label, x0, y);
    ctx.font = `700 ${sz}px "Cinzel"`;
    ctx.shadowColor = `rgba(255,200,100,${0.5 + 0.5 * pop})`; ctx.shadowBlur = 20 + 30 * pop;
    ctx.fillStyle = pop > 0.4 || inf ? GOLD_HI : GOLD;
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
      for (const [h, amp] of [[ev.hook, 16], [ev.punish, 14], [ev.drop, 30]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      const lr = lastRoll(t);
      if (lr && t < ev.drop) shake += 6 * Math.exp(-(t - lr.t) * 10);
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      if (t < ev.punish) {
        const zoom = 1 + 0.05 * sm(0, ev.punish, t);
        ctx.translate(DX, DY); ctx.scale(zoom, zoom); ctx.translate(-DX, -DY);
        sky(ctx, tf(t), 0);
        door(ctx, t);
        death(ctx, t);
        hourglass(ctx, t);
        embers(ctx, tf(t));
      } else {
        scene2(ctx, t);
        embers(ctx, t, t >= ev.drop ? 1.5 * Math.exp(-(t - ev.drop)) : 0);
      }
      ctx.restore();
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.fillRect(0, 0, W, H); }
      let f = 0;
      if (t >= ev.drop) f = 0.9 * Math.exp(-(t - ev.drop) * 9);
      else if (t >= ev.punish && t < ev.punish + 0.4) f = 0.7 * Math.exp(-(t - ev.punish) * 12);
      else if (t < 0.25) f = 0.35 * Math.exp(-t * 14);
      if (f > 0.01) { ctx.fillStyle = `rgba(255,236,200,${f})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx, t);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
