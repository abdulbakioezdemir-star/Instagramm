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

## 2026-11-11 18:00 (Tag 3 · Teil 2)
- Zahlen 17:25 (Windsor, ohne force_refresh) – Follower **13** (gestern 6):
  | Reel | Views | Reach | Skip | Ø Watch | Likes | Komm. | Shares | Saves |
  |---|---|---|---|---|---|---|---|---|
  | Tag 1 (09.11., 49 s) | 1.549 | 1.181 | 43,0 % | 21,5 s | 31 | 8 | 2 | 3 |
  | Tag 2 T1 (12:00, 49 s) | 2.205 | 1.746 | 27,6 % | 20,1 s | 38 | 2 | 1 | 2 |
  | Tag 2 T2 (18:00, 31 s) | 1.165 | 925 | 37,9 % | 12,0 s | 20 | 13 | 0 | 3 |
  | **Tag 3 T1 (12:00, 31,7 s)** | **2.456 in 6 h** | 1.850 | **26,0 %** | **20,1 s (≈63 %)** | 30 | 2 | **3** | 0 |
- **Tagestest Tag 3 T1 (Peinlichkeits-Hook „Ich hab Lena gesagt, meine Kamera ist kaputt. Sie war an.“): Gewinner.**
  Bestes Reel aller Zeiten nach 6 h, Skip 26 % (= Rekord), Ø Watch 20 s bei nur 31,7 s Länge → Retention fast verdoppelt ggü. 49 s-Folgen. Meiste Shares (3).
  → Peinlichkeits-Behauptung als erster Satz + Text ≤ 8 Wörter ist ab jetzt Standard-Hook. 28–32 s bestätigt.
- **Teil 1 vs. Teil 2:** Teil 1 (12 Uhr) holt ~2× Views, Teil 2 (18 Uhr) holt die Kommentare (13 vs. 2) durch die A/B-Frage. Teil 2 hat höhere Skip (38 %) und nur Ø 12 s.
- **Geändert in Teil 2 (Test heute):** Einblendung „VORHIN BEI AHMED…“ ersetzt durch Hook-Text „SIE SAH NUR MEINE NASENLÖCHER.“ (0–2,4 s); erster Satz bleibt Peinlichkeits-Behauptung. Morgen Skip mit Tag 2 T2 (37,9 %) vergleichen.
- Hook-Varianten Teil 2: (1) „Lena hat mich gesehen. Nicht Emre. Nur meine Nasenlöcher.“ (2) „Ich hab Lena gesagt, meine Nasenlöcher sind ein Filter.“ (3) „POV: Sie sieht dich zum ersten Mal – von unten.“ → **(1)** (schon gerendert/getestet, Text-Overlay aus (1) abgeleitet).
- Gepostet 18:00, media_id 18123486640985940 (30,4 s).
- Kommentare: Zuschauer schlagen Ausreden vor („Sag dein Handy wurde gehackt“, „Sag die Wahrheit“) → in Tag 4 als Easter-Egg einbauen (z. B. Ahmed: „Einer sagt, sag, du wurdest gehackt… Wer hackt ein Handy mit 3 % Akku?“). Frage „wie machst du diese videos?“ ehrlich beantwortet (KI-Hilfe).
  7 Kommentare beantwortet (inkl. 3 übersehene B-Stimmen von gestern), kein Spam.
- **Für die nächsten Teile:**
  - Teil 2 nicht nur mit Rückblick-Satz starten: idealerweise neue Pointe/Peinlichkeit in Sekunde 0, die ohne Teil 1 verständlich ist.
  - Teil 1 holt kaum Kommentare (2) → im Teil 1 eine Ein-Wort-Frage einbauen („Was würdest DU sagen? 1 Wort!“) und testen.
  - Saves = 0 bei T1 → Caption-Test „Speicher dir das für dein nächstes Date“.
  - Watch-Time: Teil 2 verliert in der Poll-Karte (21–30 s, 9 s statisch). Poll kürzer (≤ 6 s) und Ahmed-Reaktion animieren.

