// THE SONG — dark Nordic score for „Die Fessel, die es nicht gibt“, all synthesized from score.js.
const path = require('path');
const { SR, Bus, reverb, pingpong } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const sc = require('./score');
const { T, BEAT, DURATION, m, ev, clock } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), low = bus(), str = bus(), brass = bus(), bells = bus(), fx = bus();
const verb = bus(), dly = bus();
const inBreath = (t) => t >= ev.breath && t < ev.drop;

// ---------- hook: boom on frame one ----------
fx.addMono(I.subBoom(2.0, 70, 30), ev.hook, 0.8);
drums.addMono(I.timpani(m('D2'), { decay: 1.6 }), ev.hook, 0.9);
verb.addMono(I.timpani(m('D2'), { decay: 1.6 }), ev.hook, 0.3);

// ---------- strings: low sustained chords (the whole film except the held breath) ----------
for (const c of sc.chords) {
  let t1 = c.t1;
  if (c.t0 < ev.breath && t1 > ev.breath) t1 = ev.breath;
  const loud = c.t0 >= ev.drop ? 1.4 : c.t0 >= sc.S.forge[0] ? 1.1 : 1;
  for (const n of c.notes) { const s = I.strings(n, t1 - c.t0, { attack: 0.4, release: 0.8, bright: 0.6, seed: n }); str.addStereo(s.L, s.R, c.t0, 0.07 * loud); verb.addStereo(s.L, s.R, c.t0, 0.03); }
  const b = I.strings(c.bass, t1 - c.t0, { attack: 0.3, release: 0.8, bright: 0.4, seed: 3 });
  low.addStereo(b.L, b.R, c.t0, 0.16 * loud);
}

// ---------- heartbeat while the wolf grows ----------
for (let t = ev.grow; t < ev.chain1; t += BEAT * 2) drums.addMono(I.heartbeat(), t, 0.7);

// ---------- timpani: bar downbeats, rolls into each snap ----------
const kicks = [];
clock.eachStep(3, 15, 4, (t, b, s) => {
  if (inBreath(t)) return;
  if (s === 0) { drums.addMono(I.timpani(m('D2'), { decay: 0.9, seed: b }), t, 0.55); kicks.push(t); }
});
for (const hit of [ev.snap1, ev.snap2, ev.drop]) {
  const start = hit === ev.drop ? ev.breath - BEAT * 1.5 : hit - BEAT * 2;
  const end = hit === ev.drop ? ev.breath - 0.12 : hit - BEAT / 4; // roll stops an 8th early: the hit is clean
  for (let t = start, i = 0; t < end; t += BEAT / 6, i++) drums.addMono(I.timpani(m('A1'), { decay: 0.35, seed: 40 + i }), t, 0.12 + 0.25 * ((t - start) / (end - start)));
}
// chain rattles while the chains are on
for (const [a, b] of [[ev.chain1, ev.snap1], [ev.chain2, ev.snap2]]) for (let t = a; t < b - 0.3; t += BEAT) fx.addMono(I.glass(Math.round(t * 10), { size: 0.4 }), t, 0.1, 0.3);

// ---------- snaps: metal crack ----------
for (const t of [ev.snap1, ev.snap2]) {
  fx.addMono(I.thwack(), t, 0.7); fx.addMono(I.glass(Math.round(t * 3), { size: 1.2 }), t, 0.35);
  drums.addMono(I.crash(18), t, 0.35); fx.addMono(I.subBoom(1.4, 60, 30), t, 0.6);
  drums.addMono(I.timpani(m('D2'), { decay: 1.4, seed: 9 }), t, 0.8);
}

