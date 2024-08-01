from positioning_plotter.distance_list import DistanceList
from positioning_plotter.plotter import Plotter
from simplexmesh.algorithm import get_position_by_anchors_2d_lls
from simplexmesh.grid import Point2D

if __name__ == '__main__':
    anchor_positions = {}
    anchor_addresses = []
    measurements = []
    distance_by_address = {}
    target = None
    n_anchors = 0
    ordered_anchors = []

    plotter = Plotter(xrange=(-7, 7), yrange=(-4, 10))
    # fn = "positioning_tests/24-07-31_14-12-03_positioning.csv"
    # fn = "positioning_tests/24-07-31_13-53-22_positioning.csv"
    fn = "positioning_tests/24-07-31_12-59-37_positioning.csv"
    with open(fn, "r") as f:
        while line := f.readline():
            line = line.strip().split(",")
            if line[0] == "target":
                target = Point2D((float(line[1]), float(line[2])))
                print(f"Target at {target}")

            if line[0] == "anchor":
                position = Point2D((float(line[1]), float(line[2])))
                addr = line[3]
                anchor_positions[addr] = position
                anchor_addresses.append(addr)
                print(f"Anchor {addr} at {position}")

            if line[0] == "measurement":
                val = float(line[1])
                addr = line[2]
                if addr not in distance_by_address.keys():
                    distance_by_address[addr] = DistanceList()
                distance_by_address[addr].add(val)

                completed_anchor_addresses = [addr for addr in distance_by_address.keys()
                                   if distance_by_address[addr].get_value() is not None]
                if len(completed_anchor_addresses) > n_anchors:
                    print(f"New anchor acquired: {addr}")
                    ordered_anchors.append(anchor_positions[addr])

                n_anchors = len(completed_anchor_addresses)
                if n_anchors < 3:
                    continue

                position = get_position_by_anchors_2d_lls(
                    a=[anchor_positions[addr] for addr in completed_anchor_addresses],
                    d=[distance_by_address[addr].get_value() for addr in completed_anchor_addresses]
                )
                print(f"Position: {position}   ({n_anchors} anchors)")
                plotter.set_n_anchors(n_anchors)
                plotter.add_point(position)

        for anchor in anchor_positions.values():
            if anchor not in ordered_anchors:
                ordered_anchors.append(anchor)

        plotter.plot_anchors(ordered_anchors)
        plotter.plot_target(target)
        plotter.plot_end(position)
        plotter.show()