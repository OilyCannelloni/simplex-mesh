import random

from network import Network

random.seed(42)
network = Network(16)
node = network.nodes[0]

print("Initial")
print("\n".join(f"{id}: {info.distance.get()}" for id, info in node.node_info.items()))

for _ in range(100):
    node.try_measure_new_length()

print("True")
print("\n".join(f"{id}: {dst}" for id, dst in network.get_true_distances(0).items()))
print("Measured")
print("\n".join(f"{id}: {info.distance.get()}" for id, info in node.node_info.items()))