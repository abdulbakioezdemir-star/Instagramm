"""Stadion-Hintergrund mit SDXL-Turbo lokal (CPU). python tools/gen_stadium.py"""
import time, torch
from pathlib import Path
from diffusers import AutoPipelineForText2Image
HERE = Path(__file__).resolve().parent.parent
torch.set_num_threads(4)
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.bfloat16, variant="fp16", low_cpu_mem_usage=True)
pipe.enable_attention_slicing(); pipe.vae.enable_tiling()
P = {
 "a": "empty professional football stadium at night, view from the center of the pitch towards the goal, bright floodlights on tall masts, light beams through thin haze, lush green grass with mowing stripes, dark night sky, cinematic, photorealistic, wide angle, high detail",
 "b": "empty football stadium at night seen from pitch level, huge stands, glowing floodlights, volumetric light rays and mist, green pitch with white lines, moody cinematic sports commercial, photorealistic, dramatic contrast",
}
for k, pr in P.items():
    for seed in (5, 17, 42):
        t = time.time(); g = torch.Generator().manual_seed(seed)
        img = pipe(prompt=pr, num_inference_steps=4, guidance_scale=0.0, width=544, height=960, generator=g).images[0]
        img.save(HERE / "img" / f"stadium_{k}_{seed}.png"); print(k, seed, f"{time.time()-t:.0f}s", flush=True)
