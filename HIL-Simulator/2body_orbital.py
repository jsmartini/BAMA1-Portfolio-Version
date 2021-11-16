import scipy as sci
import scipy.integrate
import matplotlib.pyplot as plt
import numpy as np

class Object:
    def __init__(self,name,mu,I_matrix,prop_time):
        self.name = name
        self.mu = mu
        self.I = I_matrix
        self.invI = np.linalg.inv(I_matrix)
        self.tspan = prop_time
        self.M_magts = np.zeros(3)
    

    def init_state(self,position,velocity,quaternion,ang_rates):
        #edit so this takes orbital elements and converts them into these values
        self.inits = np.concatenate((position,velocity,quaternion,ang_rates))

    @staticmethod
    def dynamics(inits,t,Obj):
        #translational
        pos = inits[0:3]
        vel = inits[3:6]
        acc = -Obj.mu*pos/sci.linalg.norm(pos)**3

        #rotational
        p = inits[10]
        q = inits[11]
        r = inits[12]
        quat = np.reshape(inits[6:10],(4,1))
        pqr = inits[10:]

        pqr_mat = np.array([[0,-p,-q,-r],[p,0,r,-q],[q,-r,0,p],[r,q,-p,0]])
        quatdot = 0.5*np.matmul(pqr_mat,quat)
        quatdot = np.reshape(quatdot,4)

        H = np.reshape(np.matmul(Obj.I,pqr),3)
        pqrdot = np.matmul(Obj.invI,Obj.M_magts - np.cross(pqr,H))
        deriv =np.concatenate((vel,acc,quatdot,pqrdot))

        
        return deriv
    
    def controller(self):
        b_field = self.igrf_call()
        # write bdot
        #update self.M_magts

    def igrf_call(self):
        # convert pos to lat,long,r
        #call igrf model
        #convert NED to body coords
        b_field = np.reshape([0,0,0],(1,3))
        return b_field
        
    def propagate(self):
        self.sol = sci.integrate.odeint(self.dynamics,self.inits,self.tspan,args=(self,))
        print(self.sol.shape)
        self.plots()

    def plots(self):
        self.plot_pos()
        self.plot_angrates()
    
    def plot_pos(self):
        x = self.sol[:,0]
        y = self.sol[:,1]
        z = self.sol[:,2]

        plt.figure()
        plt.plot(x,y,label='Bama-1')
        plt.scatter(0,0,label='Earth')
        plt.axis('equal')
        plt.xlabel('x (km)')
        plt.ylabel('y (km)')
        plt.legend()
        plt.show

        plt.figure()
        plt.plot(x,z,label='Bama-1')
        plt.scatter(0,0,label='Earth')
        plt.axis('equal')
        plt.xlabel('x (km)')
        plt.ylabel('z (km)')
        plt.legend()
        plt.show

    def plot_angrates(self):
        wx = self.sol[:,10]
        wy = self.sol[:,11]
        wz = self.sol[:,12]
        plt.figure()
        plt.plot(self.tspan,wx,label='wx')
        plt.plot(self.tspan,wy,label='wy')
        plt.plot(self.tspan,wz,label='wz')
        plt.xlabel('time (s)')
        plt.ylabel('ang velocity (rad/s)')
        plt.legend()
        plt.title('angular rates')
        plt.show()


#init values from simulink model
pos = np.array([4.3202e3,-5.1486e3,0])
vel = np.array([-0.7036,-0.5904,7.6461])
ang_rates = np.array([np.pi,np.pi,np.pi])
quat = np.array([1,0,0,0])

mu = 398600     #grav param of earth, km3/s2
I_matrix = np.array([[1.731,0,0],[0,1.726,0],[0,0,0.264]])/1000
period = 5.4836e3   #s
num_orbits = 1
dt = 1              #s
prop_time = np.arange(0,num_orbits*period,dt)

Sat = Object("Sat",mu,I_matrix,prop_time)
Sat.init_state(pos,vel,quat,ang_rates)
Sat.propagate()





# to do
# add igrf model
# make it convert from orbital elements
# controller