import random

from network import Network

random.seed(42)

n_nodes = 16
network = Network(n_nodes, sd=0.5)

print("Initial")
na = 0
for origin_id, node in network.nodes.items():
    print("\t".join(f"{id}: {info.distance.getr():7}" for id, info in node.node_info.items()))
    na += sum(1 for id, info in node.node_info.items() if info.distance.getr() == "n/a")
print(na - n_nodes)

for _ in range(50):
    print(f"ITERATION {_}")
    for node in network.nodes.values():
        node.try_measure_new_length()


na = 0
abs_diffs = []



for origin_id, origin_node in network.nodes.items():
    print(f'{f"[{origin_id}]:":8}', end="")
    for target_id, target_info in origin_node.node_info.items():
        if target_id == origin_id:
            print(" " * 8, end="")
            continue
        d = target_info.distance.getr()
        print(f'{f"{target_id}: {d}":8}', end="")
        if d == "n/a":
            na += 1
            continue

        diff = abs(d - network.network_measurement.id_exact_d(origin_id, target_id))
        abs_diffs.append(diff)
    print()


print("N/A:", na)
print("AVG ABS DIFF:", sum(abs_diffs) / len(abs_diffs))
print("MAX ABS DIFFS", sorted(abs_diffs)[-10:])
