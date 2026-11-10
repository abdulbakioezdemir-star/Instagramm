// LOREBOUND – „Der hundertste Schlag“ (Gleichnis). Gleichnisse in 30 Sekunden #1
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
    work: T(1),
    reveal: T(7),
    last: T(10),
    breath: T(10, 3),
    drop: T(11),
    end: T(12, 2),
    follow: T(13, 2),
  };

  // every hammer strike: { t, n } – n = the counter value shown after the strike
  const strikes = [{ t: 0, n: 1 }];
  for (let k = 0; k < 24; k++) strikes.push({ t: ev.work + k * BEAT, n: Math.round(2 + 94 * Math.pow(k / 23, 1.6)) });
  strikes.push({ t: T(10, 0), n: 97 }, { t: T(10, 1), n: 98 }, { t: T(10, 2), n: 99 });
  const finalStrike = { t: ev.drop, n: 100 };

  const S = {
    hook: [0, T(1)], work: [T(1), T(7)], reveal: [T(7), T(10)], last: [T(10), ev.breath],
    breath: [ev.breath, ev.drop], drop: [ev.drop, ev.end], outro: [ev.end, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Dm: { notes: ['D3', 'F3', 'A3'], bass: 'D2' },
    Bb: { notes: ['D3', 'F3', 'Bb3'], bass: 'Bb1' },
    Gm: { notes: ['D3', 'G3', 'Bb3'], bass: 'G1' },
    A: { notes: ['C#3', 'E3', 'A3'], bass: 'A1' },
    F: { notes: ['C3', 'F3', 'A3'], bass: 'F1' },
    Dsus: { notes: ['D3', 'G3', 'A3'], bass: 'D2' },
  }, [
    [0, 0, 4, 'Dm'], [1, 0, 4, 'Dm'], [2, 0, 4, 'Bb'], [3, 0, 4, 'Gm'], [4, 0, 4, 'Dm'], [5, 0, 4, 'Bb'], [6, 0, 4, 'A'],
    [7, 0, 4, 'Dm'], [8, 0, 4, 'F'], [9, 0, 4, 'Gm'], [10, 0, 3, 'A'],
    [11, 0, 4, 'Dm'], [12, 0, 4, 'Bb'], [13, 0, 4, 'Dsus'], [14, 0, 4, 'Dm'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: T(2) - 0.1, lines: ['99 SCHLÄGE.', 'KEIN *RISS*.'] },
    { t: T(2), end: T(3, 2) - 0.1, lines: ['DIE LEUTE', '*LACHTEN*.'] },
    { t: T(3, 2), end: T(5) - 0.1, lines: ['„GIB AUF.', 'DER STEIN IST *STÄRKER*.“'], small: true },
    { t: T(5), end: ev.reveal - 0.1, lines: ['ER NICKTE HÖFLICH.', 'UND SCHLUG *WEITER*.'], small: true },
    { t: ev.reveal, end: T(8, 2) - 0.1, lines: ['VON AUSSEN:', '*NICHTS*.'] },
    { t: T(8, 2), end: ev.last - 0.1, lines: ['DOCH INNEN WAR LÄNGST', '*ALLES* GERISSEN.'], small: true },
    { t: ev.last, end: ev.drop - 0.05, lines: ['UND DANN …'] },
    { t: ev.drop, end: ev.end - 0.1, lines: ['SCHLAG *100*.'] },
    { t: ev.end, end: DURATION + 1, lines: ['NICHT DER LETZTE SCHLAG', 'BRACH DEN STEIN.', '*SONDERN ALLE DAVOR.*'], small: true },
  ];

  const markers = {
    reveal: ev.reveal,
    last: ev.last,
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    end: ev.end,
    follow: ev.follow,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, strikes, finalStrike, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
