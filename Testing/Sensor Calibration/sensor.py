import sys
import matplotlib.pyplot as plt
import numpy as np
import csv

dir = sys.argv[1]

import os

os.chdir(dir)

files=  os.listdir()

def dat2np(fname):
    data = []
    with open(fname, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            data.append([float(i) for i in row[:-1]])
    return np.array(data)

channels = [dat2np(i) for i in files]

fig, ax = plt.subplots(3)

sizing = lambda i: np.arange(0, len(i), 1)

for i in range(len(ax)):
    for ch, j in zip(channels, range(len(channels))):
        ax[i].plot(sizing(ch), ch[:, i], label=f"ch{j}")

ax[0].title.set_text("X")
ax[1].title.set_text("Y")
ax[2].title.set_text("Z")
fig.suptitle("Measurements")
ax[0].legend()
ax[1].legend()
ax[2].legend()


plt.show()
