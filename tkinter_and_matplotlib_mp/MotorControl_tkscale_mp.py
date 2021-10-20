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
from multiprocessing import Process, Pipe
from array import array
from struct import *
import math

class Buffer:
	def __init__(self):
		self.step_size = 0.001
		queue_max = int(4.5/self.step_size)	# 4.5秒分のqueueを用意

		# define queues
		self.deque_voltage = collections.deque(maxlen=queue_max)
		self.deque_current = collections.deque(maxlen=queue_max)
		self.deque_speed = collections.deque(maxlen=queue_max)
		self.deque_loadTorqueStep_tau = collections.deque(maxlen=queue_max)
		self.deque_target = collections.deque(maxlen=queue_max)
		self.deque_time = collections.deque(maxlen=queue_max)
		self.deque_cpuload = collections.deque(maxlen=queue_max)
		


class MotorControl:

	
	def __init__(self):
		self.root = tkinter.Tk()
		self.root.title("DC Motor Control")
		
		w = self.root.winfo_screenwidth()    #モニター横幅取得
		h = self.root.winfo_screenheight()   #モニター縦幅取得
		
		#self.root.geometry("120x100+"+str(w)+"+0")    #位置設定
		self.root.geometry(str(int(w/2))+"x"+str(int(h/2))+"+"+str(int(w/2))+"+0")    #位置設定
		
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
		scale.pack(side = tkinter.LEFT)
		
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
		
		
		self.FMU_conn, self.plot_conn = Pipe()
		self.plot_p = Process(target=FMU_handler, args=(self.FMU_conn,))
		self.plot_p.start()
		
		self._y = 0
		
		#self.FMU_handler()
		self.Info_handler()
		self.plot_handler()
		
		self.root.mainloop()

	#スケール用関数
	def change(self, value):
		if self.scalbln.get():
			self._y = value
			self.plot_conn.send_bytes(array('d',[float(self._y), float(self.sinbln.get()),float(self.sawtoothbln.get())]))
	
	def Info_handler(self):
		self.plot_conn.send_bytes(array('d',[float(self._y), float(self.sinbln.get()),float(self.sawtoothbln.get())]))
		self.root.after(100, self.Info_handler)
	
	# plot用関数(タイマハンドラ)
	def plot_handler(self):
		conn = self.plot_conn
		if conn.poll():
			tmp = conn.recv_bytes(128*1024)
			deque_voltage = list(range(int(len(tmp)/8)))
			for i in range(0,int(len(tmp)/8)):
				deque_voltage[i] = unpack('d',tmp[(i*8):(i*8+8)])[0]
			tmp = conn.recv_bytes(128*1024)
			deque_current = list(range(int(len(tmp)/8)))
			for i in range(0,int(len(tmp)/8)):
				deque_current[i] = unpack('d',tmp[(i*8):(i*8+8)])[0]
			tmp = conn.recv_bytes(128*1024)
			deque_speed = list(range(int(len(tmp)/8)))
			for i in range(0,int(len(tmp)/8)):
				deque_speed[i] = unpack('d',tmp[(i*8):(i*8+8)])[0]
			tmp = conn.recv_bytes(128*1024)
			deque_loadTorqueStep_tau = list(range(int(len(tmp)/8)))
			for i in range(0,int(len(tmp)/8)):
				deque_loadTorqueStep_tau[i] = unpack('d',tmp[(i*8):(i*8+8)])[0]
			tmp = conn.recv_bytes(128*1024)
			deque_target = list(range(int(len(tmp)/8)))
			for i in range(0,int(len(tmp)/8)):
				deque_target[i] = unpack('d',tmp[(i*8):(i*8+8)])[0]
			tmp = conn.recv_bytes(128*1024)
			deque_time = list(range(int(len(tmp)/8)))
			for i in range(0,int(len(tmp)/8)):
				deque_time[i] = unpack('d',tmp[(i*8):(i*8+8)])[0]
			tmp = conn.recv_bytes(128*1024)
			deque_cpuload = list(range(int(len(tmp)/8)))
			for i in range(0,int(len(tmp)/8)):
				deque_cpuload[i] = unpack('d',tmp[(i*8):(i*8+8)])[0]
		
			if self.pausebln.get() == False:
				self.ax.lines[0].set_data( np.array(deque_time), np.array(deque_target) )
				self.ax.lines[1].set_data( np.array(deque_time), np.array(deque_voltage) )
				self.ax.lines[2].set_data( np.array(deque_time), np.array(deque_speed) )
				self.ax.lines[3].set_data( np.array(deque_time), np.array(deque_loadTorqueStep_tau) )
				self.ax.lines[4].set_data( np.array(deque_time), np.array(deque_current) )
				if self.cpuloadbln.get():
					self.ax.lines[5].set_data( np.array(deque_time), np.array(deque_cpuload) )
				self.ax.relim()                  # recompute the data limits
				self.ax.autoscale_view()         # automatic axis scaling
				self.ax.set_ylim(-70,200)
				self.ax.set_xlim(deque_time[len(deque_time)-1]-4.0,deque_time[len(deque_time)-1])
				self.canvas.draw()
		
		self.root.after(1, self.plot_handler)

