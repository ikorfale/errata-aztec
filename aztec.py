"""Exact uniform random domino tilings of the Aztec diamond by domino shuffling (Elkies-Kuperberg-Larsen-Propp 1992).

Grid of order n: 2n x 2n array, cell (i, j) (row i top-down, column j) lies in the diamond iff
|i - n + 0.5| + |j - n + 0.5| <= n. A domino is (r, c, t): t in N, S (horizontal, cells (r,c),(r,c+1)) or W, E
(vertical, cells (r,c),(r+1,c)). In a created 2x2 block, horizontal = N on top + S below; vertical = W left + E right,
so every domino moves away from its block-mate when it slides (N up, S down, W left, E right).

Step n -> n+1: shift by (1,1); destroy facing pairs (S directly above N, E directly left of W); slide; fill the holes,
which split uniquely into 2x2 blocks, each horizontal or vertical with probability 1/2.
"""
import numpy as np

N, S, W, E = 0, 1, 2, 3
DR = np.array([-1, 1, 0, 0]); DC = np.array([0, 0, -1, 1])


def inside(n):
    i = np.arange(2 * n)[:, None]; j = np.arange(2 * n)[None, :]
    return np.abs(i - n + 0.5) + np.abs(j - n + 0.5) <= n


def cells(d):
    """Both cells of every domino: arrays (r1, c1, r2, c2)."""
    r, c, t = d[:, 0], d[:, 1], d[:, 2]
    hor = t <= S
    return r, c, r + (~hor), c + hor


def occupancy(d, n):
    occ = np.zeros((2 * n, 2 * n), dtype=np.int32)
    r1, c1, r2, c2 = cells(d)
    np.add.at(occ, (r1, c1), 1); np.add.at(occ, (r2, c2), 1)
    return occ


def step(d, n, rng):
    """Tiling of order n (array k x 3) -> uniform tiling of order n+1."""
    m = n + 1
    if len(d):
        d = d.copy(); d[:, :2] += 1
        # destruction: index dominoes by (r, c, t) and find facing pairs
        key = {}
        for k, (r, c, t) in enumerate(d): key[(r, c, t)] = k
        kill = np.zeros(len(d), bool)
        for k, (r, c, t) in enumerate(d):
            if t == S:
                o = key.get((r + 1, c, N))
                if o is not None: kill[k] = kill[o] = True
            elif t == E:
                o = key.get((r, c + 1, W))
                if o is not None: kill[k] = kill[o] = True
        d = d[~kill]
        d[:, 0] += DR[d[:, 2]]; d[:, 1] += DC[d[:, 2]]
    ins = inside(m)
    occ = occupancy(d, m) if len(d) else np.zeros((2 * m, 2 * m), np.int32)
    assert occ.max() <= 1 and not (occ.astype(bool) & ~ins).any(), 'overlap or outside after sliding'
    hole = ins & (occ == 0)
    new = []
    for i, j in zip(*np.nonzero(hole)):  # row-major: the first hole met is a block's top-left
        if not hole[i, j]: continue
        assert hole[i, j + 1] and hole[i + 1, j] and hole[i + 1, j + 1], f'hole at {(i, j)} is not a 2x2 block'
        hole[i:i + 2, j:j + 2] = False
        if rng.random() < 0.5: new += [(i, j, N), (i + 1, j, S)]
        else: new += [(i, j, W), (i, j + 1, E)]
    if new: d = np.vstack([d, np.array(new)]) if len(d) else np.array(new)
    return d


def sample(n, seed=None, rng=None):
    rng = rng or np.random.default_rng(seed)
    d = np.zeros((0, 3), dtype=np.int64)
    for k in range(n): d = step(d, k, rng)
    occ = occupancy(d, n)
    assert (occ == inside(n)).all(), 'not a tiling'
    return d


def type_grid(d, n):
    """2n x 2n array: domino type at each cell, -1 outside."""
    g = -np.ones((2 * n, 2 * n), dtype=np.int8)
    r1, c1, r2, c2 = cells(d)
    g[r1, c1] = d[:, 2]; g[r2, c2] = d[:, 2]
    return g
