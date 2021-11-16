import scipy as sci
import scipy.integrate
import matplotlib.pyplot as plt
import numpy as np
import zmq
import pyIGRF
import json
from log import *
import sys 
from datetime import timedelta
import ast
import pickle
from mpl_toolkits.mplot3d import Axes3D
import os
from time import sleep
from RT3DPlotter import *
from RT2DPlotter import *
from RTQuaternionPlotter import *
from csvrecorder import *

norm = lambda *args: np.sqrt(np.sum([np.power(i, 2) for i in args]))




dates2nparrange = lambda begin, end, ts: np.arange(0,int(end.timestamp() - begin.timestamp()), ts)

def transf_e(phi, theta, psi):
    ct = np.cos(theta);
    st = np.sin(theta);
    sp = np.sin(phi);
    cp = np.cos(phi);
    ss = np.sin(psi);
    cs = np.cos(psi);

    T = [
        [ct*cs,sp*st*cs-cp*ss,cp*st*cs+sp*ss],
        [ct*ss,sp*st*ss+cp*cs,cp*st*ss-sp*cs],
        [-st,sp*ct,cp*ct]
        ];

    return np.array(T)

def transf_q(quat):
    #compute R such that v(inertial) = TIB v(body)
    # creates transformation matrix from quaternion
    q0, q1, q2, q3 = quat

    T = [
            [(q0**2+q1**2-q2**2-q3**2), 2*(q1*q2-q0*q3),  2*(q0*q2+q1*q3)],
            [2*(q1*q2+q0*q3), (q0**2-q1**2+q2**2-q3**2), 2*(q2*q3-q0*q1)],
            [2*(q1*q3-q0*q2), 2*(q0*q1+q2*q3), (q0**2-q1**2-q2**2+q3**2)]
      ]
    
    return np.array(T)


def setup_simulation_server(port):
    """
        Sets up the ZMQ Server (REP/REQ)
        for the BAMA-1 satellite to connect to.

        hosts the simulator on the network
    """
    try:
        ctx = zmq.Context()
        skt = ctx.socket(zmq.REP)
        skt.bind(f"tcp://*:{port}")
        info(f"Bound to port {port}")
    except zmq.Error as e:
        critical(e)
        exit(-1)
    return skt, ctx

    """
        self.tspan = prop_time
        self.M_magts = np.zeros(3)
        # network server socket
        self.skt = setup_simulation_server(port)
    """
plt.ion()

