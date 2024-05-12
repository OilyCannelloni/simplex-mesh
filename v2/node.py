from __future__ import annotations
import itertools
from dataclasses import dataclass
from functools import reduce
from random import sample

from algorithm import simplex_diagonal

DISTANCE_SET_THRESHOLD = 0.4
NODE_REACH = 6


class DistanceSet:
    def __init__(self, dist=None):
        self._set = []
        self.cached_value = dist

    def add(self, x):
        self._set.append(x)
        self.try_reduce()

    def extend(self, arr):
        self._set.extend(arr)
        self.try_reduce()

    def try_reduce(self):
        if len(self._set) <= 2:
            for sol in self._set:
                if sol < 0.5 * NODE_REACH:
                    self._set.remove(sol)
            return

        for sol1, sol2 in itertools.combinations(self._set, 2):
            if abs(sol1 - sol2) < DISTANCE_SET_THRESHOLD:
                self.cached_value = (sol1 + sol2) / 2

    def get(self):
        return self.cached_value

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
    def __init__(self, id):
        self.network_nodes = {}
        self.id = id
        self.node_info: dict[int, NodeInfo] = {}

    def update_network_info(self, network_nodes, neighbor_info):
        self.network_nodes = network_nodes
        for id, node in network_nodes.items():
            self.node_info[id] = NodeInfo(node=node, distance=DistanceSet())

        for id, dist in neighbor_info.items():
            self.node_info[id].distance.cached_value = dist

    def upsert_nodeinfo(self, target_id, solutions):
        if target_id not in self.node_info.keys():
            self.node_info[target_id] = NodeInfo(self.network_nodes[target_id])
        self.node_info[target_id].distance.extend(solutions)

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
            if target_id in known_distance_ids or target_id == self.id:
                continue

            p1p4 = self.ask_for_distance(gate[0].node, target_id)
            p2p4 = self.ask_for_distance(gate[1].node, target_id)
            p3p4 = self.ask_for_distance(gate[2].node, target_id)

            if None in (p1p4, p2p4, p3p4):
                return None

            solutions = simplex_diagonal(p0p1, p0p2, p0p3, p1p2, p2p3, p1p3, p1p4, p2p4, p3p4)
            self.upsert_nodeinfo(target_id, solutions)
            print(f"{self.id} -> {target_id} via {[x.node.id for x in gate]}: {solutions}")





