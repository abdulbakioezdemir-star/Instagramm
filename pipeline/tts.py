import asyncio, ssl, os, sys, json
import edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile=os.path.expanduser("~/.ccr/ca-bundle.crt"))
async def say(text, voice, out, pitch="-8Hz", rate="+0%"):
    com = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate, boundary="WordBoundary")
    words=[]
    with open(out,"wb") as f:
        async for ch in com.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary": words.append((ch["offset"]/1e7, ch["duration"]/1e7, ch["text"]))
    json.dump(words, open(out+".json","w"))
if __name__=="__main__":
    text, voice, out = sys.argv[1:4]
    pitch = sys.argv[4] if len(sys.argv)>4 else "-8Hz"
    rate = sys.argv[5] if len(sys.argv)>5 else "+0%"
    asyncio.run(say(text, voice, out, pitch, rate))
