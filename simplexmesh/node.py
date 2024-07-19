import random
import abc
from abc import ABC
from simplexmesh.solution import *
from simplexmesh.grid import Grid, Network
from simplexmesh.algorithm import simplex_diagonal


class TargetNode(int):
    """
    Class describing information about a node from the perspective of an origin node.
    """
    def __new__(cls, id: int, hops: int = 0, completed: bool = False) -> "TargetNode":
        """
        :param id: ID of the node
        :param hops: Hops required to get to the node
        :param completed: Whether the distance to the node is known
        :param do_logging:
        """
        x = int.__new__(cls, id)
        x.hops = hops
        x.completed = False
        return x




class Node(ABC):
    __anchors_required = config["grid"]["n_required_anchors"]

    def __init__(self, id: int, network: Network, grid: Grid):
        if network.get_node(id) is not None:
            raise ValueError("ID already in use")

        self._id = id
        self._network = network
        self._grid = grid
        self._network.add_node(self)

        self.is_anchor = False
        self.anchor_reached = False
        self.anchors = {}
        self.position = None

        self._known: dict[TargetNode, SolutionSet] = {}
        self._neighbors: set[TargetNode] = set()
        self._neighbors.update(self.broadcast_is_neighbor())

        self.do_logging = False


    """
    Remotes
    """

    def broadcast_is_neighbor(self):
        return [TargetNode(x, 1) for x in self._grid.get_neighbors_of(self._id)]

    def measure_distance(self, target_id) -> float | None:
        return self._grid.get_measured_distance(self._id, target_id)

    def ask_node_for_distance(self, node_id, target_id) -> Solution | None:
        return self._network.get_node(node_id).get_known_to(target_id)

    def ask_node_for_all_completed_ids(self, node_id) -> set[TargetNode]:
        return self._network.get_node(node_id).get_all_completed()

    def ask_node_is_anchor_and_position(self, node_id) -> tuple[int, int] | None:
        return self._network.get_node(node_id).get_is_anchor_and_position()

    def send_solutions_to_target(self, node_id, solutions) -> None:
        self._network.get_node(node_id).add_solution_to_node(self._id, solutions)


    """
    Locals
    """
    def get_known_to(self, target_id) -> Solution | None:
        solset = self._known.get(target_id, None)
        if solset is None:
            return None
        return solset.get()

    def set_is_anchor(self):
        self.is_anchor = True
        self.position = self._grid.get_true_position(self._id)

    def get_is_anchor_and_position(self):
        if self.is_anchor:
            return self.position
        return None

    def set_logging(self, logging: bool = True):
        self.do_logging = logging

    def measure_distances_to_neighbors(self):
        for neigh in self._neighbors:
            d = self.measure_distance(neigh)
            if d is not None:
                neigh.completed = True
                self.add_exact_solution(neigh, d)

    def add_solutions(self, target: TargetNode, solutions: list[Solution]):
        if target not in self._known.keys():
            self._known[target] = SolutionSet()
        solution_ready = self._known[target].extend(solutions)

        return solution_ready

    def add_exact_solution(self, target: TargetNode, value: float):
        if target not in self._known.keys():
            self._known[target] = SolutionSet(exact_value=value)
        else:
            self._known[target].add(Solution(value=value, is_exact=True, badness=0))

    def mark_known(self, target: TargetNode):
        self.check_anchor_hit(target)

    def check_anchor_hit(self, target: TargetNode):
        if (pos := self.ask_node_is_anchor_and_position(target)) is not None:
            self.anchors[target] = pos
            if len(self.anchors.keys()) == self.__anchors_required:
                print(f"[{self._id}] Required anchors acquired")
                self.anchor_reached = True


    """
    Procedures
    """
    def compute_solutions(self, target: TargetNode, gate: tuple[int, int], p0p1: Solution,
                         p0p2: Solution, p1p2: Solution, p1p3: Solution, p2p3: Solution):

        solutions = [Solution(x, badness=max(edge.badness for edge in (p0p1, p0p2, p1p2, p1p3, p2p3)), gate=gate)
                     for x in simplex_diagonal(p0p1, p0p2, p1p2, p1p3, p2p3)]

        return solutions


    def log_new_edge(self, target: TargetNode):
        if not self.do_logging:
            return
        m = round(self._known[target].get(), 2)
        r = round(self._grid.get_true_distance(self._id, target, True), 2)
        print(f"{self._id:2} -> {target:2}" +
              f" {str(m):4}" +
              f" (true {r})" +
              ("  X" if abs(m - r) > 0.3 else "")
              )
        if abs(m - r) > 0.3:
            print(self._known[target]._solutions)


    @abc.abstractmethod
    def try_measure_new_length(self):
        pass


