# Learnings – was funktioniert, was nicht

## 2026-11-09 (Start)
- Reel 16:13 (Tag 1): 390 Views, 302 Reach, 4 Likes, 2 Kommentare (1×A, 1×B), 0 Shares.
  Skip-Rate in den ersten 3 s: **54 %**, Ø Watch-Time 16,6 s.
- Reel 11:06 ohne Caption: 48 Views, Skip-Rate 60 %.
- **Ändern:** Hook in Sekunde 0–1 (Ahmeds Gesicht + Konflikt-Satz sofort, kein langsames Intro).
  Immer Caption mit Hook + A/B-Aufruf (Post ohne Caption lief deutlich schlechter).
- Besitzer mag: Stil + Stimme von Tag 1. Mag nicht: 3D-Klötzchen-Stil, andere KI-Stimmen.

## 2026-11-10 12:00 (Tag 2 · Teil 1)
- Stand Tag-1-Reel vor dem Post: 681 Views, 526 Reach, 14 Likes, 4 Kommentare (2×A, 2×B), 0 Shares.
  Skip-Rate **46,5 %** (vorher 54 %), Ø Watch-Time 20,1 s (vorher 16,6 s). Follower: 2.
- Abstimmung 2:2 → „Beides“. Teil 1 = 49 s, Hook ab 0,05 s (kalte Dusche + „KALT!!!“), Cliffhanger „ANNEHMEN?“ + „Teil 2 heute 18 Uhr“.
- **Problem:** Stimmen-Namen waren nirgends gespeichert → per Spektral-Abgleich mit tag02_beides_v2.mp4 rekonstruiert
  (Ahmed Florian +7 %, Lena Seraphina, Dönermann Conrad). Jetzt in state.json + AUTOMATION.md festgehalten.
- **Ändern:** 0 Shares bisher → in Teil 2 einen klar teilbaren Gag (Erdbeben-Zittern) und CTA „Schick das deinem Freund, der nie duscht“ testen.

## 2026-11-10 Analyse (Chat mit Besitzer, 17:30)
- Tag 1 ist das stärkste Reel aller Konten: 1.469 Views, 31 Likes, 8 Kommentare, Skip 43 %, Ø 21,6 s.
  Die A/B-Abstimmung zieht Kommentare – unbedingt bei jedem Teil 2/2 beibehalten.
- Tag 2 · Teil 1: 438 Views nach 5 h, Skip 36 % (bester Wert bisher) → der Cold Open mit Konflikt in Sekunde 0 funktioniert.
- A/B-Optionen immer zusätzlich groß als Text im Bild und in der Caption.

## 2026-11-10 18:00 (Tag 2 · Teil 2)
- Gepostet 18:00:05, media_id 18112940438615129 (31 s). Kommentar unter Teil 1 beantwortet.
- Zahlen 17:30 (Windsor, ohne force_refresh): Follower **6** (vorher 2).
  - Tag 1 (16:13, 09.11.): 1.469 Views, 1.113 Reach, Skip-Rate **43,2 %**, Ø Watch 21,6 s, 31 Likes, 2 Shares, 3 Saves, 8 Kommentare (inkl. 4 Antworten).
  - Tag 2 Teil 1 (12:00, 49 s): 446 Views in 5,5 h, 361 Reach, Skip-Rate **35,7 %** (bester Wert bisher), Ø Watch 16,0 s (≈33 % von 49 s), 7 Likes, 0 Shares, 0 Saves, 1 Kommentar.
  - Reel 09.11. 11:06 ohne Caption: 190 Views, Skip 51 %, Ø Watch 7,9 s.
- **Funktioniert:** Cold-Open-Hook (kalte Dusche + „KALT!!!“ ab 0,05 s) senkt die Skip-Rate deutlich (54 → 43 → 36 %).
  Zuschauer schlagen von selbst Lösungen vor („Gehe nicht ran, sag du bist auf der Arbeit“) → Story-Fragen ziehen Kommentare.
- **Funktioniert nicht:** Watch-Time bricht bei 49 s nach ~16 s ein; Teil 1 hat 0 Shares/Saves. Ohne A/B-Frage kaum Kommentare (1 vs. 8).
- **Geändert in Teil 2:** auf **31 s** gekürzt (Zeile a09 „Denk nach…“ gestrichen, Abspann 2,4 → 2,0 s) – Vorgabe BEFEHLE.md 28–32 s.
  Share-CTA in der Caption getestet („Schick das deinem Freund, der nie duscht“).
