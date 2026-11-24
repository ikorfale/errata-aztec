"""Large-order check that is not forced by symmetry: EKLP (1992) prove sum_T t^{v(T)/2} = (1+t)^{n(n+1)/2},
v = number of vertical dominoes. So for a uniform tiling v/2 ~ Binomial(n(n+1)/2, 1/2) exactly: the whole
distribution, not only the mean 1/2 that the quarter-turn symmetry forces. One observation per tiling.
Usage: python3 binom_check.py n samples seed [control]
Negative controls (the check must fail them): control=spikes returns the all-horizontal tiling or its quarter-turn,
50/50 (mean still exactly 1/2; suggested by theone); control=coin0.505 builds blocks vertical with chance 0.505.
control=mirror is the blind spot: a uniform tiling or its left-right mirror, whichever has more horizontal dominoes
in its left half. The mirror keeps v, so v/2 stays exactly binomial while the sampler is not uniform; only the
side statistic lr = (horizontal left) - (horizontal right), whose mean is 0 by mirror symmetry, sees it.
Sign test of lr (theone): conditional on lr != 0, + and - are equally likely under mirror symmetry; ties reported apart, exact binomial.
(A KS test was tried and dropped: on discrete data scipy's kstest rejects a correct sampler, p=0.0004 at n=30.)"""
import sys, json, numpy as np
from scipy import stats
from aztec import sample, W, E
n, k, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rng = np.random.default_rng(seed)
ctl = sys.argv[4] if len(sys.argv) > 4 else ''
M = n * (n + 1) // 2
if ctl == 'spikes': x = rng.integers(0, 2, k) * M; lr = np.zeros(k)
else:
    q = float(ctl[4:]) if ctl.startswith('coin') else 0.5
    x, lr = [], []
    for _ in range(k):
        d = sample(n, rng=rng, q=q)
        x.append(int((d[:, 2] >= W).sum()) // 2)
        h = d[d[:, 2] < W]
        a = int((h[:, 1] + 1 <= n - 1).sum()) - int((h[:, 1] >= n).sum())
        lr.append(abs(a) if ctl == 'mirror' else a)  # mirror of a tiling negates a and keeps v
    x, lr = np.array(x), np.array(lr)
mean, var = x.mean(), x.var(ddof=1)
# chi2 against exact binomial on bins with expected >= 5 (tails merged)
lo, hi = stats.binom.ppf(1e-4, M, .5), stats.binom.isf(1e-4, M, .5)
edges = np.arange(lo, hi + 1)
obs = np.array([(x < lo).sum()] + [(x == e).sum() for e in edges] + [(x > hi).sum()])
p = np.concatenate([[stats.binom.cdf(lo - 1, M, .5)], stats.binom.pmf(edges, M, .5), [stats.binom.sf(hi, M, .5)]])
exp = p * k
# merge small bins greedily
o2, e2, ao, ae = [], [], 0, 0
for a, b in zip(obs, exp):
    ao += a; ae += b
    if ae >= 5: o2.append(ao); e2.append(ae); ao = ae = 0
if ae: o2[-1] += ao; e2[-1] += ae
chi = stats.chisquare(o2, e2)
# variance test: under H0 (k-1)s^2/sigma^2 ~ approx chi2(k-1)
s2 = M / 4
pv = 2 * min(stats.chi2.cdf((k - 1) * var / s2, k - 1), stats.chi2.sf((k - 1) * var / s2, k - 1))
out = dict(n=n, samples=k, seed=seed, control=ctl or 'none', dominoes_per_tiling=n * (n + 1), binomial_trials=M, mean_frac_vertical=round(2 * mean / (2 * M), 5),
           mean_z=round((mean - M / 2) / np.sqrt(s2 / k), 2), var_ratio=round(var / s2, 4), var_p=round(pv, 3),
           chi2_p=round(chi.pvalue, 3), chi2_bins=len(o2),
           lr_sign=dict(plus=int((lr > 0).sum()), minus=int((lr < 0).sum()), ties=int((lr == 0).sum()),
                        p=float(f'{stats.binomtest(int((lr > 0).sum()), int((lr != 0).sum()), .5).pvalue:.3g}') if (lr != 0).any() else None),
           lr_mean_z=round(lr.mean() / (lr.std(ddof=1) / np.sqrt(k)), 2) if lr.std() > 0 else None)
print(json.dumps(out))
