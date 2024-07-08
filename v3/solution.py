from __future__ import annotations
import bisect
from config import config


class Solution(float):
    """
    Describes a single solution for an edge.
    See description of SolutionSet for more information.
    """
    @staticmethod
    def get_tag(gate: tuple[int]):
        return 2*min(gate) + 3*max(gate)

    def __new__(cls, value, badness, is_exact=False, gate=None):
        """
        Creates a new solution.
        :param value: Float value of the calculated distance
        :param badness: [TO BE USED SOON] how far is the solution from the exact measurement,
        i.e. how many simplex algorithm steps were used to come to it.
        The bigger the badness, the more inaccurate the solution can be.
        :param is_exact: Used to fix the solution so that it cannot be overwritten by others.
        Use this to mark the solutions derived from direct measurements.
        :param gate: Tuple of two node IDs forming the gate used to create this solution.
        """
        x = float.__new__(cls, value)
        x.badness = badness
        x.is_exact = is_exact
        x.tag = -1 if gate is None else Solution.get_tag(gate)
        return x

    def __repr__(self):
        return round(self.real, 2).__repr__()


class SolutionSet:
    """
    Describes a process of calculating a precise solution for a missing edge in the node graph.
    When the nodes not in direct contact with each other want to measure distance between them,
    they follow the Simplex Algorithm:
    - Find 2 or 3 common neighbors (the Gate) - depending on if the calculation is 2D ir 3D.
    - All nodes in the gate must be in direct contact.
    - Use the Cayley-Menger formula to produce TWO potential solutions for the distance, one correct and one wrong
    - Repeat the process with another gate to find another TWO potential solutions
    - Take the solution which repeats itself in both measurements.

    Due to the solutions being inaccurate, a more advanced metric has to be defined
    in order to extract the repeating one, especially if the incorrect ones lie close to the correct ones.
    """

    __deriv_filter_size = config["solution_set"]["deriv_filter_size"]
    __deriv_filter_sum_thr = config["solution_set"]["deriv_filter_avg_threshold"] * __deriv_filter_size
    __max_set_length = config["solution_set"]["max_set_length"]

    def __init__(self, exact_value=None):
        """
        :param exact_value: Initializes the SolutionSet with a value that is assumed to be
        a correct solution from the start.
        """
        self._solutions: list[Solution] = []
        self._cached_value: Solution | None = None
        self.SOLUTION_CUTOFF = config["node"]["max_reach"] * config["solution_set"]["max_reach_constant"]
        self.MIN_LENGTH_TIMES_FILTER = config["solution_set"]["min_set_length_times_filter"]
        self.is_exact = False

        if exact_value is not None:
            self.is_exact = True
            self._cached_value = Solution(exact_value, is_exact=True, badness=0)


    def _add(self, solution: Solution) -> None:
        if solution.is_exact:
            self.is_exact = True
            self._cached_value = solution
            return

        if solution < self.SOLUTION_CUTOFF:
            return

        for sol in self._solutions:
            if sol.tag == solution.tag and sol.tag != -1:
                return

        bisect.insort_right(self._solutions, solution)

    def add(self, solution: Solution) -> bool:
        """
        Puts a new solution into the SolutionSet.
        The set is a sorted list which enables the value-picking process to be more effective.
        :param solution: The solution to be added
        :return: True if a correct solution was picked thanks to the addition of the new one, False otherwise.
        """
        if len(self._solutions) > self.__max_set_length:
            return True
        self._add(solution)
        return self.update_cached_value()

    def extend(self, solutions: list[Solution]) -> bool:
        """
        Puts many new solutions into the SolutionSet.
        The set is a sorted list which enables the value-picking process to be more effective.
        :param solutions: The solution to be added
        :return: True if a correct solution was picked thanks to the addition of the new ones, False otherwise.
        """
        if len(self._solutions) > self.__max_set_length:
            return True
        for sol in solutions:
            self._add(sol)
        return self.update_cached_value()


    def get(self) -> Solution | None:
        """
        :return: True length of the edge if it's available, None otherwise
        """
        return self._cached_value

    def update_cached_value(self) -> bool:
        if self.is_exact:
            return False

        if len(self._solutions) < 2 * self.__deriv_filter_size:
            return False

        results = [sol for sol in self._solutions]
        deriv = [results[i + 1] - results[i] for i in range(len(results) - 1)]
        delta = self.__deriv_filter_size // 2
        deriv_sum = [sum(deriv[i-delta:i+delta]) for i in range(delta, len(deriv) - delta)]

        deriv_sum_minimum = min(deriv_sum)
        must_choose = len(self._solutions) > self.__max_set_length
        if not must_choose and deriv_sum_minimum > self.__deriv_filter_sum_thr:
            return False

        deriv_sum_min_index = deriv_sum.index(deriv_sum_minimum)
        self._cached_value = self._solutions[deriv_sum_min_index + delta]
        return True


if __name__ == '__main__':
    import random

    solution_set = SolutionSet()
    for _ in range(20):
        solution_set.add(Solution(random.random() * 10, random.random() * 100))

    print(solution_set._solutions)
    print(solution_set.get())






