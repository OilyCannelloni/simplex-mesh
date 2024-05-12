from math import sqrt
from random import random
from node import *


class Network:
    MIN_POINT_DISTANCE = 1.5
    DOMAIN = (8, 8, 8)

    def __init__(self, n_nodes):
        self.point_locations = {}

        for i in range(n_nodes):
            while True:
                p = tuple(round(random() * d, 2) for d in self.DOMAIN)
                for q in self.point_locations.values():
                    if self._d(p, q) < self.MIN_POINT_DISTANCE:
                        break
                else:
                    self.point_locations[i] = p
                    break

        self.nodes = {}
        for id in self.point_locations.keys():
            self.nodes[id] = Node(id)

        for id, node in self.nodes.items():
            node.update_network_info(self.nodes, self.get_neighbor_info(id))

        print("\n".join(f"{k}: ({v[0]}, {v[1]}, {v[2]})" for k, v in self.point_locations.items()))

    def get_neighbor_info(self, origin: int) -> dict[int, float]:
        result = {}
        origin_pos = self.point_locations[origin]
        for id, pos in self.point_locations.items():
            if id == origin:
                continue
            distance = self._d(origin_pos, pos)
            if distance < NODE_REACH:
                result[id] = distance
        return result

    def get_true_distances(self, origin):
        return {id: self._idd(origin, id) for id in self.point_locations.keys()}


    @staticmethod
    def _d(p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)

    def _idd(self, id1, id2):
        return self._d(self.point_locations[id1], self.point_locations[id2])