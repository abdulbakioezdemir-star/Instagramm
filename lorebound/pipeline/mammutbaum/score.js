// LOREBOUND – „Der Riese, der auf Feuer wartet“ (Wissen im Gleichnis-Bauplan). Wissen in 30 Sekunden #2
// THE SCORE — single source of truth for music AND picture.
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
    giant: T(1, 1),    // 2.5 s  up to 3,000 years old
    closed: T(2, 3),   // 5.5 s  its cones stay shut
    dry: T(4, 2),      // 9 s    summer. winter. nothing.
    fire: T(6, 1),     // 12.5 s then the fire comes
    burn: T(7, 3),     // 15.5 s everything burns. he stays.
    breath: T(8, 3),   // 17.5 s
    drop: T(9),        // 18 s   the heat opens the cones
    seeds: T(10, 2),   // 21 s   seeds like oat flakes
    lesson: T(12),     // 24 s
    end: T(13, 2),     // 27 s
  };

  // years 1..20 with the cone shut
  const years = [];
  for (let k = 1; k <= 20; k++) {
    const x = (k - 1) / 19;
    years.push({ t: ev.closed + 0.5 + (ev.fire - 0.5 - ev.closed - 0.5) * Math.pow(x, 0.8), n: k });
  }

  const S = {
    hook: [0, ev.giant], giant: [ev.giant, ev.closed], closed: [ev.closed, ev.fire], fire: [ev.fire, ev.breath],
    breath: [ev.breath, ev.drop], drop: [ev.drop, ev.lesson], outro: [ev.lesson, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Em: { notes: ['E3', 'G3', 'B3'], bass: 'E2' },
    C: { notes: ['E3', 'G3', 'C4'], bass: 'C2' },
    Am: { notes: ['E3', 'A3', 'C4'], bass: 'A1' },
    B: { notes: ['D#3', 'F#3', 'B3'], bass: 'B1' },
    G: { notes: ['D3', 'G3', 'B3'], bass: 'G1' },
    D: { notes: ['D3', 'F#3', 'A3'], bass: 'D2' },
    E: { notes: ['E3', 'G#3', 'B3'], bass: 'E2' },
  }, [
    [0, 0, 4, 'Em'], [1, 0, 4, 'Em'], [2, 0, 4, 'C'], [3, 0, 4, 'Am'], [4, 0, 4, 'Em'],
    [5, 0, 4, 'C'], [6, 0, 4, 'Am'], [7, 0, 4, 'B'], [8, 0, 4, 'B'],
    [9, 0, 4, 'Em'], [10, 0, 4, 'C'], [11, 0, 4, 'G'], [12, 0, 4, 'D'], [13, 0, 4, 'C'], [14, 0, 4, 'E'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: ev.giant - 0.1, lines: ['DIESER RIESE', '*WARTET AUF FEUER*.'] },
    { t: ev.giant, end: ev.closed - 0.1, lines: ['MAMMUTBAUM.', 'BIS *3.000 JAHRE* ALT.'] },
    { t: ev.closed, end: ev.dry - 0.1, lines: ['SEINE ZAPFEN', 'BLEIBEN *ZU*.'] },
    { t: ev.dry, end: ev.fire - 0.1, lines: ['SOMMER. WINTER.', '*NICHTS*.'] },
    { t: ev.fire, end: ev.burn - 0.1, lines: ['DANN KOMMT', 'DAS *FEUER*.'] },
    { t: ev.burn, end: ev.drop - 0.15, lines: ['ALLES BRENNT.', 'ER *BLEIBT STEHEN*.'] },
    { t: ev.drop, end: ev.seeds - 0.1, lines: ['DIE HITZE', '*ÖFFNET* DIE ZAPFEN.'] },
    { t: ev.seeds, end: ev.lesson - 0.1, lines: ['SAMEN, KLEIN WIE', '*HAFERFLOCKEN*.'] },
    { t: ev.lesson, end: ev.end - 0.1, lines: ['MANCHES IN DIR', 'ÖFFNET SICH', '*ERST IM FEUER.*'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['DEIN FEUER IST', '*NICHT DEIN ENDE*.'] },
  ];

  const markers = {
    giant: ev.giant,
    closed: ev.closed,
    dry: ev.dry,
    fire: ev.fire,
    burn: ev.burn,
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    seeds: ev.seeds,
    lesson: ev.lesson,
    end: ev.end,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, years, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