- **Für die nächsten Teile:** jeder Teil 28–32 s, max. 5 Sprechzeilen; auch Teil 1 mit einer Mini-Frage enden („Was würdest du tun?“), damit Kommentare kommen;
  Zuschauer-Vorschläge als Easter-Egg einbauen (z. B. Ahmed: „Einer sagt, ich soll sagen, ich bin auf der Arbeit… Bruder, ich wurde gefeuert!“).
- Pipeline-Fix: README-Setup-Schleife für `tag2/` schluckte stdin (ffmpeg) → nur 1 Zeile erzeugt, Import brach ab. Jetzt `ffmpeg -nostdin` + Lena-Stimme korrekt.
- **Für Tag 3 (BEFEHLE.md Befehl 3 beachten):** Start mitten in der Situation mit Peinlichkeits-Behauptung + Text ≤ 8 Wörter in s 0–2,
  3 Hook-Varianten schreiben, ≥ 3 Alltags-Lacher (Erwartung vs. Realität, z. B. Emre im Videocall vs. Ahmed im Hintergrund), stärkste Pointe am Ende.
  Tagestest Tag 3: Hook als Peinlichkeits-Behauptung statt Rückblick – mit Skip-Rate von Tag 2 Teil 2 vergleichen.

## 2026-11-11 12:00 (Tag 3 · Teil 1)
- Abstimmung Tag 2 Teil 2: **B 7 : A 0** (7 Kommentare – bisher meiste Stimmen). → „Meine Kamera ist kaputt“.
- Zahlen 11:15 (Windsor, ohne force_refresh):
  - Tag 2 Teil 1 (49 s): **1.962 Views** (jetzt bestes Reel), 1.520 Reach, Skip **26,1 %** (Rekord), Ø 20,4 s, 35 Likes, 1 Share, 2 Saves.
  - Tag 2 Teil 2 (31 s): 603 Views, 497 Reach, Skip 39,1 %, Ø 11,6 s (≈37 %), 13 Likes, 7 Kommentare, 0 Shares, 3 Saves.
  - Tag 1: 1.518 Views, Skip 43,1 %.
- Erkenntnis: Teil 1 (12 Uhr, Cold Open mit Action) bekommt viel mehr Reichweite als Teil 2 (18 Uhr, Rückblick-Start). Teil 2 startet mit „Vorhin bei Ahmed…“ → höhere Skip-Rate. Für Teil 2 künftig auch mit neuer Pointe in Sekunde 0 starten statt Rückblick-Satz.
- Hook-Varianten Tag 3 Teil 1: (1) „Ich hab Lena gesagt, meine Kamera ist kaputt. Sie war an.“ (2) „POV: Du lügst, deine Kamera ist kaputt – und sie ist an.“ (3) „7 von 7 sagen B. Nicht mal meine Mama vertraut mir so.“ → **(1) gewählt** (Peinlichkeits-Behauptung + Text „MEINE KAMERA WAR AN.“ ab 0 s, LIVE-Stempel bei Sekunde ~3).
- **Tagestest:** Hook als Peinlichkeits-Behauptung statt Rückblick/Action → mit Skip 26 % (Tag 2 T1) vergleichen.
- Gags (Alltag): Front-Kamera von unten/„HD-Nasenlöcher“ (Erwartung vs. Realität), „Ihr wollt mein Gesicht also genauso wenig sehen wie ich“, Daumen hoch „Alles schwarz. Voll schade.“ während man ihn sieht.
- Länge 31,7 s (Vorgabe 28–32 s). Caption endet mit Frage „Was würdest DU jetzt sagen?“ (Test: Kommentare unter Teil 1).
- Pipeline: neue Vorlage `pipeline/tag03/` (tag03.py mit Szenen cold/vote/call/nose/poll); Teil 2 schon fertig geschrieben + getestet (30,4 s). Whisper-Prüfung: Transkript korrekt, nur „Ahmed?“ von Lena wird als „Ok Matt“ erkannt (klingt aber ok).
- 4 Abstimmungs-Kommentare als Ahmed beantwortet, keine Beleidigungen/Spam.