## 2026-11-12 12:00 (Tag 4 · Teil 1)
- Abstimmung Tag 3 Teil 2: **B 5 : A 2** → „Ich bin Emres Zwilling“. (A-Stimmen: „Die Wahrheit“, „mach dich hübscher und dann die Wahrheit“.)
- Zahlen 11:15 (Windsor, ohne force_refresh), Follower 13 (unverändert):
  | Reel | Views | Reach | Skip | Ø Watch | Likes | Komm. | Shares | Saves |
  |---|---|---|---|---|---|---|---|---|
  | Tag 2 T1 (49 s) | 2.288 | 1.815 | 28,1 % | 19,9 s | 39 | 2 | 1 | 2 |
  | Tag 2 T2 (31 s) | 1.246 | 1.001 | 39,4 % | 12,0 s | 20 | 19 | 0 | 3 |
  | **Tag 3 T1 (31,7 s)** | **3.071** | 2.366 | 26,5 % | **23,0 s (≈73 %)** | 36 | 4 | **4** | 0 |
  | Tag 3 T2 (30,4 s) | 1.678 (17 h) | 1.267 | **28,6 %** | 15,8 s | 24 | 7 | 1 | 0 |
- **Test gestern (Teil 2 mit Hook-Text „SIE SAH NUR MEINE NASENLÖCHER.“ statt „VORHIN BEI AHMED…“): Gewinner.** Skip Teil 2 von 39,4 % → **28,6 %**, Ø Watch 12,0 → 15,8 s.
  → Teil 2 startet ab jetzt immer mit eigener Peinlichkeits-Hook-Zeile + Text, nie mit Rückblick.
- Tag 3 T1 ist bestes Reel (3.071 Views, 73 % Watch-Ratio) → Gewinner-Format (Peinlichkeits-Behauptung + Text ≤ 8 Wörter in s 0) beibehalten.
- Problem: Follower stagnieren bei 13 trotz ~3.000 Views/Reel; Saves = 0 bei den letzten zwei Reels.
- Hook-Varianten Tag 4 T1: (1) „Ich hab Lena gesagt, ich bin Emres Zwilling. Wir sehen uns null ähnlich.“ (2) „POV: Du erfindest einen Zwilling und sie will ein Familienfoto.“ (3) „5 zu 2 für B. Ich hab jetzt offiziell einen Zwilling.“ → **(1)** (gleiche Bauart wie Gewinner Tag 3 T1, Pointe am Satzende). Text „ICH HAB JETZT EINEN ZWILLING.“
- Gags (Alltag): Zuschauer-Easter-Egg „mach dich hübsch“ → „Bruder… das war schon hübsch.“; „Er hat die Muskeln gekriegt. Ich das WLAN-Passwort.“; Cousin antwortet seit 3 Wochen nur mit Daumen hoch (Cliffhanger).
- Länge 32,4 s. Whisper-Check: alles korrekt; Seraphinas kurzes „Süß!“ wurde als „Sass“ erkannt → umformuliert zu „Voll süß!“ (wird korrekt erkannt).
- **Tagestest:** Caption von Teil 1 endet mit Ein-Wort-Frage („Wie kommt Ahmed an ein Zwillingsfoto? 1 Wort 👇“) → Kommentare unter T1 mit Tag 3 T1 (4) vergleichen.
- Gepostet 12:00:48, media_id 18422693974152086 (https://www.instagram.com/reel/Dfo5duujRhl/).
- Teil 2 fertig geschrieben + getestet (31,8 s): Panorama-Trick, Foto mit 3 Armen, „ZU DRITT?!“, Poll A = echten Emre anrufen / B = Ahmed spielt beide. Poll-Karte kürzer (Abspann 1,6 s).
- 8 Kommentare als Ahmed beantwortet (5× B, 2× A, 1 Frage „wie machst du die Videos?“ – ehrlich: KI-Hilfe), kein Spam/keine Beleidigungen.
