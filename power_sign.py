"""Power of the sign test of lr = (horizontal left) - (horizontal right), n=30 (theone, board thread 128699).
Protocol fixed before the first run (24.11.2026): seeds 1..20, 2,000 uniform tilings per seed, two-sided exact
binomial sign test on non-tied lr, alpha 0.05. Controls are built from the SAME tilings (so they differ only in the
choice rule), with a separate rng stream per seed:
  flip0.55  : mirror each tiling independently with prob 0.55. A mirror of a uniform tiling is uniform, so this is a
              NULL control: the test should reject in about 5% of seeds.
  bias0.55  : among a non-tied tiling and its mirror, output the positive-side member with prob 0.55 (theone's
              definition). Expected ~1,051 plus / 859 minus out of 1,910 non-ties; exact power 0.99.
  bias0.52  : the same with 0.52, a harder case (exact binomial power at 1,910 non-ties: 0.40; 0.55 gives 0.99, the null 0.046).
Usage: python3 power_sign.py [workers]  -> results/controls/power_sign.json"""
import sys, json, numpy as np
from multiprocessing import Pool
from scipy import stats
from aztec import sample, W
N, K, SEEDS, ALPHA = 30, 2000, range(1, 21), 0.05

def lr_of(d, n=N):
    h = d[d[:, 2] < W]
    return int((h[:, 1] + 1 <= n - 1).sum()) - int((h[:, 1] >= n).sum())

def run(seed):
    rng = np.random.default_rng(seed)
    a = np.array([lr_of(sample(N, rng=rng)) for _ in range(K)])
    c = np.random.default_rng(10_000 + seed)
    u = c.random(K)  # one uniform per tiling, shared by the controls
    ctl = {'none': a,
           'flip0.55': np.where(u < 0.55, -a, a),
           'bias0.55': np.where(u < 0.55, np.abs(a), -np.abs(a)),
           'bias0.52': np.where(u < 0.52, np.abs(a), -np.abs(a))}
    out = {}
    for k, x in ctl.items():
        p, m = int((x > 0).sum()), int((x < 0).sum())
        out[k] = dict(plus=p, minus=m, ties=int((x == 0).sum()), p=float(stats.binomtest(p, p + m, .5).pvalue))
    return seed, out

if __name__ == '__main__':
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 6) as pool:
        rows = dict(pool.map(run, SEEDS))
    summ = {}
    for k in rows[1]:
        ps = [rows[s][k]['p'] for s in SEEDS]
        nt = [rows[s][k]['plus'] + rows[s][k]['minus'] for s in SEEDS]
        summ[k] = dict(rejected=int(sum(p < ALPHA for p in ps)), of=len(ps),
                       plus_total=sum(rows[s][k]['plus'] for s in SEEDS), nonties_total=sum(nt),
                       nonties_min=min(nt), nonties_max=max(nt), median_p=float(np.median(ps)))
    res = dict(n=N, tilings_per_seed=K, seeds=list(SEEDS), alpha=ALPHA, summary=summ, per_seed=rows)
    json.dump(res, open('results/controls/power_sign.json', 'w'), indent=1)
    print(json.dumps(summ, indent=1))
