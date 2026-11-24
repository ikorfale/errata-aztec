"""Arctic circle measurement. For each order n and sample, the frozen run from each of the 4 corners along the middle
row/column (row n-1, column n-1): consecutive cells from the edge with the corner cell's domino type. The arctic circle
theorem (Jockusch-Propp-Shor 1995) predicts run/n -> 1 - 1/sqrt(2) = 0.29289; Johansson (2005) predicts fluctuations
of order n^(1/3). Seeds: seed = 1000003*n + k. Writes results.json {n: [[W,E,N,S] per sample]}."""
import json, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0, '/home/board/work/lab/aztec')
from aztec import sample, type_grid

def run(line):
    first = line[line >= 0]; t = first[0]; k = 0
    for v in first:
        if v != t: break
        k += 1
    return int(k)

def one(a):
    n, k = a
    g = type_grid(sample(n, seed=1000003 * n + k), n)
    row, col = g[n - 1], g[:, n - 1]
    return n, [run(row), run(row[::-1]), run(col), run(col[::-1])]

if __name__ == '__main__':
    plan = [(25, 1000), (50, 1000), (100, 400), (200, 200), (400, 60)]
    jobs = [(n, k) for n, r in plan for k in range(r)]
    out = {}
    with Pool(4) as p:
        for n, v in p.imap_unordered(one, sorted(jobs, key=lambda a: -a[0]), chunksize=1):
            out.setdefault(n, []).append(v)
    json.dump(out, open('/home/board/work/lab/aztec/results.json', 'w'))
    for n in sorted(out):
        a = np.array(out[n]) / n; print(n, len(out[n]), a.mean(0).round(4), (np.array(out[n]).std(0)).round(2))
    print('=== end')
