import numpy
import numpy as np
from math import sqrt
import sympy
from simplexmesh.grid import Point2D


def determinant_roots(d):
    m = np.array([[0,       d[0][1], d[0][2],       0, 1],
                  [d[0][1], 0      , d[1][2], d[1][3], 1],
                  [d[0][2], d[1][2],       0, d[2][3], 1],
                  [     1j, d[1][3], d[2][3],       0, 1],
                  [      1,       1,       1,       1, 0]])

    det = np.linalg.det(m)

    m = np.delete(m, 0, 0)
    m = np.delete(m, 3, 1)

    xdet = np.linalg.det(m)

    a, b, c = -xdet.imag, det.imag - xdet.real, det.real
    d2 = b*b-4*a*c
    if d2 < 0:
        return []

    rd = sqrt(d2)
    roots = [(-b - rd)/(2 * a), (-b + rd)/(2 * a)]
    return [sqrt(r) for r in roots if r > 0]


def sympy_determinant_roots(d):
    x = sympy.Symbol('x')
    m = [[      0, d[0][1], d[0][2],       x, 1],
         [d[0][1],       0, d[1][2], d[1][3], 1],
         [d[0][2], d[1][2],       0, d[2][3], 1],
         [      x, d[1][3], d[2][3],       0, 1],
         [      1,       1,       1,       1, 0]]

    M = sympy.Matrix(m)
    poly = sympy.simplify(M.det(method='berkowitz').as_poly())

    roots = [float(x) for x in sympy.roots(poly).keys() if not x.as_real_imag()[1]]
    results = [sqrt(abs(x)) for x in roots if x > 0]

    return results


def simplex_diagonal(p0p1, p0p2, p1p2, p1p3, p2p3, use_sympy=False):
    d = [
        [0, p0p1, p0p2, 0],
        [p0p1, 0, p1p2, p1p3],
        [p0p2, p1p2, 0, p2p3],
        [0, p1p3, p2p3, 0],
    ]

    for row in d:
        for i in range(len(row)):
            row[i] **= 2

    return determinant_roots(d) if not use_sympy else sympy_determinant_roots(d)


def get_position_by_anchors_2d(a: list["Point2D"], d: list[float]):
    a0 = a.pop()
    d0 = d.pop()

    A = numpy.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            A[j, i] = 2*(a[j][i] - a0[i])

    B = numpy.zeros((2, 1))
    for i in range(2):
        B[i, 0] = (d0**2-d[i]**2) - (a0[0]**2-a[i][0]**2) - (a0[1]**2-a[i][1]**2)

    position = numpy.linalg.solve(A, B)

    p = tuple(position.flatten())
    return Point2D(p)


def get_position_by_anchors_2d_lls(a: list["Point2D"], d: list[float]):
    a0 = a.pop()
    d0 = d.pop()
    n_equations = len(a)
    assert n_equations == len(d)

    A = numpy.zeros((n_equations, 2))
    for i in range(n_equations):
        for j in range(2):
            A[i, j] = 2*(a[i][j] - a0[j])

    B = numpy.zeros((n_equations, 1))
    for i in range(n_equations):
        B[i, 0] = (d0**2-d[i]**2) - (a0[0]**2-a[i][0]**2) - (a0[1]**2-a[i][1]**2)

    position = numpy.linalg.lstsq(A, B, rcond=None)[0]
    p = tuple(position.flatten())
    return Point2D(p)




if __name__ == '__main__':
    anchors = [Point2D((-1, 6)), Point2D((8, 6)), Point2D((9, -1)), Point2D((-4, -1)), Point2D((-1, 11))]
    distances = [5.0, 6.0, 7.0, 8.0, 9.0]
    get_position_by_anchors_2d_lls(anchors, distances)


    # t = time.time()
    # simplex_diagonal(1, 2, 3, 4, 1)
    # print(time.time() - t)
    #
    # for _ in range(100):
    #     d = (np.random.rand(5) * 10) ** 2
    #
    #     drs = sorted(simplex_diagonal(*d))
    #     sdrs = sorted(simplex_diagonal(*d, use_sympy=True))
    #
    #     for r1, r2 in zip(drs, sdrs):
    #         if abs(r1 - r2) > 0.0001:
    #             print(drs, sdrs)
    #             break