class BasicStrategyNode(Node, ABC):
    def __init__(self, id: int, network: Network, grid: Grid):
        super().__init__(id, network, grid)
        self._known_set: set[TargetNode] = set()
        self._unknown_set = self.create_unknown_set()  # So that random.choice() is more efficient
        self._target_set = self.create_unknown_set(with_self=True)

    def get_all_completed(self) -> set[TargetNode]:
        return self._known_set

    def add_solution_to_node(self, node_id: int, solutions: list[Solution]):
        self.add_solutions(self._target_set[node_id], solutions)

    def add_solutions(self, target: TargetNode, solutions: list[Solution]):
        solution_ready = super().add_solutions(target, solutions)
        if solution_ready:
            self.mark_known(target)
            self.log_new_edge(target)

    def add_exact_solution(self, target: TargetNode, value: float):
        super().add_exact_solution(target, value)
        self.mark_known(target)

    def create_unknown_set(self, with_self=False) -> list[TargetNode]:
        ret = []
        for x in range(self._network.get_node_count()):
            if not with_self and x == self._id:
                continue
            ret.append(TargetNode(x))
        return ret

    def mark_known(self, target: TargetNode):
        if target not in self._unknown_set:  # TODO check why this happens as it should not.
            return
        self._unknown_set.remove(target)
        self._known_set.add(target)
        super().mark_known(target)

    def _compute_solutions_and_mark_known(self, target: TargetNode, gate: tuple[int, int], p0p1: Solution,
                         p0p2: Solution, p1p2: Solution, p1p3: Solution, p2p3: Solution):

        solutions = self.compute_solutions(target, gate, p0p1, p0p2, p1p2, p1p3, p2p3)
        self.add_solutions(target, solutions)
        self.send_solutions_to_target(target, solutions)


class RandomTargetStrategyNode(BasicStrategyNode, ABC):
    def __init__(self, id: int, network: Network, grid: Grid):
        super().__init__(id, network, grid)

    def try_measure_new_length(self):
        if len(self._unknown_set) == 0:
            return
        target = random.choice(self._unknown_set)
        self._try_measure_new_length_to_target(target)

    def _try_measure_new_length_to_target(self, target: TargetNode):
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
        self._compute_solutions_and_mark_known(self._target_set[target], gate, p0p1, p0p2, p1p2, p1p3, p2p3)



class RandomGateStrategyNode(BasicStrategyNode, ABC):
    def __init__(self, id: int, network: Network, grid: Grid):
        super().__init__(id, network, grid)

    def get_random_gate(self):
        return random.sample([id for id, solset in self._known.items() if solset.get() is not None], 2)

    def try_measure_new_length(self):
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

            self._compute_solutions_and_mark_known(self._target_set[target], gate, p0p1, p0p2, p1p2, p1p3, p2p3)



class RandomTargetHopLevelStrategyNode(RandomTargetStrategyNode, ABC):
    def __init__(self, id: int, network: Network, grid: Grid):
        self.hop_info = grid.get_hop_counts_from(id)
        self.hop_level = 2
        self.current_target_source = self.hop_info[2].copy()
        self.known_count_by_hop_level = [0] * len(self.hop_info)
        super().__init__(id, network, grid)

    def create_unknown_set(self, with_self=False) -> list[TargetNode]:
        ret = []
        for x in range(self._network.get_node_count()):
            if not with_self and x == self._id:
                continue

            for n_hops, hop_subset in enumerate(self.hop_info):
                if x in hop_subset:
                    tn = TargetNode(x, n_hops)
                    ret.append(tn)
                    break
        return ret



    def process_hop_level(self, target: TargetNode):
        if target in self.current_target_source:
            self.current_target_source.remove(target)

        self.known_count_by_hop_level[target.hops] += 1
        if target.hops == self.hop_level:
            completion_frac = self.known_count_by_hop_level[self.hop_level] / len(self.hop_info[self.hop_level])
            if completion_frac > config["node"]["hop_level_advance_threshold"]:
                self.hop_level += 1
                print(f"{[self._id]} Hop level -> {self.hop_level}")
                self.current_target_source.extend(self.hop_info[self.hop_level])

    def mark_known(self, target: TargetNode):
        super().mark_known(target)
        self.process_hop_level(target)

    def try_measure_new_length(self):
        if len(self.current_target_source) == 0:
            return
        target = random.choice(self.current_target_source)
        self._try_measure_new_length_to_target(target)


