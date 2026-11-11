// LOREBOUND – „Ein Tag länger als ein Jahr“ (Wissen: Venus). Wissen in 30 Sekunden #1
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
    name: T(1),
    zoom: T(2),
    year: T(7),        // 225 days: one orbit done
    still: T(8),
    breath: T(9, 3),
    drop: T(10),       // 243 days: one rotation done
    retro: T(11, 2),
    joke: T(12, 2),
    end: T(13, 2),
    follow: T(13, 2),
  };

  // day counter ticks: { t, n } – n = Earth days passed
  const ticks = [];
  for (let k = 0; k <= 20; k++) ticks.push({ t: ev.zoom + k * BEAT, n: Math.round(1 + 224 * Math.pow(k / 20, 1.25)) });
  for (let k = 1; k <= 14; k++) ticks.push({ t: ev.year + k * BEAT, n: 225 + Math.round((17 * k) / 14) });
  const finalTick = { t: ev.drop, n: 243 };
  const YEAR = 224.7, ROT = 243;

  const S = {
    hook: [0, T(2)], count: [T(2), T(7)], year: [T(7), ev.breath],
    breath: [ev.breath, ev.drop], drop: [ev.drop, ev.retro], outro: [ev.retro, DURATION],
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
    [0, 0, 4, 'Em'], [1, 0, 4, 'Em'], [2, 0, 4, 'C'], [3, 0, 4, 'Am'], [4, 0, 4, 'Em'], [5, 0, 4, 'C'], [6, 0, 4, 'B'],
    [7, 0, 4, 'G'], [8, 0, 4, 'Am'], [9, 0, 3, 'B'],
    [10, 0, 4, 'Em'], [11, 0, 4, 'C'], [12, 0, 4, 'D'], [13, 0, 4, 'Esus'], [14, 0, 4, 'Em'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: ev.name - 0.1, lines: ['HIER IST EIN TAG', 'LÄNGER ALS EIN *JAHR*.'] },
    { t: ev.name, end: ev.zoom - 0.1, lines: ['DAS IST *VENUS*.'] },
    { t: ev.zoom, end: T(4) - 0.1, lines: ['WIR ZÄHLEN', '*ERDTAGE*.'] },
    { t: T(4), end: ev.year - 0.1, lines: ['EINMAL UM DIE SONNE.', 'EINMAL UM SICH *SELBST*.'], small: true },
    { t: ev.year, end: ev.still - 0.1, lines: ['*225* TAGE:', 'EIN JAHR IST UM.'], small: true },
    { t: ev.still, end: ev.drop - 0.05, lines: ['UND DER TAG?', 'NOCH *NICHT* VORBEI.'], small: true },
    { t: ev.drop, end: ev.retro - 0.1, lines: ['*243* TAGE.', 'FÜR EINE DREHUNG.'] },
    { t: ev.retro, end: ev.joke - 0.1, lines: ['UND SIE DREHT SICH', '*RÜCKWÄRTS*.'], small: true },
    { t: ev.joke, end: ev.end - 0.1, lines: ['SILVESTER KOMMT DORT', 'VOR DEM *FEIERABEND*.'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['*ZEIT* IST', 'ANSICHTSSACHE.'] },
  ];

  const markers = {
    name: ev.name,
    zoom: ev.zoom,
    year: { t: ev.year, sync: 'a' },
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    retro: ev.retro,
    follow: ev.follow,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, ticks, finalTick, YEAR, ROT, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