// ---------- the six impossible things: bells ----------
for (const n of sc.bells) {
  const f = 440 * Math.pow(2, (n.midi - 69) / 12);
  const b = I.bell(f, 0.5, 1.6, 2.0);
  bells.addMono(b, n.t, 0.35, (sc.bells.indexOf(n) % 2 ? 0.25 : -0.25)); verb.addMono(b, n.t, 0.25); dly.addMono(b, n.t, 0.12);
}
// Gleipnir appears: shimmer arpeggio
['D6', 'F6', 'A6', 'D7', 'F7', 'A7'].forEach((nm, i) => { const b = I.bell(440 * Math.pow(2, (m(nm) - 69) / 12), 0.35, 1.2, 2.0); const t = ev.gleipnir + i * BEAT / 4; bells.addMono(b, t, 0.18, i % 2 ? 0.4 : -0.4); verb.addMono(b, t, 0.2); dly.addMono(b, t, 0.1); });
fx.addMono(I.noiseSweep(1.5, 1200, 9000, { q: 1.4, pink: true }), ev.gleipnir - 0.2, 0.15);

// ---------- pledge: heartbeat speeds up, riser into the breath ----------
for (let t = ev.hand, k = 0; t < ev.breath - 0.2; k++) { drums.addMono(I.heartbeat(), t, 0.6 + k * 0.05); t += BEAT * Math.max(0.5, 1.2 - k * 0.15); }
fx.addMono(I.noiseSweep(ev.breath - ev.hand, 150, 5000, { q: 0.9, shape: (x) => x * x, pink: true }), ev.hand, 0.35);

// ---------- drop: jaws snap ----------
fx.addMono(I.subBoom(2.6, 75, 26), ev.drop, 0.9);
fx.addMono(I.thwack(), ev.drop, 0.8);
drums.addMono(I.timpani(m('D2'), { decay: 2.0, seed: 77 }), ev.drop, 1.0);
drums.addMono(I.crash(19), ev.drop, 0.45);
// horns: the Lorebound motif
const horn = [[ev.drop, 'D4', 3.6], [ev.drop, 'A3', 3.6], [ev.end, 'D4', 1.0], [ev.end + 1.0, 'F4', 0.5], [ev.end + 1.5, 'E4', 0.5], [ev.end + 2.0, 'D4', 3.5], [ev.end + 2.0, 'A3', 3.5]];
for (const [t, nm, d] of horn) {
  const a = I.brassNote(m(nm), d, { bright: 0.55, seed: 14 }), b = I.brassNote(m(nm) - 12, d, { bright: 0.4, seed: 31 });
  brass.addStereo(a.L, a.R, t, 0.22); brass.addStereo(b.L, b.R, t, 0.14); verb.addStereo(a.L, a.R, t, 0.12);
}
bells.addMono(I.bell(440 * Math.pow(2, (m('D6') - 69) / 12), 0.9, 1.4, 2.0), ev.end, 0.25);
verb.addMono(I.bell(440 * Math.pow(2, (m('D6') - 69) / 12), 0.9, 1.4, 2.0), ev.end, 0.3);
// title-card whooshes
for (const c of sc.cards) if (c.t > 1 && ![ev.snap1, ev.snap2, ev.drop].includes(c.t)) fx.addMono(I.noiseSweep(0.35, 600, 3000, { q: 1, pink: true }), c.t - 0.12, 0.12);

// ---------- mix ----------
MIX.sidechain([str, low], kicks.filter((t) => t >= ev.drop));
const stems = { drums, low, str, brass, bells, fx, verb: reverb(verb, { room: 0.9, damp: 0.4 }), dly: pingpong(dly, BEAT * 0.75, 0.35, 3000) };
const GAIN = { drums: 0.6, low: 1.0, str: 1.6, brass: 1.6, bells: 0.8, fx: 0.8, verb: 1, dly: 1 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 25);
MIX.gate(mix, ev.breath, ev.drop);
MIX.fadeOut(mix, DURATION - 1.8, DURATION);
const M = MIX.master(mix, parseFloat(process.env.DRIVE || '0.8'), undefined, { lufs: process.env.LUFS ? parseFloat(process.env.LUFS) : null });
MIX.writeWav(path.join(out, 'music.wav'), mix);
console.log(`wrote out/music.wav (${DURATION.toFixed(2)}s${M.lufs !== undefined ? `, ${M.lufs.toFixed(1)} LUFS` : ''})`);
