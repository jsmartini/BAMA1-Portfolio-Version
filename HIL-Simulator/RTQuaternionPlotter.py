import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib, time
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
from random import randrange as random
from numpy import sin, cos
from collections import deque

plt.ion()

def sphere():
    r = 1
    pi = np.pi
    cos = np.cos
    sin = np.sin
    phi, theta = np.mgrid[0.0:pi:100j, 0.0:2.0*pi:100j]
    x = r*sin(phi)*cos(theta)
    y = r*sin(phi)*sin(theta)
    z = r*cos(phi)
    return [x,y,z]

class RTQuaternionPlotter:

    def __init__(self, **kwargs):
        self.fig = plt.figure()
        self.ax = plt.subplot(111, projection = "3d")
        self.sphere = sphere()
        self.history = deque(maxlen=kwargs["history"])

    def __init__(self, **kwargs):
        self.fig = kwargs["fig"]
        self.ax = kwargs["ax"]
        self.history = deque(maxlen=kwargs["history"])
        self.sphere = sphere()

    def update(self, quaternion):
        self.ax.clear()
        self.history.append(quaternion)
        data = np.array(self.history)
        x = data[:, 1]
        y = data[:, 2]
        z = data[:, 3]
        u, v, w = quaternion[1:]
        self.ax.quiver(0,0,0, u, v, w, length=1.0)
        self.ax.plot_wireframe(self.sphere[0], self.sphere[1], self.sphere[2],color="r", alpha=0.15)
        self.ax.plot(x, y, z, color="g", alpha=0.65)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_ax(self, quaternion):
        self.ax.clear()
        self.history.append(quaternion)
        data = np.array(self.history)
        x = data[:, 1]
        y = data[:, 2]
        z = data[:, 3]
        u, v, w = quaternion[1:]
        self.ax.quiver(0,0,0, u, v, w, length=1.0)
        self.ax.plot_wireframe(self.sphere[0], self.sphere[1], self.sphere[2],color="r", alpha=0.15)
        self.ax.plot(x, y, z, color="g", alpha=0.65)



if __name__ == "__main__":
    plot = RTQuaternionPlotter(history=5)
    from time import sleep
    for i in range(100):
        sleep(0.1)
        q = [0, random(-1,1), random(-1,1), random(-1,1)]
        plot.update(q)
