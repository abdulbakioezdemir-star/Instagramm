// THE SONG — cosmic, building score for „Ein Tag länger als ein Jahr“, all synthesized from score.js.
const path = require('path');
const { SR, Bus, reverb, pingpong } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { T, BEAT, DURATION, m, ev, clock } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), low = bus(), str = bus(), brass = bus(), bells = bus(), fx = bus(), ticks = bus();
const verb = bus(), dly = bus();
const inBreath = (t) => t >= ev.breath && t < ev.drop;
const hz = (nm) => 440 * Math.pow(2, (m(nm) - 69) / 12);

// ---------- strings / pads ----------
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.45 : c.t0 >= ev.year ? 1.15 : c.t0 >= T(4) ? 1.0 : 0.85;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.4, release: 0.9, bright: 0.55, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.035); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.15 * loud);
}

// ---------- hook: boom + shimmer on frame one ----------
fx.addMono(I.subBoom(2.2, 70, 28), ev.hook, 0.8);
drums.addMono(I.timpani(m('E2'), { decay: 1.6 }), ev.hook, 0.85);
fx.addMono(I.glass(5, { size: 1.2 }), ev.hook, 0.18);
bells.addMono(I.bell(hz('E6'), 0.8, 1.6, 2.0), ev.name, 0.25); verb.addMono(I.bell(hz('E6'), 0.8, 1.6, 2.0), ev.name, 0.25);
fx.addMono(I.noiseSweep(1.0, 400, 6000, { q: 1.2, pink: true }), ev.zoom - 0.5, 0.18);

// ---------- every counted day = a marimba tick, climbing an E-minor scale ----------
const scale = ['E4', 'G4', 'A4', 'B4', 'D5', 'E5', 'G5', 'A5', 'B5', 'D6'];
sc.ticks.forEach((tk, k) => {
  const nm = scale[k % scale.length];
  const g = 0.45 + 0.4 * Math.min(1, k / 34);
  ticks.addMono(I.marimba(m(nm), { decay: 0.35, seed: 13 + k }), tk.t, 0.5 * g, k % 2 ? 0.25 : -0.25);
  ticks.addMono(I.clap({ decay: 0.04, seed: k }), tk.t, 0.08 * g);
  dly.addMono(I.marimba(m(nm), { decay: 0.3, seed: 40 + k }), tk.t, 0.08);
});

// ---------- timpani pulse on downbeats ----------
const kicks = [];
clock.eachStep(2, 10, 4, (t, b, s) => { if (s === 0 && !inBreath(t)) { drums.addMono(I.timpani(m('E2'), { decay: 0.8, seed: b }), t, 0.38); kicks.push(t); } });

// ---------- 225 days: the year is done (bell chord) ----------
['E5', 'B5', 'G5', 'E6'].forEach((nm, i) => {
  const b = I.bell(hz(nm), 0.9, 1.6, 2.0);
  bells.addMono(b, ev.year + i * 0.04, 0.28, i % 2 ? 0.3 : -0.3); verb.addMono(b, ev.year, 0.22);
});
drums.addMono(I.timpani(m('G2'), { decay: 1.2, seed: 9 }), ev.year, 0.7);
// tension: riser + heartbeat into the breath
fx.addMono(I.noiseSweep(ev.breath - ev.still, 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.still, 0.28);
for (let t = ev.still, k = 0; t < ev.breath - 0.2; k++) { drums.addMono(I.heartbeat(), t, 0.5 + k * 0.06); t += BEAT; }

// ---------- drop: day 243 ----------
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 1.0);
fx.addMono(I.thwack(), ev.drop, 0.7);
fx.addMono(I.glass(77, { size: 1.6 }), ev.drop, 0.3);
drums.addMono(I.timpani(m('E2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.45);
clock.eachStep(11, 14, 4, (t, b, s) => { if (s === 0) { drums.addMono(I.timpani(m('E2'), { decay: 0.9, seed: 80 + b }), t, 0.42); kicks.push(t); } });
// horns: the Lorebound motif
const horn = [[ev.drop, 'E4', 3.4], [ev.drop, 'B3', 3.4], [ev.end, 'E4', 1.0], [ev.end + 1.0, 'G4', 0.5], [ev.end + 1.5, 'F#4', 0.5], [ev.end + 2.0, 'E4', 3.0], [ev.end + 2.0, 'B3', 3.0]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.22); brass.addStereo(b.L, b.R, t, 0.14); verb.addStereo(a.L, a.R, t, 0.12);
}
// retro: reversed-feeling whoosh; joke: small music-box sting
fx.addMono(I.noiseSweep(0.8, 5000, 400, { q: 1.2, pink: true }), ev.retro - 0.1, 0.16);
['B5', 'G5', 'E5'].forEach((nm, i) => { const b = I.musicBox(m(nm), { decay: 0.9, seed: 60 + i }); bells.addMono(b, ev.joke + 0.9 + i * 0.25, 0.35); verb.addMono(b, ev.joke + 0.9 + i * 0.25, 0.15); });
bells.addMono(I.bell(hz('E6'), 0.9, 1.4, 2.0), ev.follow, 0.25);
verb.addMono(I.bell(hz('E6'), 0.9, 1.4, 2.0), ev.follow, 0.3);
for (const c of sc.cards) if (c.t > 1 && c.t !== ev.drop) fx.addMono(I.noiseSweep(0.35, 600, 3000, { q: 1, pink: true }), c.t - 0.12, 0.08);

// ---------- mix ----------
MIX.sidechain([str, low], kicks.filter((t) => t >= ev.drop));
const stems = { drums, low, str, brass, bells, fx, ticks, verb: reverb(verb, { room: 0.88, damp: 0.4 }), dly: pingpong(dly, BEAT * 0.75, 0.35, 3000) };
const GAIN = { drums: 0.6, low: 1.0, str: 1.6, brass: 1.6, bells: 0.8, fx: 0.8, ticks: 0.9, verb: 1, dly: 1 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 25);
MIX.gate(mix, ev.breath, ev.drop);
MIX.fadeOut(mix, DURATION - 1.6, DURATION);
const M = MIX.master(mix, parseFloat(process.env.DRIVE || '0.8'), undefined, { lufs: process.env.LUFS ? parseFloat(process.env.LUFS) : null });
MIX.writeWav(path.join(out, 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s${M.lufs !== undefined ? `, ${M.lufs.toFixed(1)} LUFS` : ''})`);
