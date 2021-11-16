import sys
import matplotlib.pyplot as plt

dir = sys.argv[1]

import os

os.chdir(dir)

files=  os.listdir()
fname0 = files[0]
fname1 = files[1]
fname2 = files[2]

import csv
import numpy as np
def dat2np(fname):
    data = []
    with open(fname, "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            data.append([float(i) for i in row[:-1]])
    return np.array(data)

ch0 = dat2np(fname0)
ch1 = dat2np(fname1)
ch2 = dat2np(fname2)


sizing = lambda i: np.arange(0, len(i), 1)

fig, (ax1, ax2, ax3) = plt.subplots(3)



ax1.plot(sizing(ch0), ch0[:, 0], label="ch0")
ax1.plot(sizing(ch1), ch1[:, 0], label="ch1")
ax1.plot(sizing(ch2), ch2[:, 0], label="ch2")
ax2.plot(sizing(ch0), ch0[:, 1], label="ch0")
ax2.plot(sizing(ch1), ch1[:, 1], label="ch1")
ax2.plot(sizing(ch2), ch2[:, 1], label="ch2")
ax3.plot(sizing(ch0), ch0[:, 2], label="ch0")
ax3.plot(sizing(ch1), ch1[:, 2], label="ch1")
ax3.plot(sizing(ch2), ch2[:, 2], label="ch2")
ax1.title.set_text("X")
ax2.title.set_text("Y")
ax3.title.set_text("Z")
fig.suptitle("Measurements")
ax1.legend()
ax2.legend()
ax3.legend()


plt.show()