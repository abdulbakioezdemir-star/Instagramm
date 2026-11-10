import sys, subprocess, numpy as np
from faster_whisper import WhisperModel
raw = subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout
audio = np.frombuffer(raw, dtype=np.float32)
m = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else "small", device="cpu", compute_type="int8")
segs, info = m.transcribe(audio, language="de")
for s in segs:
    print(f"{s.start:5.1f}–{s.end:5.1f}s  {s.text.strip()}")
