from __future__ import annotations

import itertools
import random
from config import config
from math import sqrt
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

random.seed(42)

class Grid:
    NODE_REACH = config["node"]["max_reach"]

    real_node_coords: list[tuple[float, float]]

    def __init__(self, n_nodes: int, grid_size: int, sd: float = 0.2):
        self.n_nodes = n_nodes
        self.grid_size = grid_size
        self.sd = sd
        self.real_node_coords = []
        self.setup()

    def setup(self):
        for i in range(self.n_nodes):
            while True:
                point = (random.random() * self.grid_size, random.random() * self.grid_size)
                for target in self.real_node_coords:
                    if self._d(point, target) < config["grid"]["min_node_real_distance"]:
                        break
                else:
                    self.real_node_coords.append(point)
                    break


    def _d(self, p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def get_true_distance(self, origin_id: int, target_id: int, override_range=False):
        p1, p2 = self.real_node_coords[origin_id], self.real_node_coords[target_id]
        distance = self._d(p1, p2)
        if not override_range and distance > Grid.NODE_REACH:
            return None
        return distance

    def get_measured_distance(self, origin_id: int, target_id: int) -> float:
        if self.sd > 0:
            return random.normalvariate(self.get_true_distance(origin_id, target_id), self.sd)
        return self.get_true_distance(origin_id, target_id)

    def get_neighbors_of(self, origin_id: int):
        return [id for id in range(len(self.real_node_coords))
                if id != origin_id
                and self.get_true_distance(origin_id, id) is not None]

    def plot(self):
        fig, ax = plt.subplots()

        xs = [tpl[0] for tpl in self.real_node_coords]
        ys = [tpl[1] for tpl in self.real_node_coords]
        ax.scatter(x=xs, y=ys)

        for id in range(len(self.real_node_coords)):
            plt.annotate(str(id), (xs[id]+.06, ys[id]+.06))

        lines = []
        for p1, p2 in itertools.product(range(self.n_nodes), repeat=2):
            if p1 == p2:
                continue
            if self.get_true_distance(p1, p2) is None:
                continue
            lines.append([(self.real_node_coords[p1]), self.real_node_coords[p2]])

        lc = LineCollection(lines)
        ax.add_collection(lc)
        plt.show()


grid = Grid(config["grid"]["n_nodes"], config["grid"]["size"], config["measurement"]["sd"])


class Network:
    _nodes: dict[int, Node] = {}

    def __init__(self):
        pass

    def add_node(self, node):
        self._nodes[node._id] = node

    def get_node(self, id: int) -> Node:
        return self._nodes.get(id, None)


network = Network()