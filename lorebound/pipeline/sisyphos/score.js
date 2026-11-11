// LOREBOUND – „Sisyphos – Der Mann, der den Tod betrog“. Mythen in 30 Sekunden #1
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
    chain: T(1),
    frozen: T(2),
    escape: T(3),
    punish: T(4),
    last: T(10),
    breath: T(10, 3),
    drop: T(11),
    end: T(12, 2),
    follow: T(13, 2),
  };

  // push cycles on the mountain (time-lapse: they get faster). lengths in beats.
  const lens = [6, 5, 4, 3, 2, 2, 1, 1];
  const counts = [1, 2, 3, 12, 140, 900, 4000, 9999];
  const cycles = [];
  let t = ev.punish;
  lens.forEach((b, k) => {
    const t0 = t, t1 = t + b * BEAT;
    const tp = t0 + (t1 - t0) * (b >= 4 ? 0.78 : 0.66);
    cycles.push({ t0, tp, t1, n: counts[k] });
    t = t1;
  });
  const rolls = cycles.map((c) => ({ t: c.tp, n: c.n })); // the boulder slips back -> counter

  const S = {
    hook: [0, T(1)], chain: [T(1), T(2)], frozen: [T(2), T(3)], escape: [T(3), T(4)],
    punish: [T(4), T(10)], last: [T(10), ev.breath], breath: [ev.breath, ev.drop], drop: [ev.drop, ev.end], outro: [ev.end, DURATION],
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
    [0, 0, 4, 'Em'], [1, 0, 4, 'C'], [2, 0, 4, 'Am'], [3, 0, 4, 'B'],
    [4, 0, 4, 'Em'], [5, 0, 4, 'C'], [6, 0, 4, 'Am'], [7, 0, 4, 'B'], [8, 0, 4, 'Em'], [9, 0, 4, 'C'], [10, 0, 3, 'B'],
    [11, 0, 4, 'G'], [12, 0, 4, 'D'], [13, 0, 4, 'C'], [14, 0, 4, 'E'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: T(1) - 0.1, lines: ['ER BETROG', 'DEN *TOD*.'] },
    { t: T(1), end: T(2) - 0.1, lines: ['KÖNIG SISYPHOS LEGTE', 'DEN TOD IN *KETTEN*.'], small: true },
    { t: T(2), end: T(3) - 0.1, lines: ['NIEMAND', 'STARB *MEHR*.'] },
    { t: T(3), end: T(4) - 0.1, lines: ['DANN ENTKAM ER', 'SOGAR DER *UNTERWELT*.'], small: true },
    { t: T(4), end: T(5, 2) - 0.1, lines: ['DIE STRAFE:', 'EIN FELS. *FÜR IMMER*.'], small: true },
    { t: T(5, 2), end: T(7) - 0.1, lines: ['FAST OBEN?', 'IMMER NUR *FAST*.'] },
    { t: T(7), end: T(8, 2) - 0.1, lines: ['DIE GÖTTER WOLLTEN', 'IHN *BRECHEN*.'], small: true },
    { t: T(8, 2), end: ev.last - 0.1, lines: ['SINNLOSE ARBEIT.', '*OHNE ENDE*.'], small: true },
    { t: ev.last, end: ev.drop - 0.05, lines: ['UND DOCH …'] },
    { t: ev.drop, end: ev.end - 0.1, lines: ['DER FELS ROLLT.', 'ER *LÄCHELT*.'] },
    { t: ev.end, end: DURATION + 1, lines: ['„MAN MUSS SICH SISYPHOS', 'ALS *GLÜCKLICHEN* MENSCHEN', 'VORSTELLEN.“'], small: true, by: '— ALBERT CAMUS' },
  ];

  const markers = {
    chain: ev.chain,
    punish: ev.punish,
    last: ev.last,
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    end: ev.end,
    follow: ev.follow,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, cycles, rolls, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
