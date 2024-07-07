
from grid import Grid, Network
from node import *
from config import config


class Simulation:
    def __init__(self):
        self.N_NODES = config["grid"]["n_nodes"]
        self.REQ_ANCHORS = config["grid"]["n_required_anchors"]
        self.nodes: list[Node] = []
        self.grid = Grid(config["grid"]["n_nodes"], config["grid"]["size"], config["measurement"]["sd"])
        self.network = Network()

    def create(self):
        n_anchors = config["grid"]["n_anchors"]
        self.nodes = []

        node_class_str = config["simulation"]["node"]
        node_class = globals()[node_class_str]

        for i in range(self.N_NODES):
            node = node_class(i, self.network, self.grid)
            if i < n_anchors:
                node.set_is_anchor()
                node.set_logging(False)
            self.nodes.append(node)

        for node in self.nodes:
            node.measure_distances_to_neighbors()


    def run(self):
        for i in range(config["simulation"]["iterations"]):
            for node in self.nodes:
                node.try_measure_new_length()
            if i % 100 == 0:
                print(f"------ ITERATION {i} ------")


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

        print(f"Anchors: {'    '.join([f'{n._id}:{list(n.anchors.keys())}' for n in self.nodes])}")

    def show_plots(self):
        self.grid.plot(self.network)

if __name__ == '__main__':
    sim = Simulation()
    sim.create()
    try:
        sim.run()
    except:
        pass

    sim.show_results()
    sim.show_plots()









