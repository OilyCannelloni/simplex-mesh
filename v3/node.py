import random
from solution import *
from grid import grid, network
import algorithm


class TargetNode(int):
    def __new__(cls, id: int, hops: int, completed: bool = False):
        x = int.__new__(cls, id)
        x.hops = hops
        x.completed = False
        return x


class Node:
    __id = 0

    def __init__(self, is_anchor=False):
        self._id = Node.__id
        Node.__id += 1
        network.add_node(self)

        self.hop_info = self.broadcast_get_hop_count()
        self.hop_level = 2
        self.current_hop_node_source = self.hop_info[1].copy()
        self.current_target_source = self.hop_info[2].copy()
        self.known_count_by_hop_level = [0] * len(self.hop_info)

        self._known: dict[TargetNode, SolutionSet] = {}
        self._unknown_set: list[TargetNode] = self.create_unknown_set()
        self._target_set: list[TargetNode] = self.create_unknown_set(with_self=True)
        self._known_set: set[TargetNode] = set()

        self._neighbors: set[TargetNode] = set()
        self._neighbors.update(self.broadcast_is_neighbor())

        self.is_anchor = is_anchor
        self.anchor_reached = is_anchor
        self.anchors = {}
        self.position = None if not self.is_anchor else grid.real_node_coords[self._id]


    def measure_distances_to_neighbors(self):
        for neigh in self._neighbors:
            d = self.measure_distance(neigh)
            if d is not None:
                neigh.completed = True
                self.add_exact_solution(neigh, d)


    def create_unknown_set(self, with_self=False) -> list[TargetNode]:
        ret = []
        for x in range(network.get_node_count()):
            if not with_self and x == self._id:
                continue

            for n_hops, hop_subset in enumerate(self.hop_info):
                if x in hop_subset:
                    tn = TargetNode(x, n_hops)
                    ret.append(tn)
                    break
        return ret

    """
    Private Locals
    """

    def get_all_nodes_known_distance(self) -> list[TargetNode]:
        return [id for id, solset in self._known.items() if solset.get() is not None]

    def get_random_gate(self) -> list[TargetNode]:
        return random.sample(self.get_all_nodes_known_distance(), 2)

    def get_random_gate_from(self, source: list[TargetNode]) -> list[TargetNode]:
        return random.sample(source, 2)

    def add_solutions(self, target: TargetNode, solutions: list[Solution]):
        if target not in self._known.keys():
            self._known[target] = SolutionSet()
        solution_ready = self._known[target].extend(solutions)
        if solution_ready:
            self.mark_known(target)
        return solution_ready

    def add_exact_solution(self, target: TargetNode, value: float):
        if target not in self._known.keys():
            self._known[target] = SolutionSet(exact_value=value)
        else:
            self._known[target].add(Solution(value=value, is_exact=True, badness=0))
        self.mark_known(target, process_hop_level=False)

    def process_hop_level(self, target: TargetNode):
        if target in self.current_target_source:
            self.current_target_source.remove(target)
        if target.hops <= self.hop_level:
            self.current_hop_node_source.append(target)

        # update hop level
        self.known_count_by_hop_level[target.hops] += 1
        if target.hops == self.hop_level:
            completion_frac = self.known_count_by_hop_level[self.hop_level] / len(self.hop_info[self.hop_level])
            if completion_frac > config["node"]["hop_level_advance_threshold"]:
                self.hop_level += 1
                print(f"{[self._id]} Hop level -> {self.hop_level}")
                for node in self._known_set:
                    if node.completed and node.hops <= self.hop_level and node not in self.current_hop_node_source:
                        self.current_hop_node_source.append(node)

                self.current_target_source.extend(self.hop_info[self.hop_level])

    def check_anchor_hit(self, target: TargetNode):
        if pos := self.ask_node_is_anchor_and_position(target) is not None:
            self.anchors[target] = pos
            if len(self.anchors.keys()) == config["grid"]["n_required_anchors"]:
                print(f"[{self._id}] Required anchors acquired")
                self.anchor_reached = True


    def mark_known(self, target: TargetNode, process_hop_level=True, check_anchor_hit=True):
        if target not in self._unknown_set:  # TODO check why this happens as it should not.
            return
        self._unknown_set.remove(target)
        self._known_set.add(target)

        if process_hop_level:
            self.process_hop_level(target)

        if check_anchor_hit:
            self.check_anchor_hit(target)










    """
    Public locals
    """

    def get_known_to(self, target_id) -> Solution | None:
        solution_set = self._known.get(target_id, None)
        if solution_set is None:
            return None
        return solution_set.get()

    def get_all_completed(self) -> set[TargetNode]:
        return self._known_set

    def add_solution_to_node(self, node_id: int, solutions: list[Solution]):
        self.add_solutions(self._target_set[node_id], solutions)

    def get_is_anchor_and_position(self):
        if self.is_anchor:
            return self.position

    """
    Remotes
    """
    def broadcast_get_hop_count(self):
        return grid.get_hop_count_from(self._id)

    def broadcast_is_neighbor(self):
        return [TargetNode(x, 1) for x in grid.get_neighbors_of(self._id)]

    def measure_distance(self, target_id) -> float | None:
        return grid.get_measured_distance(self._id, target_id)

    def ask_node_for_distance(self, node_id, target_id) -> Solution | None:
        return network.get_node(node_id).get_known_to(target_id)

    def ask_node_for_all_completed_ids(self, node_id) -> set[TargetNode]:
        return network.get_node(node_id).get_all_completed()

    def ask_node_is_anchor_and_position(self, node_id) -> tuple[int, int] | None:
        return network.get_node(node_id).get_is_anchor_and_position()

    def send_solutions_to_target(self, node_id, solutions):
        network.get_node(node_id).add_solution_to_node(self._id, solutions)

    """
    Procedures
    """
    def compute_solution(self, target: TargetNode, gate: tuple[int, int], p0p1: Solution,
                         p0p2: Solution, p1p2: Solution, p1p3: Solution, p2p3: Solution):

        solutions = [Solution(x, badness=max(edge.badness for edge in (p0p1, p0p2, p1p2, p1p3, p2p3)), gate=gate)
                     for x in algorithm.simplex_diagonal(p0p1, p0p2, p1p2, p1p3, p2p3)]

        edge_ready = self.add_solutions(target, solutions)
        self.send_solutions_to_target(target, solutions)

        if edge_ready:
            m = round(self._known[target].get(), 2)
            r = round(grid.get_true_distance(self._id, target, True), 2)

            print(f"{self._id:2} -> {target:2}  via {str(gate):9}" +
                  f" {str(m):4}" +
                  f" (true {r})" +
                  ("  X" if abs(m - r) > 0.3 else "")
                  )

            if abs(m - r) > 0.3:
                print(self._known[target]._solutions)


    def try_measure_random_target(self, by_hops=False):
        if by_hops:
            if len(self.current_target_source) == 0:
                return
            target = random.choice(self.current_target_source)
        else:
            target = random.choice(self._unknown_set)

        target_neighs = self.ask_node_for_all_completed_ids(target)
        gate_pool = target_neighs.intersection(self._known_set)
        if len(gate_pool) < 2:
            return

        gate = random.sample(gate_pool, 2)
        p0p1 = self._known[gate[0]].get()
        p0p2 = self._known[gate[1]].get()
        p1p2 = self.ask_node_for_distance(gate[0], gate[1])
        if p1p2 is None:
            return

        p1p3 = self.ask_node_for_distance(target, gate[0])
        p2p3 = self.ask_node_for_distance(target, gate[1])
        self.compute_solution(self._target_set[target], gate, p0p1, p0p2, p1p2, p1p3, p2p3)


    def try_measure_random_gate(self, by_hops=False):
        if by_hops:
            gate = self.get_random_gate_from(self.current_hop_node_source)
        else:
            gate = self.get_random_gate()

        p0p1 = self._known[gate[0]].get()
        p0p2 = self._known[gate[1]].get()

        p1p2 = self.ask_node_for_distance(gate[0], gate[1])
        if any([x is None for x in (p0p1, p0p2, p1p2)]):
            return


        left_targets = self.ask_node_for_all_completed_ids(gate[0])
        right_targets = self.ask_node_for_all_completed_ids(gate[1])
        targets = left_targets.intersection(right_targets)


        for target in targets:
            if target in self._neighbors or target == self._id:
                continue

            p1p3 = self.ask_node_for_distance(gate[0], target)
            p2p3 = self.ask_node_for_distance(gate[1], target)
            if p1p3 is None or p2p3 is None:
                continue

            self.compute_solution(self._target_set[target], gate, p0p1, p0p2, p1p2, p1p3, p2p3)
