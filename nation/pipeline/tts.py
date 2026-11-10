"""Erzeugt l*.mp3 + l*.mp3.json (Wortzeiten [start_s, dauer_s, wort]) aus einer lines-TSV. Aufruf: python3 tts.py lines_xxx.tsv"""
import asyncio, json, sys, inspect, os, ssl, edge_tts
if os.path.exists("/root/.ccr/ca-bundle.crt"):  # Proxy-CA in der Cloud-Umgebung
    edge_tts.communicate._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
VOICE, PITCH, RATE = "de-DE-FlorianMultilingualNeural", "-4Hz", "+4%"
async def one(k, text):
    kw = dict(voice=VOICE, pitch=PITCH, rate=RATE)
    if "boundary" in inspect.signature(edge_tts.Communicate).parameters: kw["boundary"] = "WordBoundary"
    c = edge_tts.Communicate(text, **kw)
    words = []
    with open(f"{k}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append((ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"]))
    json.dump(words, open(f"{k}.mp3.json", "w"), ensure_ascii=False)
    print(k, len(words), "Wörter")
async def main():
    for ln in open(sys.argv[1], encoding="utf-8"):
        if "\t" in ln:
            k, t = ln.rstrip("\n").split("\t", 1); await one(k, t)
asyncio.run(main())
