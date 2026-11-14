// LOREBOUND – „Das Schwert des Damokles“ (Mythen #2). Every frame is a pure function of t.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio;
  const { ev } = S;
  const { clamp, lerp, ease } = U;
  const W = G.W, H = G.H;
  const GOLD = '#E3B04B', GOLD_HI = '#FFD98A', INK = '#F2EBDD';
  const GROUND = H * 0.75;
  const SEAT = GROUND - 200;
  const CX = W / 2;
  const ANCHOR_Y = -30, POMMEL = 560, TIP = 955; // sword geometry (y in world)
  const sm = (a, b, t) => { const x = clamp((t - a) / (b - a)); return x * x * (3 - 2 * x); };
  const lastOf = (list, t) => { let l = null; for (const s of list) if (t >= s.t) l = s; return l; };

  // ---------- visibility / state ----------
  function swordAlpha(t) {
    if (t < ev.envy) return 1 - sm(ev.envy - 0.25, ev.envy - 0.05, t);
    if (t < ev.up) return 0;
    return 1;
  }
  function swordAngle(t) {
    let a = 0.022 * Math.sin(t * 1.25);
    if (t >= ev.up) a += 0.012 * Math.sin(t * 7.3) * sm(ev.hair, ev.breath, t);
    if (t >= ev.up) a += 0.05 * Math.exp(-(t - ev.up) * 3) * Math.sin((t - ev.up) * 9);
    if (t >= ev.drop) a += 0.06 * Math.exp(-(t - ev.drop) * 2.5) * Math.sin((t - ev.drop) * 11);
    if (t < 1.2) a += 0.07 * Math.exp(-t * 2.5) * Math.cos(t * 8);
    return a;
  }
  // Damokles position: standing left (envy) -> walks to throne (swap) -> seated (sit..)
  function damokles(t) {
    if (t < ev.envy) return { x: CX, seated: true, a: 0 };            // hook: throne empty (a=0)
    if (t < ev.swap + 0.6) return { x: W * 0.2, seated: false, a: sm(ev.envy, ev.envy + 0.4, t) };
    if (t < ev.sit) { const u = ease.inOutCubic(clamp((t - ev.swap - 0.6) / (ev.sit - 0.25 - ev.swap - 0.6))); return { x: lerp(W * 0.2, CX, u), seated: false, a: 1, walk: u > 0 && u < 1 }; }
    return { x: CX, seated: true, a: 1 };
  }
  function king(t) {
    if (t < ev.envy || t > ev.sit + 1.2) return null;
    if (t < ev.swap + 0.3) return { x: CX, seated: true, a: sm(ev.envy, ev.envy + 0.4, t) };
    const u = ease.inOutCubic(clamp((t - ev.swap - 0.3) / 1.6));
    return { x: lerp(CX, W * 0.82, u), seated: u < 0.15, a: 1 - sm(ev.sit + 0.2, ev.sit + 1.2, t) * 0.75 };
  }
  function lookUp(t) { return sm(ev.up - 0.05, ev.up + 0.25, t); }

  // ---------- hall ----------
  function hall(ctx, t) {
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#040408'); g.addColorStop(0.55, '#0d0b10'); g.addColorStop(1, '#171009');
    ctx.fillStyle = g; ctx.fillRect(-200, -200, W + 400, H + 400);
    // back wall arches
    ctx.strokeStyle = 'rgba(227,176,75,0.10)'; ctx.lineWidth = 3;
    for (const ax of [CX - 330, CX + 330]) { ctx.beginPath(); ctx.moveTo(ax - 120, GROUND); ctx.lineTo(ax - 120, GROUND - 520); ctx.arc(ax, GROUND - 520, 120, Math.PI, 0); ctx.lineTo(ax + 120, GROUND); ctx.stroke(); }
    // columns
    for (const cx of [95, W - 95]) {
      const cg = ctx.createLinearGradient(cx - 60, 0, cx + 60, 0);
      cg.addColorStop(0, '#0c0a09'); cg.addColorStop(0.5, '#2a231b'); cg.addColorStop(1, '#0a0908');
      ctx.fillStyle = cg; ctx.fillRect(cx - 55, -100, 110, GROUND + 100);
      ctx.strokeStyle = 'rgba(227,176,75,0.35)'; ctx.lineWidth = 2;
      for (const dx of [-30, 0, 30]) { ctx.beginPath(); ctx.moveTo(cx + dx, -100); ctx.lineTo(cx + dx, GROUND - 40); ctx.stroke(); }
      ctx.fillStyle = '#2d251c'; ctx.fillRect(cx - 75, GROUND - 40, 150, 40);
      ctx.strokeStyle = 'rgba(227,176,75,0.55)'; ctx.strokeRect(cx - 75, GROUND - 40, 150, 40);
    }
    // floor
    const fg = ctx.createLinearGradient(0, GROUND, 0, H);
    fg.addColorStop(0, '#1d150d'); fg.addColorStop(1, '#060506');
    ctx.fillStyle = fg; ctx.fillRect(-200, GROUND, W + 400, H);
    ctx.strokeStyle = 'rgba(227,176,75,0.45)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(-50, GROUND); ctx.lineTo(W + 50, GROUND); ctx.stroke();
    ctx.strokeStyle = 'rgba(227,176,75,0.12)';
    for (let i = -6; i <= 6; i++) { ctx.beginPath(); ctx.moveTo(CX + i * 90, GROUND); ctx.lineTo(CX + i * 260, H + 50); ctx.stroke(); }
    // spotlight on throne (warm)
    const sp = ctx.createRadialGradient(CX, SEAT - 80, 20, CX, SEAT - 80, 620);
    sp.addColorStop(0, 'rgba(255,205,120,0.16)'); sp.addColorStop(1, 'rgba(255,205,120,0)');
    ctx.fillStyle = sp; ctx.fillRect(CX - 700, SEAT - 700, 1400, 1400);
  }
  function lightCone(ctx, t) { // from above when the sword is revealed
    const a = t < ev.envy ? 0.8 * (1 - sm(ev.envy - 0.25, ev.envy, t)) : t >= ev.up ? 1 : 0;
    if (a <= 0) return;
    const pulse = t >= ev.up ? 1 + 0.6 * Math.exp(-(t - ev.up) * 3) : 1;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    const g = ctx.createLinearGradient(0, 0, 0, GROUND);
    g.addColorStop(0, `rgba(255,220,150,${0.13 * a * pulse})`); g.addColorStop(1, 'rgba(255,220,150,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.moveTo(CX - 40, -50); ctx.lineTo(CX + 40, -50); ctx.lineTo(CX + 300, GROUND); ctx.lineTo(CX - 300, GROUND); ctx.closePath(); ctx.fill();
    ctx.restore();
  }

  // ---------- throne ----------
  function throne(ctx) {
    ctx.save();
    const draw = (rim) => {
      ctx.beginPath(); // back with pointed top
      ctx.moveTo(CX - 150, SEAT); ctx.lineTo(CX - 150, GROUND - 600);
      ctx.quadraticCurveTo(CX - 150, GROUND - 690, CX, GROUND - 720);
      ctx.quadraticCurveTo(CX + 150, GROUND - 690, CX + 150, GROUND - 600);
      ctx.lineTo(CX + 150, SEAT); ctx.closePath();
      rim ? ctx.stroke() : ctx.fill();
      ctx.beginPath(); ctx.rect(CX - 190, SEAT, 380, 64); rim ? ctx.stroke() : ctx.fill();           // seat
      for (const lx of [CX - 180, CX + 150]) { ctx.beginPath(); ctx.rect(lx, SEAT + 64, 30, GROUND - SEAT - 64); rim ? ctx.stroke() : ctx.fill(); }
      for (const s of [-1, 1]) { ctx.beginPath(); ctx.rect(CX + s * 190 - (s > 0 ? 34 : 0), SEAT - 110, 34, 110); rim ? ctx.stroke() : ctx.fill(); // armrests
        ctx.beginPath(); ctx.arc(CX + s * 173, SEAT - 118, 22, 0, 7); rim ? ctx.stroke() : ctx.fill(); }
      ctx.beginPath(); ctx.rect(CX - 230, GROUND - 22, 460, 22); rim ? ctx.stroke() : ctx.fill();   // step
    };
    ctx.strokeStyle = 'rgba(227,176,75,0.85)'; ctx.lineWidth = 8; draw(true);
    const g = ctx.createLinearGradient(0, GROUND - 720, 0, GROUND);
    g.addColorStop(0, '#3b2d18'); g.addColorStop(1, '#171109');
    ctx.fillStyle = g; draw(false);
    // ornaments: gold inner frame + star
    ctx.strokeStyle = 'rgba(255,217,138,0.6)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(CX - 110, SEAT - 20); ctx.lineTo(CX - 110, GROUND - 590); ctx.quadraticCurveTo(CX, GROUND - 670, CX + 110, GROUND - 590); ctx.lineTo(CX + 110, SEAT - 20); ctx.stroke();
    star(ctx, CX, GROUND - 610, 22, GOLD_HI);
    ctx.restore();
  }
  function star(ctx, x, y, r, col) {
    ctx.fillStyle = col; ctx.beginPath();
    for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.42 : r; ctx.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
    ctx.closePath(); ctx.fill();
  }

  // ---------- feast table (right of throne) ----------
  function feast(ctx, t) {
    if (t < ev.sit) return;
    const tx = CX + 330, ty = GROUND - 190;
    const cold = sm(ev.dry, ev.dry + 1.5, t);
    ctx.save();
    ctx.fillStyle = '#1a130b'; ctx.strokeStyle = 'rgba(227,176,75,0.6)'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.rect(tx - 120, ty, 240, 20); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.rect(tx - 12, ty + 20, 24, GROUND - ty - 20); ctx.fill(); ctx.stroke();
    const pop = (i) => { const u = t - S.feast[i]; return u < 0 ? 0 : ease.outBack ? ease.outBack(clamp(u / 0.35)) : clamp(u / 0.35); };
    // gold coins
    let p = pop(0); if (p > 0) { for (let k = 0; k < 6; k++) { ctx.fillStyle = k % 2 ? GOLD : GOLD_HI; ctx.beginPath(); ctx.ellipse(tx - 80 + (k % 3) * 18, ty - 8 - Math.floor(k / 3) * 12 * p, 16 * p, 6 * p, 0, 0, 7); ctx.fill(); } }
    // goblet with wine (and steam that stops when cold)
    p = pop(1); if (p > 0) {
      ctx.save(); ctx.translate(tx, ty); ctx.scale(p, p);
      ctx.fillStyle = GOLD; ctx.beginPath(); ctx.moveTo(-26, -80); ctx.lineTo(26, -80); ctx.quadraticCurveTo(24, -40, 4, -36); ctx.lineTo(4, -8); ctx.lineTo(18, 0); ctx.lineTo(-18, 0); ctx.lineTo(-4, -8); ctx.lineTo(-4, -36); ctx.quadraticCurveTo(-24, -40, -26, -80); ctx.fill();
      ctx.fillStyle = '#5a0f18'; ctx.beginPath(); ctx.ellipse(0, -79, 24, 6, 0, 0, 7); ctx.fill();
      ctx.restore();
    }
    // grapes / bread
    p = pop(2); if (p > 0) {
      for (let k = 0; k < 9; k++) { const gx = tx + 60 + (k % 3) * 13 - Math.floor(k / 3) * 6, gy = ty - 10 - Math.floor(k / 3) * 12; ctx.fillStyle = lerpCol(cold, [120, 60, 140], [70, 60, 70]); ctx.beginPath(); ctx.arc(gx, gy, 9 * p, 0, 7); ctx.fill(); }
    }
    // steam over the food until it goes cold
    const steam = (1 - cold) * sm(ev.sit + 1.5, ev.sit + 2, t);
    if (steam > 0) { ctx.strokeStyle = `rgba(240,230,210,${0.25 * steam})`; ctx.lineWidth = 3; for (let k = 0; k < 3; k++) { ctx.beginPath(); for (let i = 0; i < 20; i++) { const y = ty - 40 - i * 6, x = tx + 60 + (k - 1) * 16 + Math.sin(t * 3 + i * 0.5 + k) * 6; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); } ctx.stroke(); } }
    ctx.restore();
  }
  function lerpCol(u, a, b) { return `rgb(${Math.round(lerp(a[0], b[0], u))},${Math.round(lerp(a[1], b[1], u))},${Math.round(lerp(a[2], b[2], u))})`; }

  // ---------- people (gold rim silhouettes) ----------
  function person(ctx, t, p, { crown = false, look = 0, walk = false } = {}) {
    if (!p || p.a <= 0) return;
    ctx.save(); ctx.globalAlpha = p.a;
    const bob = walk ? Math.abs(Math.sin(t * 9)) * 8 : 0;
    const shapes = (rim) => {
      const fill = () => (rim ? ctx.stroke() : ctx.fill());
      let hx, hy;
      if (p.seated) {
        ctx.beginPath(); ctx.moveTo(p.x - 70, SEAT + 6); ctx.lineTo(p.x - 52, SEAT - 175); ctx.quadraticCurveTo(p.x, SEAT - 200, p.x + 52, SEAT - 175); ctx.lineTo(p.x + 70, SEAT + 6); ctx.closePath(); fill(); // torso
        ctx.beginPath(); ctx.moveTo(p.x - 78, SEAT + 2); ctx.lineTo(p.x + 78, SEAT + 2); ctx.lineTo(p.x + 66, GROUND - 26); ctx.lineTo(p.x - 66, GROUND - 26); ctx.closePath(); fill(); // robe over legs
        hx = p.x; hy = SEAT - 228;
      } else {
        ctx.beginPath(); ctx.moveTo(p.x - 72, GROUND - 2); ctx.lineTo(p.x - 48, GROUND - 290 - bob); ctx.quadraticCurveTo(p.x, GROUND - 318 - bob, p.x + 48, GROUND - 290 - bob); ctx.lineTo(p.x + 72, GROUND - 2); ctx.closePath(); fill();
        hx = p.x; hy = GROUND - 345 - bob;
      }
      ctx.beginPath(); ctx.arc(hx, hy - look * 6, 40, 0, 7); fill();
      return [hx, hy - look * 6];
    };
    ctx.strokeStyle = 'rgba(227,176,75,0.85)'; ctx.lineWidth = 7; shapes(true);
    const g = ctx.createLinearGradient(0, SEAT - 300, 0, GROUND);
    g.addColorStop(0, '#2c2620'); g.addColorStop(1, '#100d0b');
    ctx.fillStyle = g; const [hx, hy] = shapes(false);
    // face hint: eye glint (looks at throne / up)
    ctx.fillStyle = GOLD_HI;
    if (look > 0) { ctx.beginPath(); ctx.arc(hx - 12, hy - 18 * look, 4, 0, 7); ctx.arc(hx + 12, hy - 18 * look, 4, 0, 7); ctx.fill(); }
    else if (!p.seated) { ctx.beginPath(); ctx.arc(hx + 18, hy - 6, 4, 0, 7); ctx.fill(); }
    if (crown) {
      ctx.fillStyle = GOLD; ctx.beginPath();
      ctx.moveTo(hx - 34, hy - 30); ctx.lineTo(hx - 34, hy - 62); ctx.lineTo(hx - 17, hy - 44); ctx.lineTo(hx, hy - 70); ctx.lineTo(hx + 17, hy - 44); ctx.lineTo(hx + 34, hy - 62); ctx.lineTo(hx + 34, hy - 30); ctx.closePath(); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- the sword on a hair ----------
  function sword(ctx, t) {
    const a = swordAlpha(t); if (a <= 0) return;
    const ang = swordAngle(t);
    const glow = t >= ev.up ? sm(ev.hair, ev.hair + 0.5, t) * (t < ev.drop ? 1 : Math.exp(-(t - ev.drop) * 0.5)) : 0;
    ctx.save(); ctx.globalAlpha = a;
    ctx.translate(CX, ANCHOR_Y); ctx.rotate(ang); ctx.translate(-CX, -ANCHOR_Y);
    // the hair
    ctx.save();
    if (glow > 0) { ctx.shadowColor = `rgba(255,215,130,${glow})`; ctx.shadowBlur = 24 * glow; }
    ctx.strokeStyle = `rgba(240,225,195,${0.55 + 0.45 * glow})`; ctx.lineWidth = 1.6 + 1.6 * glow;
    ctx.beginPath(); ctx.moveTo(CX, ANCHOR_Y); ctx.lineTo(CX + Math.sin(t * 13) * 0.8 * glow, (ANCHOR_Y + POMMEL) / 2); ctx.lineTo(CX, POMMEL - 18); ctx.stroke();
    ctx.restore();
    // pommel, grip, guard
    ctx.fillStyle = GOLD; ctx.beginPath(); ctx.arc(CX, POMMEL, 20, 0, 7); ctx.fill();
    ctx.fillStyle = '#3a2614'; ctx.fillRect(CX - 12, POMMEL + 16, 24, 92);
    ctx.strokeStyle = GOLD; ctx.lineWidth = 3; for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(CX - 12, POMMEL + 24 + i * 14); ctx.lineTo(CX + 12, POMMEL + 32 + i * 14); ctx.stroke(); }
    ctx.fillStyle = GOLD; ctx.beginPath(); ctx.moveTo(CX - 110, POMMEL + 108); ctx.quadraticCurveTo(CX, POMMEL + 96, CX + 110, POMMEL + 108); ctx.lineTo(CX + 110, POMMEL + 126); ctx.quadraticCurveTo(CX, POMMEL + 118, CX - 110, POMMEL + 126); ctx.closePath(); ctx.fill();
    ctx.fillStyle = GOLD_HI; ctx.beginPath(); ctx.arc(CX, POMMEL + 113, 9, 0, 7); ctx.fill();
    // blade
    const by = POMMEL + 124;
    const bg = ctx.createLinearGradient(CX - 30, 0, CX + 30, 0);
    bg.addColorStop(0, '#6d7076'); bg.addColorStop(0.48, '#e9ecef'); bg.addColorStop(0.52, '#9da2a8'); bg.addColorStop(1, '#4b4e53');
    ctx.fillStyle = bg; ctx.beginPath(); ctx.moveTo(CX - 28, by); ctx.lineTo(CX + 28, by); ctx.lineTo(CX + 22, TIP - 70); ctx.lineTo(CX, TIP); ctx.lineTo(CX - 22, TIP - 70); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(255,217,138,0.5)'; ctx.lineWidth = 2; ctx.stroke();
    // glint running down the blade (hook, reveal, drop)
    for (const h of [0.15, ev.up + 0.1, ev.drop + 0.05]) {
      const u = (t - h) / 0.6; if (u < 0 || u > 1) continue;
      const gy = lerp(by, TIP, u);
      const gg = ctx.createRadialGradient(CX, gy, 0, CX, gy, 70);
      gg.addColorStop(0, 'rgba(255,250,235,0.95)'); gg.addColorStop(1, 'rgba(255,250,235,0)');
      ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = gg; ctx.fillRect(CX - 70, gy - 70, 140, 140); ctx.globalCompositeOperation = 'source-over';
    }
    ctx.restore();
  }

  function embers(ctx, t, boost = 0) {
    const r = U.mulberry32(21);
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let i = 0; i < 34; i++) {
      const sp = 30 + r() * 60, x0 = r() * W, ph = r() * 40, sz = 1.5 + r() * 3, ra = r();
      const y = H - ((t * sp + ph * 50) % (H * 1.1));
      const x = x0 + Math.sin(t * 0.8 + i) * 30;
      ctx.fillStyle = `rgba(255,200,110,${Math.min(1, (0.15 + 0.28 * ra) * (1 + boost))})`;
      ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
    }
    ctx.restore();
  }

  // ---------- text ----------
  function seriesTag(ctx) {
    ctx.save(); ctx.textAlign = 'center'; ctx.globalAlpha = 0.9;
    ctx.font = '700 34px "Cinzel"'; ctx.fillStyle = GOLD;
    ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 12;
    ctx.fillText('MYTHEN IN 30 SEKUNDEN · #2', W / 2, S.SAFE.y + 34);
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
      const appear = c.t === ev.hook || c.t === ev.drop || c.t === ev.up ? 1 : ease.outCubic(clamp((t - c.t - i * 0.12) / 0.28));
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
        ctx.fillText(p, x, y); ctx.fillText(p, x, y);
        x += ctx.measureText(p).width;
      });
    });
    ctx.restore();
  }
  function counter(ctx, t) {
    if (t < ev.up || t >= ev.breath) return;
    const l = lastOf(S.beats, t);
    const n = l ? String(l.n) : '72';
    const pop = l ? Math.exp(-(t - l.t) * 9) : 0;
    const x = (t - ev.up) / (ev.breath - ev.up);
    const a = sm(ev.up, ev.up + 0.25, t);
    ctx.save(); ctx.globalAlpha = a;
    const y = H * 0.79;
    ctx.fillStyle = 'rgba(6,6,10,0.7)'; ctx.fillRect(W / 2 - 230, y - 92, 460, 120);
    const label = 'PULS ';
    const sz = 84 * (1 + 0.14 * pop);
    ctx.font = '700 40px "Cinzel"'; const lw = ctx.measureText(label).width;
    ctx.font = `700 ${sz}px "Cinzel"`; const nw = ctx.measureText(n).width;
    const x0 = W / 2 - (lw + nw) / 2;
    ctx.textAlign = 'left';
    ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 16;
    ctx.font = '700 40px "Cinzel"'; ctx.fillStyle = 'rgba(242,235,221,0.8)'; ctx.fillText(label, x0, y);
    ctx.font = `700 ${sz}px "Cinzel"`;
    ctx.shadowColor = `rgba(255,${Math.round(200 - 120 * x)},90,${0.5 + 0.5 * pop})`; ctx.shadowBlur = 20 + 30 * pop;
    ctx.fillStyle = lerpCol(x, [227, 176, 75], [235, 80, 55]);
    if (pop > 0.5) ctx.fillStyle = GOLD_HI;
    ctx.fillText(n, x0 + lw, y);
    ctx.restore();
  }
  function footer(ctx, t) {
    const a = sm(ev.follow, ev.follow + 0.6, t);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center';
    const y = H * 0.745;
    ctx.fillStyle = 'rgba(6,6,10,0.88)'; ctx.fillRect(W / 2 - 330, y - 62, 660, 130);
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
      for (const [h, amp] of [[ev.hook, 16], [ev.up, 18], [ev.drop, 36]]) if (t >= h) shake += amp * Math.exp(-(t - h) * 6);
      if (t >= ev.up && t < ev.breath) { const l = lastOf(S.beats, t); if (l) shake += 3 * Math.exp(-(t - l.t) * 12) * (1 + 2 * (t - ev.up) / (ev.breath - ev.up)); }
      // camera: hook close on the sword, wide in the story, push on reveal and at the end
      let zoom = 1, fx = CX, fy = 820;
      zoom += 0.32 * (1 - ease.inOutCubic(clamp(t / (ev.envy - 0.1)))) * (t < ev.envy ? 1 : 0);
      if (t < ev.envy) fy = lerp(700, 820, ease.inOutCubic(clamp(t / ev.envy)));
      zoom += 0.12 * sm(ev.up, ev.up + 0.4, t) * (1 - sm(ev.hair, ev.hair + 1.5, t)) + 0.08 * sm(ev.hair, ev.breath, t) * (1 - sm(ev.drop, ev.drop + 0.3, t));
      zoom += 0.05 * sm(ev.drop, ev.follow, t);
      ctx.save();
      ctx.translate(U.noise1(t * 30, 1) * shake, U.noise1(t * 30, 2) * shake);
      ctx.translate(fx, fy); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy);
      hall(ctx, t);
      lightCone(ctx, t);
      throne(ctx);
      feast(ctx, t);
      const k = king(t);
      person(ctx, t, k, { crown: true });
      const d = damokles(t);
      person(ctx, t, d, { look: lookUp(t), walk: d.walk });
      sword(ctx, t);
      embers(ctx, t, t >= ev.drop ? 1.5 * Math.exp(-(t - ev.drop)) : 0);
      ctx.restore();
      // dread: the hall darkens around the light after the reveal, red pulse on heartbeats
      if (t >= ev.up && t < ev.drop) {
        const l = lastOf(S.beats, t); const p = l ? Math.exp(-(t - l.t) * 7) : 0;
        const x = (t - ev.up) / (ev.breath - ev.up);
        const vg = ctx.createRadialGradient(CX, H * 0.45, H * 0.25, CX, H * 0.45, H * 0.75);
        vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, `rgba(${Math.round(60 * p * x)},0,0,${0.35 + 0.2 * x})`);
        ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
      }
      if (t >= ev.breath && t < ev.drop) { ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(0, 0, W, H); }
      let f = 0;
      if (t >= ev.drop) f = 0.9 * Math.exp(-(t - ev.drop) * 9);
      else if (t >= ev.up) f = 0.6 * Math.exp(-(t - ev.up) * 10);
      else if (t < 0.2) f = 0.25 * Math.exp(-t * 14);
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
