
from grid import grid
from node import Node
from config import config


class Simulation:
    def __init__(self):
        self.N_NODES = config["grid"]["n_nodes"]
        self.REQ_ANCHORS = config["grid"]["n_required_anchors"]
        self.nodes = []

    def create(self):
        n_anchors = config["grid"]["n_anchors"]
        self.nodes = [Node(is_anchor=(i < n_anchors)) for i in range(config["grid"]["n_nodes"])]

    def run_random_target(self, by_hops=False):
        for i in range(config["simulation"]["iterations"]):
            for node in self.nodes:
                node.try_measure_random_target(by_hops=by_hops)
            if i % 1000 == 0:
                print(f"------ ITERATION {i} ------")

    def run_random_gate(self, by_hops=False):
        for i in range(config["simulation"]["iterations"]):
            for node in self.nodes:
                node.try_measure_random_gate(by_hops=by_hops)
            if i % 100 == 0:
                print(f"------ ITERATION {i} ------")

    def run(self):
        if config["simulation"]["method"] == "random-gate":
            self.run_random_gate(by_hops=config["simulation"]["by_hops"])
        elif config["simulation"]["method"] == "random-target":
            self.run_random_target(by_hops=config["simulation"]["by_hops"])


    def show_results(self):
        for node in self.nodes:
            print(f"{node._id} |   " + "  ".join(
                f"{f'{target}: {x.get() if (x := node._known.get(target)) is not None else None}':10}"
                if target != node._id
                else " " * 10
                for target in range(config["grid"]["n_nodes"])
            ))

        n_anchored = len([x for x in self.nodes if x.is_anchor or len(x.anchors.keys()) >= self.REQ_ANCHORS])
        print(f"Nodes anchored: {n_anchored} / {self.N_NODES}")

    def show_plots(self):
        grid.plot()

if __name__ == '__main__':
    sim = Simulation()
    sim.create()
    sim.run()
    sim.show_results()
    sim.show_plots()









