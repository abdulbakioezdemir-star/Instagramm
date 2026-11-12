// THE SONG — „Die leere Truhe“: a guarded hoard, a child, an empty chest, a warm reveal. All synthesized from score.js.
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
  const loud = c.t0 >= ev.village ? 1.5 : c.t0 >= ev.drop ? 1.1 : c.t0 >= ev.knights && c.t0 < ev.child ? 1.15 : 0.85;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.35, release: 0.8, bright: 0.6, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// hook: the dragon's eye opens — boom + timpani + low growl sweep
fx.addMono(I.subBoom(2.2, 60, 26), ev.hook, 0.85);
drums.addMono(I.timpani(m('D2'), { decay: 1.8 }), ev.hook, 0.85);
fx.addMono(I.noiseSweep(1.4, 120, 600, { q: 1.4, shape: (x) => 1 - x, pink: true }), ev.hook, 0.35);
bells.addMono(I.bell(hz('A5'), 0.6, 1.6, 2.0), ev.hook, 0.22); verb.addMono(I.bell(hz('A5'), 0.6, 1.6, 2.0), ev.hook, 0.2);

// every year: a coin chime (marimba, D minor pentatonic)
const pent = ['D5', 'F5', 'G5', 'A5', 'C6', 'D6', 'C6', 'A5'];
sc.ticks.forEach((tk, k) => {
  if (k === 0) return;
  const s = I.marimba(m(pent[k % pent.length]), { decay: 0.3, seed: 13 + k });
  keys.addMono(s, tk.t, 0.12 + 0.06 * (k / 36), k % 2 ? 0.3 : -0.3); dly.addMono(s, tk.t, 0.03);
  bells.addMono(I.bell(hz(pent[k % pent.length]) * 2, 0.15, 3.1, 1.5), tk.t, 0.035);
});
// pulse
const kicks = [];
clock.eachStep(1, 7, 4, (t, b, s) => { if (s === 0) drums.addMono(I.timpani(m('D2'), { decay: 0.7, seed: b }), t, 0.3); });
// knights: fire whoosh + thud each
for (const f of sc.fires) {
  fx.addMono(I.noiseSweep(0.9, 200, 3500, { q: 0.8, shape: (x) => Math.sqrt(x) * (1 - x), pink: true }), f.t - 0.05, 0.5);
  fx.addMono(I.subBoom(1.0, 70, 30), f.t, 0.45);
  drums.addMono(I.thud(110, 0.15, 7), f.t, 0.6);
}
// child footsteps
sc.steps.forEach((t, k) => fx.addMono(I.woodTick(0.5 + (k % 2) * 0.1), t, 0.14));
// tension: riser + heartbeat into the breath
fx.addMono(I.noiseSweep(ev.breath - ev.may, 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.may, 0.26);
for (let t = ev.last, k = 0; t < ev.breath - 0.1; k++) { drums.addMono(I.heartbeat(), t, 0.55 + k * 0.05); t += BEAT; }

// drop: the lid flies open — empty
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 0.95);
fx.addMono(I.thwack(), ev.drop, 0.8);
fx.addMono(I.thud(90, 0.2, 99), ev.drop, 1.0);
drums.addMono(I.timpani(m('D2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.4);
// hollow echo of emptiness
['D6', 'A5', 'F5', 'D5'].forEach((nm, i) => { const b = I.bell(hz(nm), 0.4, 1.6, 2.4); bells.addMono(b, ev.drop + 0.3 + i * 0.4, 0.18); verb.addMono(b, ev.drop + 0.3 + i * 0.4, 0.3); });
// village reveal: warm bell shimmer + horns
['D5', 'F#5', 'A5', 'D6', 'E6', 'F#6', 'A6', 'D7'].forEach((nm, i) => {
  const t = ev.village + i * BEAT * 0.5;
  const b = I.bell(hz(nm), 0.5, 1.6, 2.0);
  bells.addMono(b, t, 0.22, i % 2 ? 0.3 : -0.3); verb.addMono(b, t, 0.22); dly.addMono(b, t, 0.1);
});
clock.eachStep(10, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('D2'), { decay: 0.9, seed: 80 + b }), t, 0.42); kicks.push(t); } });
const horn = [[ev.village, 'F4', 2.0], [ev.village, 'C4', 2.0], [ev.pass, 'G4', 1.5], [ev.pass, 'C4', 1.5], [ev.pass + 1.5, 'E4', 1.5],
  [ev.end, 'D4', 1.0], [ev.end + 1.0, 'F#4', 0.5], [ev.end + 1.5, 'E4', 0.5], [ev.end + 2.0, 'D4', 3.5], [ev.end + 2.0, 'A3', 3.5]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.22); brass.addStereo(b.L, b.R, t, 0.14); verb.addStereo(a.L, a.R, t, 0.12);
}
bells.addMono(I.bell(hz('D6'), 0.9, 1.4, 2.0), ev.follow, 0.25);
verb.addMono(I.bell(hz('D6'), 0.9, 1.4, 2.0), ev.follow, 0.3);
for (const c of sc.cards) if (c.t > 1 && c.t !== ev.drop) fx.addMono(I.noiseSweep(0.35, 600, 3000, { q: 1, pink: true }), c.t - 0.12, 0.1);

// mix
MIX.sidechain([str, low], kicks.filter((t) => t >= ev.village));
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
