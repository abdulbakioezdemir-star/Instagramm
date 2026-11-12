// LOREBOUND – „Die leere Truhe“ (Fantasy #1). Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const GROUND = H * 0.70;
  const CX = W * 0.5;                       // chest centre
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const lastOf = (list, t) => { let l = null; for (const s of list) if (t >= s.t) l = s; return l; };
  const DRAGON = '#0b0d14', SCALE = '#161a26';

  // ---------- sky + mountains + village ----------
  function sky(ctx, t) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#04050a'); g.addColorStop(0.55, '#0a0c15'); g.addColorStop(1, '#120d09');
    ctx.fillStyle = g; ctx.fillRect(-300, -300, W + 600, H + 600);
    const r = U.mulberry32(5);
    for (let i = 0; i < 120; i++) {
      const x = r() * W, y = r() * H * 0.62;
      const a = 0.1 + 0.3 * r() * (0.6 + 0.4 * Math.sin(t * 1.3 + i));
      ctx.fillStyle = `rgba(230,220,200,${a})`; ctx.fillRect(x, y, 2.2, 2.2);
    }
    const mx = W * 0.82, my = H * 0.40;
    const mg = ctx.createRadialGradient(mx, my, 0, mx, my, 320);
    mg.addColorStop(0, 'rgba(255,226,170,0.18)'); mg.addColorStop(1, 'rgba(255,226,170,0)');
    ctx.fillStyle = mg; ctx.fillRect(mx - 340, my - 340, 680, 680);
    ctx.fillStyle = 'rgba(255,232,190,0.85)'; ctx.beginPath(); ctx.arc(mx, my, 36, 0, 7); ctx.fill();
  }
  function mountains(ctx) {
    const layers = [[H * 0.585, '#0d1019', 7, 120], [H * 0.63, '#0a0c13', 11, 80]];
    for (const [base, col, seed, amp] of layers) {
      const r = U.mulberry32(seed);
      ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(-300, H + 300); ctx.lineTo(-300, base);
      for (let x = -300; x <= W + 300; x += 90) ctx.lineTo(x, base - amp * (0.3 + r()) );
      ctx.lineTo(W + 300, base); ctx.lineTo(W + 300, H + 300); ctx.fill();
    }
  }
  const HOUSES = (() => { const r = U.mulberry32(41), a = []; for (let i = 0; i < 11; i++) a.push({ x: W * 0.56 + i * W * 0.037 + r() * 10, w: 26 + r() * 20, h: 24 + r() * 18, y: H * 0.535 - Math.sin(i / 10 * Math.PI) * 30 }); return a; })();
  function village(ctx, t) {
    const lit = sm(ev.village - 0.2, ev.village + 1.2, t);
    for (const [i, h] of HOUSES.entries()) {
      ctx.fillStyle = '#07080d';
      ctx.fillRect(h.x, h.y - h.h, h.w, h.h);
      ctx.beginPath(); ctx.moveTo(h.x - 4, h.y - h.h); ctx.lineTo(h.x + h.w / 2, h.y - h.h - 18); ctx.lineTo(h.x + h.w + 4, h.y - h.h); ctx.fill();
      const on = clamp(lit * 1.6 - i * 0.05);
      if (on > 0.01) {
        ctx.save(); ctx.globalCompositeOperation = 'lighter';
        const gx = h.x + h.w / 2, gy = h.y - h.h / 2;
        const gr = ctx.createRadialGradient(gx, gy, 0, gx, gy, 46);
        gr.addColorStop(0, `rgba(255,200,110,${0.45 * on})`); gr.addColorStop(1, 'rgba(255,200,110,0)');
        ctx.fillStyle = gr; ctx.fillRect(gx - 46, gy - 46, 92, 92);
        ctx.fillStyle = `rgba(255,214,140,${0.95 * on})`; ctx.fillRect(gx - 5, gy - 6, 10, 11);
        ctx.restore();
        // smoke
        if (i % 3 === 0) for (let k = 0; k < 6; k++) {
          const u = ((t * 0.5 + k / 6) % 1);
          ctx.fillStyle = `rgba(180,170,160,${0.12 * on * (1 - u)})`;
          ctx.beginPath(); ctx.arc(h.x + h.w * 0.7 + Math.sin(u * 5 + i) * 8, h.y - h.h - 20 - u * 90, 6 + u * 14, 0, 7); ctx.fill();
        }
      }
    }
  }
  function ground(ctx) {
    const g = ctx.createLinearGradient(0, GROUND - 20, 0, H);
    g.addColorStop(0, '#15100b'); g.addColorStop(1, '#060505');
    ctx.fillStyle = g; ctx.fillRect(-300, GROUND - 10, W + 600, H);
    ctx.strokeStyle = 'rgba(227,176,75,0.35)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(-300, GROUND - 10); ctx.lineTo(W + 300, GROUND - 10); ctx.stroke();
  }

  // ---------- the dragon ----------
  function headPose(t) {
    let rec = 0; // recoil when breathing fire
    for (const f of S.fires) { const u = t - f.t; if (u > -0.15 && u < 0.6) rec += u < 0 ? (u + 0.15) / 0.15 : Math.exp(-u * 5); }
    const nod = Math.sin(clamp((t - ev.last - 0.2) / 0.8) * Math.PI) * 60;
    const lowerToChild = 50 * sm(ev.child, ev.last, t);
    const breathe = Math.sin(t * 1.6) * 6;
    return { x: W * 0.60 + rec * 26, y: H * 0.47 + nod + lowerToChild + breathe - rec * 14, rot: -rec * 0.12 + nod * 0.003 };
  }
  function dragon(ctx, t) {
    const hp = headPose(t);
    // folded wing
    ctx.save();
    ctx.fillStyle = '#0e111b'; ctx.strokeStyle = 'rgba(227,176,75,0.35)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(W * 0.66, GROUND - 230); ctx.lineTo(W * 0.80, H * 0.50 + Math.sin(t * 1.6) * 4); ctx.lineTo(W * 0.98, GROUND - 260);
    ctx.quadraticCurveTo(W * 0.86, GROUND - 230, W * 0.80, GROUND - 200); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.restore();
    // body hump + tail curling round the chest front
    ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    const body = () => {
      ctx.beginPath();
      ctx.moveTo(W * 0.14, GROUND - 26);
      ctx.bezierCurveTo(W * 0.30, GROUND + 10, W * 0.62, GROUND + 20, W * 0.82, GROUND - 60);
      ctx.bezierCurveTo(W * 0.95, GROUND - 140, W * 0.92, GROUND - 270, W * 0.78, GROUND - 270);
      ctx.bezierCurveTo(W * 0.70, GROUND - 270, W * 0.70, GROUND - 330, hp.x + 40, hp.y + 60);
    };
    body(); ctx.strokeStyle = 'rgba(227,176,75,0.45)'; ctx.lineWidth = 92; ctx.stroke();
    body(); ctx.strokeStyle = DRAGON; ctx.lineWidth = 86; ctx.stroke();
    body(); ctx.strokeStyle = SCALE; ctx.lineWidth = 30; ctx.setLineDash([18, 26]); ctx.stroke(); ctx.setLineDash([]);
    // spikes along the hump
    const r = U.mulberry32(3);
    ctx.fillStyle = 'rgba(227,176,75,0.6)';
    for (let i = 0; i < 7; i++) {
      const x = W * (0.72 + i * 0.03), y = GROUND - 312 + Math.abs(i - 3) * 14;
      ctx.beginPath(); ctx.moveTo(x - 10, y + 6); ctx.lineTo(x, y - 22 - r() * 8); ctx.lineTo(x + 10, y + 6); ctx.fill();
    }
    ctx.restore();
    // head
    ctx.save(); ctx.translate(hp.x, hp.y); ctx.rotate(hp.rot);
    ctx.fillStyle = DRAGON; ctx.strokeStyle = 'rgba(227,176,75,0.5)'; ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(60, -40); ctx.quadraticCurveTo(10, -70, -60, -50); ctx.lineTo(-150, -22); ctx.quadraticCurveTo(-170, 0, -150, 14);
    ctx.lineTo(-60, 30); ctx.quadraticCurveTo(20, 50, 70, 40); ctx.quadraticCurveTo(100, 0, 60, -40); ctx.closePath(); ctx.fill(); ctx.stroke();
    // horns
    ctx.fillStyle = 'rgba(227,176,75,0.85)';
    for (const [hx, hy, len] of [[30, -50, 80], [55, -38, 60]]) { ctx.beginPath(); ctx.moveTo(hx - 10, hy); ctx.quadraticCurveTo(hx + 30, hy - len * 0.6, hx + 50, hy - len); ctx.quadraticCurveTo(hx + 18, hy - len * 0.4, hx + 10, hy); ctx.fill(); }
    // nostril glow (before fire)
    let fireNear = 0; for (const f of S.fires) fireNear = Math.max(fireNear, Math.exp(-Math.abs(t - f.t) * 6));
    ctx.fillStyle = `rgba(255,140,60,${0.25 + 0.7 * fireNear})`; ctx.beginPath(); ctx.arc(-146, -6, 6, 0, 7); ctx.fill();
    // eye
    eye(ctx, t, -40, -22);
    ctx.restore();
    return hp;
  }
  function eye(ctx, t, x, y) {
    let open = 0.25 + 0.75 * ease.outCubic(clamp(t / 0.35));
    const blinkT = ev.child + 0.8; const bu = t - blinkT; if (bu > 0 && bu < 0.25) open *= Math.abs(1 - bu / 0.125);
    const wide = 1 + 0.25 * sm(ev.drop - 0.1, ev.drop + 0.2, t) * (1 - sm(ev.village, ev.village + 1, t));
    const rx = 30 * wide, ry = 15 * open * wide;
    ctx.save(); ctx.translate(x, y);
    ctx.shadowColor = 'rgba(255,190,80,0.9)'; ctx.shadowBlur = 30;
    ctx.fillStyle = GOLD_HI; ctx.beginPath(); ctx.ellipse(0, 0, rx, Math.max(1, ry), 0, 0, 7); ctx.fill();
    ctx.shadowBlur = 0;
    const look = -10 * sm(ev.child, ev.child + 1, t) + 4 * sm(ev.village, ev.village + 1, t);
    ctx.fillStyle = '#120a02'; ctx.beginPath(); ctx.ellipse(look, 0, 4.5 * wide, Math.max(0.5, ry * 0.92), 0, 0, 7); ctx.fill();
    ctx.restore();
  }
  function fire(ctx, t, hp) {
    for (const f of S.fires) {
      const u = t - f.t; if (u < 0 || u > 0.55) continue;
      const a = u < 0.08 ? u / 0.08 : 1 - (u - 0.08) / 0.47;
      const mx = hp.x - 155, my = hp.y - 4, tx = W * 0.10, ty = GROUND - 70;
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const len = Math.hypot(tx - mx, ty - my), ang = Math.atan2(ty - my, tx - mx);
      ctx.translate(mx, my); ctx.rotate(ang);
      const g = ctx.createLinearGradient(0, 0, len, 0);
      g.addColorStop(0, `rgba(255,240,190,${a})`); g.addColorStop(0.4, `rgba(255,150,50,${0.85 * a})`); g.addColorStop(1, `rgba(200,60,20,${0.3 * a})`);
      ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(0, -8); ctx.quadraticCurveTo(len * 0.6, -70, len * 1.05, -120); ctx.lineTo(len * 1.05, 120); ctx.quadraticCurveTo(len * 0.6, 70, 0, 8); ctx.fill();
      ctx.restore();
      // ground glow
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const gg = ctx.createRadialGradient(tx, ty, 0, tx, ty, 260); gg.addColorStop(0, `rgba(255,150,60,${0.5 * a})`); gg.addColorStop(1, 'rgba(255,150,60,0)');
      ctx.fillStyle = gg; ctx.fillRect(tx - 260, ty - 260, 520, 520); ctx.restore();
    }
  }
  // ---------- knights ----------
  function knight(ctx, x, y, dir, t, k) {
    ctx.save(); ctx.translate(x, y); ctx.scale(dir, 1);
    const bob = Math.abs(Math.sin(t * 14 + k)) * 6;
    ctx.translate(0, -bob);
    ctx.fillStyle = '#1b1f2b'; ctx.strokeStyle = 'rgba(227,176,75,0.55)'; ctx.lineWidth = 2;
    ctx.fillRect(-14, -110, 28, 60); ctx.strokeRect(-14, -110, 28, 60);         // torso
    ctx.fillRect(-12, -50, 9, 50); ctx.fillRect(3, -50, 9, 50);                    // legs
    ctx.beginPath(); ctx.arc(0, -126, 16, 0, 7); ctx.fill(); ctx.stroke();         // helmet
    ctx.fillStyle = GOLD; ctx.beginPath(); ctx.moveTo(-4, -142); ctx.quadraticCurveTo(-20, -168, -34, -150); ctx.quadraticCurveTo(-18, -150, -4, -138); ctx.fill(); // plume
    ctx.fillStyle = '#262b3a'; ctx.beginPath(); ctx.moveTo(14, -104); ctx.lineTo(40, -104); ctx.lineTo(40, -70); ctx.lineTo(27, -56); ctx.lineTo(14, -70); ctx.closePath(); ctx.fill(); ctx.stroke(); // shield
    ctx.strokeStyle = '#8c8c95'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-10, -96); ctx.lineTo(80, -120); ctx.stroke(); // lance
    ctx.restore();
  }
  function knights(ctx, t) {
    S.fires.forEach((f, k) => {
      const u = t - f.t;
      if (u < -1.0 || u > 0.8) return;
      let x, dir = 1;
      if (u < 0) x = lerp(-80, W * 0.17, ease.outCubic((u + 1.0) / 1.0));
      else { x = lerp(W * 0.17, -160, ease.inCubic(clamp(u / 0.7))); dir = -1; }
      knight(ctx, x, GROUND - 8, dir, t, k);
      if (u > 0 && u < 0.6) { // smoke puff on the fleeing knight
        ctx.fillStyle = `rgba(60,55,50,${0.5 * (1 - u / 0.6)})`;
        ctx.beginPath(); ctx.arc(x, GROUND - 150 - u * 120, 20 + u * 60, 0, 7); ctx.fill();
      }
    });
  }
  // ---------- the child ----------
  function childX(t) { return lerp(-60, W * 0.33, ease.inOutQuad(clamp((t - ev.child) / (ev.last - 0.3 - ev.child)))); }
  function child(ctx, t) {
    if (t < ev.child) return;
    const x = childX(t), walking = t < ev.last - 0.3;
    const ph = walking ? (t - ev.child) * Math.PI * 2 : 0;
    const y = GROUND - 8 - (walking ? Math.abs(Math.sin(ph)) * 5 : 0);
    // lantern glow
    const lx = x + 32, ly = y - 66;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const gr = ctx.createRadialGradient(lx, ly, 0, lx, ly, 200); gr.addColorStop(0, 'rgba(255,200,110,0.45)'); gr.addColorStop(1, 'rgba(255,200,110,0)');
    ctx.fillStyle = gr; ctx.fillRect(lx - 200, ly - 200, 400, 400); ctx.restore();
    ctx.save(); ctx.translate(x, y);
    ctx.fillStyle = '#20263a'; ctx.strokeStyle = 'rgba(227,176,75,0.6)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(-22, -24); ctx.lineTo(-14, -88); ctx.lineTo(14, -88); ctx.lineTo(22, -24); ctx.closePath(); ctx.fill(); ctx.stroke(); // dress/cloak
    const sw = walking ? Math.sin(ph) * 9 : 0;
    ctx.fillRect(-10 + sw * 0.4, -26, 7, 26); ctx.fillRect(3 - sw * 0.4, -26, 7, 26);       // legs
    ctx.beginPath(); ctx.arc(0, -108, 20, 0, 7); ctx.fill(); ctx.stroke();                     // head
    ctx.fillStyle = '#2a2f45'; ctx.beginPath(); ctx.arc(-4, -114, 21, Math.PI * 0.9, Math.PI * 2.05); ctx.fill(); // hair
    ctx.strokeStyle = '#20263a'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(10, -78); ctx.lineTo(30, -66); ctx.stroke(); // arm
    ctx.fillStyle = GOLD_HI; ctx.fillRect(26, -72, 12, 16); ctx.strokeStyle = GOLD; ctx.lineWidth = 2; ctx.strokeRect(25, -73, 14, 18);
    ctx.restore();
  }
  // ---------- the chest ----------
  function chest(ctx, t) {
    const w = 230, h = 140, x = CX - w / 2, y = GROUND - 12 - h;
    const open = t >= ev.drop ? ease.outBack(clamp((t - ev.drop) / 0.35)) : 0;
    const rattle = (t > ev.last && t < ev.breath) ? Math.sin(t * 60) * 2 * sm(ev.last, ev.breath, t) : 0;
    ctx.save(); ctx.translate(rattle, 0);
    // interior (empty) when open
    if (open > 0) {
      ctx.fillStyle = '#050403'; ctx.fillRect(x + 8, y - 8, w - 16, 30);
    }
    ctx.fillStyle = '#3a2716'; ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = 'rgba(0,0,0,0.5)'; ctx.lineWidth = 2;
    for (let k = 1; k < 4; k++) { ctx.beginPath(); ctx.moveTo(x, y + k * h / 4); ctx.lineTo(x + w, y + k * h / 4); ctx.stroke(); }
    ctx.fillStyle = GOLD; for (const bx of [x + 22, x + w - 36]) ctx.fillRect(bx, y, 14, h);
    ctx.strokeStyle = GOLD; ctx.lineWidth = 4; ctx.strokeRect(x, y, w, h);
    // lid: hinge at back-top, rotates up and back
    ctx.save(); ctx.translate(x, y);
    const ang = -open * 1.9;
    ctx.translate(0, 0); ctx.transform(1, 0, 0, Math.cos(ang), 0, 0);
    ctx.fillStyle = '#4a321c'; ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, -34); ctx.quadraticCurveTo(w / 2, -70, w, -34); ctx.lineTo(w, 0); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = GOLD; ctx.lineWidth = 4; ctx.stroke();
    ctx.fillStyle = GOLD; for (const bx of [22, w - 36]) ctx.fillRect(bx, -52, 14, 52);
    ctx.restore();
    // lock
    if (open < 0.2) {
      const glint = 0.5 + 0.5 * Math.sin(t * 3);
      ctx.fillStyle = GOLD_HI; ctx.fillRect(CX - 16, y - 8, 32, 38);
      ctx.save(); ctx.globalCompositeOperation = 'lighter';
      const gr = ctx.createRadialGradient(CX, y + 10, 0, CX, y + 10, 60); gr.addColorStop(0, `rgba(255,220,150,${0.35 * glint})`); gr.addColorStop(1, 'rgba(255,220,150,0)');
      ctx.fillStyle = gr; ctx.fillRect(CX - 60, y - 50, 120, 120); ctx.restore();
      ctx.fillStyle = '#120a02'; ctx.fillRect(CX - 3, y + 6, 6, 12);
    }
    ctx.restore();
    // dust rising out of the empty chest
    if (t >= ev.drop) {
      const r = U.mulberry32(66);
      for (let i = 0; i < 40; i++) {
        const st = ev.drop + r() * 1.2, u = t - st, sp = 50 + r() * 70, x0 = CX + (r() - 0.5) * 180;
        if (u < 0) continue;
        const yy = y - 10 - u * sp, a = Math.max(0, 0.5 - u * 0.1);
        if (a <= 0) continue;
        ctx.fillStyle = `rgba(210,200,180,${a})`; ctx.beginPath(); ctx.arc(x0 + Math.sin(u * 2 + i) * 20, yy, 2 + r() * 2.5, 0, 7); ctx.fill();
      }
    }
  }

  function embers(ctx, t, boost = 0) {
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 34; i++) {
      const sp = 40 + r() * 70, x0 = r() * W, ph = r() * 40, sz = 1.5 + r() * 3, ra = r();
      const y = H - ((t * sp + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.8 + i) * 30;
      ctx.fillStyle = `rgba(255,200,110,${Math.min(1, (0.16 + 0.28 * ra) * (1 + boost))})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- text ----------
  function seriesTag(ctx) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.fillText('FANTASY IN 30 SEKUNDEN · #1', W / 2, S.SAFE.y + 34);
    ctx.fillStyle = 'rgba(227,176,75,0.5)'; ctx.fillRect(W / 2 - 60, S.SAFE.y + 52, 120, 2);
    ctx.restore();
  }
  function card(ctx, c, t) {
    if (t < c.t - 0.01 || t > c.end + 0.1) return;
    let size = c.small ? 92 : 128; const lh = size * 1.02;
    const fadeOut = 1 - clamp((t - c.end) / 0.1);
    const y0 = S.SAFE.y + 100 + size * 0.8;
    ctx.save(); ctx.textBaseline = 'alphabetic';
    ctx.font = `400 ${size}px "Bebas Neue"`;
    c.lines.forEach((line, i) => {
      const appear = c.t === ev.hook || c.t === ev.drop ? 1 : ease.outCubic(clamp((t - c.t - i * 0.12) / 0.28));
      const a = appear * fadeOut; if (a <= 0) return;
      const parts = line.split('*');
      let total = parts.reduce((w, p) => w + ctx.measureText(p).width, 0);
      let sc = 1; if (total > W - 120) sc = (W - 120) / total;
      let x = W / 2 - total * sc / 2; const y = y0 + i * lh + (1 - appear) * 30;
      ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc);
      let xx = 0;
      parts.forEach((p, j) => {
        ctx.globalAlpha = a;
        ctx.shadowColor = 'rgba(0,0,0,0.95)'; ctx.shadowBlur = 26;
        ctx.fillStyle = j % 2 ? GOLD : INK;
        ctx.fillText(p, xx, 0);
        xx += ctx.measureText(p).width;
      });
      ctx.restore();
    });
    ctx.restore();
  }
  function counter(ctx, t) {
    if (t >= ev.drop) return;
    const l = lastOf(S.ticks, t);
    const label = 'JAHR ', n = l ? l.n.toLocaleString('de-DE') : '';
    const pop = l ? Math.exp(-(t - l.t) * 8) : 0;
    ctx.save(); ctx.globalAlpha = 1 - sm(ev.breath - 0.2, ev.breath, t);
    const y = H * 0.765;
    const sz = 80 * (1 + 0.15 * pop);
    ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(n).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left';
    ctx.fillStyle = 'rgba(6,6,10,0.6)'; ctx.fillRect(W / 2 - 250, y - 86, 500, 116);
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
    ctx.fillStyle = 'rgba(6,6,10,0.88)'; ctx.fillRect(W / 2 - 330, y - 62, 660, 130);
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
      for (const [h, amp] of [[ev.hook, 14], [ev.drop, 34], ...S.fires.map((f) => [f.t, 9])]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      const zoom = 1.14 + 0.08 * sm(0, ev.breath, t) - 0.14 * sm(ev.village - 0.3, ev.village + 2.2, t);
      const fy = H * 0.60;
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      ctx.translate(W / 2, fy); ctx.scale(zoom, zoom); ctx.translate(-W / 2, -fy);
      sky(ctx, t);
      mountains(ctx);
      village(ctx, t);
      ground(ctx);
      const hp = dragon(ctx, t);
      knights(ctx, t);
      fire(ctx, t, hp);
      chest(ctx, t);
      child(ctx, t);
      embers(ctx, t, t >= ev.drop ? 1.2 * Math.exp(-(t - ev.drop)) : 0);
      ctx.restore();
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(0, 0, W, H); }
      const f = t >= ev.drop ? 0.9 * Math.exp(-(t - ev.drop) * 9) : (t < 0.25 ? 0.2 * Math.exp(-t * 12) : 0);
      if (f > 0.01) { ctx.fillStyle = `rgba(255,236,200,${f})`; ctx.fillRect(0, 0, W, H); }
      // darken top so cards read
      const tg = ctx.createLinearGradient(0, 0, 0, H * 0.42); tg.addColorStop(0, 'rgba(0,0,0,0.45)'); tg.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = tg; ctx.fillRect(0, 0, W, H * 0.42);
      if (t >= ev.end - 0.5) { ctx.fillStyle = `rgba(4,4,8,${0.5 * sm(ev.end - 0.5, ev.end + 0.5, t)})`; ctx.fillRect(0, 0, W, H); }
      seriesTag(ctx);
      counter(ctx, t);
      footer(ctx, t);
      for (const c of S.cards) card(ctx, c, t);
    },
    post: { paper: 0, vignette: 0.55, grain: 0.04 },
  });
})();
