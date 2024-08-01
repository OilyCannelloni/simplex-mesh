import random

import datetime
import time

import matplotlib.pyplot as plt

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
addr_pattern = re.compile("Addr: *(([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")

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


def serial_measurements(port="COM4"):
    ser = serial.Serial(port, 115200)
    while True:
        line = ser.read_until(b"best").decode()
        if line is None or len(line) == 0:
            continue

        dist_matches = re.findall(distance_pattern, line)
        if len(dist_matches) == 0:
            continue
        distance = float(dist_matches[0])
        _address_groups = re.findall(addr_pattern, line)
        if len(_address_groups) == 0:
            continue
        address = _address_groups[0][0]

        yield address, distance


def create_test_serial():
    for i in range(300):
        addr = random.choices(
            population=addresses,
            weights=weights,
            k=1
        )[0]
        measurement = measure(addr)
        test_strs.append(f"""
    Measurement result:
         Addr: {addr} (random)
         Quality: ok
         Distance estimates: mcpd: ifft={round(measurement, 2)} phase_slope=0.28 rssi_openspace=0.28 best=0.29
         """)


def generate_test_csv():
    fname = "test.csv"
    with open(fname, "w") as f:
        f.write(f"target,{target[0]},{target[1]}\n")

        for addr in addresses:
            f.write(f"anchor,{true_positions[addr][0]},{true_positions[addr][1]},{addr}\n")

        for i in range(300):
            addr = random.choices(
                population=addresses,
                weights=weights,
                k=1
            )[0]
            measurement = measure(addr)
            f.write(f"measurement,{round(measurement, 2)},{addr}\n")


def generate_csv_from_serial(port="COM4", shuffle=False):
    dt = datetime.datetime.now().strftime("%y-%m-%d_%H-%M-%S")
    fname = "positioning_tests/" + dt + "_positioning.csv"
    try:
        with open(fname, "w") as f:
            for addr, dist in serial_measurements(port):
                print(dist, addr)
                f.write(f"measurement,{round(dist, 2)},{addr}\n")
    except KeyboardInterrupt:
        if shuffle:
            shuffle_csv(fname)


def plot_from_serial(port="COM4"):
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)

    start_time = time.time()

    for addr, dist in serial_measurements(port):
        delta = (time.time() - start_time) * 1000
        x = (delta % 10000) / 1000
        ax.scatter(x, dist, c="orange")
        plt.pause(0.1)
        if delta > 10000:
            plt.cla()
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 5)
            start_time = time.time()

    plt.show()




def shuffle_csv(fname):
    with open(fname, "r") as f:
        lines = f.readlines()
        random.shuffle(lines)
    with open(fname, "w") as f:
        f.writelines(lines)


if __name__ == '__main__':
    # shuffle_csv("positioning_tests/24-07-31_14-12-03_positioning.csv")
    # generate_csv_from_serial("COM8", shuffle=False)
    plot_from_serial("COM25")
    # for addr, dist in serial_measurements("COM25"):
    #     print(addr, dist)
