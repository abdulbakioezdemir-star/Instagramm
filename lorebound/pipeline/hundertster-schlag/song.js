// THE SONG — dark, building score for „Der hundertste Schlag“, all synthesized from score.js.
const path = require('path');
const { SR, Bus, reverb, pingpong } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { T, BEAT, DURATION, m, ev, clock } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), low = bus(), str = bus(), brass = bus(), bells = bus(), fx = bus(), hits = bus();
const verb = bus(), dly = bus();
const inBreath = (t) => t >= ev.breath && t < ev.drop;
const hz = (nm) => 440 * Math.pow(2, (m(nm) - 69) / 12);

// ---------- strings: low sustained chords ----------
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.45 : c.t0 >= ev.reveal ? 1.15 : c.t0 >= T(4) ? 1.05 : 0.9;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.35, release: 0.8, bright: 0.6, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// ---------- hammer strikes: stone knock + short metal ring; grow louder as the count rises ----------
const strikeHit = (t, k, g) => {
  hits.addMono(I.thud(110, 0.12, 21 + k), t, 0.9 * g);
  hits.addMono(I.thwack(), t, 0.22 * g);
  hits.addMono(I.timpani(m('A2'), { decay: 0.28, seed: 50 + k }), t, 0.35 * g);
  fx.addMono(I.glass(k + 3, { size: 0.35 }), t + 0.01, 0.05 * g, k % 2 ? 0.3 : -0.3);
  verb.addMono(I.thud(110, 0.12, 21 + k), t, 0.2 * g);
};
sc.strikes.forEach((s, k) => strikeHit(s.t, k, k === 0 ? 1.4 : 0.55 + 0.45 * (s.n / 99)));
// hook: boom on frame one
fx.addMono(I.subBoom(2.0, 70, 30), ev.hook, 0.75);
drums.addMono(I.timpani(m('D2'), { decay: 1.6 }), ev.hook, 0.8);

// ---------- timpani on downbeats while he works ----------
const kicks = [];
clock.eachStep(2, 10, 4, (t, b, s) => { if (s === 0 && !inBreath(t)) { drums.addMono(I.timpani(m('D2'), { decay: 0.8, seed: b }), t, 0.4); kicks.push(t); } });

// ---------- reveal: inner cracks glow — bell shimmer, one per glint ----------
['D5', 'F5', 'A5', 'C6', 'D6', 'F6', 'E6', 'A6'].forEach((nm, i) => {
  const t = ev.reveal + i * BEAT * 1.5;
  const b = I.bell(hz(nm), 0.5, 1.6, 2.0);
  bells.addMono(b, t, 0.3, i % 2 ? 0.3 : -0.3); verb.addMono(b, t, 0.25); dly.addMono(b, t, 0.12);
});
fx.addMono(I.noiseSweep(1.4, 1200, 8000, { q: 1.4, pink: true }), ev.reveal - 0.3, 0.14);
// riser into the breath
fx.addMono(I.noiseSweep(ev.breath - T(9), 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), T(9), 0.3);
for (let t = T(9), k = 0; t < ev.last - 0.1; k++) { drums.addMono(I.heartbeat(), t, 0.55 + k * 0.05); t += BEAT * 1.0; }

// ---------- drop: strike 100, the stone splits ----------
hits.addMono(I.thud(90, 0.2, 99), ev.drop, 1.2);
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 0.95);
fx.addMono(I.thwack(), ev.drop, 0.8);
fx.addMono(I.glass(77, { size: 1.6 }), ev.drop, 0.35);
drums.addMono(I.timpani(m('D2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.45);
clock.eachStep(12, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('D2'), { decay: 0.9, seed: 80 + b }), t, 0.45); kicks.push(t); } });
// horns: the Lorebound motif
const horn = [[ev.drop, 'D4', 3.4], [ev.drop, 'A3', 3.4], [ev.end, 'D4', 1.0], [ev.end + 1.0, 'F4', 0.5], [ev.end + 1.5, 'E4', 0.5], [ev.end + 2.0, 'D4', 3.5], [ev.end + 2.0, 'A3', 3.5]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.22); brass.addStereo(b.L, b.R, t, 0.14); verb.addStereo(a.L, a.R, t, 0.12);
}
bells.addMono(I.bell(hz('D6'), 0.9, 1.4, 2.0), ev.follow, 0.25);
verb.addMono(I.bell(hz('D6'), 0.9, 1.4, 2.0), ev.follow, 0.3);
// title-card whooshes
for (const c of sc.cards) if (c.t > 1 && c.t !== ev.drop) fx.addMono(I.noiseSweep(0.35, 600, 3000, { q: 1, pink: true }), c.t - 0.12, 0.1);

// ---------- mix ----------
MIX.sidechain([str, low], kicks.filter((t) => t >= ev.drop));
const stems = { drums, low, str, brass, bells, fx, hits, verb: reverb(verb, { room: 0.85, damp: 0.4 }), dly: pingpong(dly, BEAT * 0.75, 0.35, 3000) };
const GAIN = { drums: 0.6, low: 1.0, str: 1.6, brass: 1.6, bells: 0.8, fx: 0.8, hits: 0.7, verb: 1, dly: 1 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 25);
MIX.gate(mix, ev.breath, ev.drop);
MIX.fadeOut(mix, DURATION - 1.6, DURATION);
const M = MIX.master(mix, parseFloat(process.env.DRIVE || '0.8'), undefined, { lufs: process.env.LUFS ? parseFloat(process.env.LUFS) : null });
MIX.writeWav(path.join(out, 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s${M.lufs !== undefined ? `, ${M.lufs.toFixed(1)} LUFS` : ''})`);
