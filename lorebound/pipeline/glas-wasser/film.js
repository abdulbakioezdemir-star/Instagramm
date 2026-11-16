// LOREBOUND – „Das Glas Wasser“ (Gleichnis #4). Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const TABLE = H * 0.70;
  const GX = W * 0.46, GH = 390, GTW = 270, GBW = 205; // glass centre x, height, top/bottom width
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const lastOf = (list, t) => { let l = null; for (const s of list) if (t >= s.t) l = s; return l; };

  // ---------- strain over time ----------
  function strain(t) { // 0 calm .. 1 exhausted
    if (t >= ev.drop) return 0;
    if (t < ev.hour) return 0.04;
    if (t < ev.day) return lerp(0.12, 0.5, (t - ev.hour) / (ev.day - ev.hour));
    return lerp(0.5, 1.0, clamp((t - ev.day) / (ev.dry - ev.day)));
  }
  function tickPulse(t) { // flash on each hour
    let v = 0;
    for (const g of S.hours) { const u = t - g.t; if (u >= 0 && u < 0.5) v = Math.max(v, Math.exp(-u * 7)); }
    return v;
  }
  function tremor(t) {
    let a = strain(t);
    if (t < ev.ask) a += 0.5 * Math.exp(-t * 2.2); // hook slosh
    return a;
  }
  // bottom of the glass (y) over time
  function glassBottom(t) {
    const held = H * 0.615 + 85 * Math.pow(strain(t), 1.4);
    if (t < ev.breath) return held;
    if (t < ev.drop) { const x = (t - ev.breath) / (ev.drop - ev.breath); return lerp(held, TABLE, x * x); }
    return TABLE;
  }
  function glassPose(t) {
    const a = tremor(t);
    const jx = U.noise1(t * 9, 3) * 9 * a + U.noise1(t * 23, 4) * 4 * a;
    const jy = U.noise1(t * 11, 5) * 5 * a;
    const rot = U.noise1(t * 7, 6) * 0.05 * a + (t < ev.ask ? 0.06 * Math.sin(t * 9) * Math.exp(-t * 2) : 0);
    return { x: GX + (t < ev.drop ? jx : 0), y: glassBottom(t) + (t < ev.drop ? jy : 0), rot: t < ev.drop ? rot : 0, a };
  }

  // ---------- room ----------
  function room(ctx, t) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#050509'); g.addColorStop(0.6, '#0b0b11'); g.addColorStop(1, '#120d09');
    ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    // spotlight cone from above onto the glass
    const after = sm(ev.drop, ev.drop + 1.2, t);
    const cone = ctx.createRadialGradient(GX, TABLE - 160, 20, GX, TABLE - 160, 760);
    cone.addColorStop(0, `rgba(255,214,150,${0.16 + 0.14 * after})`); cone.addColorStop(1, 'rgba(255,214,150,0)');
    ctx.fillStyle = cone; ctx.fillRect(-200, 0, W + 400, H);
    // dust in the light
    const r = U.mulberry32(5);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 70; i++) {
      const x = GX - 380 + r() * 760, y0 = r() * TABLE, sp = 8 + r() * 14;
      const y = (y0 + t * sp) % TABLE;
      const d = Math.hypot(x - GX, y - (TABLE - 300)) / 600;
      ctx.fillStyle = `rgba(255,225,170,${Math.max(0, 0.22 * (1 - d))})`; ctx.fillRect(x, y, 2.4, 2.4);
    }
    ctx.restore();
    // candle on the left of the table
    const cx = W * 0.14, cy = TABLE;
    const fl = 1 + 0.08 * U.noise1(t * 6, 9);
    const halo = ctx.createRadialGradient(cx, cy - 150, 0, cx, cy - 150, 300 * fl);
    halo.addColorStop(0, 'rgba(255,190,110,0.28)'); halo.addColorStop(1, 'rgba(255,190,110,0)');
    ctx.fillStyle = halo; ctx.fillRect(cx - 320, cy - 470, 640, 640);
    ctx.fillStyle = '#d8ccb4'; ctx.fillRect(cx - 22, cy - 120, 44, 120);
    ctx.fillStyle = '#efe5d0'; ctx.beginPath(); ctx.ellipse(cx, cy - 120, 22, 6, 0, 0, 7); ctx.fill();
    ctx.save(); ctx.translate(cx + U.noise1(t * 5, 8) * 2, cy - 128); ctx.scale(1, fl);
    const fg = ctx.createRadialGradient(0, -18, 0, 0, -18, 26);
    fg.addColorStop(0, '#fff6d8'); fg.addColorStop(0.5, '#ffc760'); fg.addColorStop(1, 'rgba(255,140,40,0)');
    ctx.fillStyle = fg; ctx.beginPath(); ctx.ellipse(0, -18, 12, 28, 0, 0, 7); ctx.fill();
    ctx.restore();
  }
  function table(ctx) {
    const g = ctx.createLinearGradient(0, TABLE, 0, H);
    g.addColorStop(0, '#2a1c11'); g.addColorStop(0.06, '#1a120b'); g.addColorStop(1, '#070505');
    ctx.fillStyle = g; ctx.fillRect(-200, TABLE, W + 400, H - TABLE + 200);
    ctx.strokeStyle = 'rgba(227,176,75,0.5)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(-50, TABLE); ctx.lineTo(W + 50, TABLE); ctx.stroke();
    const r = U.mulberry32(31);
    ctx.strokeStyle = 'rgba(90,64,40,0.35)'; ctx.lineWidth = 2;
    for (let i = 0; i < 9; i++) { const y = TABLE + 30 + i * 22 + r() * 10; ctx.beginPath(); ctx.moveTo(-20, y); ctx.bezierCurveTo(W * 0.3, y + r() * 12 - 6, W * 0.7, y + r() * 12 - 6, W + 20, y); ctx.stroke(); }
  }
  function shadow(ctx, t) {
    const p = glassPose(t);
    const lift = (TABLE - p.y) / 300; // 0 when on the table
    ctx.save();
    ctx.fillStyle = `rgba(0,0,0,${0.55 - 0.3 * clamp(lift)})`;
    ctx.beginPath(); ctx.ellipse(p.x + 20, TABLE + 6, GBW * 0.6 * (1 + 0.6 * lift), 14 * (1 + lift), 0, 0, 7); ctx.fill();
    ctx.restore();
  }

  // ---------- glass ----------
  function glassPath(ctx) {
    ctx.beginPath();
    ctx.moveTo(-GBW / 2, 0); ctx.lineTo(-GTW / 2, -GH); ctx.lineTo(GTW / 2, -GH); ctx.lineTo(GBW / 2, 0); ctx.closePath();
  }
  function water(ctx, t, p) {
    const level = -GH * 0.74;
    const amp = t >= ev.drop ? 1.2 * Math.exp(-(t - ev.drop) * 3) : 3 + p.a * 18;
    const sp = 6 + 10 * p.a;
    ctx.save(); glassPath(ctx); ctx.clip();
    const wg = ctx.createLinearGradient(0, level, 0, 0);
    const warm = sm(ev.drop, ev.drop + 1.0, t);
    wg.addColorStop(0, `rgba(${lerp(90, 200, warm)},${lerp(120, 160, warm)},${lerp(150, 90, warm)},0.55)`);
    wg.addColorStop(1, 'rgba(20,30,45,0.75)');
    ctx.fillStyle = wg;
    ctx.beginPath(); ctx.moveTo(-GTW, 10);
    for (let x = -GTW; x <= GTW; x += 6) ctx.lineTo(x, level + Math.sin(x * 0.045 + t * sp) * amp + Math.sin(x * 0.09 - t * sp * 1.3) * amp * 0.4);
    ctx.lineTo(GTW, 10); ctx.closePath(); ctx.fill();
    // surface highlight
    ctx.strokeStyle = `rgba(255,220,150,${0.55 + 0.4 * warm})`; ctx.lineWidth = 3;
    ctx.beginPath();
    for (let x = -GTW; x <= GTW; x += 6) { const y = level + Math.sin(x * 0.045 + t * sp) * amp + Math.sin(x * 0.09 - t * sp * 1.3) * amp * 0.4; x === -GTW ? ctx.moveTo(x, y) : ctx.lineTo(x, y); }
    ctx.stroke();
    ctx.restore();
    // calm gold rings after the drop
    if (t >= ev.drop) {
      for (let k = 0; k < 3; k++) {
        const u = t - ev.drop - k * 0.45; if (u < 0 || u > 2.2) continue;
        const rr = 10 + u * 60, a = Math.max(0, 0.8 * (1 - u / 2.2));
        ctx.strokeStyle = `rgba(255,217,138,${a})`; ctx.lineWidth = 2.5;
        ctx.beginPath(); ctx.ellipse(0, level, Math.min(rr, GTW * 0.42), Math.min(rr, GTW * 0.42) * 0.18, 0, 0, 7); ctx.stroke();
      }
    }
  }
  function glass(ctx, t, p) {
    ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot);
    // body tint
    ctx.fillStyle = 'rgba(200,215,230,0.06)'; glassPath(ctx); ctx.fill();
    water(ctx, t, p);
    // outline + gold rim
    ctx.strokeStyle = 'rgba(230,235,240,0.55)'; ctx.lineWidth = 4; glassPath(ctx); ctx.stroke();
    ctx.strokeStyle = GOLD; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.ellipse(0, -GH, GTW / 2, 12, 0, 0, 7); ctx.stroke();
    ctx.strokeStyle = 'rgba(227,176,75,0.6)'; ctx.beginPath(); ctx.ellipse(0, 0, GBW / 2, 9, 0, 0, Math.PI); ctx.stroke();
    // reflections
    ctx.strokeStyle = 'rgba(255,255,255,0.28)'; ctx.lineWidth = 8; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-GTW / 2 + 26, -GH + 30); ctx.lineTo(-GBW / 2 + 22, -24); ctx.stroke();
    ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(-GTW / 2 + 48, -GH + 40); ctx.lineTo(-GBW / 2 + 40, -60); ctx.stroke();
    ctx.restore();
  }
  // drops that spill when the arm shakes
  function spill(ctx, t) {
    if (t < ev.day || t >= ev.drop + 0.6) return;
    ctx.save();
    for (let k = 0; k < 18; k++) {
      const t0 = ev.day + 0.6 + k * 0.32; const u = t - t0; if (u < 0 || u > 0.7) continue;
      const p = glassPose(t0), side = k % 2 ? 1 : -1;
      const x = p.x + side * (GTW / 2 - 6) + side * u * 40, y = p.y - GH + 10 + 900 * u * u;
      if (y > TABLE) continue;
      ctx.fillStyle = `rgba(200,225,255,${0.8 * (1 - u / 0.7)})`;
      ctx.beginPath(); ctx.ellipse(x, y, 4, 7, 0, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- arm + hand (from bottom right) ----------
  function release(t) { return sm(ev.drop + 0.35, ev.drop + 0.8, t); }
  function retreat(t) { return sm(ev.drop + 0.7, ev.drop + 1.8, t); }
  function armGeom(t, p) {
    const wx = p.x + GTW / 2 - 4 + 80 * release(t), wy = p.y - GH * 0.45;
    const rt = retreat(t);
    return { wx: wx + rt * 700, wy: wy + rt * 500, ex: W + 160 + rt * 400, ey: p.y + 360 + rt * 300 };
  }
  function arm(ctx, t, p, front) {
    const g = armGeom(t, p);
    const burn = clamp(strain(t) * 1.25 - 0.1) * (0.75 + 0.25 * tickPulse(t));
    if (!front) {
      // forearm: tapered quad wrist -> elbow, gold rim
      const dx = g.ex - g.wx, dy = g.ey - g.wy, L = Math.hypot(dx, dy), nx = -dy / L, ny = dx / L;
      const w0 = 62, w1 = 110;
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(g.wx + nx * w0, g.wy + ny * w0); ctx.lineTo(g.ex + nx * w1, g.ey + ny * w1);
      ctx.lineTo(g.ex - nx * w1, g.ey - ny * w1); ctx.lineTo(g.wx - nx * w0, g.wy - ny * w0); ctx.closePath();
      const ag = ctx.createLinearGradient(g.wx, g.wy, g.ex, g.ey);
      ag.addColorStop(0, '#2c241d'); ag.addColorStop(1, '#100c09');
      ctx.fillStyle = ag; ctx.fill();
      ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 4; ctx.stroke();
      if (burn > 0.01) { // the arm burns: red heat inside the silhouette
        ctx.clip();
        const mx = lerp(g.wx, g.ex, 0.55), my = lerp(g.wy, g.ey, 0.55);
        const rg = ctx.createRadialGradient(mx, my, 0, mx, my, 360);
        rg.addColorStop(0, `rgba(255,70,30,${0.75 * burn})`); rg.addColorStop(1, 'rgba(255,70,30,0)');
        ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = rg; ctx.fillRect(mx - 400, my - 400, 800, 800);
      }
      ctx.restore();
      // palm behind the glass' right edge
      ctx.save(); ctx.translate(g.wx, g.wy); ctx.scale(1.3, 1.3);
      ctx.fillStyle = '#2a221b'; ctx.strokeStyle = 'rgba(227,176,75,0.7)'; ctx.lineWidth = 4;
      ctx.beginPath(); ctx.ellipse(10, 0, 62, 92, -0.15, 0, 7); ctx.fill(); ctx.stroke();
      ctx.restore();
      return;
    }
    // fingers wrapping the front of the glass + thumb
    const open = release(t), rt = retreat(t);
    if (rt >= 1) return;
    ctx.save(); ctx.translate(g.wx, g.wy); ctx.scale(1.3, 1.3);
    const len = lerp(GTW * 0.62 / 1.3, 26, open);
    for (let k = 0; k < 4; k++) {
      const fy = -54 + k * 36, fl = len * (k === 3 ? 0.8 : 1) - k * 4;
      ctx.beginPath();
      const x0 = -fl, y0 = fy - 16;
      ctx.moveTo(10, y0); ctx.lineTo(x0 + 16, y0); ctx.arc(x0 + 16, fy, 16, -Math.PI / 2, Math.PI / 2, true); ctx.lineTo(10, fy + 16); ctx.closePath();
      const fg = ctx.createLinearGradient(x0, 0, 10, 0);
      fg.addColorStop(0, '#3a3027'); fg.addColorStop(1, '#241d17');
      ctx.fillStyle = fg; ctx.fill();
      ctx.strokeStyle = 'rgba(227,176,75,0.75)'; ctx.lineWidth = 3; ctx.stroke();
    }
    // thumb over the top
    ctx.fillStyle = '#30281f'; ctx.strokeStyle = 'rgba(227,176,75,0.75)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.ellipse(-20 + 30 * open, -96, 44, 18, -0.35, 0, 7); ctx.fill(); ctx.stroke();
    ctx.restore();
  }

  function embers(ctx, t, boost = 0) {
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 30; i++) {
      const sp = 40 + r() * 70, x0 = r() * W, ph = r() * 40, sz = 1.5 + r() * 3, ra = r();
      const y = H - ((t * sp + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.8 + i) * 30;
      ctx.fillStyle = `rgba(255,200,110,${Math.min(1, (0.14 + 0.25 * ra) * (1 + boost))})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- text ----------
  function seriesTag(ctx) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('GLEICHNISSE IN 30 SEKUNDEN · #4', W / 2, S.SAFE.y + 34);
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
    if (t < ev.minute || t >= ev.breath) return;
    let label, l;
    if (t < ev.hour) { l = lastOf(S.minutes, t); label = 'MINUTE '; }
    else { l = lastOf(S.hours, t); label = 'STUNDE '; }
    const n = l ? String(l.n) : '0';
    const pop = l ? Math.exp(-(t - l.t) * 8) : 0;
    const hot = t >= ev.hour ? strain(t) : 0;
    const a = sm(ev.minute, ev.minute + 0.3, t) * (1 - sm(ev.breath - 0.3, ev.breath, t));
    ctx.save(); ctx.globalAlpha = clamp(a);
    const y = H * 0.775;
    const sz = 84 * (1 + 0.15 * pop);
    ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(n).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left';
    ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
    ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = 'rgba(242,235,221,0.8)'; ctx.fillText(label, x0, y);
    ctx.font = `700 ${sz}px "Cinzel"`;
    ctx.shadowColor = hot > 0.4 ? `rgba(255,80,40,${0.5 + 0.5 * pop})` : `rgba(255,200,100,${0.5 + 0.5 * pop})`; ctx.shadowBlur = 20 + 30 * pop;
    ctx.fillStyle = hot > 0.55 ? '#FF8A5C' : pop > 0.4 ? GOLD_HI : GOLD;
    ctx.fillText(n, x0 + lw, y);
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
    ctx.fillText('FOLGE FÜR TEIL #5', W / 2, y);
    ctx.font = '500 30px "Oswald"'; ctx.fillStyle = 'rgba(242,235,221,0.85)';
    ctx.fillText('SCHREIB »ABGESTELLT«, WENN DU ES TUST', W / 2, y + 48);
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
      for (const [h, amp] of [[ev.hook, 14], [ev.drop, 30]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      shake += 5 * tickPulse(t) * strain(t);
      // camera: slow push-in as the strain grows, settles after the drop
      const zoom = 1.04 + 0.12 * strain(t) + 0.05 * sm(ev.drop, ev.follow, t) - 0.04 * sm(0, ev.ask, t);
      const fx = GX, fy = H * 0.52;
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      ctx.translate(fx, fy); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy);
      room(ctx, t);
      table(ctx);
      shadow(ctx, t);
      const p = glassPose(t);
      arm(ctx, t, p, false);
      glass(ctx, t, p);
      arm(ctx, t, p, true);
      spill(ctx, t);
      embers(ctx, t, t >= ev.drop ? 1.5 * Math.exp(-(t - ev.drop)) : 0);
      ctx.restore();
      // red strain vignette pulsing on the hours
      const st = strain(t);
      if (st > 0.15 && t < ev.drop) {
        const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.75);
        v.addColorStop(0, 'rgba(120,10,0,0)'); v.addColorStop(1, `rgba(140,15,5,${0.45 * st * (0.6 + 0.4 * tickPulse(t))})`);
        ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
      }
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(0, 0, W, H); }
      const f = t >= ev.drop ? 0.85 * Math.exp(-(t - ev.drop) * 9) : (t < 0.2 ? 0.25 * Math.exp(-t * 14) : 0);
      if (f > 0.01) { ctx.fillStyle = `rgba(255,236,200,${f})`; ctx.fillRect(0, 0, W, H); }
      if (t >= ev.end - 0.5) { ctx.fillStyle = `rgba(4,4,8,${0.45 * sm(ev.end - 0.5, ev.end + 0.5, t)})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
