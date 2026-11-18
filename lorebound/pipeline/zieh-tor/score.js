// LOREBOUND – „Das Tor, das niemand öffnete“ (Fantasy-Gleichnis). Fantasy in 30 Sekunden #2
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
    gate: T(1, 1),     // 2.5 s  300 years shut
    charge: T(2, 2),   // 5 s    they struck, they pushed
    magic: T(4, 2),    // 9 s    rams, spells, dragon fire
    still: T(6),       // 12 s   it did not move
    child: T(7),       // 14 s   then came a child
    read: T(8),        // 16 s   it read what was written
    breath: T(8, 3),   // 17.5 s
    drop: T(9),        // 18 s   PULL
    dry: T(10, 2),     // 21 s   1,000 knights had pushed
    lesson: T(12),     // 24 s
    end: T(13, 2),     // 27 s
  };

  // the knights: 22 charges, faster and faster, count runs 1 -> 1,000
  const hits = [];
  const NH = 22;
  for (let k = 0; k < NH; k++) {
    const x = k / (NH - 1);
    const t = ev.charge + 0.35 + (ev.still - 0.25 - ev.charge - 0.35) * Math.pow(x, 0.75);
    const n = k === 0 ? 1 : Math.round(1000 * Math.pow(x, 2.3)) || k + 1;
    hits.push({ t, n: Math.max(n, k + 1), side: k % 2 ? 1 : -1, k });
  }
  hits[NH - 1].n = 1000;
  const spells = [{ t: ev.magic + 1.0, kind: 'zap' }, { t: ev.magic + 2.0, kind: 'fire' }];
  const steps = [];
  for (let k = 0; k < 8; k++) steps.push(ev.child + 0.25 + k * 0.25 * 1.0);

  const S = {
    hook: [0, ev.gate], gate: [ev.gate, ev.charge], charge: [ev.charge, ev.still], still: [ev.still, ev.child],
    child: [ev.child, ev.breath], breath: [ev.breath, ev.drop], drop: [ev.drop, ev.lesson], outro: [ev.lesson, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Dm: { notes: ['D3', 'F3', 'A3'], bass: 'D2' },
    Bb: { notes: ['D3', 'F3', 'Bb3'], bass: 'Bb1' },
    F: { notes: ['C3', 'F3', 'A3'], bass: 'F1' },
    C: { notes: ['C3', 'E3', 'G3'], bass: 'C2' },
    Gm: { notes: ['D3', 'G3', 'Bb3'], bass: 'G1' },
    A: { notes: ['C#3', 'E3', 'A3'], bass: 'A1' },
    D: { notes: ['D3', 'F#3', 'A3'], bass: 'D2' },
  }, [
    [0, 0, 4, 'Dm'], [1, 0, 4, 'Dm'], [2, 0, 4, 'Bb'], [3, 0, 4, 'Gm'], [4, 0, 4, 'Dm'],
    [5, 0, 4, 'Bb'], [6, 0, 4, 'A'], [7, 0, 4, 'Dm'], [8, 0, 4, 'A'],
    [9, 0, 4, 'D'], [10, 0, 4, 'Bb'], [11, 0, 4, 'F'], [12, 0, 4, 'C'], [13, 0, 4, 'Bb'], [14, 0, 4, 'D'],
  ]);

  // title cards; *word* = gold accent
  const cards = [
    { t: ev.hook, end: ev.gate - 0.1, lines: ['1.000 RITTER.', '*EIN KIND.*'] },
    { t: ev.gate, end: ev.charge - 0.1, lines: ['DIESES TOR WAR', '*300 JAHRE* ZU.'] },
    { t: ev.charge, end: ev.magic - 0.1, lines: ['SIE SCHLUGEN.', 'SIE *DRÜCKTEN*.'] },
    { t: ev.magic, end: ev.still - 0.1, lines: ['RAMMEN. ZAUBER.', '*DRACHENFEUER*.'] },
    { t: ev.still, end: ev.child - 0.1, lines: ['DAS TOR RÜHRTE', 'SICH *NICHT*.'] },
    { t: ev.child, end: ev.read - 0.1, lines: ['DANN KAM', 'EIN *KIND*.'] },
    { t: ev.read, end: ev.drop - 0.15, lines: ['ES LAS, WAS', '*DRANSTAND*.'] },
    { t: ev.drop, end: ev.dry - 0.1, lines: ['*ZIEHEN.*'], big: true },
    { t: ev.dry, end: ev.lesson - 0.1, lines: ['1.000 RITTER', 'HATTEN *GEDRÜCKT*.'] },
    { t: ev.lesson, end: ev.end - 0.1, lines: ['NICHT JEDE TÜR BRAUCHT', 'MEHR KRAFT. MANCHE NUR', '*EINEN ZWEITEN BLICK.*'], small: true },
    { t: ev.end, end: DURATION + 1, lines: ['LIES, WAS', '*DRANSTEHT*.'] },
  ];

  const markers = {
    gate: ev.gate, charge: ev.charge, magic: ev.magic, still: ev.still, child: ev.child,
    read: ev.read, breath: ev.breath,
    drop: { t: ev.drop, sync: 'av' },
    dry: ev.dry, lesson: ev.lesson, end: ev.end,
  };

  const SCORE = { FPS, FORMAT, W, H, SAFE, WIDE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, hits, spells, steps, cards, markers };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
