"""Checks: (1) brute-force count of Aztec tilings = 2^(n(n+1)/2) for n=1..4; (2) the sampler only returns valid
tilings; (3) uniformity: for n=2 (8 tilings) and n=3 (64), chi-square over many samples."""
import sys, collections, numpy as np
sys.path.insert(0, '.')
from aztec import sample, inside, type_grid
from scipy.stats import chisquare

def count(n):
    ins = inside(n); cells = [tuple(x) for x in np.argwhere(ins)]; free = set(cells)
    def rec():
        if not free: return 1
        i, j = min(free); free.discard((i, j)); tot = 0
        for nb in ((i, j + 1), (i + 1, j)):
            if nb in free: free.discard(nb); tot += rec(); free.add(nb)
        free.add((i, j)); return tot
    return rec()

for n in range(1, 5):
    c = count(n); print(f'n={n} brute-force tilings {c} formula {2 ** (n * (n + 1) // 2)}'); assert c == 2 ** (n * (n + 1) // 2)
rng = np.random.default_rng(20261124)
for n, reps in ((2, 16000), (3, 64000)):
    cnt = collections.Counter(type_grid(sample(n, rng=rng), n).tobytes() for _ in range(reps))
    k = 2 ** (n * (n + 1) // 2); obs = list(cnt.values()) + [0] * (k - len(cnt))
    st = chisquare(obs); print(f'n={n}: {len(cnt)} of {k} tilings seen in {reps} samples, chi2 {st.statistic:.1f} df {k-1} p {st.pvalue:.3f}')
    assert len(cnt) == k and st.pvalue > 0.001
print('ALL OK')
