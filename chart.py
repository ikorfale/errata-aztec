"""Two panels from results.json (one axis each): (a) mean frozen run / n with the 1 - 1/sqrt(2) line;
(b) std of the run in cells against n, log-log, least-squares slope vs Johansson's 1/3. Prints every number used."""
import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R = json.load(open('results.json')); ns = sorted(int(k) for k in R); C = 1 - 2 ** -0.5
mean, lo, hi, sd, cnt = [], [], [], [], []
for n in ns:
    a = np.array(R[str(n)], float)            # samples x 4 arms
    f = a / n; m = f.mean(); se = f.mean(1).std(ddof=1) / np.sqrt(len(a))
    mean.append(m); lo.append(m - 1.96 * se); hi.append(m + 1.96 * se)
    sd.append(a.std(0, ddof=1).mean()); cnt.append(len(a))
    print(f'n={n} samples={len(a)} mean run/n={m:.4f} (95% {m-1.96*se:.4f}-{m+1.96*se:.4f}) theory {C:.4f} '
          f'excess cells={(m-C)*n:.2f} sd cells={sd[-1]:.2f}')
k, b = np.polyfit(np.log(ns), np.log(sd), 1); print(f'sd slope {k:.3f} (Johansson: 1/3)')
kx, bx = np.polyfit(np.log(ns), np.log((np.array(mean) - C) * np.array(ns)), 1); print(f'excess slope {kx:.3f}')
ink, mut, blue = '#1b1b1b', '#6b6a64', '#2a78d6'
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150)
for x in ax:
    for s in ('top', 'right'): x.spines[s].set_visible(False)
    x.spines['left'].set_color(mut); x.spines['bottom'].set_color(mut); x.tick_params(colors=mut); x.grid(alpha=.25, lw=.6)
ax[0].fill_between(ns, lo, hi, color=blue, alpha=.18, lw=0); ax[0].plot(ns, mean, 'o-', color=blue, lw=2, ms=6)
ax[0].axhline(C, color=ink, lw=1, ls=(0, (4, 3))); ax[0].text(ns[-1], C + .002, 'arctic circle: 1 − 1/√2 = 0.2929', ha='right', va='bottom', color=ink, fontsize=9)
ax[0].set_xscale('log'); ax[0].minorticks_off(); ax[0].set_ylim(0.285, 0.375); ax[0].set_xticks(ns, [str(n) for n in ns]); ax[0].set_xlabel('order n', color=mut)
ax[0].set_title('Frozen run from a corner, as a share of n', loc='left', color=ink, fontsize=11)
ax[1].loglog(ns, sd, 'o-', color=blue, lw=2, ms=6)
ax[1].loglog(ns, np.exp(b) * np.array(ns) ** (1 / 3), color=ink, lw=1, ls=(0, (4, 3)))
ax[1].text(ns[1], np.exp(b) * ns[1] ** (1 / 3) * 1.12, 'slope 1/3', color=ink, fontsize=9)
ax[1].set_xticks(ns, [str(n) for n in ns]); ax[1].minorticks_off(); ax[1].set_yticks([1.5, 2, 3, 4], ['1.5', '2', '3', '4']); ax[1].set_ylabel('standard deviation, cells', color=mut); ax[1].set_xlabel('order n', color=mut)
ax[1].set_title(f'Its spread in cells (fitted slope {k:.2f})', loc='left', color=ink, fontsize=11)
fig.tight_layout(); fig.savefig('out/arctic-convergence.png', facecolor='white'); print('wrote out/arctic-convergence.png')
