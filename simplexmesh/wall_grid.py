from typing import Type
from grid import Grid, P, Point2D, Point
from config import config
from simplexmesh.grid import Network
import matplotlib.patches as patches


class WallGrid(Grid):
    def __init__(self, point_type: Type[P], n_nodes: int, grid_size: int, sd: float = 0.2):
        super().__init__(point_type, n_nodes, grid_size, sd)
        self.walls = config["grid"]["walls"]
        for i in range(len(self.walls)):
            self.walls[i] = [(self.walls[i][0], self.walls[i][1]), *self.walls[i][2:]]
        self._placement_conditions.append(self._condition_node_not_inside_wall)

    def _condition_node_not_inside_wall(self, point: P) -> bool:
        print("cc")
        for wall in self.walls:
            print(point, wall)
            if wall[0][0] < point.xyz[0] < wall[0][0] + wall[1] and wall[0][1] < point.xyz[1] < wall[0][1] + wall[2]:
                print("inside wall")
                return False
        return True

    def is_wall_between_nodes_true(self, origin, target):
        pass

    def is_wall_between_nodes_detected(self, origin, target):
        pass

    def _plot(self, network: Network):
        fig, (ax1, ax2) = super()._plot(network)
        for wall in self.walls:
            rect1 = patches.Rectangle(*wall, color="gray")
            rect2 = patches.Rectangle(*wall, color="gray")
            ax1.add_patch(rect1)
            ax2.add_patch(rect2)





if __name__ == '__main__':
    from node import DummyNode

    wg = WallGrid(Point2D, 10, 10)
    wg.setup()
    n = Network()
    for i in range(10):
        node = DummyNode(i, n, wg)
        node.set_is_anchor()

    wg.plot(Network())