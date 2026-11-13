// THE SONG — „Das dünne Seil“: strain, resignation, release. All synthesized from score.js.
const path = require('path');
const { SR, Bus, reverb, pingpong } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { T, BEAT, DURATION, m, ev, clock } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), low = bus(), str = bus(), brass = bus(), bells = bus(), fx = bus(), keys = bus();
const verb = bus(), dly = bus();
const hz = (nm) => 440 * Math.pow(2, (m(nm) - 69) / 12);

// strings
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.45 : c.t0 >= ev.stop && c.t0 < ev.years ? 0.7 : 1.0;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.35, release: 0.8, bright: 0.6, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// hook: boom + rope strain thwack on frame one
fx.addMono(I.subBoom(2.0, 65, 30), ev.hook, 0.8);
drums.addMono(I.timpani(m('E2'), { decay: 1.6 }), ev.hook, 0.85);
fx.addMono(I.thwack(), ev.hook, 0.55);
bells.addMono(I.bell(hz('B5'), 0.6, 1.6, 2.0), ev.hook, 0.22); verb.addMono(I.bell(hz('B5'), 0.6, 1.6, 2.0), ev.hook, 0.2);

// every tug: a thud (strength) + a marimba step (E minor, falling as he tires)
const steps = ['E4', 'G4', 'A4', 'B4', 'D5', 'E5', 'D5', 'B4'];
sc.tugs.forEach((g, k) => {
  fx.addMono(I.thud(70 + (k % 3) * 8, 0.18, 10 + k), g.t, 0.55 * g.s);
  fx.addMono(I.woodTick(0.9 - k * 0.01), g.t, 0.12 * g.s);
  const s = I.marimba(m(steps[k % steps.length]) - (k > 14 ? 12 : 0), { decay: 0.35, seed: 13 + k });
  keys.addMono(s, g.t, 0.18 * (0.5 + g.s * 0.5), k % 2 ? 0.25 : -0.25); dly.addMono(s, g.t, 0.04);
});
// gave up: one lonely low bell, then soft pulse
bells.addMono(I.bell(hz('E4'), 0.8, 1.8, 2.0), ev.stop, 0.3); verb.addMono(I.bell(hz('E4'), 0.8, 1.8, 2.0), ev.stop, 0.3);
const kicks = [];
clock.eachStep(1, 4, 4, (t, b, s) => { if (s === 0 && t > 0.5) drums.addMono(I.timpani(m('E2'), { decay: 0.7, seed: b }), t, 0.3); });
// years: each year a rising marimba note, heavier steps
const up = ['E4', 'F#4', 'G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F#5', 'G5', 'A5', 'B5', 'C6', 'D6', 'E6', 'F#6', 'G6', 'A6', 'B6', 'E7'];
sc.years.forEach((y, k) => {
  const s = I.marimba(m(up[k]), { decay: 0.35, seed: 60 + k });
  keys.addMono(s, y.t, 0.2, k % 2 ? 0.3 : -0.3); dly.addMono(s, y.t, 0.05);
});
fx.addMono(I.noiseSweep(ev.could - ev.years, 200, 2400, { q: 0.8, pink: true }), ev.years, 0.16);
// heavy footsteps when he is big
for (const t of [ev.could, ev.could + BEAT * 2]) { fx.addMono(I.subBoom(0.8, 50, 30), t, 0.45); drums.addMono(I.timpani(m('E2'), { decay: 0.6, seed: 5 }), t, 0.4); }
// riser + heartbeat into the breath
fx.addMono(I.noiseSweep(ev.breath - ev.dry, 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.dry, 0.3);
for (let t = ev.dry, k = 0; t < ev.breath - 0.1; k++) { drums.addMono(I.heartbeat(), t, 0.5 + k * 0.06); t += BEAT; }

// drop: the rope dissolves
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 0.95);
fx.addMono(I.thwack(), ev.drop, 0.8);
fx.addMono(I.thud(90, 0.2, 99), ev.drop, 1.0);
drums.addMono(I.timpani(m('E2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.45);
fx.addMono(I.noiseSweep(3.0, 400, 7000, { q: 1.0, shape: (x) => Math.sqrt(x) * (1 - x), pink: true }), ev.drop, 0.22);
['E6', 'G6', 'B6', 'D7', 'E7', 'B6'].forEach((nm, i) => {
  const t = ev.drop + 0.25 + i * BEAT * 0.5; const b = I.bell(hz(nm), 0.5, 1.6, 2.0);
  bells.addMono(b, t, 0.18, i % 2 ? 0.3 : -0.3); verb.addMono(b, t, 0.2); dly.addMono(b, t, 0.1);
});
clock.eachStep(10, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('E2'), { decay: 0.9, seed: 80 + b }), t, 0.45); kicks.push(t); } });
// horns: Lorebound motif
const horn = [[ev.drop, 'E4', 3.4], [ev.drop, 'B3', 3.4], [T(11, 2), 'G4', 1.5], [T(11, 2), 'C4', 1.5],
  [ev.end, 'E4', 1.0], [ev.end + 1.0, 'G4', 0.5], [ev.end + 1.5, 'F#4', 0.5], [ev.end + 2.0, 'D4', 1.5], [ev.end + 3.5, 'E4', 3.5], [ev.end + 3.5, 'B3', 3.5]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.22); brass.addStereo(b.L, b.R, t, 0.14); verb.addStereo(a.L, a.R, t, 0.12);
}
bells.addMono(I.bell(hz('E6'), 0.9, 1.4, 2.0), ev.follow, 0.25);
verb.addMono(I.bell(hz('E6'), 0.9, 1.4, 2.0), ev.follow, 0.3);
for (const c of sc.cards) if (c.t > 1 && c.t !== ev.drop) fx.addMono(I.noiseSweep(0.35, 600, 3000, { q: 1, pink: true }), c.t - 0.12, 0.1);

// mix
MIX.sidechain([str, low], kicks.filter((t) => t >= ev.drop));
const stems = { drums, low, str, brass, bells, fx, keys, verb: reverb(verb, { room: 0.85, damp: 0.4 }), dly: pingpong(dly, BEAT * 0.75, 0.35, 3000) };
const GAIN = { drums: 0.6, low: 1.0, str: 1.6, brass: 1.6, bells: 0.8, fx: 0.8, keys: 0.9, verb: 1, dly: 1 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 25);
MIX.gate(mix, ev.breath, ev.drop);
MIX.fadeOut(mix, DURATION - 1.6, DURATION);
const M = MIX.master(mix, parseFloat(process.env.DRIVE || '0.8'), undefined, { lufs: process.env.LUFS ? parseFloat(process.env.LUFS) : null });
MIX.writeWav(path.join(out, 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s${M.lufs !== undefined ? `, ${M.lufs.toFixed(1)} LUFS` : ''})`);
