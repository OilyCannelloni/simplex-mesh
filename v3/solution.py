from __future__ import annotations
import bisect
import dataclasses
from config import config


class Solution(float):
    @staticmethod
    def get_tag(gate):
        return 2*min(gate) + 3*max(gate)

    def __new__(cls, value, badness, is_exact=False, gate=None):
        x = float.__new__(cls, value)
        x.badness = badness
        x.is_exact = is_exact
        x.tag = -1 if gate is None else Solution.get_tag(gate)
        return x

    def __repr__(self):
        return round(self.real, 2).__repr__()


class SolutionSet:
    __deriv_filter_size = config["solution_set"]["deriv_filter_size"]
    __deriv_filter_sum_thr = config["solution_set"]["deriv_filter_avg_threshold"] * __deriv_filter_size
    __max_set_length = config["solution_set"]["max_set_length"]

    def __init__(self, exact_value=None):
        self._solutions: list[Solution] = []
        self._cached_value: Solution | None = None
        self.SOLUTION_CUTOFF = config["node"]["max_reach"] * config["solution_set"]["max_reach_constant"]
        self.MIN_LENGTH_TIMES_FILTER = config["solution_set"]["min_set_length_times_filter"]
        self.is_exact = False

        if exact_value is not None:
            self.is_exact = True
            self._cached_value = Solution(exact_value, is_exact=True, badness=0)


    def _add(self, solution):
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

    def add(self, solution):
        self._add(solution)
        self.update_cached_value()

    def extend(self, solutions: list[Solution]) -> bool:
        for sol in solutions:
            self._add(sol)
        return self.update_cached_value()


    def get(self):
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






