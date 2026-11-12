// THE SONG — „Der Bambus“: quiet patience, then a rising burst. All synthesized from score.js.
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
const inBreath = (t) => t >= ev.breath && t < ev.drop;
const hz = (nm) => 440 * Math.pow(2, (m(nm) - 69) / 12);

// strings
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.45 : c.t0 >= ev.reveal ? 1.15 : 0.9;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.35, release: 0.8, bright: 0.6, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// hook: boom + water splash on frame one
fx.addMono(I.subBoom(2.0, 70, 30), ev.hook, 0.75);
drums.addMono(I.timpani(m('D2'), { decay: 1.6 }), ev.hook, 0.8);
fx.addMono(I.pop(1400, 3), ev.hook, 0.5);
bells.addMono(I.bell(hz('A5'), 0.6, 1.6, 2.0), ev.hook, 0.25); verb.addMono(I.bell(hz('A5'), 0.6, 1.6, 2.0), ev.hook, 0.2);

// every day: a water drop (pop) + a soft marimba step (D minor pentatonic, cycling)
const pent = ['D4', 'F4', 'G4', 'A4', 'C5', 'D5', 'C5', 'A4'];
sc.ticks.forEach((tk, k) => {
  if (k === 0) return;
  fx.addMono(I.pop(900 + (k % 5) * 160, 10 + k), tk.t, 0.16);
  const s = I.marimba(m(pent[k % pent.length]), { decay: 0.35, seed: 13 + k });
  keys.addMono(s, tk.t, 0.16 + 0.1 * (k / 40), k % 2 ? 0.25 : -0.25); dly.addMono(s, tk.t, 0.04);
});
// soft pulse on downbeats before the reveal
const kicks = [];
clock.eachStep(1, 6, 4, (t, b, s) => { if (s === 0) drums.addMono(I.timpani(m('D2'), { decay: 0.7, seed: b }), t, 0.3); });
// seasons: wind
fx.addMono(I.noiseSweep(T(6) - ev.seasons, 300, 1800, { q: 0.7, pink: true }), ev.seasons, 0.18);

// reveal: roots glow — bell shimmer
['D5', 'F5', 'A5', 'C6', 'D6', 'F6', 'E6', 'A6'].forEach((nm, i) => {
  const t = ev.reveal + i * BEAT * 1.0;
  const b = I.bell(hz(nm), 0.5, 1.6, 2.0);
  bells.addMono(b, t, 0.3, i % 2 ? 0.3 : -0.3); verb.addMono(b, t, 0.25); dly.addMono(b, t, 0.12);
});
fx.addMono(I.noiseSweep(1.2, 4000, 400, { q: 1.2, pink: true }), ev.reveal - 0.3, 0.16);
fx.addMono(I.subBoom(1.6, 55, 30), ev.reveal, 0.35);
// riser + heartbeat into the breath
fx.addMono(I.noiseSweep(ev.breath - T(7), 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), T(7), 0.3);
for (let t = ev.roots, k = 0; t < ev.breath - 0.1; k++) { drums.addMono(I.heartbeat(), t, 0.5 + k * 0.05); t += BEAT; }

// drop: the bamboo bursts out
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 0.95);
fx.addMono(I.thwack(), ev.drop, 0.8);
fx.addMono(I.thud(90, 0.2, 99), ev.drop, 1.0);
drums.addMono(I.timpani(m('D2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.45);
fx.addMono(I.noiseSweep(3.0, 400, 7000, { q: 1.0, shape: (x) => Math.sqrt(x) * (1 - x), pink: true }), ev.drop, 0.22);
// every metre: a rising marimba + wood creak
const up = ['D4', 'E4', 'F4', 'G4', 'A4', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'C6', 'D6', 'E6', 'F6', 'G6', 'A6', 'C7', 'D7', 'D7'];
sc.metres.forEach((mt, k) => {
  const s = I.marimba(m(up[k]), { decay: 0.4, seed: 60 + k });
  keys.addMono(s, mt.t, 0.24, k % 2 ? 0.3 : -0.3); dly.addMono(s, mt.t, 0.06);
  fx.addMono(I.woodTick(0.7 + k * 0.03), mt.t, 0.12);
});
clock.eachStep(9, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('D2'), { decay: 0.9, seed: 80 + b }), t, 0.45); kicks.push(t); } });
// horns: Lorebound motif
const horn = [[ev.drop, 'D4', 3.4], [ev.drop, 'A3', 3.4], [ev.height, 'F4', 1.5], [ev.height, 'C4', 1.5], [ev.height + 1.5, 'G4', 1.5],
  [ev.end, 'D4', 1.0], [ev.end + 1.0, 'F4', 0.5], [ev.end + 1.5, 'E4', 0.5], [ev.end + 2.0, 'D4', 3.5], [ev.end + 2.0, 'A3', 3.5]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.22); brass.addStereo(b.L, b.R, t, 0.14); verb.addStereo(a.L, a.R, t, 0.12);
}
bells.addMono(I.bell(hz('D6'), 0.9, 1.4, 2.0), ev.follow, 0.25);
verb.addMono(I.bell(hz('D6'), 0.9, 1.4, 2.0), ev.follow, 0.3);
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
