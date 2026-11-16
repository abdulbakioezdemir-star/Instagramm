// THE SONG — „Das Glas Wasser“: ease, strain, release. All synthesized from score.js.
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

// strings: quiet in the calm minute, swelling with strain
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.45 : c.t0 >= ev.day ? 1.25 : c.t0 >= ev.hour ? 1.05 : c.t0 >= ev.minute ? 0.65 : 0.9;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.35, release: 0.8, bright: 0.6, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// hook: boom + glass ring + slosh on frame one
fx.addMono(I.subBoom(2.0, 65, 30), ev.hook, 0.8);
drums.addMono(I.timpani(m('D2'), { decay: 1.6 }), ev.hook, 0.85);
fx.addMono(I.thwack(), ev.hook, 0.4);
const clink = (nm, a, t) => { const b = I.bell(hz(nm), 0.35, 1.2, 2.76); bells.addMono(b, t, a); verb.addMono(b, t, a * 0.8); };
clink('A6', 0.22, ev.hook); clink('E7', 0.12, ev.hook + 0.02);
fx.addMono(I.noiseSweep(0.9, 300, 1400, { q: 1.4, pink: true }), ev.hook + 0.05, 0.22);
// the question: a single glass tap
clink('D7', 0.2, ev.ask); clink('A6', 0.12, ev.ask + 0.04);

// minutes: light marimba climbing + soft clock tick
const calm = ['D5', 'F5', 'A5', 'C6', 'D6', 'A5', 'F5', 'G5', 'A5', 'C6', 'D6', 'F6', 'E6', 'D6'];
sc.minutes.forEach((g, k) => {
  fx.addMono(I.woodTick(1.3), g.t, 0.13);
  const s = I.marimba(m(calm[k % calm.length]), { decay: 0.35, seed: 13 + k });
  keys.addMono(s, g.t, 0.16, k % 2 ? 0.25 : -0.25); dly.addMono(s, g.t, 0.04);
});
// hours: heavy tick-tock, falling marimba, getting louder
const heavy = ['D4', 'C4', 'A#3', 'A3', 'G3', 'F3', 'E3', 'D3'];
sc.hours.forEach((g, k) => {
  const x = k / 23;
  fx.addMono(I.woodTick(k % 2 ? 0.7 : 0.85), g.t, 0.16 + 0.12 * x);
  fx.addMono(I.thud(70 + (k % 3) * 6, 0.14, 40 + k), g.t, 0.25 + 0.4 * x);
  const s = I.marimba(m(heavy[k % heavy.length]), { decay: 0.4, seed: 60 + k });
  keys.addMono(s, g.t, 0.14 + 0.08 * x, k % 2 ? 0.3 : -0.3); dly.addMono(s, g.t, 0.04);
});
bells.addMono(I.bell(hz('D4'), 0.8, 1.8, 2.0), ev.hour, 0.25); verb.addMono(I.bell(hz('D4'), 0.8, 1.8, 2.0), ev.hour, 0.25);
bells.addMono(I.bell(hz('A3'), 0.9, 1.8, 2.0), ev.day, 0.3); verb.addMono(I.bell(hz('A3'), 0.9, 1.8, 2.0), ev.day, 0.3);
fx.addMono(I.noiseSweep(ev.dry - ev.hour, 150, 2200, { q: 0.8, pink: true, shape: (x) => x }), ev.hour, 0.14);
// heartbeat from the day onward, faster into the breath
for (let t = ev.day, k = 0; t < ev.breath - 0.15; k++) { drums.addMono(I.heartbeat(), t, 0.35 + k * 0.03); t += k < 6 ? BEAT : BEAT * 0.75; }
fx.addMono(I.noiseSweep(ev.breath - ev.dry, 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.dry, 0.3);

// drop: the glass meets the table
fx.addMono(I.thud(95, 0.2, 99), ev.drop, 1.0);
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 0.9);
fx.addMono(I.thwack(), ev.drop, 0.55);
drums.addMono(I.timpani(m('D2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.4);
clink('A6', 0.35, ev.drop); clink('D7', 0.2, ev.drop + 0.015);
['D6', 'F6', 'A6', 'C7', 'D7', 'A6'].forEach((nm, i) => {
  const t = ev.drop + 0.3 + i * BEAT * 0.5; const b = I.bell(hz(nm), 0.5, 1.6, 2.0);
  bells.addMono(b, t, 0.16, i % 2 ? 0.3 : -0.3); verb.addMono(b, t, 0.2); dly.addMono(b, t, 0.1);
});
const kicks = [];
clock.eachStep(10, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('D2'), { decay: 0.9, seed: 80 + b }), t, 0.42); kicks.push(t); } });
// horns: Lorebound motif
const horn = [[ev.drop, 'D4', 3.4], [ev.drop, 'A3', 3.4], [T(11, 2), 'F4', 1.5], [T(11, 2), 'A#3', 1.5],
  [ev.end, 'D4', 1.0], [ev.end + 1.0, 'F4', 0.5], [ev.end + 1.5, 'E4', 0.5], [ev.end + 2.0, 'C4', 1.5], [ev.end + 3.5, 'D4', 3.5], [ev.end + 3.5, 'A3', 3.5]];
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
