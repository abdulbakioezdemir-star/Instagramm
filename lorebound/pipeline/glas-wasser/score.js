// LOREBOUND – „Das Glas Wasser“ (Gleichnis). Gleichnisse in 30 Sekunden #4
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
    ask: T(1, 2),      // 3 s   how heavy is this glass?
    minute: T(3),      // 6 s   one minute: no problem
    hour: T(5),        // 10 s  one hour: the arm burns
    day: T(7),         // 14 s  one day: the arm gives up
    dry: T(8, 2),      // 17 s  the glass never got heavier
    breath: T(9, 3),   // 19.5 s
    drop: T(10),       // 20 s  set it down
    end: T(12),        // 24 s
    follow: T(13, 2),  // 27 s
  };

  // minutes 1..60 (calm), hours 1..24 (strain)
  const minutes = [];
  const NM = 14;
  for (let k = 0; k < NM; k++) {
    const x = k / (NM - 1);
    minutes.push({ t: ev.minute + 0.2 + (ev.hour - 0.45 - ev.minute - 0.2) * x, n: Math.max(1, Math.round(60 * Math.pow(x, 1.6))) });
  }
  const hours = [];
  for (let k = 1; k <= 24; k++) {
    const x = (k - 1) / 23;
    hours.push({ t: ev.hour + 0.15 + (ev.dry - 0.4 - ev.hour - 0.15) * Math.pow(x, 0.85), n: k });
  }

  const S = {
    hook: [0, ev.ask], ask: [ev.ask, ev.minute], minute: [ev.minute, ev.hour], hour: [ev.hour, ev.day],
    day: [ev.day, ev.dry], dry: [ev.dry, ev.breath], breath: [ev.breath, ev.drop], drop: [ev.drop, ev.end], outro: [ev.end, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Dm: { notes: ['D3', 'F3', 'A3'], bass: 'D2' },
    Bb: { notes: ['D3', 'F3', 'A#3'], bass: 'A#1' },
    Gm: { notes: ['D3', 'G3', 'A#3'], bass: 'G1' },
    A: { notes: ['C#3', 'E3', 'A3'], bass: 'A1' },
    F: { notes: ['C3', 'F3', 'A3'], bass: 'F1' },
    C: { notes: ['C3', 'E3', 'G3'], bass: 'C2' },
    D: { notes: ['D3', 'F#3', 'A3'], bass: 'D2' },
  }, [
    [0, 0, 4, 'Dm'], [1, 0, 4, 'Dm'], [2, 0, 4, 'Bb'], [3, 0, 4, 'F'], [4, 0, 4, 'C'],
    [5, 0, 4, 'Gm'], [6, 0, 4, 'Bb'], [7, 0, 4, 'Gm'], [8, 0, 4, 'A'], [9, 0, 3, 'A'],
    [10, 0, 4, 'Dm'], [11, 0, 4, 'Bb'], [12, 0, 4, 'F'], [13, 0, 4, 'C'], [14, 0, 4, 'D'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: ev.ask - 0.1, lines: ['250 GRAMM.', '*ZU SCHWER*.'] },
    { t: ev.ask, end: ev.minute - 0.1, lines: ['WIE SCHWER IST', '*DIESES GLAS*?'] },
    { t: ev.minute, end: ev.hour - 0.1, lines: ['EINE MINUTE:', '*KEIN PROBLEM*.'] },
    { t: ev.hour, end: ev.day - 0.1, lines: ['EINE STUNDE:', 'DER ARM *BRENNT*.'] },
    { t: ev.day, end: ev.dry - 0.1, lines: ['EINEN TAG:', 'DER ARM *GIBT AUF*.'] },
    { t: ev.dry, end: ev.drop - 0.05, lines: ['DAS GLAS WURDE', 'NIE SCHWERER.'] },
    { t: ev.drop, end: ev.end - 0.1, lines: ['NICHT DAS GEWICHT', 'BRICHT DICH.', '*SONDERN DIE DAUER.*'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['STELL ES', '*HEUTE ABEND* AB.'] },
  ];

  const markers = {
    ask: ev.ask,
    minute: ev.minute,
    hour: ev.hour,
    day: ev.day,
    dry: ev.dry,
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    end: ev.end,
    follow: ev.follow,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, minutes, hours, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
