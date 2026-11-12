"""Erzeugt die 9 Startbilder mit SDXL-Turbo lokal auf der CPU.
python gen_images.py [shot-nummern...]  (ohne Argumente: alle)"""
import sys, time, json, torch
from pathlib import Path
from diffusers import AutoPipelineForText2Image
HERE = Path(__file__).resolve().parent.parent
SHOTS = json.load(open(HERE / "tools" / "shots.json"))
torch.set_num_threads(4)
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.bfloat16, variant="fp16", low_cpu_mem_usage=True)
pipe.enable_attention_slicing()
pipe.vae.enable_tiling()
STYLE = ", photorealistic, premium automotive commercial photography, soft natural light, clean, high detail, sharp focus, 35mm"
SEEDS = [11, 23]
want = [int(a) for a in sys.argv[1:]] or [s["n"] for s in SHOTS]
for s in SHOTS:
    if s["n"] not in want:
        continue
    for take, seed in enumerate(s.get("seeds", SEEDS)):
        t = time.time()
        g = torch.Generator().manual_seed(seed)
        img = pipe(prompt=s["prompt"] + STYLE, num_inference_steps=4, guidance_scale=0.0, width=544, height=960, generator=g).images[0]
        out = HERE / "img" / f"shot{s['n']}_{take}.png"
        img.save(out)
        print(f"shot {s['n']} take {take} seed {seed}: {time.time() - t:.0f}s -> {out.name}", flush=True)