_y = 0
# FMUシミュレーション用関数(タイマハンドラ)
def FMU_handler(conn):
	global _y
	model_sub1 = FMUModelCS2( "PID.fmu", "", _connect_dll=True)
	model_sub2 = FMUModelCS2( "Motor.fmu", "", _connect_dll=True)
	model_dummy = Dummy_FMUModelCS2([], "Dummy.fmu", "", _connect_dll=False)
	
	model_dummy.values[model_dummy.get_variable_valueref("y")] = 0
	
	def do_dummy(current_t, step_size, new_step=True):
		global _y
		model_dummy.values[model_dummy.get_variable_valueref("y")] = _y
		model_dummy.completed_integrator_step()
		return 0
	
	
	model_dummy.do_step = do_dummy
	
	models = [model_sub1, model_sub2, model_dummy]
	connections = [(model_dummy,"y", model_sub1,"target" ),
		(model_sub1,"y",model_sub2,"voltage"),
		(model_sub2,"speed",model_sub1,"u")]


	master = Master(models, connections)
	
	# define timers
	start_tick = time.perf_counter()
	opts = master.simulate_options()
	step_size = 0.001
	opts["step_size"] = step_size
	opts["initialize"] = 1
	currenttime = 0
	buf = Buffer()
	cnt = 0
	sinbln = False
	sawtoothbln = False
	g_y = 0.0
	while True:
		flg_snd = False
		y_tmp = g_y
		
		if conn.poll(0):
			tmp = conn.recv_bytes(64)
			y_tmp = unpack('d',tmp[0:8])[0]
			g_y = y_tmp;
			
			if unpack('d',tmp[8:16])[0] > 0:
				sinbln = True
			else:
				sinbln = False
			
			if unpack('d',tmp[16:24])[0] > 0:
				sawtoothbln = True
			else:
				sawtoothbln = False
			
		
		# sin波生成
		if sinbln:
			y_tmp = math.sin(currenttime*4)*50+50
		
		# のこぎり波生成
		if sawtoothbln:
			A = 100
			N = 500
			y = 0.0
			omega = 1/2
			for n in range(1,N):
				y += - A / (np.pi * n) * np.sin( n * 2 * np.pi * omega * currenttime)
			y += A / 2.0
			y_tmp += y
		
		_y = y_tmp
		
		
		current_tick = time.perf_counter()
		delta_tick = current_tick - start_tick;
		start_tick = current_tick
		delta_simulate = delta_tick
		
		with redirect_stdout(open(os.devnull, 'w')):
			res = master.simulate(start_time=currenttime, final_time=currenttime+delta_simulate-step_size/100, options=opts)
		opts["initialize"] = 0
		step_size = buf.step_size
		opts["step_size"] = step_size
		
		currenttime = currenttime + delta_simulate
		
		buf.deque_voltage.extend(res[model_sub2]['voltage'])
		buf.deque_current.extend(res[model_sub2]['current'])
		buf.deque_speed.extend(res[model_sub2]['speed'])
		buf.deque_loadTorqueStep_tau.extend(res[model_sub2]['loadTorqueStep.tau'])
		buf.deque_target.extend(res[model_sub1]['target'])
		buf.deque_time.extend(res[model_sub2]['time'])
		buf.deque_cpuload.extend(np.ones(len(res[model_sub2]['time']))*delta_simulate*1000)
		
		if cnt >= 10:
			start = time.perf_counter()
			print("start:" + str(start))
			conn.send_bytes(array('d',buf.deque_voltage))
			conn.send_bytes(array('d',buf.deque_current))
			conn.send_bytes(array('d',buf.deque_speed))
			conn.send_bytes(array('d',buf.deque_loadTorqueStep_tau))
			conn.send_bytes(array('d',buf.deque_target))
			conn.send_bytes(array('d',buf.deque_time))
			conn.send_bytes(array('d',buf.deque_cpuload))
			end = time.perf_counter()
			print("end:" + str(end))
			print("diff:" + str(end - start) )
			cnt = 0
		cnt = cnt + 1
	

if __name__ == '__main__':
	app = MotorControl()