import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

class Plotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.points = []
        self.n_anchors = 3
        self.anchor_colors = {3: 'y', 4: 'orange', 5: 'r', 6: 'purple'}

        self.ax.set_xlim(-6, 13)
        self.ax.set_ylim(-6, 13)

    def set_n_anchors(self, n_anchors):
        self.n_anchors = n_anchors

    def plot_target(self, point):
        self.ax.plot(point[0], point[1], color="black", markersize=8, marker="x")

    def plot_end(self, point):
        self.ax.plot(point[0], point[1], color=self.anchor_colors[self.n_anchors], markersize=12, marker="*")

    def plot_anchors(self, points_list):
        for point in points_list:
            print(point)
            self.ax.plot(point[0], point[1], color="black", markersize=8, marker=".")

    def add_point(self, point):
        color = self.anchor_colors[self.n_anchors]
        if len(self.points) > 0:
            self.ax.plot((self.points[-1][0], point[0]), (self.points[-1][1], point[1]), color=color, lw=1)
        self.ax.plot(point[0], point[1], color=color, marker=".")
        self.points.append(point)

    def show(self):
        plt.show()

