from pyfmi import load_fmu
import numpy as np
import matplotlib.pyplot as plt


model = load_fmu('Motor.fmu')

# Create an axis of time.
t = np.linspace(0.,2.,200) 

# Creation of the Ramp function. 
# (Drive from 0[V] to 100[V] in 0.2[s] to 1.0[s].)
x = np.linspace(-20, 220, 200)
x = np.maximum(x, 0)
x = np.minimum(100, x)


u = np.transpose(np.vstack((t,x)))

input_object = ('voltage', u)

res = model.simulate(start_time=0.0,final_time=2.0, input=input_object)


voltage = res['voltage']
current = res['current']
speed = res['speed']
loadTorqueStep_tau = res['loadTorqueStep.tau']
t = res['time']

plt.plot(t, voltage, label="voltage")
plt.plot(t, current, label="current")
plt.plot(t, speed, label="speed")
plt.plot(t, loadTorqueStep_tau, label="loadTorqueStep.tau")
plt.legend(loc='best')
plt.xlabel('time [sec]')

plt.grid(which='both')
plt.show()