class OrbitalSimulator:
    
    def __init__(self, **kwargs):
        info("Initializing Simulator")
        self.name = kwargs['name']
        self.mu = kwargs['mu']
        self.I = kwargs['I']
        self.invI = np.linalg.inv(self.I)
        self.current_time = kwargs['initial_date'] + timedelta(seconds=kwargs["time_step"])
        self.init_time = self.current_time
        self.end_time = kwargs['end_date']    # proptime
        self.magnetic_field = np.zeros(3)
        self.skt, self.ctx = setup_simulation_server(kwargs["port"])
        self.time_step = kwargs['time_step']
        
        self.last_time = self.init_time
        self.tspan = [0, self.time_step]
        delta = (self.end_time - self.init_time).days
        self.time_list = np.arange(0, delta * 24 * 3600 * 10, 1)
        self.time_idx =0
        # define figures to update
        self.torque = np.zeros(3)
        hist = kwargs['hist']
        self.fig1 = plt.figure()
        self.fig2 = plt.figure()
        self.D3plot = RT3DPlot(
                history=10000,
                fig = self.fig1,
                ax = self.fig1.add_subplot(121, projection="3d")
            )
        self.Qplot = RTQuaternionPlotter(
                history=30,
                fig = self.fig1,
                ax=self.fig1.add_subplot(122, projection="3d")
            )
        
        self.WXPlot = RT2DPlot(
            history=30,
            fig = self.fig2,
            ax=self.fig2.add_subplot(121),
        )
        self.WYPlot = RT2DPlot(
            history=30,
            fig = self.fig2,
            ax=self.fig2.add_subplot(122), 
            
        )
        self.WZPlot = RT2DPlot(
            history=30,
            fig = self.fig2,
            ax=self.fig2.add_subplot(221),
            
        )
        self.MXPlot = RT2DPlot(
            history=30,
            fig = self.fig2,
            ax=self.fig2.add_subplot(222),
            
        )
        self.MYPlot = RT2DPlot(
            history=30,
            fig = self.fig2,
            ax=self.fig2.add_subplot(321),
            
        )
        self.MZPlot = RT2DPlot(
            history=30,
            fig = self.fig2,
            ax=self.fig2.add_subplot(322),
            
        )
        self.fig1.tight_layout()
        self.fig2.tight_layout()
        


    def init_state(self,position,velocity,quaternion,ang_rates):
        #edit so this takes orbital elements aself.history = np.array(shape=(1,13))
        self.inits = np.concatenate((position,velocity,quaternion,ang_rates))
        self.current_state = self.inits
        self.sol = [self.current_state]

    @staticmethod
    def dynamics(inits,t, obj_ref, torque):
        # obj_ref is the self reference being passed to scipy odeint
        #translational
        pos = inits[0:3]
        vel = inits[3:6]
        acc = -obj_ref.mu*pos/sci.linalg.norm(pos)**3
        p = inits[10]
        q = inits[11]
        r = inits[12]
        quat = np.reshape(inits[6:10],(4,1))
        pqr = inits[10:]
        
        pqr_mat = np.array([[0,-p,-q,-r],[p,0,r,-q],[q,-r,0,p],[r,q,-p,0]])
        quatdot = 0.5*np.matmul(pqr_mat,quat)
        quatdot = np.reshape(quatdot,4)
        H = np.reshape(np.matmul(obj_ref.I,pqr),3) 
        pqrdot = np.matmul(obj_ref.invI,torque - np.cross(pqr,H))
        
        deriv = np.concatenate((vel, acc, quatdot, pqrdot))
        return deriv

    def _step(self):
        self.time_idx += 1
        # integrate only a time step forward (by sensor sampling time)
        
        magnetometer_reading = self.MMC5883MASense(self.current_state)

        self.current_state = sci.integrate.odeint(self.dynamics, self.current_state, self.tspan, args=(self,self.torque,))[1]
        self.sol.append(self.current_state.tolist())
        self.last_time = self.current_state
        self.current_time += timedelta(seconds=self.time_step)
        update(time=self.current_time, data=self.current_state, color=Fore.CYAN, units="STATE SPACE")
        return magnetometer_reading
        
        #controller_response = ast.literal_eval(controller_response)
        #print(controller_response)

    def propagate(self):
        self.sol = sci.integrate.odeint(self.dynamics,self.inits,self.tspan,args=(self,))
        self.plots()
  
    def MMC5883MASense(self, state):
        #simulates reading from the MMC5883MA magnetometers
        # converts R vector to lat lon H for IGRF calls
        x, y, z = state[0:3]
        quat = state[6:10]
        r = norm(x,y,z)
        phiE = 0
        psiE = np.arctan2(y,x)
        thetaE = np.arccos(z/r)
        lat = 90 - thetaE*180/np.pi
        long = psiE*180/np.pi

        BN, BE, BD = pyIGRF.igrf_value(lat, long, alt=r, year=self.current_time.year)[3:-1]
        BI = transf_e(phiE,thetaE+np.pi,psiE)@np.array([BN,BE,BD])     #mag field in inertial frame
        BB = transf_q(quat).T*BI;                                   #transposed bc normally BI=T*BB, mag field in body frame
        B_body = BB/1e9;                                        #convert to T from nT and then to Gauss
        return B_body.diagonal()

    def serve_simulator(self):
        info("Serving Orbital Simulator")
        while 1:
            
            res = self.skt.recv_string()
            self.mag_reading = self._step()
            self.skt.send_string(
            json.dumps(
                    {
                    "time": self.current_time.strftime("%y-%m-%d %H:%M:%S"),
                    "data": self.mag_reading.tolist(),
                    }
                )
            )
            print(f"\n\n\nTIME\n{self.current_time.strftime('%y-%m-%d %H:%M:%S')}\n\nEND TIME")
            res = self.skt.recv_string()            
            res = json.loads(res)
            if type(res) != dict:
                res = json.loads(res)
            self.torque = np.array(res["torque"])
            update(self.current_time, np.array(res["torque"]), color=Fore.LIGHTCYAN_EX, units="Nm")
            self.skt.send_string("ACK") # preventing deadlock of REP/REQ
            self.plot_continuous()
            recorder(self.current_state.tolist())
            #sleep(0.1)
            
    
    def plot_continuous(self):
        sol = np.array(self.sol)    
        x = self.current_state[0]
        y = self.current_state[1]
        z = self.current_state[2]
        self.D3plot.update_ax(x, y ,z)
        quat = self.current_state[6:10].tolist()
        self.Qplot.update_ax(quat)
        wx, wy, wz = self.current_state[10:].tolist()
        t = self.current_time.timestamp()
        self.WXPlot.update_ax(t, wx,XLabel = "time", YLabel = "Angular Velocity X")
        self.WYPlot.update_ax(t, wy,XLabel = "time", YLabel = "Angular Velocity Y")
        self.WZPlot.update_ax(t, wz,XLabel = "time", YLabel = "Angular Velocity Z")
        mx, my, mz = self.mag_reading.tolist()
        self.MXPlot.update_ax(t, mx,XLabel = "time", YLabel = "Magnetometer X")
        self.MYPlot.update_ax(t, my,XLabel = "time", YLabel = "Magnetometer Y")
        self.MZPlot.update_ax(t, mz,XLabel = "time", YLabel = "Magnetometer Z")
        
        self.fig1.canvas.draw()
        self.fig1.canvas.flush_events()
        self.fig2.canvas.draw()
        self.fig2.canvas.flush_events()


if __name__ == '__main__':
    import sys
    LEVEL = sys.argv[1]
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

    Sat = OrbitalSimulator(
        name = "BAMA-1",
        mu=mu,
        I=I_matrix,
        initial_date = datetime.datetime(year=2010, month=3, day=1),
        end_date = datetime.datetime(year=2010, month=4, day=15),
        time_step = 0.1,
        port = 7777,
        hist=1000
    )
    Sat.init_state(pos,vel,quat,ang_rates)
    Sat.serve_simulator()
    
