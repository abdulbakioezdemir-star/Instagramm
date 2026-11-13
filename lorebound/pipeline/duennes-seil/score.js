// LOREBOUND – „Das dünne Seil“ (Gleichnis). Gleichnisse in 30 Sekunden #3
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
    back: T(1, 2),     // 3 s  flashback: tied as a calf
    pull: T(3),        // 6 s  pulled day and night
    stop: T(4, 2),     // 9 s  gave up
    years: T(6),       // 12 s years passed (grows)
    could: T(7, 2),    // 15 s could tear it out
    dry: T(8, 2),      // 17 s doesn't even try
    breath: T(9, 3),   // 19.5 s
    drop: T(10),       // 20 s
    end: T(12),        // 24 s
    follow: T(13, 2),  // 27 s
  };

  // tugs as a calf: each tug = a thud; n = attempt counter
  const tugs = [];
  const NT = 22;
  for (let k = 0; k < NT; k++) {
    const x = k / (NT - 1);
    tugs.push({ t: ev.back + 0.3 + (ev.stop - 0.5 - ev.back - 0.3) * Math.pow(x, 0.85), n: Math.round(1 + 999 * Math.pow(x, 2.2)) });
  }
  // the last tugs get weaker: strength 1 -> 0.25
  tugs.forEach((g, k) => { g.s = 1 - 0.75 * Math.pow(k / (NT - 1), 2); });
  // years: 1..20 while he grows
  const years = [];
  for (let k = 1; k <= 20; k++) years.push({ t: ev.years + 0.15 + (ev.could - 0.45 - ev.years) * Math.pow(k / 20, 0.9), n: k });

  const S = {
    hook: [0, ev.back], back: [ev.back, ev.stop], stop: [ev.stop, ev.years], years: [ev.years, ev.could],
    could: [ev.could, ev.breath], breath: [ev.breath, ev.drop], drop: [ev.drop, ev.end], outro: [ev.end, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Em: { notes: ['E3', 'G3', 'B3'], bass: 'E2' },
    C: { notes: ['E3', 'G3', 'C4'], bass: 'C2' },
    Am: { notes: ['E3', 'A3', 'C4'], bass: 'A1' },
    B: { notes: ['D#3', 'F#3', 'B3'], bass: 'B1' },
    G: { notes: ['D3', 'G3', 'B3'], bass: 'G1' },
    D: { notes: ['D3', 'F#3', 'A3'], bass: 'D2' },
    Esus: { notes: ['E3', 'A3', 'B3'], bass: 'E2' },
  }, [
    [0, 0, 4, 'Em'], [1, 0, 4, 'Em'], [2, 0, 4, 'C'], [3, 0, 4, 'Am'], [4, 0, 4, 'B'], [5, 0, 4, 'Em'],
    [6, 0, 4, 'C'], [7, 0, 4, 'Am'], [8, 0, 4, 'B'], [9, 0, 3, 'B'],
    [10, 0, 4, 'Em'], [11, 0, 4, 'C'], [12, 0, 4, 'G'], [13, 0, 4, 'D'], [14, 0, 4, 'Em'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: ev.back - 0.1, lines: ['4 TONNEN.', 'EIN *DÜNNES SEIL*.'] },
    { t: ev.back, end: ev.pull - 0.1, lines: ['ALS ER KLEIN WAR,', 'BANDEN SIE IHN *AN*.'], small: true },
    { t: ev.pull, end: ev.stop - 0.1, lines: ['ER ZOG.', '*TAG UND NACHT*.'] },
    { t: ev.stop, end: ev.years - 0.1, lines: ['IRGENDWANN', 'HÖRTE ER *AUF*.'] },
    { t: ev.years, end: ev.could - 0.1, lines: ['DANN WURDE', 'ER *GROSS*.'] },
    { t: ev.could, end: ev.dry - 0.1, lines: ['EIN SCHRITT –', 'UND DER PFLOCK *FLIEGT*.'], small: true },
    { t: ev.dry, end: ev.drop - 0.05, lines: ['ER VERSUCHT', 'ES NICHT MAL.'] },
    { t: ev.drop, end: ev.end - 0.1, lines: ['IHN HÄLT KEIN SEIL.', '*IHN HÄLT EINE', 'ERINNERUNG.*'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['WELCHES SEIL', 'HÄLT *DICH* NOCH?'] },
  ];

  const markers = {
    back: ev.back,
    stop: ev.stop,
    years: ev.years,
    could: ev.could,
    dry: ev.dry,
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    end: ev.end,
    follow: ev.follow,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, tugs, years, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
