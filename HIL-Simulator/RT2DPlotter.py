import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib, time
from collections import deque
from numpy import cos

plt.ion()

class RT2DPlot:

    MIN = -10
    MAX = 10 

    def __init__(self, **kwargs):
        self.fig = plt.figure()
        self.ax  = self.fig.add_subplot(111)
        self.history = deque(maxlen=kwargs["history"])
        self.ax.set_autoscaley_on(True)

    def __init__(self, **kwargs):
        self.fig = kwargs["fig"]
        self.ax = kwargs["ax"]
        self.history = deque(maxlen=kwargs["history"])
        self.ax.set_autoscaley_on(True)
        self.ax.set_ylim(self.MIN, self.MAX)

    def update(self, x, y, **kwargs):
        self.history.append([x,y])
        self.ax.clear()
        self.ax.set_xlabel(kwargs["XLabel"])
        self.ax.set_ylabel(kwargs["YLabel"])
        data = np.array(self.history)
        x = data[:, 0]
        y = data[:, 1]
        self.ax.plot(x, y, "b")
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_ax(self, x, y, **kwargs):
        self.history.append([x,y])
        self.ax.clear()
        self.ax.set_xlabel(kwargs["XLabel"])
        self.ax.set_ylabel(kwargs["YLabel"])
        self.ax.relim()
        self.ax.autoscale_view()
        data = np.array(self.history)
        x = data[:, 0]
        y = data[:, 1]
        self.ax.plot(x, y, "b")

class SubRTPlots:

    def __init__(self, **kwargs):
        self.subplots = kwargs.pop("subplots")
        self.fig = kwargs["fig"]

    def update(self):
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()



if __name__ == "__main__":

    plot = RT2DPlot(history = 30)
    from time import sleep
    for i in range(500):
        plot.update(i, cos(i), XLabel = "time", YLabel = "cos")
        sleep(0.1)
