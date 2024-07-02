
from grid import grid
from node import Node
from config import config


if __name__ == '__main__':
    nodes = [Node() for _ in range(config["grid"]["n_nodes"])]

    for i in range(100):
        for node in nodes:
            node.try_measure_new_length()

    for node in nodes:
        print(f"{node._id} |   " + "  ".join(
            f"{f'{target}: {x.get() if (x := node._known.get(target)) is not None else None}':10}"
            if target != node._id
            else " "*10
            for target in range(config["grid"]["n_nodes"])
        ))

    grid.plot()