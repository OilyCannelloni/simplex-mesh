from math import sqrt

import sympy


def simplex_diagonal(p0p1, p0p2, p0p3, p1p2, p2p3, p1p3, p1p4, p2p4, p3p4, verbose=False):
    d = [
        [0, p0p1, p0p2, p0p3, 0],
        [p0p1, 0, p1p2, p1p3, p1p4],
        [p0p2, p1p2, 0, p2p3, p2p4],
        [p0p3, p1p3, p2p3, 0, p3p4],
        [0, p1p4, p2p4, p3p4, 0]
    ]

    for row in d:
        for i in range(len(row)):
            row[i] **= 2

    x = sympy.Symbol('x')
    m = [[0, d[0][1], d[0][2], d[0][3], x, 1],
         [d[0][1], 0, d[1][2], d[1][3], d[1][4], 1],
         [d[0][2], d[1][2], 0, d[2][3], d[2][4], 1],
         [d[0][3], d[1][3], d[2][3], 0, d[3][4], 1],
         [x, d[1][4], d[2][4], d[3][4], 0, 1],
         [1, 1, 1, 1, 1, 0]]

    M = sympy.Matrix(m)
    poly = sympy.simplify(M.det(method='berkowitz').as_poly())
    if verbose:
        print(poly)

    roots = sympy.roots(poly).keys()
    results = [sqrt(abs(x)) for x in roots if abs(x) > 0]

    if verbose:
        print(results)

    return results
