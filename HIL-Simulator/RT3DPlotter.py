import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FixedLocator, FormatStrFormatter
import matplotlib, time
from collections import deque
from numpy import sin, cos, tan

plt.ion()

def sphere(r):
    pi = np.pi
    cos = np.cos
    sin = np.sin
    phi, theta = np.mgrid[0.0:pi:100j, 0.0:2.0*pi:100j]
    x = r*sin(phi)*cos(theta)
    y = r*sin(phi)*sin(theta)
    z = r*cos(phi)
    return [x,y,z]


class RT3DPlot:

    def __init__(self, **kwargs):
        self.fig = plt.figure()
        self.ax  = self.fig.add_subplot(111, projection="3d")
        self.history = deque(maxlen=kwargs["history"])
        self.sphere = sphere(6370)

    def __init__(self, **kwargs):
        self.fig = kwargs["fig"]
        self.ax = kwargs["ax"]
        self.history = deque(maxlen=kwargs["history"])
        self.sphere = sphere(6370)

    def update(self, x, y, z):
        self.ax.clear()
        self.history.append([x,y,z])
        self.ax.set_xlabel("X <KM>")
        self.ax.set_ylabel("Y <KM>")
        self.ax.set_zlabel("Z <KM>")
        data = np.array(self.history)
        xh = data[:, 0]
        yh = data[:, 1]
        zh = data[:, 2]
        self.ax.plot(xh, yh, zh, "b", label="Orbit")
        #self.ax.scatter3D([0], [0], [0], "g", label="Earth")
        self.ax.scatter3D([x], [y], [z], "r", label="BAMA-1")
        self.ax.plot_wireframe(self.sphere[0], self.sphere[1], self.sphere[2],color="r", alpha=0.15)
        self.ax.legend()
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def update_ax(self, x, y, z):
        self.ax.clear()
        self.history.append([x,y,z])
        self.ax.set_xlabel("X <KM>")
        self.ax.set_ylabel("Y <KM>")
        self.ax.set_zlabel("Z <KM>")
        data = np.array(self.history)
        xh = data[:, 0]
        yh = data[:, 1]
        zh = data[:, 2]
        self.ax.plot(xh, yh, zh, "b", label="Orbit")
        #self.ax.scatter3D([0], [0], [0], "g", label="Earth")
        self.ax.scatter3D([x], [y], [z], "r", label="BAMA-1")
        self.ax.plot_wireframe(self.sphere[0], self.sphere[1], self.sphere[2],color="r", alpha=0.15)
        self.ax.legend()


if __name__ == "__main__":
    plot = RT3DPlot(history=30)

    for i in range(500):
        plot.update(
            x= sin(i),
            y= cos(i),
            z= tan(i)
        )
