from __future__ import annotations

import abc
import dataclasses
import itertools
import math
import random
from simplexmesh.config import config
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
from abc import ABC
from typing import Generic, TypeVar, Type, Collection, TYPE_CHECKING

if TYPE_CHECKING:
    from node import Node


"""
To preserve the same network in testing phase
"""
random.seed(43)


"""Abstract class for a N-dimensional point in an Euclidean Space."""
class Point(ABC):
    """Dimension of the point, eg. 3 for XYZ"""
    dim = 0

    @property
    @abc.abstractmethod
    def xyz(self):
        """A tuple-like structure that contains the coordinates."""
        pass

    @staticmethod
    def d2(origin: Point, target: Point):
        """Returns the squared distance between two points"""
        return origin.d2_to(target)

    @staticmethod
    def distance(origin: Point, target: Point):
        """Returns the distance between two points"""
        return math.sqrt(origin.d2_to(target))

    def d2_to(self, other: Point):
        """Returns the square of the distance to another point"""
        return sum((a-b)*(a-b) for a, b in zip(self.xyz, other.xyz))

    def distance_to(self, other: Point):
        """Returns the distance to another point"""
        return math.sqrt(self.d2_to(other))

    @classmethod
    def random(cls, lower_bound=0, upper_bound=1) -> Point:
        """
        Creates a new object of a subclass of Point, which has random coordinates in the given range
        :param lower_bound: minimal value of coordinates
        :param upper_bound: maximal value of coordinates
        :return: a Point with random coordinates
        """
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
    xyz: tuple[float, ...] = (0, 0)

    def __repr__(self):
        return super().__repr__()


@dataclasses.dataclass
class Point3D(Point, ABC):
    dim = 3
    xyz: tuple[float, ...] = (0, 0, 0)

    def __repr__(self):
        return super().__repr__()


class Network:
    """
    Takes care of communication between nodes.
    Any node can get access to another by its ID (address)
    """
    _nodes: dict = {}

    def __init__(self):
        pass

    def add_node(self, node) -> None:
        self._nodes[node._id] = node

    def get_node(self, id: int) -> Node | None:
        return self._nodes.get(id, None)

    def get_node_count(self) -> int:
        return config["grid"]["n_nodes"]

    def nodes(self) -> Collection[Node]:
        return self._nodes.values()


P = TypeVar("P", bound=Point)

class Grid(Generic[P]):
    """
    Manages the physical placement of the network nodes.
    Works in either 2D or 3D, a point_type parameter needs to be provided.
    """

    """Maximum distance below which nodes can communicate with each other"""
    NODE_REACH = config["node"]["max_reach"]

    def __init__(self, point_type: Type[P], n_nodes: int, grid_size: int, sd: float = 0.2):
        """
        :param point_type: Point2D or Point3D
        :param n_nodes: Number of nodes in the network
        :param grid_size: Size of a single dimension in units. It is assumed the grid is a square or a cube
        :param sd: Standard deviation for the normal distribution used to provide simulated measurement results.
        The distribution is always centered on the real value.
        """
        self.P = point_type
        self.n_nodes = n_nodes
        self.grid_size = grid_size
        self.sd = sd
        self.real_node_coords: list[P] = []
        self.setup()

    def setup(self):
        """
        Creates the points on the grid, such that no two lie closer together than a constant given in configuration.
        :return: None
        """
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
        """
        Returns the real position of a node with given ID / Address
        :param node_id: ID of node
        :return: Point object describing the position
        """
        return self.real_node_coords[node_id]

    def get_true_distance(self, origin_id: int, target_id: int, override_range=False):
        """
        Returns the real distance between two points with given IDs.
        If the distance is larger than maximal node reach, returns None
        :param origin_id: ID of first node
        :param target_id: ID of second node
        :param override_range: Return the true distance even if it's larger than maximal range of node.
        :return: True distance between the nodes
        """
        p1, p2 = self.real_node_coords[origin_id], self.real_node_coords[target_id]
        distance = p1.distance_to(p2)
        if not override_range and distance > Grid.NODE_REACH:
            return None
        return distance

    def get_measured_distance(self, origin_id: int, target_id: int) -> float:
        """
        Returns a distorted distance between two nodes to simulate a real environment.
        Distortion is given by the normal distribution with SD that can be set up as a parameter of the Grid class.
        :param origin_id: ID of first node
        :param target_id: ID of second node
        :return: A value close to the true distance between the nodes.
        """
        if self.sd > 0:
            return random.normalvariate(self.get_true_distance(origin_id, target_id), self.sd)
        return self.get_true_distance(origin_id, target_id)

    def get_neighbors_of(self, origin_id: int) -> list[int]:
        """
        Returns a list of IDs of nodes in range of the origin node
        :param origin_id: ID of origin node
        :return: A list of IDs of neighboring nodes
        """
        return [id for id in range(len(self.real_node_coords))
                if id != origin_id
                and self.get_true_distance(origin_id, id) is not None]

    def get_hop_counts_from(self, origin):
        """
        Traverses the network using the BFS algorithm in order to find minimal hop counts
        to get from origin to all nodes in the network.
        :param origin:
        :return: A list of lists with structure
            number_of_hops: [node_1, node_2, ...]
            where n_hops is between 0 (origin) and a maximum number of hops to reach any node.
        """
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
        """
        Plots the network and connections.
        :param network: Network describing the nodes
        :return: None
        """
        fig, (ax, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(20, 10)

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
            ax.annotate(str(id), (xs[id]+.06, ys[id]+.06), zorder=3)

        calc_xs = [node.position[0] for node in network.nodes()]
        calc_ys = [node.position[1] for node in network.nodes()]
        lines2 = [[node.position.xyz, self.real_node_coords[node._id].xyz] for node in network.nodes()]

        lc2 = LineCollection(lines2, zorder=1)
        ax2.set_xlim(0, self.grid_size)
        ax2.set_ylim(0, self.grid_size)
        ax2.add_collection(lc2)
        ax2.scatter(calc_xs, calc_ys, c="r", zorder=2)
        for id in range(len(self.real_node_coords)):
            ax2.annotate(str(id), (calc_xs[id]+.06, calc_ys[id]+.06), zorder=3)

        plt.show()


if __name__ == '__main__':

    r = Point2D.random(upper_bound=5)
    print(r)

    r2 = Point3D.random(5, 6)
    print(r2)

    r3 = Point3D.random(upper_bound=2)
    print(r3)
    print(r2.distance_to(r3))
