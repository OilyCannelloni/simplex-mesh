from math import sqrt
from matplotlib import pyplot as plt
from itertools import product

nPoints = 14
points = {0:(0, 0), 1:(0, 10), 2:(10, 0), 3:(1, 6), 4:(7, 5), 5:(8, 4), 6:(3, 9),
          7:(5, 4), 8:(5, 10), 9:(2, 3), 10:(8, 1), 11:(6, 2), 12: (4, 1), 13:(5, 0)}

adj = {
    0: [9, 12],
    1: [3, 6, 8],
    2: [5, 10],
    3: [1, 6, 7, 9],
    4: [5, 6, 7, 8, 11],
    5: [2, 4, 10, 11],
    6: [1, 3, 4, 7, 8],
    7: [3, 4, 6, 9, 11, 12],
    8: [4, 6, 1],
    9: [0, 3, 7, 12],
    10: [2, 5, 11, 12],
    11: [4, 5, 7, 10, 12, 13],
    12: [0, 7, 9, 10, 11, 13],
    13: [11, 12]
}

fixed = [0, 1, 2]


# validate ADJ
for x, xns in adj.items():
    for n in xns:
        if x not in adj[n]:
            raise AssertionError("jebac pis", x, n)


def _d(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def heron(a, b, c):
    p = (a + b + c) / 2
    return sqrt(r) if (r := p*(p-a)*(p-b)*(p-c)) > 0 else 0


def quad_distance(ab, bc, cd, ad, ac):
    p = heron(ac, cd, ad) + heron(ab, bc, ac)
    q = (ab ** 2 - bc ** 2 + cd ** 2 - ad ** 2) ** 2
    return sqrt(16 * p ** 2 + q) / (2 * ac)


def measure_distance(px, py):
    if py not in adj[px]:
        return 0
    return _d(points[px], points[py])


def get_xy(p):
    if p not in fixed:
        return None
    return points[p]


def get_distances_from_vertex(v_origin):
    distances = [0] * nPoints

    # Measure distance to neighbors
    for p in range(nPoints):
        d = measure_distance(v_origin, p)
        if d != 0:
            distances[p] = d

    completed = set(adj[v_origin])
    while len(completed) < nPoints - 1:
        for n1, n2 in product(completed, repeat=2):
            if n1 not in adj[n2]:
                continue

            for target in adj[n1]:
                if distances[target] != 0:
                    continue
                if target == v_origin:
                    continue
                if target in adj[n2]:
                    distances[target] = quad_distance(
                        ab=distances[n1],
                        bc=distances[n2],
                        cd=measure_distance(n2, target),
                        ad=measure_distance(n1, target),
                        ac=measure_distance(n1, n2)
                    )
                    completed.add(target)

    return distances


if __name__ == "__main__":
    DM = [[0]*nPoints for _ in range(nPoints)]
    for v in range(nPoints):
        DM[v] = get_distances_from_vertex(v)

    print(*DM, sep="\n")



