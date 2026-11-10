// LOREBOUND – „Die Fessel, die es nicht gibt“ (Fenrir & Gleipnir, nordische Mythologie)
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
  const DURATION = T(19); // 38 s

  const ev = {
    hook: 0,
    grow: T(1),
    chain1: T(3), snap1: T(4),
    chain2: T(4, 2), snap2: T(5, 2),
    dwarves: T(6, 2),
    items: [T(7), T(7, 2), T(8), T(8, 2), T(9), T(9, 2)],
    gleipnir: T(10, 2),
    pledge: T(12),
    hand: T(13),
    breath: T(14, 3),
    drop: T(15),
    end: T(16, 2),
  };

  const S = {
    hook: [0, T(1)], grow: [T(1), T(3)], chains: [T(3), T(6, 2)], forge: [T(6, 2), T(10, 2)],
    gleipnir: [T(10, 2), T(12)], pledge: [T(12), ev.breath], breath: [ev.breath, ev.drop], drop: [ev.drop, ev.end], outro: [ev.end, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Dm: { notes: ['D3', 'F3', 'A3'], bass: 'D2' },
    Bb: { notes: ['D3', 'F3', 'Bb3'], bass: 'Bb1' },
    Gm: { notes: ['D3', 'G3', 'Bb3'], bass: 'G1' },
    A: { notes: ['C#3', 'E3', 'A3'], bass: 'A1' },
    F: { notes: ['C3', 'F3', 'A3'], bass: 'F1' },
    Dsus: { notes: ['D3', 'G3', 'A3'], bass: 'D2' },
  }, [
    [0, 0, 4, 'Dm'], [1, 0, 4, 'Dm'], [2, 0, 4, 'Bb'], [3, 0, 4, 'Dm'], [4, 0, 4, 'Bb'], [5, 0, 4, 'A'],
    [6, 0, 4, 'Dm'], [7, 0, 4, 'F'], [8, 0, 4, 'Bb'], [9, 0, 4, 'Gm'], [10, 0, 4, 'A'], [11, 0, 4, 'Dm'],
    [12, 0, 4, 'Bb'], [13, 0, 4, 'Gm'], [14, 0, 3, 'A'],
    [15, 0, 4, 'Dm'], [16, 0, 4, 'Bb'], [17, 0, 4, 'Dsus'], [18, 0, 4, 'Dm'],
  ]);

  // one bell note per impossible ingredient (rising, D minor)
  const bells = ev.items.map((t, i) => ({ t, midi: m(['A5', 'C6', 'D6', 'E6', 'F6', 'A6'][i]) }));

  const items = ['DER SCHRITT EINER KATZE', 'DER BART EINER FRAU', 'DIE WURZELN EINES BERGES', 'DIE SEHNEN EINES BÄREN', 'DER ATEM EINES FISCHES', 'DER SPEICHEL EINES VOGELS'];

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: T(3) - 0.1, lines: ['DIE GÖTTER HATTEN', '*ANGST* VOR', 'EINEM WOLF.'] },
    { t: ev.chain1 + 0.05, end: ev.snap1 - 0.05, lines: ['SIE LEGTEN IHN', 'IN *KETTEN*.'] },
    { t: ev.snap1, end: ev.chain2 + 1.6, lines: ['ER *ZERRISS* SIE.'] },
    { t: ev.snap2, end: ev.dwarves - 0.05, lines: ['AUCH DIE ZWEITE.'] },
    { t: ev.dwarves, end: ev.gleipnir - 0.05, lines: ['DA SCHMIEDETEN ZWERGE', 'EINE FESSEL AUS DINGEN,', 'DIE ES *NICHT GIBT*:'], small: true },
    { t: ev.gleipnir, end: T(12) - 0.05, lines: ['*GLEIPNIR*.', 'DÜNN WIE SEIDE.'] },
    { t: ev.pledge, end: ev.hand - 0.05, lines: ['DER WOLF ROCH DIE LIST.', 'ER WOLLTE EIN *PFAND*.'], small: true },
    { t: ev.hand, end: ev.drop - 0.05, lines: ['EINE HAND', 'IN SEINEM *MAUL*.'] },
    { t: ev.drop, end: ev.end - 0.05, lines: ['DIE FESSEL HIELT.', 'TYR VERLOR SEINE *HAND*.'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['DIE STÄRKSTE FESSEL', 'IST DIE, DIE MAN', '*NICHT SIEHT*.'] },
  ];

  const markers = {
    snap1: { t: ev.snap1, sync: 'av' },
    snap2: { t: ev.snap2, sync: 'av' },
    gleipnir: ev.gleipnir,
    hand: ev.hand,
    breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    end: ev.end,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, bells, items, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
