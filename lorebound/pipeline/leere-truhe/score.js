// LOREBOUND – „Die leere Truhe“ (Fantasy). Fantasy in 30 Sekunden #1
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
    knights: T(1, 2),   // 3.0
    ask: T(3, 2),       // 7.0
    child: T(5),        // 10.0
    may: T(6),          // 12.0
    last: T(7),         // 14.0
    breath: T(7, 3),    // 15.5
    drop: T(8),         // 16.0
    why: T(9),          // 18.0
    village: T(10),     // 20.0
    pass: T(11),        // 22.0
    end: T(12, 2),      // 25.0
    follow: T(13, 2),   // 27.0
  };

  // three knights charge from the left, each met by fire
  const fires = [{ t: 4.0 }, { t: 5.0 }, { t: 6.0 }];

  // years: each tick = a soft coin chime, n = year counter
  const ticks = [{ t: 0, n: 1 }];
  const NT = 36;
  for (let k = 1; k <= NT; k++) ticks.push({ t: 0.5 + (k - 1) * (ev.last - 0.5) / (NT - 1), n: Math.round(1 + 999 * Math.pow(k / NT, 1.4)) });
  // child's footsteps
  const steps = [];
  for (let t = ev.child + 0.25; t < ev.last - 0.2; t += BEAT) steps.push(t);

  const S = {
    hook: [0, ev.knights], knights: [ev.knights, ev.ask], ask: [ev.ask, ev.child], child: [ev.child, ev.last],
    last: [ev.last, ev.breath], breath: [ev.breath, ev.drop], drop: [ev.drop, ev.village], village: [ev.village, ev.end], outro: [ev.end, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Dm: { notes: ['D3', 'F3', 'A3'], bass: 'D2' },
    Bb: { notes: ['D3', 'F3', 'Bb3'], bass: 'Bb1' },
    Gm: { notes: ['D3', 'G3', 'Bb3'], bass: 'G1' },
    A: { notes: ['C#3', 'E3', 'A3'], bass: 'A1' },
    F: { notes: ['C3', 'F3', 'A3'], bass: 'F1' },
    C: { notes: ['C3', 'E3', 'G3'], bass: 'C2' },
    D: { notes: ['D3', 'F#3', 'A3'], bass: 'D2' },
  }, [
    [0, 0, 4, 'Dm'], [1, 0, 4, 'Dm'], [2, 0, 4, 'Bb'], [3, 0, 4, 'Gm'], [4, 0, 4, 'Dm'], [5, 0, 4, 'F'],
    [6, 0, 4, 'Gm'], [7, 0, 3, 'A'],
    [8, 0, 4, 'Dm'], [9, 0, 4, 'Bb'], [10, 0, 4, 'F'], [11, 0, 4, 'C'], [12, 0, 4, 'Bb'], [13, 0, 4, 'D'], [14, 0, 4, 'D'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: ev.knights - 0.1, lines: ['1.000 JAHRE.', 'EINE *LEERE* TRUHE.'] },
    { t: ev.knights, end: ev.ask - 0.1, lines: ['RITTER KAMEN.', 'RITTER *RANNTEN*.'] },
    { t: ev.ask, end: ev.child - 0.1, lines: ['ALLE FRAGTEN:', 'WAS IST *DRIN*?'] },
    { t: ev.child, end: ev.may - 0.1, lines: ['DANN KAM', 'EIN *KIND*.'] },
    { t: ev.may, end: ev.last - 0.1, lines: ['„DARF ICH', '*MAL* GUCKEN?“'] },
    { t: ev.last, end: ev.drop - 0.05, lines: ['DER DRACHE', '*NICKTE*.'] },
    { t: ev.drop, end: ev.why - 0.1, lines: ['*NICHTS.*'] },
    { t: ev.why, end: ev.village - 0.1, lines: ['„WARUM?“,', 'FRAGTE ES.'] },
    { t: ev.village, end: ev.pass - 0.1, lines: ['HINTER IHM', 'SCHLIEF EIN *DORF*.'], small: true },
    { t: ev.pass, end: ev.end - 0.1, lines: ['WER DEN SCHATZ WOLLTE,', 'KAM ZU *IHM*.', 'NIE ZUM DORF.'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['ER BEWACHTE', 'NICHTS.', '*UND SCHÜTZTE ALLES.*'], small: true },
  ];

  const markers = {
    knights: ev.knights,
    child: ev.child,
    last: ev.last,
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    village: ev.village,
    end: ev.end,
    follow: ev.follow,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, fires, ticks, steps, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
