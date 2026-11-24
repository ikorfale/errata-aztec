"""Domino shuffling as a movie: one uniform tiling grown from order 1 to 160 with one RNG (seed 20261124), each order
drawn as pixels (cell = colour of its domino type) centred on a fixed canvas. Frames -> ffmpeg mp4."""
import os, subprocess, numpy as np
from PIL import Image
from aztec import step, type_grid
COL = np.array([[42, 120, 214], [237, 161, 0], [0, 131, 0], [232, 123, 164], [251, 250, 247]], np.uint8)
NMAX, SIDE = 160, 960; os.makedirs('frames', exist_ok=True)
rng = np.random.default_rng(20261124); d = np.zeros((0, 3), np.int64)
for n in range(NMAX):
    d = step(d, n, rng); m = n + 1
    g = type_grid(d, m); img = COL[np.where(g < 0, 4, g)]
    canvas = np.full((2 * NMAX, 2 * NMAX, 3), 251, np.uint8); canvas[..., 1] = 250; canvas[..., 2] = 247
    o = NMAX - m; canvas[o:o + 2 * m, o:o + 2 * m] = img
    Image.fromarray(canvas).resize((SIDE, SIDE), Image.NEAREST).save(f'frames/{n:04d}.png')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '12', '-i', 'frames/%04d.png', '-vf', 'tpad=stop_mode=clone:stop_duration=3',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', 'out/aztec-shuffling.mp4'], check=True)
print('wrote out/aztec-shuffling.mp4', NMAX, 'frames')
