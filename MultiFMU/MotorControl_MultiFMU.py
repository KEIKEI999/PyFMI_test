from pyfmi import FMUModelCS2, Master
import numpy as np
import matplotlib.pyplot as plt

model_sub1 = FMUModelCS2( "PID.fmu", "", _connect_dll=True)
model_sub2 = FMUModelCS2( "Motor.fmu", "", _connect_dll=True)
model_sub3 = FMUModelCS2( "Ramp.fmu", "", _connect_dll=True)

models = [model_sub1, model_sub2, model_sub3]
connections = [
    (model_sub3,"y",model_sub1,"target"),
    (model_sub1,"y",model_sub2,"voltage"),
    (model_sub2,"speed",model_sub1,"u"),
    ]

master = Master(models, connections)

opts = master.simulate_options()
opts["step_size"] = 0.001

res = master.simulate(final_time=2.0, options=opts)

voltage = res[model_sub2]['voltage']
current = res[model_sub2]['current']
speed = res[model_sub2]['speed']
loadTorqueStep_tau = res[model_sub2]['loadTorqueStep.tau']
target = res[model_sub1]['target']

t = res[model_sub1]['time']

plt.plot(t, voltage, label="voltage")
plt.plot(t, current, label="current")
plt.plot(t, speed, label="speed")
plt.plot(t, loadTorqueStep_tau, label="loadTorqueStep.tau")
plt.plot(t, target, label="target")
plt.legend(loc='best')
plt.xlabel('time [sec]')

plt.grid(which='both')
plt.show()
