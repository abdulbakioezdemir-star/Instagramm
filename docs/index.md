# Instagramm (Valmora · Lorebound · Ahmed Glowup) -- documentation

Automatisch betriebene Instagram-Serien (Valmora-Nation, Lorebound, Ahmed Glowup): Reels per Python rendern, über Windsor.ai posten.

This directory is a wiki maintained by an LLM: linked markdown pages, nothing outside the
repository. The rules are in [`CLAUDE.md`](CLAUDE.md).

## Start here

Für einen neuen Valmora-Tag: `nation/NATION.md` (Regeln) → `nation/state.json` (Spielstand) → [[valmora-reel-pipeline]] (Rendern + Posten) → `nation/LEARNINGS.md`.

Dieses Wiki wächst beim Arbeiten mit; Lorebound und Ahmed Glowup haben noch keine eigene Seite (siehe `AUTOMATION.md`).

---

## concepts

_noch keine Seiten_

## architecture

_noch keine Seiten_

## subsystems

- [[valmora-reel-pipeline]] -- Valmora-Reels: Stimme, Timeline, Audio, Bilder, Vorschau, Posten; mit Fallen

## decisions

_noch keine Seiten_

## reference

_noch keine Seiten_

## operations

_noch keine Seiten_

## history

_noch keine Seiten_

---

## Using this wiki

```
/docs-sync     right after a deploy or release -- reads only what changed since verified_at
/docs-lint     integrity check (orphans, broken links, broken sources, stale, unverified)
/docs-query    ask the docs. If it is not there, the answer says so
/docs-status   commits not yet reflected, stale pages, recent work
```

Every page carries `verified_at`, the commit it was checked against. Change code, run
`/docs-sync`.
