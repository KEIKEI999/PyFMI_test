import sys
import can
import time

def cansend( cycle = 0.1, loop = False ):
	# バス接続
	bus = can.interface.Bus(bustype='vector', channel='1', bitrate=500000, fd=True, data_bitrate=2000000)


	sndparam = [
		0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,
		100,100,
		100,95,90,85,80,75,70,65,60,55,50,45,40,35,30,25,20,15,10,5,0,
		0,0,0,0,0,0,0,0,0,0,
		80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,80,
		50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,
		20,20,20,20,20,20,20,20,20,20,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
	]
	
	while True:
		for p in sndparam:
			byts = (p*0x100).to_bytes(3, 'big', signed=True)
			send_msg = can.Message(arbitration_id=0x111, is_extended_id=0, data=[byts[0], byts[1], byts[2]],is_fd=True, bitrate_switch=True)
			print('Send msg : %s' % send_msg)
			# 送信
			bus.send( send_msg )
			
			time.sleep(cycle)
		if loop==False:
			break;

if __name__ == '__main__':
	cycle = 0.1
	loop = False
	
	args = sys.argv
	if len(args)>1:
		cycle =  float(args[1])
	if len(args)>2:
		if int(args[2]) != 0:
			loop = True
	try:
		cansend(cycle=cycle, loop=loop)
	except KeyboardInterrupt:
		pass
