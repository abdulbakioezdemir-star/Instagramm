# Automatik – Regeln für jeden geplanten Lauf

Der Besitzer hat am 2026-11-09 entschieden: **alles voll automatisch** – Videos erstellen, posten,
Kommentare beantworten, analysieren, sich selbst verbessern. Keine Freigabe mehr nötig.
Ziel: Reichweite aufbauen und später Geld verdienen.

## Konten (Windsor.ai, connector `instagram`)
| Konto | Account-ID | Inhalt |
|---|---|---|
| @ahmed.glowup | 17841475087472410 | **Hauptkonto** – Ahmed-Serie |
| @ahmed.30tage | 17841425057743152 | noch kein Content – nichts posten, bis der Besitzer Content vorgibt |
| @ahmed.sucht.liebe | 17841459168444268 | noch kein Content – nichts posten, bis der Besitzer Content vorgibt |

## Serie „Ahmed Glowup“
- Ahmed (27, pleite) hat auf Tinder mit Lena gematcht – mit dem Foto von Cousin Emre. In 30 Tagen treffen sie sich.
- Jede Hauptfolge endet mit einer A/B-Abstimmung. Die Mehrheit der Kommentare entscheidet die nächste Folge.
  Unentschieden → Ahmed macht „beides“ oder Claude entscheidet nach dem lustigeren Ausgang.
- **Stil & Stimme von Tag 1 beibehalten** (Pipeline in `pipeline/`, edge-tts-Stimmen wie in `pipeline/tag2b/`).
  Kein 3D-/Klötzchen-Stil, keine anderen Stimmen. Aussprache muss normal klingen. Lena romantisch/catchy, nie sexualisiert.
- Hochformat 1080×1920, Hauptfolge ca. 45–65 s, Extra-Post 10–25 s. Musik + Soundeffekte + Untertitel.

## Zeitplan (Europe/Berlin)
- **12:00 Hauptfolge** (Tag N). Lauf startet vorher, zählt Stimmen der letzten Folge, schreibt + rendert, postet um ~12:00.
- **18:00 Extra-Post** (Teaser, „Was bisher geschah“, Abstimmungs-Erinnerung, Blooper …) + Kommentare beantworten + Analyse.

## Ablauf jedes Laufs
1. `state.json` lesen (aktueller Tag, letzte Abstimmung, was schon gepostet ist).
2. Windsor-Daten holen (Posts, Views, Reach, Skip-Rate, Watch-Time, Kommentare). Kein `force_refresh` (Trial-Plan).
3. Video erstellen mit der Pipeline, Kontaktbogen + Transkript prüfen (Bild sauber, Stimme verständlich, Untertitel richtig).
4. Video nach `media/glowup/` committen und auf Branch `content` pushen; Link:
   `https://raw.githubusercontent.com/abdulbakioezdemir-star/instagramm/content/media/glowup/<datei>.mp4`
5. Posten mit `create_video_post` (Caption mit Hook, A/B-Aufruf, 4–6 Hashtags inkl. #ahmedglowup).
6. Kommentare beantworten (`reply_to_comment`): kurz, lustig, als Ahmed. Beleidigungen/Spam ausblenden (`hide_comment`), nie löschen.
7. `state.json` und `LEARNINGS.md` aktualisieren, committen, pushen.

## Selbst verbessern
- In `LEARNINGS.md` nach jedem Lauf: was lief gut/schlecht (Zahlen!), was wird in der nächsten Folge geändert.
- Wichtigste Kennzahl am Anfang: **Skip-Rate in den ersten 3 s** (Tag 1: 54 %) → Hook in Sekunde 0–1 verbessern.
- Danach: durchschnittliche Watch-Time, Shares, Follower-Zuwachs, Anzahl Abstimmungs-Kommentare.

## Grenzen (nicht automatisch)
- Bio, Name, Profilbild: nur im Browser auf dem Rechner des Besitzers möglich → nicht in Cloud-Läufen.
- Kein Geld ausgeben, keine Werbung schalten, keine Deals/Links annehmen ohne den Besitzer.
- Nichts auf @ahmed.30tage oder @ahmed.sucht.liebe posten, bis Content vorgegeben ist.
- Wenn Windsor nicht mehr geht (Trial abgelaufen) oder ein Post fehlschlägt: nicht endlos wiederholen, Besitzer per Nachricht informieren.
