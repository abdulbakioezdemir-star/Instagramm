// THE SONG — „Das Schwert des Damokles“: splendour, dread, release. All synthesized from score.js.
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

// strings (quieter in the splendour part, tense under the sword)
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.45 : c.t0 >= ev.up ? 1.1 : 0.85;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.35, release: 0.8, bright: 0.6, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// hook: boom + metallic sword ring on frame one
fx.addMono(I.subBoom(2.0, 65, 30), ev.hook, 0.8);
drums.addMono(I.timpani(m('D2'), { decay: 1.6 }), ev.hook, 0.85);
fx.addMono(I.thwack(), ev.hook, 0.5);
const ring = (t, g) => { for (const [nm, a] of [['A5', 1], ['D6', 0.6], ['E7', 0.3]]) { const b = I.bell(hz(nm), 1.4, 3.2, 2.76); bells.addMono(b, t, g * a); verb.addMono(b, t, g * a * 0.8); } };
ring(ev.hook, 0.2);

// splendour (envy/swap/sit): harp-like marimba arpeggios, 8ths
clock.eachStep(1, 6, 8, (t, b, s) => {
  if (t < ev.envy) return;
  const c = sc.chordAt(t); if (!c) return;
  const ns = c.notes.map((n) => (typeof n === 'number' ? n : m(n)) + 12);
  const nn = ns[[0, 1, 2, 1][s % 4]] + (s >= 4 ? 12 : 0);
  const v = I.marimba(nn, { decay: 0.5, seed: 40 + s });
  keys.addMono(v, t, 0.12, s % 2 ? 0.3 : -0.3); dly.addMono(v, t, 0.04);
});
// feast: three golden chimes (gold, wine, power)
sc.feast.forEach((t, i) => { const b = I.bell(hz(['D6', 'F6', 'A6'][i]), 0.7, 2.0, 2.0); bells.addMono(b, t, 0.2, [-0.3, 0, 0.3][i]); verb.addMono(b, t, 0.18); });
for (const t of [ev.sit, ev.sit + BEAT * 2]) drums.addMono(I.timpani(m('D2'), { decay: 0.7, seed: 4 }), t, 0.35);

// he looks up: sting — sub boom, ring, cut of the arpeggios
fx.addMono(I.subBoom(1.6, 70, 30), ev.up, 0.85);
fx.addMono(I.thwack(), ev.up, 0.6);
drums.addMono(I.timpani(m('D2'), { decay: 1.4, seed: 9 }), ev.up, 0.9);
ring(ev.up, 0.24);
// heartbeat = pulse counter; every beat + a low marimba tick
sc.beats.forEach((b, k) => {
  const x = (b.t - ev.up) / (ev.breath - ev.up);
  drums.addMono(I.heartbeat(), b.t, 0.45 + 0.4 * x);
  const v = I.marimba(m(['D3', 'D3', 'A2', 'D3'][k % 4]), { decay: 0.25, seed: 70 + k });
  keys.addMono(v, b.t, 0.1 + 0.08 * x);
});
// the hair creaks: thin high string tremble, rising
fx.addMono(I.noiseSweep(ev.breath - ev.hair, 3000, 9000, { q: 4, shape: (x) => 0.3 + 0.7 * x, pink: false }), ev.hair, 0.05);
fx.addMono(I.noiseSweep(ev.breath - ev.dry, 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.dry, 0.3);
for (const c of sc.cards) if (c.t > 1 && c.t !== ev.drop && c.t !== ev.up) fx.addMono(I.noiseSweep(0.35, 600, 3000, { q: 1, pink: true }), c.t - 0.12, 0.1);

// drop
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 0.95);
fx.addMono(I.thwack(), ev.drop, 0.8);
fx.addMono(I.thud(90, 0.2, 99), ev.drop, 1.0);
drums.addMono(I.timpani(m('D2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.45);
ring(ev.drop, 0.3);
['D6', 'F6', 'A6', 'C7', 'D7', 'A6'].forEach((nm, i) => {
  const t = ev.drop + 0.25 + i * BEAT * 0.5; const b = I.bell(hz(nm), 0.5, 1.6, 2.0);
  bells.addMono(b, t, 0.16, i % 2 ? 0.3 : -0.3); verb.addMono(b, t, 0.2); dly.addMono(b, t, 0.1);
});
const kicks = [];
clock.eachStep(10, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('D2'), { decay: 0.9, seed: 80 + b }), t, 0.45); kicks.push(t); } });
// horns: Lorebound motif in D minor
const horn = [[ev.drop, 'D4', 3.4], [ev.drop, 'A3', 3.4], [T(11, 2), 'F4', 1.5], [T(11, 2), 'Bb3', 1.5],
  [ev.end, 'D4', 1.0], [ev.end + 1.0, 'F4', 0.5], [ev.end + 1.5, 'E4', 0.5], [ev.end + 2.0, 'C#4', 1.5], [ev.end + 3.5, 'D4', 3.5], [ev.end + 3.5, 'A3', 3.5]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.22); brass.addStereo(b.L, b.R, t, 0.14); verb.addStereo(a.L, a.R, t, 0.12);
}
bells.addMono(I.bell(hz('D6'), 0.9, 1.4, 2.0), ev.follow, 0.25);
verb.addMono(I.bell(hz('D6'), 0.9, 1.4, 2.0), ev.follow, 0.3);

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
