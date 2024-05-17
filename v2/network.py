from math import sqrt
from random import random, normalvariate
from node import *





class Network:
    MIN_POINT_DISTANCE = 1.5
    DOMAIN = (8, 8, 8)

    def __init__(self, n_nodes, sd=0):
        self.point_locations = {}

        for i in range(n_nodes):
            while True:
                p = tuple(round(random() * d, 2) for d in self.DOMAIN)
                for q in self.point_locations.values():
                    if NetworkMeasurement.exact_d(p, q) < self.MIN_POINT_DISTANCE:
                        break
                else:
                    self.point_locations[i] = p
                    break

        self.network_measurement = NetworkMeasurement(self.point_locations, sd)

        self.nodes = {}
        for id in self.point_locations.keys():
            self.nodes[id] = Node(id, self.point_locations[id])

        for id, node in self.nodes.items():
            node.update_network_info(self.nodes, self.get_neighbor_info(id), self.point_locations)

        print("\n".join(f"{k}: ({v[0]}, {v[1]}, {v[2]})" for k, v in self.point_locations.items()))

    def get_neighbor_info(self, origin: int) -> dict[int, float]:
        result = {}
        origin_pos = self.point_locations[origin]
        for target_id, pos in self.point_locations.items():
            if target_id == origin:
                continue

            true_distance = NetworkMeasurement.exact_d(origin_pos, pos)
            if true_distance < NODE_REACH:
                result[target_id] = self.network_measurement.get_measurement_result(origin, target_id)
        return result

    def get_true_distances(self, origin):
        return {id: self.network_measurement.id_exact_d(origin, id) for id in self.point_locations.keys()}




