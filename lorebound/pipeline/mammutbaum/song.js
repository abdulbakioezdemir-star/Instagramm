// THE SONG — „Der Riese, der auf Feuer wartet“: patience, fire, release. All synthesized from score.js.
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
const rnd = (() => { let s = 7; return () => ((s = (s * 16807) % 2147483647) / 2147483647); })();

// strings: hushed while waiting, swelling with the fire, wide after the drop
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.45 : c.t0 >= ev.fire ? 1.3 : c.t0 >= ev.closed ? 0.7 : 0.95;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.35, release: 0.8, bright: 0.6, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// hook: boom + ember whoosh + crackle on frame one
fx.addMono(I.subBoom(2.0, 62, 28), ev.hook, 0.85);
drums.addMono(I.timpani(m('E2'), { decay: 1.6 }), ev.hook, 0.85);
fx.addMono(I.thwack(), ev.hook, 0.35);
fx.addMono(I.noiseSweep(1.2, 200, 2600, { q: 1.1, pink: true }), ev.hook, 0.25);
const crackle = (t0, t1, rate, amp, seed) => {
  for (let t = t0; t < t1; t += (0.3 + rnd()) / rate) fx.addMono(I.pop(900 + rnd() * 2600, seed + Math.floor(t * 97)), t, amp * (0.5 + rnd()), rnd() * 1.2 - 0.6);
};
crackle(0, 1.6, 10, 0.18, 1);
const knock = (nm, a, t) => { const b = I.bell(hz(nm), 0.6, 1.4, 2.0); bells.addMono(b, t, a); verb.addMono(b, t, a); };
knock('B5', 0.18, ev.giant); knock('E6', 0.12, ev.giant + 0.03);

// years: each year = wood tick + marimba (E minor pentatonic), slow and patient
const pent = ['E5', 'G5', 'A5', 'B5', 'D6', 'E6', 'D6', 'B5', 'A5', 'G5'];
sc.years.forEach((g, k) => {
  fx.addMono(I.woodTick(1.1 - k * 0.01), g.t, 0.14);
  const s = I.marimba(m(pent[k % pent.length]), { decay: 0.4, seed: 13 + k });
  keys.addMono(s, g.t, 0.16, k % 2 ? 0.25 : -0.25); dly.addMono(s, g.t, 0.05);
});
// "nothing." – a hollow bell
bells.addMono(I.bell(hz('E4'), 0.9, 1.8, 2.0), ev.dry + 1.3, 0.22); verb.addMono(I.bell(hz('E4'), 0.9, 1.8, 2.0), ev.dry + 1.3, 0.25);

// fire: roar (filtered noise) + dense crackle + rising sweep + taiko pulse
fx.addMono(I.subBoom(1.8, 58, 30), ev.fire, 0.7);
drums.addMono(I.timpani(m('B1'), { decay: 1.4, seed: 21 }), ev.fire, 0.8);
fx.addMono(I.noiseSweep(ev.breath - ev.fire, 120, 900, { q: 0.6, pink: true, shape: (x) => Math.min(1, x * 3) * (0.7 + 0.3 * x) }), ev.fire, 0.35);
crackle(ev.fire, ev.breath - 0.1, 22, 0.22, 300);
fx.addMono(I.noiseSweep(ev.breath - ev.burn, 200, 5200, { q: 0.9, shape: (x) => x * x, pink: true }), ev.burn, 0.3);
for (let t = ev.fire + BEAT, k = 0; t < ev.breath - 0.1; k++) { drums.addMono(I.timpani(m('E2'), { decay: 0.5, seed: 40 + k }), t, 0.35 + k * 0.025); t += k < 4 ? BEAT : BEAT / 2; }
bells.addMono(I.bell(hz('B3'), 0.9, 1.8, 2.0), ev.burn, 0.28); verb.addMono(I.bell(hz('B3'), 0.9, 1.8, 2.0), ev.burn, 0.28);

// drop: the cone bursts open – boom + crack + rising golden bells
fx.addMono(I.subBoom(2.6, 72, 26), ev.drop, 0.95);
fx.addMono(I.thwack(), ev.drop, 0.6);
fx.addMono(I.thud(110, 0.15, 99), ev.drop, 0.7);
drums.addMono(I.timpani(m('E2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.4);
['E6', 'G6', 'B6', 'D7', 'E7', 'B6', 'G6', 'A6'].forEach((nm, i) => {
  const t = ev.drop + 0.2 + i * BEAT * 0.5; const b = I.bell(hz(nm), 0.5, 1.6, 2.0);
  bells.addMono(b, t, 0.15, i % 2 ? 0.3 : -0.3); verb.addMono(b, t, 0.2); dly.addMono(b, t, 0.1);
});
crackle(ev.drop, ev.seeds, 5, 0.08, 700);
// seeds landing: soft marimba drops; sprouts: music box
['B5', 'G5', 'E5', 'G5', 'A5', 'B5'].forEach((nm, i) => { const t = ev.seeds + 0.3 + i * 0.45; const s = I.marimba(m(nm), { decay: 0.35, seed: 90 + i }); keys.addMono(s, t, 0.12, i % 2 ? 0.3 : -0.3); dly.addMono(s, t, 0.05); });
['E6', 'B6', 'G6', 'E7'].forEach((nm, i) => { const t = ev.seeds + 1.2 + i * 0.6; const s = I.musicBox(m(nm), { decay: 1.2 }); bells.addMono(s, t, 0.1); verb.addMono(s, t, 0.12); });
const kicks = [];
clock.eachStep(9, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('E2'), { decay: 0.9, seed: 80 + b }), t, 0.4); kicks.push(t); } });
// horns: Lorebound motif
const horn = [[ev.drop, 'E4', 3.4], [ev.drop, 'B3', 3.4], [T(10, 2), 'G4', 1.5], [T(10, 2), 'C4', 1.5],
  [ev.lesson, 'E4', 1.0], [ev.lesson + 1.0, 'G4', 0.5], [ev.lesson + 1.5, 'F#4', 0.5], [ev.lesson + 2.0, 'D4', 1.0],
  [ev.end, 'E4', 3.0], [ev.end, 'B3', 3.0], [ev.end, 'G#3', 3.0]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.2); brass.addStereo(b.L, b.R, t, 0.13); verb.addStereo(a.L, a.R, t, 0.12);
}
bells.addMono(I.bell(hz('E6'), 0.9, 1.4, 2.0), ev.end, 0.22);
verb.addMono(I.bell(hz('E6'), 0.9, 1.4, 2.0), ev.end, 0.3);
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
