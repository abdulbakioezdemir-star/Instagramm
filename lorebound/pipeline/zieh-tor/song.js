// THE SONG — „Das Tor“: brute force, silence, one small pull. All synthesized from score.js.
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

// strings: heavy during the siege, hushed for the child, wide after the drop
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.45 : c.t0 >= ev.child ? 0.55 : c.t0 >= ev.charge ? 1.1 : 0.9;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.55, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.25, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// a door hit: wood thud + iron clank + low timpani
const hit = (t, a, seed) => {
  fx.addMono(I.thud(70, 0.18, seed), t, 0.8 * a);
  fx.addMono(I.thwack(), t, 0.3 * a);
  const cl = I.bell(hz('G2'), 0.35, 1.2, 1.41); bells.addMono(cl, t, 0.18 * a); verb.addMono(cl, t, 0.12 * a);
  drums.addMono(I.timpani(m('D2'), { decay: 0.7, seed }), t, 0.55 * a);
};
// hook: the biggest hit on frame one
fx.addMono(I.subBoom(2.0, 60, 28), ev.hook, 0.9);
hit(ev.hook, 1.2, 5);
drums.addMono(I.timpani(m('D2'), { decay: 1.8, seed: 2 }), ev.hook, 0.7);
// "300 years": a hollow bell
{ const b = I.bell(hz('D4'), 0.9, 1.8, 2.0); bells.addMono(b, ev.gate, 0.2); verb.addMono(b, ev.gate, 0.25); }

// the siege: one hit per charge, louder as the count climbs; marimba climbs with it
const pent = ['D5', 'F5', 'G5', 'A5', 'C6', 'D6'];
sc.hits.forEach((h, k) => {
  hit(h.t, 0.55 + 0.45 * (k / (sc.hits.length - 1)), 30 + k);
  const s = I.marimba(m(pent[k % pent.length]), { decay: 0.3, seed: 13 + k });
  keys.addMono(s, h.t, 0.1, k % 2 ? 0.3 : -0.3); dly.addMono(s, h.t, 0.04);
});
for (const sp of sc.spells) {
  if (sp.kind === 'zap') { fx.addMono(I.noiseSweep(0.5, 4000, 300, { q: 2 }), sp.t - 0.1, 0.35); fx.addMono(I.subBoom(1.0, 70, 30), sp.t, 0.5); }
  else { fx.addMono(I.noiseSweep(1.2, 150, 1200, { q: 0.6, pink: true }), sp.t - 0.1, 0.45); fx.addMono(I.subBoom(1.2, 55, 28), sp.t, 0.5); }
}
// "it did not move": the last echo, then a held bell
fx.addMono(I.subBoom(1.6, 50, 26), ev.still, 0.5);
{ const b = I.bell(hz('A3'), 0.9, 1.8, 2.0); bells.addMono(b, ev.still + 0.4, 0.22); verb.addMono(b, ev.still + 0.4, 0.3); }

// the child: small footsteps + music box
sc.steps.forEach((t, k) => fx.addMono(I.woodTick(1.5 + (k % 2) * 0.1), t, 0.06));
['A5', 'D6', 'F6', 'E6', 'D6', 'A5'].forEach((nm, i) => { const t = ev.child + 0.2 + i * 0.5; const s = I.musicBox(m(nm), { decay: 1.0 }); bells.addMono(s, t, 0.11); verb.addMono(s, t, 0.12); });
// reading: shimmer as the moss falls and the word glows
fx.addMono(I.noiseSweep(1.3, 2000, 7000, { q: 1.2, pink: true }), ev.read + 0.2, 0.12);
['D6', 'A6', 'D7'].forEach((nm, i) => { const b = I.bell(hz(nm), 0.5, 1.4, 2.0); bells.addMono(b, ev.read + 0.6 + i * 0.25, 0.1); verb.addMono(b, ev.read + 0.6 + i * 0.25, 0.15); });

// drop: PULL – huge creak-boom, gate swings open, golden bells
fx.addMono(I.subBoom(2.6, 72, 26), ev.drop, 0.95);
fx.addMono(I.thwack(), ev.drop, 0.6);
fx.addMono(I.thud(90, 0.2, 99), ev.drop, 0.8);
fx.addMono(I.noiseSweep(1.4, 900, 160, { q: 3, shape: (x) => Math.min(1, x * 8) * (1 - x) }), ev.drop, 0.3); // wood groan
drums.addMono(I.timpani(m('D2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.4);
['D6', 'F#6', 'A6', 'D7', 'A6', 'F#6', 'E6', 'D6'].forEach((nm, i) => {
  const t = ev.drop + 0.25 + i * BEAT * 0.5; const b = I.bell(hz(nm), 0.5, 1.6, 2.0);
  bells.addMono(b, t, 0.14, i % 2 ? 0.3 : -0.3); verb.addMono(b, t, 0.2); dly.addMono(b, t, 0.1);
});
const kicks = [];
clock.eachStep(9, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('D2'), { decay: 0.9, seed: 80 + b }), t, 0.4); kicks.push(t); } });
// horns: Lorebound motif
const horn = [[ev.drop, 'D4', 3.4], [ev.drop, 'A3', 3.4], [T(10, 2), 'F4', 1.5], [T(10, 2), 'Bb3', 1.5],
  [ev.lesson, 'E4', 1.0], [ev.lesson + 1.0, 'G4', 0.5], [ev.lesson + 1.5, 'F4', 0.5], [ev.lesson + 2.0, 'D4', 1.0],
  [ev.end, 'D4', 3.0], [ev.end, 'A3', 3.0], [ev.end, 'F#3', 3.0]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.2); brass.addStereo(b.L, b.R, t, 0.13); verb.addStereo(a.L, a.R, t, 0.12);
}
{ const b = I.bell(hz('D6'), 0.9, 1.4, 2.0); bells.addMono(b, ev.end, 0.22); verb.addMono(b, ev.end, 0.3); }
for (const c of sc.cards) if (c.t > 1 && c.t !== ev.drop) fx.addMono(I.noiseSweep(0.35, 600, 3000, { q: 1, pink: true }), c.t - 0.12, 0.08);

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
