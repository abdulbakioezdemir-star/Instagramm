#!/usr/bin/env python3
"""Veröffentlicht Kurzvideos aus einer Tabelle (posts.csv) und beantwortet erste Kommentare mit Fakten.

  python publish.py posten   [--csv posts.csv] [--jetzt]   # fällige Zeilen hochladen
  python publish.py antworten [--video VIDEO_ID] [--max 5]  # YouTube-Kommentare beantworten

Zugangsdaten nur über Umgebungsvariablen / Dateien, nie im Code:
  YOUTUBE_CLIENT_SECRETS  Pfad zur OAuth-Client-Datei (Google Cloud Console)
  IG_USER_ID, IG_TOKEN    Instagram-Business-Konto + Graph-API-Token
  IG_VIDEO_BASE_URL       öffentliche Basis-URL, unter der die MP4-Datei erreichbar ist (Instagram lädt per URL)
  TIKTOK_TOKEN            TikTok Content Posting API (user access token, Scope video.publish)
API-Details ändern sich: vor dem ersten Einsatz die aktuellen Docs der drei Plattformen prüfen.
"""
import argparse, csv, json, os, random, sys, time
from datetime import datetime, timezone
from pathlib import Path

import requests

HIER = Path(__file__).resolve().parent
STATE = HIER / "beantwortet.json"          # merkt sich beantwortete Kommentare
YT_SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]


# ------------------------------------------------------------------ YouTube
def youtube():
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    tok = HIER / "yt_token.json"
    creds = Credentials.from_authorized_user_file(tok, YT_SCOPES) if tok.exists() else None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(os.environ["YOUTUBE_CLIENT_SECRETS"], YT_SCOPES)
        creds = flow.run_local_server(port=0)
        tok.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def post_youtube(row):
    from googleapiclient.http import MediaFileUpload
    yt = youtube()
    body = {
        "snippet": {"title": row["titel"][:100], "description": f'{row["beschreibung"]}\n\n{row["hashtags"]}',
                    "categoryId": "2", "defaultLanguage": "de"},      # 2 = Autos & Fahrzeuge
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(HIER / row["datei"]), chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return resp["id"]


# ------------------------------------------------------------------ Instagram (Reels über die Graph API)
def post_instagram(row):
    base = "https://graph.facebook.com/v21.0"
    uid, tok = os.environ["IG_USER_ID"], os.environ["IG_TOKEN"]
    url = os.environ["IG_VIDEO_BASE_URL"].rstrip("/") + "/" + Path(row["datei"]).name
    c = requests.post(f"{base}/{uid}/media", data={"media_type": "REELS", "video_url": url,
                      "caption": f'{row["beschreibung"]}\n\n{row["hashtags"]}', "access_token": tok}, timeout=60).json()
    cid = c["id"]
    for _ in range(60):                                  # warten, bis Instagram das Video verarbeitet hat
        s = requests.get(f"{base}/{cid}", params={"fields": "status_code", "access_token": tok}, timeout=30).json()
        if s.get("status_code") == "FINISHED":
            break
        if s.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram-Verarbeitung fehlgeschlagen: {s}")
        time.sleep(10)
    p = requests.post(f"{base}/{uid}/media_publish", data={"creation_id": cid, "access_token": tok}, timeout=60).json()
    return p["id"]


# ------------------------------------------------------------------ TikTok (Content Posting API, Direct Post)
def post_tiktok(row):
    tok = os.environ["TIKTOK_TOKEN"]
    f = HIER / row["datei"]
    size = f.stat().st_size
    init = requests.post("https://open.tiktokapis.com/v2/post/publish/video/init/",
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8"},
        json={"post_info": {"title": f'{row["titel"]} {row["hashtags"]}'[:2200],
                            "privacy_level": "SELF_ONLY"},       # ungeprüfte Apps dürfen nur privat posten
              "source_info": {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": size, "total_chunk_count": 1}},
        timeout=60).json()
    data = init["data"]
    requests.put(data["upload_url"], data=f.read_bytes(), timeout=600,
                 headers={"Content-Type": "video/mp4", "Content-Range": f"bytes 0-{size - 1}/{size}"}).raise_for_status()
    return data["publish_id"]


POSTER = {"youtube": post_youtube, "instagram": post_instagram, "tiktok": post_tiktok}


def posten(csv_pfad, jetzt):
    rows = list(csv.DictReader(open(csv_pfad, encoding="utf-8")))
    now = datetime.now(timezone.utc)
    for row in rows:
        faellig = jetzt or datetime.fromisoformat(row["veroeffentlichen_um"]) <= now
        if row["status"] != "geplant" or not faellig:
            continue
        ergebnisse = {}
        for plattform in row["plattformen"].split(";"):
            try:
                ergebnisse[plattform] = POSTER[plattform](row)
                print(f"✓ {plattform}: {ergebnisse[plattform]}")
            except Exception as e:                       # eine Plattform darf die anderen nicht aufhalten
                ergebnisse[plattform] = f"FEHLER: {e}"
                print(f"✗ {plattform}: {e}", file=sys.stderr)
        row["status"] = "veroeffentlicht" if all(not str(v).startswith("FEHLER") for v in ergebnisse.values()) else "fehler"
        row["ergebnis"] = json.dumps(ergebnisse)
    felder = list(rows[0].keys()) + (["ergebnis"] if "ergebnis" not in rows[0] else [])
    with open(csv_pfad, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=felder, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


# ------------------------------------------------------------------ Kommentare beantworten (nur die ersten, nur einmal)
def antworten(video_id, maximum):
    fakten = [l.strip() for l in open(HIER / "fakten.txt", encoding="utf-8") if l.strip()]
    erledigt = set(json.loads(STATE.read_text())) if STATE.exists() else set()
    yt = youtube()
    threads = yt.commentThreads().list(part="snippet", videoId=video_id, maxResults=20, order="time").execute()["items"]
    threads.reverse()                                     # die ersten Kommentare zuerst
    gesendet = 0
    for t in threads:
        if gesendet >= maximum:
            break
        if t["id"] in erledigt or t["snippet"]["totalReplyCount"] > 0:
            continue
        text = f"Danke fürs Zuschauen! Fun Fact: {random.choice(fakten)}"
        yt.comments().insert(part="snippet", body={"snippet": {"parentId": t["id"], "textOriginal": text}}).execute()
        erledigt.add(t["id"]); gesendet += 1
        print(f"↳ geantwortet auf {t['id']}")
        time.sleep(20)                                    # nicht wie Spam wirken
    STATE.write_text(json.dumps(sorted(erledigt)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("posten"); p.add_argument("--csv", default=str(HIER / "posts.csv")); p.add_argument("--jetzt", action="store_true")
    a = sub.add_parser("antworten"); a.add_argument("--video", required=True); a.add_argument("--max", type=int, default=5)
    args = ap.parse_args()
    posten(args.csv, args.jetzt) if args.cmd == "posten" else antworten(args.video, args.max)
