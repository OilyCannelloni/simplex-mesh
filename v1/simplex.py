import random
from math import sqrt

import sympy


class Network:
    DOMAIN = (8, 8, 8)
    MAX_NODE_REACH_DISTANCE = 9
    MIN_POINT_DISTANCE = 1.9

    def __init__(self, n_points: int):
        self.nodes = []
        self.points = {}
        for i in range(n_points):
            while True:
                p = tuple(random.random() * d for d in self.DOMAIN)
                for q in self.points.values():
                    if self._d(p, q) < self.MIN_POINT_DISTANCE:
                        break
                else:
                    self.points[i] = p
                    break

    @staticmethod
    def _d(p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)

    def true_d(self, i1, i2):
        return self._d(self.points[i1], self.points[i2])

    def add_node(self, node):
        self.nodes.append(node)
        return len(self.nodes) - 1

    def request_distance(self, origin, target):
        return self.nodes[origin].md(target)


class Node:
    def __init__(self, network: Network, id: int):
        self.network = network
        self.id = id
        self.neighbors = []

    def get_neighbors(self):
        for point_id, point in self.network.points.items():
            if self.network.true_d(self.id, point_id) > self.network.MAX_NODE_REACH_DISTANCE:
                self.neighbors.append(point_id)

    def md(self, origin, target):
        return self.network.true_d(origin, target)


    @staticmethod
    def mprint(m):
        print(*([round(v, 1) if type(v) in (float, int) else '*' for v in row] for row in m), sep="\n", end="\n\n")

    def simplex_diagonal(self, p0, p1, p2, p3, p4, verbose=False):
        d = [
            [0, self.md(p0, p1), self.md(p0, p2), self.md(p0, p3), 0],
            [self.md(p0, p1), 0, self.md(p1, p2), self.md(p1, p3), self.md(p1, p4)],
            [self.md(p0, p2), self.md(p1, p2), 0, self.md(p2, p3), self.md(p2, p4)],
            [self.md(p0, p3), self.md(p1, p3), self.md(p2, p3), 0, self.md(p3, p4)],
            [0, self.md(p1, p4), self.md(p2, p4), self.md(p3, p4), 0]
        ]

        if verbose:
            self.mprint(d)

        for row in d:
            for i in range(len(row)):
                row[i] **= 2

        if verbose:
            self.mprint(d)

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


