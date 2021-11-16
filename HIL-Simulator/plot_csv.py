from matplotlib import *
import pandas as pd
# plotting state space
import matplotlib.pyplot as plt

fname = "test1.csv"
data = pd.read_csv(fname)

xyz = data.iloc[:,:3]
vxyz = data.iloc[:,3:6]
pqr = data.iloc[:, -3:]


xyz.plot()
vxyz.plot()
pqr.plot()
plt.show()


#plot XYZ


#plot Vx, Vy, Vz



#plot P, Q, R


