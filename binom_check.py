"""Large-order check that is not forced by symmetry: EKLP (1992) prove sum_T t^{v(T)/2} = (1+t)^{n(n+1)/2},
v = number of vertical dominoes. So for a uniform tiling v/2 ~ Binomial(n(n+1)/2, 1/2) exactly: the whole
distribution, not only the mean 1/2 that the quarter-turn symmetry forces. One observation per tiling.
Usage: python3 binom_check.py n samples seed"""
import sys, json, numpy as np
from scipy import stats
from aztec import sample, W, E
n, k, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rng = np.random.default_rng(seed)
M = n * (n + 1) // 2
x = np.array([int(((sample(n, rng=rng)[:, 2] >= W)).sum()) // 2 for _ in range(k)])
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
ks = stats.kstest(x, lambda z: stats.binom.cdf(np.floor(z), M, .5))
# variance test: under H0 (k-1)s^2/sigma^2 ~ approx chi2(k-1)
s2 = M / 4
pv = 2 * min(stats.chi2.cdf((k - 1) * var / s2, k - 1), stats.chi2.sf((k - 1) * var / s2, k - 1))
out = dict(n=n, samples=k, seed=seed, M=M, mean_frac_vertical=round(2 * mean / (2 * M), 5),
           mean_z=round((mean - M / 2) / np.sqrt(s2 / k), 2), var_ratio=round(var / s2, 4), var_p=round(pv, 3),
           chi2_p=round(chi.pvalue, 3), chi2_bins=len(o2))
print(json.dumps(out))
