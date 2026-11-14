// LOREBOUND – „Das Schwert des Damokles“ (Mythen & Sagen). Mythen in 30 Sekunden #2
// Quelle der Sage: Cicero, Gespräche in Tusculum V 61–62. THE SCORE — single source of truth for music AND picture.
(function () {
  const node = typeof require !== 'undefined';
  const U = node ? require('./engine/util') : globalThis.U;
  const MU = node ? require('./engine/music') : globalThis.MUSIC;
  const { m, makeClock, makeChords } = MU;

  const FPS = 30;
  const FORMAT = U.pickFormat('9:16');
  const [W, H] = U.formatSize(FORMAT);
  const SAFE = U.safeArea(W, H);
  const WIDE = W / H > 1.2;
  const clock = makeClock({ bpm: 120, offset: 0 }); // 1 bar = 2 s
  const { T, BEAT } = clock;
  const DURATION = T(15); // 30 s

  const ev = {
    hook: 0,
    envy: T(1, 2),     // 3 s  Damokles envies the king
    swap: T(3),        // 6 s  "swap with me"
    sit: T(4, 2),      // 9 s  he sits: gold, wine, power
    up: T(6),          // 12 s he looks up -> sword revealed, pulse starts
    hair: T(7, 2),     // 15 s a single horse hair
    dry: T(8, 2),      // 17 s the feast went cold
    breath: T(9, 3),   // 19.5 s
    drop: T(10),       // 20 s
    end: T(12),        // 24 s
    follow: T(13, 2),  // 27 s
  };

  // pulse counter: heartbeats accelerate 72 -> 180 between up and breath
  const beats = [];
  {
    let t = ev.up + 0.15, k = 0;
    while (t < ev.breath - 0.12) {
      const x = (t - ev.up) / (ev.breath - ev.up);
      const bpm = 72 + 108 * Math.pow(x, 1.4);
      beats.push({ t, n: Math.round(bpm), k: k++ });
      t += 60 / bpm;
    }
  }
  // feast items appear when he sits (gold, wine, power)
  const feast = [ev.sit + 0.5, ev.sit + 1.0, ev.sit + 1.5];

  const S = {
    hook: [0, ev.envy], envy: [ev.envy, ev.sit], sit: [ev.sit, ev.up], up: [ev.up, ev.hair],
    hair: [ev.hair, ev.breath], breath: [ev.breath, ev.drop], drop: [ev.drop, ev.end], outro: [ev.end, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Dm: { notes: ['D3', 'F3', 'A3'], bass: 'D2' },
    Bb: { notes: ['D3', 'F3', 'Bb3'], bass: 'Bb1' },
    Gm: { notes: ['D3', 'G3', 'Bb3'], bass: 'G1' },
    A: { notes: ['C#3', 'E3', 'A3'], bass: 'A1' },
    F: { notes: ['C3', 'F3', 'A3'], bass: 'F1' },
    C: { notes: ['C3', 'E3', 'G3'], bass: 'C2' },
  }, [
    [0, 0, 4, 'Dm'], [1, 0, 4, 'Dm'], [2, 0, 4, 'Bb'], [3, 0, 4, 'F'], [4, 0, 4, 'Bb'], [5, 0, 4, 'C'],
    [6, 0, 4, 'Dm'], [7, 0, 4, 'Gm'], [8, 0, 4, 'A'], [9, 0, 3, 'A'],
    [10, 0, 4, 'Dm'], [11, 0, 4, 'Bb'], [12, 0, 4, 'Gm'], [13, 0, 4, 'A'], [14, 0, 4, 'Dm'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: ev.envy - 0.1, lines: ['EIN SCHWERT.', 'EIN EINZIGES *HAAR*.'] },
    { t: ev.envy, end: ev.swap - 0.1, lines: ['DAMOKLES BENEIDETE', 'SEINEN *KÖNIG*.'], small: true },
    { t: ev.swap, end: ev.sit - 0.1, lines: ['DER KÖNIG SAGTE:', '„*TAUSCH MIT MIR*.“'], small: true },
    { t: ev.sit, end: ev.up - 0.1, lines: ['GOLD. WEIN.', '*MACHT*.'] },
    { t: ev.up, end: ev.hair - 0.1, lines: ['DANN SAH ER', '*NACH OBEN*.'] },
    { t: ev.hair, end: ev.dry - 0.1, lines: ['EIN PFERDEHAAR.', '*SONST NICHTS*.'] },
    { t: ev.dry, end: ev.drop - 0.05, lines: ['DAS FESTMAHL', 'WURDE KALT.'] },
    { t: ev.drop, end: ev.end - 0.1, lines: ['WER DIE KRONE WILL,', '*BEKOMMT DAS', 'SCHWERT DAZU.*'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['BENEIDE KEINEN', '*THRON*.'] },
  ];

  const markers = {
    envy: ev.envy, swap: ev.swap, sit: ev.sit,
    up: { t: ev.up, sync: 'av' },
    hair: ev.hair, dry: ev.dry, breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    end: ev.end, follow: ev.follow,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, beats, feast, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
