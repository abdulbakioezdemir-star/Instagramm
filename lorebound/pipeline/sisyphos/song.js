// THE SONG — dark, building score for „Sisyphos“, all synthesized from score.js.
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
const inFrozen = (t) => t >= ev.frozen && t < ev.escape;
const hz = (nm) => 440 * Math.pow(2, (m(nm) - 69) / 12);

// ---------- strings ----------
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.5 : c.t0 >= ev.punish ? 1.1 : 0.9;
  const bright = c.t0 >= ev.drop ? 0.8 : 0.55;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.35, release: 0.8, bright, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// ---------- hook: chains snap shut ----------
fx.addMono(I.subBoom(2.0, 70, 30), ev.hook, 0.8);
drums.addMono(I.timpani(m('E2'), { decay: 1.6 }), ev.hook, 0.85);
hits.addMono(I.thwack(), ev.hook, 0.5);
for (let k = 0; k < 4; k++) fx.addMono(I.glass(5 + k, { size: 0.6 }), ev.hook + k * 0.045, 0.16, k % 2 ? 0.4 : -0.4);
verb.addMono(I.glass(9, { size: 0.9 }), ev.hook, 0.2);
// card 2: chain clank
for (let k = 0; k < 3; k++) fx.addMono(I.glass(20 + k, { size: 0.45 }), ev.chain + k * 0.07, 0.1, k % 2 ? 0.3 : -0.3);

// heartbeat pulse in act 1 (stops while time is frozen)
const kicks = [];
clock.eachStep(0, 3, 2, (t, b, s) => { if (t > 0.2 && !inFrozen(t)) drums.addMono(I.heartbeat(), t, 0.5); });
// frozen time: one high held bell, everything else thin
const fr = I.bell(hz('B5'), 1.6, 1.2, 2.0);
bells.addMono(fr, ev.frozen, 0.25); verb.addMono(fr, ev.frozen, 0.35);
// escape: rising sweep into the punishment
fx.addMono(I.noiseSweep(ev.punish - ev.escape, 200, 6000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.escape, 0.28);

// ---------- punishment ----------
fx.addMono(I.subBoom(1.8, 70, 28), ev.punish, 0.7);
drums.addMono(I.timpani(m('E2'), { decay: 1.4, seed: 4 }), ev.punish, 0.8);
// a step-thud for each push, a heavy rolling rumble each time the stone slips back
sc.cycles.forEach((c, k) => {
  const g = 0.6 + 0.05 * k;
  for (let t = c.t0 + BEAT * 0.5; t < c.tp - 0.1; t += BEAT) hits.addMono(I.thud(80, 0.08, 30 + k), t, 0.35 * g);
  hits.addMono(I.thud(70, 0.25, 60 + k), c.tp, 0.9 * g);
  hits.addMono(I.timpani(m('B1'), { decay: 0.6, seed: 70 + k }), c.tp, 0.45 * g);
  fx.addMono(I.noiseSweep(Math.max(0.25, c.t1 - c.tp), 900, 120, { q: 0.7, pink: true }), c.tp, 0.22 * g);
  bells.addMono(I.bell(hz(['E5', 'G5', 'B5', 'E6', 'G6', 'B6', 'D6', 'E6'][k]), 0.4, 1.6, 2.0), c.tp, 0.16, k % 2 ? 0.3 : -0.3);
});
clock.eachStep(4, 10, 4, (t, b, s) => { if (s === 0 && !inBreath(t)) { drums.addMono(I.timpani(m('E2'), { decay: 0.8, seed: b }), t, 0.38); kicks.push(t); } });
// riser into the breath
fx.addMono(I.noiseSweep(ev.breath - T(9), 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), T(9), 0.3);
for (let t = ev.last, k = 0; t < ev.breath - 0.1; k++) { drums.addMono(I.heartbeat(), t, 0.6 + k * 0.05); t += BEAT; }

// ---------- drop: sunrise ----------
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 0.95);
fx.addMono(I.thwack(), ev.drop, 0.7);
fx.addMono(I.glass(77, { size: 1.6 }), ev.drop, 0.3);
drums.addMono(I.timpani(m('G2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.45);
clock.eachStep(12, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('G2'), { decay: 0.9, seed: 80 + b }), t, 0.4); kicks.push(t); } });
// the stone rolls away below
fx.addMono(I.noiseSweep(2.4, 600, 90, { q: 0.6, pink: true }), ev.drop + 0.35, 0.2);
// horns: the Lorebound motif, in G major
const horn = [[ev.drop, 'G4', 3.4], [ev.drop, 'D4', 3.4], [ev.end, 'G4', 1.0], [ev.end + 1.0, 'B4', 0.5], [ev.end + 1.5, 'A4', 0.5], [ev.end + 2.0, 'G4', 3.5], [ev.end + 2.0, 'D4', 3.5]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.2); brass.addStereo(b.L, b.R, t, 0.13); verb.addStereo(a.L, a.R, t, 0.12);
}
bells.addMono(I.bell(hz('G6'), 0.9, 1.4, 2.0), ev.follow, 0.25);
verb.addMono(I.bell(hz('G6'), 0.9, 1.4, 2.0), ev.follow, 0.3);
// title-card whooshes
for (const c of sc.cards) if (c.t > 1 && c.t !== ev.drop) fx.addMono(I.noiseSweep(0.35, 600, 3000, { q: 1, pink: true }), c.t - 0.12, 0.09);

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
