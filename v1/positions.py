from math import sqrt


def d(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

def mprint(m):
    print(*([round(v, 1) if type(v) in (float, int) else '*' for v in row] for row in m), sep="\n", end="\n\n")


if __name__ == '__main__':
    P = [(0, 0, 0), (0, 6, 2), (2, 5, 7), (5, 1, 3), (4, 2, 5), (2, 3, 1)]
    fixed = [0, 1, 2, 3]

    D = [[d(P[p], q) for q in P] for p in range(len(P))]

    mprint(D)

    