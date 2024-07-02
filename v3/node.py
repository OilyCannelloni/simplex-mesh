import random
from solution import *
from grid import grid, network
import algorithm


class Node:
    __id = 0

    def __init__(self):
        self._id = Node.__id
        Node.__id += 1
        network.add_node(self)

        self._known: dict[int, SolutionSet] = {}

        self._neighbors: set[int] = set()
        self._neighbors.update(self.broadcast_is_neighbor())

        for neigh in self._neighbors:
            d = self.measure_distance(neigh)
            if d is not None:
                self.add_solution_to_node(neigh, [Solution(d, badness=0, is_exact=True)])


    """
    Private Locals
    """

    def get_all_nodes_known_distance(self) -> list[int]:
        return [id for id, solset in self._known.items() if solset.get() is not None]

    def get_random_gate(self) -> list[int]:
        return random.sample(self.get_all_nodes_known_distance(), 2)

    def add_solutions(self, target: int, solutions: list[Solution]):
        if target not in self._known.keys():
            self._known[target] = SolutionSet()
        self._known[target].extend(solutions)

    """
    Public locals
    """

    def get_known_to(self, target_id) -> Solution | None:
        solution_set = self._known.get(target_id, None)
        if solution_set is None:
            return None
        return solution_set.get()

    def get_all_completed(self) -> set[int]:
        return set(self._known.keys())

    def add_solution_to_node(self, node_id: int, solutions: list[Solution]):
        self.add_solutions(node_id, solutions)

    """
    Remotes
    """

    def broadcast_is_neighbor(self):
        return grid.get_neighbors_of(self._id)

    def measure_distance(self, target_id) -> float | None:
        return grid.get_measured_distance(self._id, target_id)

    def ask_node_for_distance(self, node_id, target_id) -> Solution | None:
        return network.get_node(node_id).get_known_to(target_id)

    def ask_node_for_all_completed_ids(self, node_id) -> set[int]:
        return network.get_node(node_id).get_all_completed()

    def send_solutions_to_target(self, node_id, solutions):
        network.get_node(node_id).add_solution_to_node(self._id, solutions)

    """
    Procedures
    """

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


        for target_id in targets:
            if target_id in self._neighbors or target_id == self._id:
                continue

            p1p3 = self.ask_node_for_distance(gate[0], target_id)
            p2p3 = self.ask_node_for_distance(gate[1], target_id)
            if p1p3 is None or p2p3 is None:
                continue


            solutions = [Solution(x, badness=0, gate=gate) for x in
                         algorithm.simplex_diagonal(p0p1, p0p2, p1p2, p1p3, p2p3)]

            had_sol = (x := self._known.get(target_id)) is not None and x.get() is not None

            self.add_solutions(target_id, solutions)
            self.send_solutions_to_target(target_id, solutions)

            has_sol = (x := self._known.get(target_id)) is not None and x.get() is not None


            if not had_sol and has_sol:
                m = round(self._known[target_id].get(), 2)
                r = round(grid.get_true_distance(self._id, target_id, True), 2)

                print(f"{self._id:2} -> {target_id:2}  via {str(gate):9}" +
                      f" {str(m):4}" +
                      f" (true {r})" +
                      ("  X" if abs(m - r) > 0.3 else "")
                )

                if abs(m - r) > 0.3:
                    print(self._known[target_id]._solutions)





























