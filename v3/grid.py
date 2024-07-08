from __future__ import annotations

import abc
import dataclasses
import itertools
import math
import random
from config import config
from math import sqrt
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from abc import ABC
from typing import Generic, TypeVar, Type

random.seed(43)

class Point(ABC):
    dim = 0

    @property
    @abc.abstractmethod
    def xyz(self):
        pass

    @staticmethod
    def d2(origin: Point, target: Point):
        return origin.d2_to(target)

    @staticmethod
    def distance(origin: Point, target: Point):
        return math.sqrt(origin.d2_to(target))

    def d2_to(self, other: Point):
        return sum((a-b)*(a-b) for a, b in zip(self.xyz, other.xyz))

    def distance_to(self, other: Point):
        return math.sqrt(self.d2_to(other))

    @classmethod
    def random(cls, lower_bound=0, upper_bound=1) -> Point:
        assert upper_bound > lower_bound
        diff = upper_bound - lower_bound
        coords = tuple(random.random() * diff + lower_bound for _ in range(cls.dim))
        return cls.__call__(coords)

    def __repr__(self):
        return f"({', '.join([str(round(coord, 1)) for coord in self.xyz])})"

    def __getitem__(self, item):
        return self.xyz.__getitem__(item)


@dataclasses.dataclass
class Point2D(Point, ABC):
    dim = 2
    xyz: tuple[int, int] = (0, 0)

    def __repr__(self):
        return super().__repr__()


@dataclasses.dataclass
class Point3D(Point, ABC):
    dim = 3
    xyz: tuple[int, int, int] = (0, 0, 0)

    def __repr__(self):
        return super().__repr__()


class Network:
    _nodes: dict = {}

    def __init__(self):
        pass

    def add_node(self, node):
        self._nodes[node._id] = node

    def get_node(self, id: int):
        return self._nodes.get(id, None)

    def get_node_count(self):
        return config["grid"]["n_nodes"]

    def nodes(self):
        return self._nodes.values()


P = TypeVar("P", bound=Point)

class Grid(Generic[P]):
    NODE_REACH = config["node"]["max_reach"]
    real_node_coords: list[P]

    def __init__(self, point_type: Type[P], n_nodes: int, grid_size: int, sd: float = 0.2):
        self.P = point_type
        self.n_nodes = n_nodes
        self.grid_size = grid_size
        self.sd = sd
        self.real_node_coords = []
        self.setup()

    def setup(self):
        for i in range(self.n_nodes):
            while True:
                point = self.P.random(upper_bound=self.grid_size)
                for target in self.real_node_coords:
                    if point.distance_to(target) < config["grid"]["min_node_real_distance"]:
                        break
                else:
                    self.real_node_coords.append(point)
                    break

    def get_true_position(self, node_id: int):
        return self.real_node_coords[node_id]

    def get_true_distance(self, origin_id: int, target_id: int, override_range=False):
        p1, p2 = self.real_node_coords[origin_id], self.real_node_coords[target_id]
        distance = p1.distance_to(p2)
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

    def get_hop_counts_from(self, origin):
        origins = [origin]
        targets = set()
        visited = set()
        hops = [[origin]]
        while len(visited) < self.n_nodes:
            visited.update(origins)
            for node in origins:
                targets.update(self.get_neighbors_of(node))
            targets.difference_update(visited)
            hops.append(list(targets))
            origins = targets.copy()
        return hops

    def plot(self, network: Network):
        fig, ax = plt.subplots()
        fig.set_size_inches(10, 10)

        xs = [point[0] for point in self.real_node_coords]
        ys = [point[1] for point in self.real_node_coords]

        lines = []
        for p1, p2 in itertools.product(range(self.n_nodes), repeat=2):
            if p1 == p2:
                continue
            if self.get_true_distance(p1, p2) is None:
                continue
            lines.append([self.real_node_coords[p1].xyz, self.real_node_coords[p2].xyz])

        lc = LineCollection(lines, zorder=1)
        ax.add_collection(lc)

        ax.scatter(x=xs, y=ys, c=["y" if n.is_anchor else "g" if n.anchor_reached else "r" for n in network.nodes()],
                   zorder=2)
        for id in range(len(self.real_node_coords)):
            plt.annotate(str(id), (xs[id]+.06, ys[id]+.06), zorder=3)

        plt.show()


if __name__ == '__main__':

    r = Point2D.random(upper_bound=5)
    print(r)

    r2 = Point3D.random(5, 6)
    print(r2)

    r3 = Point3D.random(upper_bound=2)
    print(r3)
    print(r2.distance_to(r3))
