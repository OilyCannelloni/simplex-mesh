import itertools
import random
import sympy
from math import sqrt
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from plotting_extensions import Annotation3D


random.seed(504337921)
DOMAIN = (8, 8, 8)
nPoints = 4
MAX_DISTANCE = 9
MIN_POINT_DISTANCE = 1.9


def show_points(pts, lines=None):
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    plt.axis('off')
    font = {
        'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 12,
    }

    for i, p in enumerate(pts):
        ax.scatter(p[0], p[1], p[2], c='r')
        ax.text(p[0], p[1], p[2], str(i), fontdict=font)

    if lines is not None:
        for v, ns in lines.items():
            for n in ns:
                x = np.linspace(pts[v][0], pts[n][0], 100)
                y = np.linspace(pts[v][1], pts[n][1], 100)
                z = np.linspace(pts[v][2], pts[n][2], 100)
                ax.plot(x, y, z)

    ax.set_xlim(0, DOMAIN[0] + 1)
    ax.set_ylim(0, DOMAIN[1] + 1)
    ax.set_zlim3d(0, DOMAIN[2] + 1)
    plt.show()


def _d(i1, i2):
    p1, p2 = points[i1], points[i2]
    return _dx(p1, p2)


def _dx(p1, p2):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)


def md(p1, p2):
    # if p1 not in adj[p2]:
    #     return None
    return _d(p1, p2)


def mprint(m):
    print(*([round(v, 1) if type(v) in (float, int) else '*' for v in row] for row in m), sep="\n", end="\n\n")


def simplex_diagonal(p0, p1, p2, p3, p4, verbose=False):
    d = [
        [0, md(p0, p1), md(p0, p2), md(p0, p3), 0],
        [md(p0, p1), 0, md(p1, p2), md(p1, p3), md(p1, p4)],
        [md(p0, p2), md(p1, p2), 0, md(p2, p3), md(p2, p4)],
        [md(p0, p3), md(p1, p3), md(p2, p3), 0, md(p3, p4)],
        [0, md(p1, p4), md(p2, p4), md(p3, p4), 0]
    ]

    if verbose:
        mprint(d)

    for row in d:
        for i in range(len(row)):
            row[i] **= 2

    if verbose:
        mprint(d)

    x = sympy.Symbol('x')
    m = [[0,         d[0][1],    d[0][2],    d[0][3],       x,    1],
        [d[0][1],   0,          d[1][2],    d[1][3],    d[1][4],    1],
        [d[0][2],   d[1][2],    0,          d[2][3],    d[2][4],    1],
        [d[0][3],   d[1][3],    d[2][3],    0,          d[3][4],    1],
        [x,      d[1][4],    d[2][4],    d[3][4],    0,          1],
        [1,         1,          1,          1,          1,          0]]

    M = sympy.Matrix(m)
    poly = sympy.simplify(M.det(method='berkowitz').as_poly())
    if verbose:
        print(poly)

    roots = sympy.roots(poly).keys()
    results = [sqrt(abs(x)) for x in roots if abs(x) > 0]

    if verbose:
        print(results)

    return results


# generate graph
points = {}
for i in range(nPoints):
    while True:
        p = tuple(random.random() * d for d in DOMAIN)
        for q in points.values():
            if _dx(p, q) < MIN_POINT_DISTANCE:
                break
        else:
            points[i] = p
            break

adj = {}
for i in points.keys():
    if adj.get(i) is None:
        adj[i] = set()

    distances = [(t, _d(i, t)) for t in range(nPoints)]
    distances.sort(key=lambda x: x[1])
    targets = [t for (t, d) in distances if d < MAX_DISTANCE and d != 0]
    # if len(targets) <= 3:
    #     print(i)
    #     targets = [t for t, d in distances[:5]]

    for t in targets:
        if adj.get(t) is None:
            adj[t] = set()

        adj[t].add(i)
        adj[i].add(t)

# validate ADJ
for v, ns in adj.items():
    for n in ns:
        if n not in adj[v]:
            raise AssertionError("Adjacency map incorrect at", v, t)




if __name__ == '__main__':
    # simplex_diagonal(5, 2, 3, 9, 7, verbose=True)
    # print(_md(5, 7))
    # show_points(list(points.values()), lines=adj)
    # exit()

    distances = [[set()] * nPoints for _ in range(nPoints)]
    for origin in range(nPoints):
        for n in adj[origin]:
            distances[origin][n] = {round(md(origin, n), 3)}

        completed = adj[origin].copy()
        iterations = 7

        while len(completed) < nPoints - 1 and iterations > 0:
            iterations -= 1
            for a, b, c in itertools.combinations(completed, 3):
                if not (a in adj[b] and b in adj[c] and c in adj[a]):
                    continue

                if origin in (a, b, c) or a == b or b == c or a == c:
                    continue

                for target in adj[a].intersection(adj[b]).intersection(adj[c]):
                    if target in completed or target in (origin, a, b, c):
                        continue

                    possible_dists = simplex_diagonal(origin, a, b, c, target)
                    rounded_dists = {round(x, 2) for x in possible_dists}

                    if len(distances[origin][target]) == 0:
                        distances[origin][target] = rounded_dists
                    else:
                        distances[origin][target].intersection_update(rounded_dists)

                    if len(distances[target][origin]) == 0:
                        distances[target][origin] = rounded_dists
                    else:
                        distances[target][origin].intersection_update(rounded_dists)

                    if len(distances[origin][target]) == 1:
                        completed.add(target)



    for origin, row in enumerate(distances):
        for target, dist_set in enumerate(row):
            print(f"{f'{[*dist_set]} / {round(_d(origin, target), 2)}':25}", end='')
        print()
