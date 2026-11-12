// LOREBOUND – „Der Bambus“ (Gleichnis). Gleichnisse in 30 Sekunden #2
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
    water: T(1, 2),
    neighbour: T(3),
    seasons: T(4, 2),
    reveal: T(6),
    roots: T(7),
    last: T(8),
    breath: T(8, 3),
    drop: T(9),
    height: T(11),
    end: T(12, 2),
    follow: T(13, 2),
  };

  // days: each tick = one watering, n = day counter shown
  const ticks = [{ t: 0, n: 1 }];
  const NT = 40;
  for (let k = 1; k <= NT; k++) ticks.push({ t: T(0, 2) + (k - 1) * (ev.reveal - 0.25 - T(0, 2)) / (NT - 1), n: Math.round(1 + 1459 * Math.pow(k / NT, 1.5)) });
  // metres after the drop: tk = drop + GROW * (k/20)^1.6  (fast start, slows down)
  const GROW = 6.6;
  const metres = [];
  for (let k = 1; k <= 20; k++) metres.push({ t: T(9) + GROW * Math.pow(k / 20, 1.6), n: k });

  const S = {
    hook: [0, T(1, 2)], water: [T(1, 2), T(6)], reveal: [T(6), T(8)], last: [T(8), ev.breath],
    breath: [ev.breath, ev.drop], drop: [ev.drop, ev.end], outro: [ev.end, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Dm: { notes: ['D3', 'F3', 'A3'], bass: 'D2' },
    Bb: { notes: ['D3', 'F3', 'Bb3'], bass: 'Bb1' },
    Gm: { notes: ['D3', 'G3', 'Bb3'], bass: 'G1' },
    A: { notes: ['C#3', 'E3', 'A3'], bass: 'A1' },
    F: { notes: ['C3', 'F3', 'A3'], bass: 'F1' },
    C: { notes: ['C3', 'E3', 'G3'], bass: 'C2' },
    Dsus: { notes: ['D3', 'G3', 'A3'], bass: 'D2' },
  }, [
    [0, 0, 4, 'Dm'], [1, 0, 4, 'Dm'], [2, 0, 4, 'Bb'], [3, 0, 4, 'Gm'], [4, 0, 4, 'Dm'], [5, 0, 4, 'A'],
    [6, 0, 4, 'Dm'], [7, 0, 4, 'F'], [8, 0, 3, 'A'],
    [9, 0, 4, 'Dm'], [10, 0, 4, 'Bb'], [11, 0, 4, 'F'], [12, 0, 4, 'C'], [13, 0, 4, 'Dsus'], [14, 0, 4, 'Dm'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: ev.water - 0.1, lines: ['JAHRELANG:', '*NICHTS*.'] },
    { t: ev.water, end: ev.neighbour - 0.1, lines: ['ER GOSS IHN.', '*JEDEN* TAG.'] },
    { t: ev.neighbour, end: ev.seasons - 0.1, lines: ['„DER IST TOT“,', 'SAGTE DER *NACHBAR*.'], small: true },
    { t: ev.seasons, end: ev.reveal - 0.1, lines: ['JEDES *JAHR*.'] },
    { t: ev.reveal, end: ev.roots - 0.1, lines: ['OBEN:', '*NICHTS*.'] },
    { t: ev.roots, end: ev.last - 0.1, lines: ['UNTEN: EIN NETZ', 'AUS *WURZELN*.'], small: true },
    { t: ev.last, end: ev.drop - 0.05, lines: ['UND DANN …'] },
    { t: ev.drop, end: ev.height - 0.1, lines: ['BIS ZU *1 METER*', 'AM TAG.'] },
    { t: ev.height, end: ev.end - 0.1, lines: ['IN ZWEI MONATEN:', '*ÜBER 20 METER*.'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['DU BIST NICHT', 'ZU LANGSAM.', '*DU WÄCHST NACH UNTEN.*'], small: true },
  ];

  const markers = {
    reveal: ev.reveal,
    roots: ev.roots,
    last: ev.last,
    height: ev.height,
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    end: ev.end,
    follow: ev.follow,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, ticks, metres, GROW, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
