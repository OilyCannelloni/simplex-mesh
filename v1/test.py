import itertools

from simplex import Network


n_points = 8
network = Network(n_points)


# show_points(list(points.values()), lines=adj)
# exit()




distances = [[set()] * n_points for _ in range(n_points)]
for origin in range(n_points):
    for n in network.adj[origin]:
        distances[origin][n] = {round(network.md(origin, n), 3)}

    completed = network.adj[origin].copy()
    iterations = 7

    while len(completed) < n_points - 1 and iterations > 0:
        iterations -= 1
        for a, b, c in itertools.combinations(completed, 3):
            if not (a in network.adj[b] and b in network.adj[c] and c in network.adj[a]):
                continue

            if origin in (a, b, c) or a == b or b == c or a == c:
                continue

            for target in network.adj[a].intersection(network.adj[b]).intersection(network.adj[c]):
                if target in completed or target in (origin, a, b, c):
                    continue

                possible_dists = network.simplex_diagonal(origin, a, b, c, target)
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
        print(f"{f'{[*dist_set]} / {round(network._md(origin, target), 2)}':25}", end='')
    print()