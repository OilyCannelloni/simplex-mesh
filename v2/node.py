from __future__ import annotations
import itertools
import statistics
from dataclasses import dataclass
from functools import reduce
from math import sqrt
from random import sample, normalvariate

from algorithm import simplex_diagonal

DISTANCE_SET_THRESHOLD = 0.5
NODE_REACH = 6


class NetworkMeasurement:
    def __init__(self, id_point_map: dict[int, tuple[float, ...]], sd=0):
        self.id_point_map = id_point_map
        self.sd = sd

    @staticmethod
    def exact_d(p1: tuple[float, ...], p2: tuple[float, ...]) -> float:
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)

    def id_exact_d(self, id1, id2):
        return self.exact_d(self.id_point_map[id1], self.id_point_map[id2])

    def get_measurement_result(self, origin, target):
        return normalvariate(self.id_exact_d(origin, target), self.sd) if self.sd > 0 else self.id_exact_d(origin, target)


class DistanceSet:
    def __init__(self, dist=None, true=None):
        self._set = []
        self.cached_value = dist
        self.bounding_box = None
        self.true = true

    def __str__(self):
        if self.cached_value is not None:
            return f"\033[32m{round(self.cached_value, 2)}\033[39m   (true {round(self.true, 2)})"
        return str([round(x, 2) for x in self._set])

    def add(self, x):
        if self.cached_value is None:
            self._set.append(x)
            return

        if self.check_bounding_box(x):
            self._set.append(x)
            self.update_cached_value()

    def extend(self, *args):
        for x in args:
            self.add(x)
        self.try_reduce()

    def update_cached_value(self):
        self.cached_value = statistics.median(self._set)
        self.bounding_box = (
            self.cached_value - 2 * DISTANCE_SET_THRESHOLD, self.cached_value + 2 * DISTANCE_SET_THRESHOLD)

    def check_bounding_box(self, x):
        if self.bounding_box is None:
            return True
        return self.bounding_box[0] < x < self.bounding_box[1]

    def try_reduce(self):
        if len(self._set) <= 2:
            for sol in self._set:
                if sol < 0.3 * NODE_REACH:
                    self._set.remove(sol)

        for sol1, sol2, sol3 in itertools.combinations(self._set, 3):
            if (abs(sol1 - sol2) < DISTANCE_SET_THRESHOLD and abs(sol1 - sol3) < DISTANCE_SET_THRESHOLD
                    and abs(sol2 - sol3) < DISTANCE_SET_THRESHOLD):
                self.update_cached_value()

    def get(self):
        return self.cached_value

    def getr(self):
        return round(self.cached_value, 2) if self.cached_value is not None else "n/a"

    def length(self):
        return len(self._set)


@dataclass
class NodeInfo:
    node: Node
    is_neighbor: bool = False
    distance: DistanceSet = DistanceSet()

    def __eq__(self, other: NodeInfo):
        return self.node.id == other.node.id


class Node:
    def __init__(self, id, exact_xyz):
        self.network_nodes = {}
        self.id = id
        self.exact_xyz = exact_xyz
        self.node_info: dict[int, NodeInfo] = {}
        self.neighbor_ids = []

    def update_network_info(self, network_nodes: dict[int, Node], neighbor_info: dict[int, float], true_info):
        self.network_nodes = network_nodes
        for id, node in network_nodes.items():
            true_distance = NetworkMeasurement.exact_d(true_info[self.id], true_info[id])
            self.node_info[id] = NodeInfo(node=node, distance=DistanceSet(true=true_distance))

        for id, dist in neighbor_info.items():
            self.node_info[id].distance.cached_value = dist

        self.neighbor_ids = neighbor_info.keys()

    def upsert_nodeinfo(self, target_id, solutions):
        if target_id not in self.node_info.keys():
            self.node_info[target_id] = NodeInfo(self.network_nodes[target_id])
        self.node_info[target_id].distance.extend(*solutions)

    def get_all_nodes_known_distance(self) -> list[NodeInfo]:
        return [node for node in self.node_info.values() if node.distance.get() is not None]

    def get_random_gate(self) -> list[NodeInfo]:
        keys_list = self.get_all_nodes_known_distance()
        return sample(keys_list, 3)

    def ask_for_distance(self, origin: Node, target_id: int) -> float | None:
        return origin.node_info[target_id].distance.get()

    def ask_for_all_completed_ids(self, origin: Node) -> set[int]:
        return set([nodeinfo.node.id for nodeinfo in origin.get_all_nodes_known_distance()])

    def try_measure_new_length(self):
        gate = self.get_random_gate()

        p0p1 = gate[0].distance.get()
        p0p2 = gate[1].distance.get()
        p0p3 = gate[2].distance.get()

        p1p2 = self.ask_for_distance(gate[0].node, gate[1].node.id)
        p2p3 = self.ask_for_distance(gate[1].node, gate[2].node.id)
        p1p3 = self.ask_for_distance(gate[0].node, gate[2].node.id)

        if None in (p1p2, p2p3, p1p3):
            return None

        gate_targets = [self.ask_for_all_completed_ids(nodeinfo.node) for nodeinfo in gate]
        target_ids = gate_targets[0].intersection(gate_targets[1]).intersection(gate_targets[2])
        known_distance_ids = list(map(lambda n: n.node.id, self.get_all_nodes_known_distance()))

        for target_id in target_ids:
            # if target_id in known_distance_ids or target_id == self.id:
            #     continue
            if target_id in self.neighbor_ids or target_id == self.id:
                continue

            p1p4 = self.ask_for_distance(gate[0].node, target_id)
            p2p4 = self.ask_for_distance(gate[1].node, target_id)
            p3p4 = self.ask_for_distance(gate[2].node, target_id)

            if None in (p1p4, p2p4, p3p4):
                return None

            solutions = simplex_diagonal(p0p1, p0p2, p0p3, p1p2, p2p3, p1p3, p1p4, p2p4, p3p4)
            self.upsert_nodeinfo(target_id, solutions)
            self.network_nodes[target_id].upsert_nodeinfo(self.id, solutions)

            print(
                f"{self.id} -> {target_id} via {[x.node.id for x in gate]}: {str(self.node_info[target_id].distance)}")
