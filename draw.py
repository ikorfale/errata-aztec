"""Render one uniform tiling of order n as a PNG: each domino a filled rectangle in its type colour with a thin gap,
the arctic circle (radius n/sqrt(2) cells around the centre) as a thin dark line. Usage: draw.py n seed out.png"""
import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle, Circle
sys.path.insert(0, '/home/board/work/lab/aztec'); from aztec import sample
n, seed, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
COL = {0: '#2a78d6', 1: '#eda100', 2: '#008300', 3: '#e87ba4'}  # N S W E
d = sample(n, seed=seed); g = 0.12 if n <= 60 else 0.0
fig, ax = plt.subplots(figsize=(10, 10), dpi=160); fig.patch.set_facecolor('#fbfaf7')
for t in range(4):
    s = d[d[:, 2] == t]; w, h = (2, 1) if t <= 1 else (1, 2)
    ax.add_collection(PatchCollection([Rectangle((c + g / 2, -(r + h) + g / 2), w - g, h - g) for r, c, _ in s],
                                      facecolor=COL[t], edgecolor='none'))
ax.add_patch(Circle((n, -n), n / np.sqrt(2), fill=False, lw=1.2, ec='#1b1b1b', ls=(0, (4, 3))))
ax.set_xlim(-1, 2 * n + 1); ax.set_ylim(-2 * n - 1, 1); ax.set_aspect('equal'); ax.axis('off')
fig.savefig(out, bbox_inches='tight', facecolor=fig.get_facecolor()); print('wrote', out, len(d), 'dominoes')
