from pyfmi import load_fmu, FMUModelCS2, Master
from pyfmi.tests.test_util import Dummy_FMUModelCS2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import collections
import time
import sys
import tkinter
import os
from contextlib import redirect_stdout
import math
import can

class MotorControl:
	def do_dummy(self, current_t, step_size, new_step=True):
		self.model_dummy.values[self.model_dummy.get_variable_valueref("y")] = self._y
		self.model_dummy.completed_integrator_step()
		return 0
	
	def __init__(self):
		# バス接続
		self.bus = can.interface.Bus(bustype='vector', channel='1', bitrate=500000)

		self.root = tkinter.Tk()
		self.root.title("DC Motor Control")
		
		w = self.root.winfo_screenwidth()    #モニター横幅取得
		h = self.root.winfo_screenheight()   #モニター縦幅取得
		
		#self.root.geometry("120x100+"+str(w)+"+0")    #位置設定
		self.root.geometry(str(int(w/2))+"x"+str(int(h/2))+"+"+str(int(w/2))+"+0")    #位置設定
		
		self.model_sub1 = FMUModelCS2( "PID.fmu", "", _connect_dll=True)
		self.model_sub2 = FMUModelCS2( "Motor.fmu", "", _connect_dll=True)
		self.model_dummy = Dummy_FMUModelCS2([], "Dummy.fmu", "", _connect_dll=False)
		
		self.model_dummy.values[self.model_dummy.get_variable_valueref("y")] = 0
		
		self._y = 0
		self._ytmp = 0
		self.y_can_tmp = 0
		
		
		self.model_dummy.do_step = self.do_dummy
		
		models = [self.model_sub1, self.model_sub2, self.model_dummy]
		connections = [(self.model_dummy,"y", self.model_sub1,"target" ),
			(self.model_sub1,"y",self.model_sub2,"voltage"),
			(self.model_sub2,"speed",self.model_sub1,"u")]


		self.master = Master(models, connections)
		
		self.step_size = 0.001
		queue_max = int(8.5/self.step_size)	# 8.5秒分のqueueを用意

		# define queues
		self.deque_voltage = collections.deque(maxlen=queue_max)
		self.deque_current = collections.deque(maxlen=queue_max)
		self.deque_speed = collections.deque(maxlen=queue_max)
		self.deque_loadTorqueStep_tau = collections.deque(maxlen=queue_max)
		self.deque_target = collections.deque(maxlen=queue_max)
		self.deque_time = collections.deque(maxlen=queue_max)
		self.deque_cpuload = collections.deque(maxlen=queue_max)

		
		# define figure
		self.fig = plt.figure()
		self.fig.set_size_inches(8.4, 4.5)
		self.ax = plt.subplot(1,1,1)
		self.ax.set_xlabel('Time')
		self.ax.set_ylabel('Value')
		#fig.show()

		# define plots
		self.ax.plot([], [], label="target[rad/s]", color='Magenta',linewidth=3)
		self.ax.plot([], [], label="voltage[V]", color='Red')
		self.ax.plot([], [], label="speed[rad/s]", color='Blue',linewidth=0.9)
		self.ax.plot([], [], label="loadTorqueStep.tau[N m]", color='Cyan')
		self.ax.plot([], [], label="current[A]", color='Green',linestyle='--',linewidth=0.8)
		self.ax.plot([], [], label="cpu_load[ms]", color='Black',linestyle='--',linewidth=1)

		self.ax.legend(bbox_to_anchor=(1, 1), borderaxespad=0, fontsize=10)
		self.ax.grid(which='both')
		
		#Figureを埋め込み
		self.canvas = FigureCanvasTkAgg(self.fig, self.root)
		self.canvas.get_tk_widget().pack(side = tkinter.RIGHT)
		
		#ツールバーを表示
		toolbar=NavigationToolbar2Tk(self.canvas, self.root)
		toolbar.place(x=0, y=h/2-40)
		
		#スケール
		scale = tkinter.Scale(
			self.root,
			label = "target Speed",
			orient=tkinter.VERTICAL,    #方向
			command=self.change,         #調整時に実行
			length = 300,
			from_ = 100,
			to = 0
			)
		#scale.pack(side = tkinter.LEFT)
		scale.place(x=0, y=140)
		
		#checkbutton
		self.scalbln = tkinter.BooleanVar()
		self.scalbln.set(True)
		chk = tkinter.Checkbutton(self.root, variable=self.scalbln, text="Enable Scale bar")
		chk.place(x=0, y=10)
		
		self.cpuloadbln = tkinter.BooleanVar()
		self.cpuloadbln.set(False)
		chk = tkinter.Checkbutton(self.root, variable=self.cpuloadbln, text="Enable Cpu Load")
		chk.place(x=0, y=30)
		
		self.pausebln = tkinter.BooleanVar()
		self.pausebln.set(False)
		chk = tkinter.Checkbutton(self.root, variable=self.pausebln, text="pause")
		chk.place(x=0, y=50)
		
		self.sinbln = tkinter.BooleanVar()
		self.sinbln.set(False)
		chk = tkinter.Checkbutton(self.root, variable=self.sinbln, text="sin wave")
		chk.place(x=0, y=70)

		self.sawtoothbln = tkinter.BooleanVar()
		self.sawtoothbln.set(False)
		chk = tkinter.Checkbutton(self.root, variable=self.sawtoothbln, text="Sawtooth wave")
		chk.place(x=0, y=90)

		self.canrcvbln = tkinter.BooleanVar()
		self.canrcvbln.set(False)
		chk = tkinter.Checkbutton(self.root, variable=self.canrcvbln, text="can rcv")
		chk.place(x=0, y=110)

		# define timers
		self.start_tick = time.perf_counter()
		self.opts = self.master.simulate_options()
		self.opts["step_size"] = self.step_size
		self.opts["initialize"] = 1
		self.currenttime = 0
		
		self.FMU_handler()
		self.plot_handler()
		
		self.root.mainloop()

	#スケール用関数
	def change(self, value):
		if self.scalbln.get():
			self._ytmp = float(value)
			self._y = float(value)
	
	# FMUシミュレーション用関数(タイマハンドラ)
	def FMU_handler(self):
		current_tick = time.perf_counter()
		delta_tick = current_tick - self.start_tick;
		self.start_tick = current_tick
		delta_simulate = delta_tick
		
		# Scale取り込み(OFFSET)
		y_tmp = 0
		if self.scalbln.get():
			y_tmp = self._ytmp
		else:
			y_tmp = 0
		
		# sin波生成
		if self.sinbln.get():
			y_tmp += math.sin(self.currenttime*4)*50+50
		
		# のこぎり波生成
		if self.sawtoothbln.get():
			A = 100
			N = 500
			y = 0.0
			omega = 1/2
			for n in range(1,N):
				y += - A / (np.pi * n) * np.sin( n * 2 * np.pi * omega * self.currenttime)
			y += A / 2.0
			y_tmp += y
		
		# CAN recv(polling)
		if self.canrcvbln.get():
			recv_msg = self.bus.recv(timeout=0.0)
			if recv_msg != None:
				if recv_msg.arbitration_id == 0x111:
					data = recv_msg.data[0]*0x10000 + recv_msg.data[1]*0x100 + recv_msg.data[2]
					self.y_can_tmp = data/255.0
					y_tmp += self.y_can_tmp
			else:
				y_tmp += self.y_can_tmp
		
		self._y = y_tmp
		
		with redirect_stdout(open(os.devnull, 'w')):
			res = self.master.simulate(start_time=self.currenttime, final_time=self.currenttime+delta_simulate-self.step_size/100, options=self.opts)
		self.opts["initialize"] = 0
		
		self.currenttime = self.currenttime + delta_simulate
		
		self.deque_voltage.extend(res[self.model_sub2]['voltage'])
		self.deque_current.extend(res[self.model_sub2]['current'])
		self.deque_speed.extend(res[self.model_sub2]['speed'])
		self.deque_loadTorqueStep_tau.extend(res[self.model_sub2]['loadTorqueStep.tau'])
		self.deque_target.extend(res[self.model_sub1]['target'])
		self.deque_time.extend(res[self.model_sub2]['time'])
		self.deque_cpuload.extend(np.ones(len(res[self.model_sub2]['time']))*delta_simulate*1000)
		
		self.root.after(1, self.FMU_handler)
	
	# plot用関数(タイマハンドラ)
	def plot_handler(self):
		if self.pausebln.get() == False:
			self.ax.lines[0].set_data( np.array(self.deque_time), np.array(self.deque_target) )
			self.ax.lines[1].set_data( np.array(self.deque_time), np.array(self.deque_voltage) )
			self.ax.lines[2].set_data( np.array(self.deque_time), np.array(self.deque_speed) )
			self.ax.lines[3].set_data( np.array(self.deque_time), np.array(self.deque_loadTorqueStep_tau) )
			self.ax.lines[4].set_data( np.array(self.deque_time), np.array(self.deque_current) )
			if self.cpuloadbln.get():
				self.ax.lines[5].set_data( np.array(self.deque_time), np.array(self.deque_cpuload) )
			self.ax.relim()                  # recompute the data limits
			self.ax.autoscale_view()         # automatic axis scaling
			self.ax.set_ylim(-70,200)
			self.ax.set_xlim(self.deque_time[-1]-8,self.deque_time[-1])
			self.canvas.draw()
		
		self.root.after(200, self.plot_handler)

if __name__ == '__main__':
	app = MotorControl()