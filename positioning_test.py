import random

from simplexmesh.algorithm import get_position_by_anchors_2d_lls
from simplexmesh.grid import Point2D
from positioning_plotter.distance_list import DistanceList
from positioning_plotter.plotter import Plotter
import serial
import re

dist_by_addr = {}
test_strs = []

distance_attribute = "ifft"
distance_pattern = re.compile(f"{distance_attribute}=([0-9]+.[0-9]+)")
addr_pattern = re.compile("Addr (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")

target = Point2D((3, 2.9))
_vals = [5.0, 6.0, 7.0, 8.0, 9.0, 7.0]
_pts = [Point2D((-1, 6)), Point2D((8, 6)), Point2D((9, -1)), Point2D((-4, -1)), Point2D((-1, 11)), Point2D((3, -4))]
addresses = ["AA:AA:38:D5:C0:ED", "BB:BB:38:D5:C0:ED", "CC:CC:38:D5:C0:ED", "DD:DD:DD:DD:DD:DD", "EE:EE:EE:EE:EE:EE", "FF:FF:FF:FF:FF:FF"]
true_vals = {addresses[i]: _vals[i] for i in range(len(addresses))}
true_positions = {addresses[i]: _pts[i] for i in range(len(addresses))}
_w = [12, 12, 12, 3, 2, 1][:len(addresses)]
weights = [el / sum(_w) for el in _w]


def measure(addr):
    sd = 2
    return random.normalvariate(true_vals[addr], sd)


def serial_gen():
    ser = serial.Serial("COM8", 115200)
    while True:
        yield ser.readline()


if __name__ == '__main__':
    for i in range(300):
        addr = random.choices(
            population=addresses,
            weights=weights,
            k=1
        )[0]
        measurement = measure(addr)
        test_strs.append(f"""
    Measurement result:
         Addr {addr} (random)
         Quality ok
         Distance estimates: mcpd: ifft={round(measurement, 2)} phase_slope=0.28 rssi_openspace=0.28 best=0.29
         """)

    plotter = Plotter()
    plotter.plot_anchors(_pts)

    ctr = 20


    for line in test_strs:
        if line is None:
            continue

        dist_matches = re.findall(distance_pattern, line)
        if len(dist_matches) == 0:
            continue
        distance = float(dist_matches[0])
        address = re.findall(addr_pattern, line)[0][0]

        if address not in dist_by_addr.keys():
            dist_by_addr[address] = DistanceList()

        dist_by_addr[address].add(distance)
        if (val := dist_by_addr[address].get_value()) is not None:
            print(f"New value:  {address}   {val}")

        completed_addrs = [addr for addr in dist_by_addr.keys() if dist_by_addr[addr].get_value() is not None]
        n_anchors = len(completed_addrs)
        if n_anchors < 3:
            continue

        position = get_position_by_anchors_2d_lls(
            a=[true_positions[addr] for addr in completed_addrs],
            d=[dist_by_addr[addr].get_value() for addr in completed_addrs]
        )
        print(f"Position: {position}   ({n_anchors} anchors)")
        plotter.set_n_anchors(n_anchors)
        plotter.add_point(position)


        if n_anchors == 6:
            ctr -= 1
            if ctr == 0:
                plotter.plot_target(target)
                plotter.plot_end(position)
                break


    plotter.show()


