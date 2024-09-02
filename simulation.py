from simplexmesh.grid import Grid, Network, Point2D
from simplexmesh.node import *
from simplexmesh.config import config
from simplexmesh.algorithm import get_position_by_anchors_2d_lls


class Simulation:
    def __init__(self):
        self.N_NODES = config["grid"]["n_nodes"]
        self.REQ_ANCHORS = config["grid"]["n_required_anchors"]
        self.nodes: list[Node] = []
        self.grid = Grid(Point2D, config["grid"]["n_nodes"], config["grid"]["size"], config["measurement"]["sd"])
        self.network = Network()

    def create(self):
        n_anchors = config["grid"]["n_anchors"]
        self.nodes = []

        node_class_str = config["simulation"]["node"]
        node_class = globals()[node_class_str]

        self.grid.setup()

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
        print("Distances")
        for node in self.nodes:
            print(f"{node._id} |   " + "  ".join(
                f"{f'{target}: {x.get() if (x := node._known.get(target)) is not None else None}':10}"
                if target != node._id
                else " " * 10
                for target in range(config["grid"]["n_nodes"])
            ))

        print("Errors")
        for node in self.nodes:
            print(f"{node._id} |   " + "  ".join(
                f"{f'{target}: {round(x.get() - self.grid.get_true_distance(node._id, target, override_range=True), 1) if (x := node._known.get(target)) is not None else None}':10}"
                if target != node._id
                else " " * 10
                for target in range(config["grid"]["n_nodes"])
            ))

        n_anchored = len([x for x in self.nodes if x.is_anchor or len(x.anchors.keys()) >= self.REQ_ANCHORS])
        print(f"Nodes anchored: {n_anchored} / {self.N_NODES}")

        print(f"Anchors: {'    '.join([f'{n._id}:{list(n.anchors.keys())}' for n in self.nodes])}")

        print("\n\n")
        print("Positions:")
        for node in self.nodes:
            if config["simulation"]["n_used_anchors"] != config["grid"]["n_required_anchors"]:
                anchor_ids = random.sample(list(node.anchors.keys()), config["simulation"]["n_used_anchors"])
            else:
                anchor_ids = node.anchors.keys()

            anchors = [node.anchors[id] for id in anchor_ids]
            distances = [node._known[id].get() for id in anchor_ids]
            if None in distances:
                continue
            position = get_position_by_anchors_2d_lls(anchors, distances)
            true_pos = self.grid.get_true_position(node._id)
            print(f"{node._id} | Calculated: {position}  | Real: {true_pos}  | Delta: {position.distance_to(true_pos)}")
            if not node.is_anchor:
                node.position = position




    def show_plots(self):
        self.grid.plot(self.network)

if __name__ == '__main__':
    sim = Simulation()
    sim.create()
    try:
        sim.run()
    except Exception as ex:
        raise ex
        pass

    sim.show_results()
    sim.show_plots()









