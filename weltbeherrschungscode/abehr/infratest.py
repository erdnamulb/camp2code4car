import sys, os, time

from basisklassen import *
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import SensorCar 


from datetime import datetime
import numpy as np

#car = SensorCar()
#print(car.infrared.read_analog())

calibrate = False
forward_speed = 80
backward_speed = 70
turning_angle = 40

max_off_track_count = 40

delay = 0.0005

lf = Infrared()
bw= Back_Wheels()
fw= Front_Wheels()


off_track_count = 0
#lf.cali_references()
irm.
a_step = 3
b_step = 10
c_step = 30
d_step = 45
bw.forward()
i=0
while i<20:
    lt_status_now = lf.read_digital()
    print(lt_status_now)
    i += 1
    time.sleep(0.5)
    # Angle calculate
"""
    if	lt_status_now == [0,0,1,0,0]:
        step = 0	
    elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
        step = a_step
    elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
        step = b_step
    elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
        step = c_step
    elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
        step = d_step

    # Direction calculate
    if	lt_status_now == [0,0,1,0,0]:
        off_track_count = 0
        fw.turn(90)
    # turn right
    elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
        off_track_count = 0
        turning_angle = int(90 - step)
    # turn left
    elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
        off_track_count = 0
        turning_angle = int(90 + step)
    elif lt_status_now == [0,0,0,0,0]:
        off_track_count += 1
        if off_track_count > max_off_track_count:
            #tmp_angle = -(turning_angle - 90) + 90
            tmp_angle = (turning_angle-90)/abs(90-turning_angle)
            tmp_angle *= fw._turning_max
            
            fw.turn(tmp_angle)
            
            
            bw.stop()

            fw.turn(turning_angle)
            time.sleep(0.2)
            bw.speed = forward_speed
            bw.forward()
            time.sleep(0.2)

            

    else:
        off_track_count = 0

    fw.turn(turning_angle)
    time.sleep(delay)
    """


"""
REFERENCES = [200, 200, 200, 200, 200]
#calibrate = True
calibrate = False
forward_speed = 80
backward_speed = 70
turning_angle = 40

max_off_track_count = 40

delay = 0.0005

fw = Front_Wheels.Front_Wheels(db='config')
bw = Back_Wheels.Back_Wheels(db='config')
lf = Infrared.Infrared()

lf.references = REFERENCES
fw.ready()
bw.ready()
fw.turning_max = 45

def straight_run():
	while True:
		bw.speed = 70
		bw.forward()
		fw.turn_straight()

def setup():
	if calibrate:
		cali()

def main():
	global turning_angle
	off_track_count = 0
	bw.speed = forward_speed

	a_step = 3
	b_step = 10
	c_step = 30
	d_step = 45
	bw.forward()
	while True:
		lt_status_now = lf.read_digital()
		print(lt_status_now)
		# Angle calculate
		if	lt_status_now == [0,0,1,0,0]:
			step = 0	
		elif lt_status_now == [0,1,1,0,0] or lt_status_now == [0,0,1,1,0]:
			step = a_step
		elif lt_status_now == [0,1,0,0,0] or lt_status_now == [0,0,0,1,0]:
			step = b_step
		elif lt_status_now == [1,1,0,0,0] or lt_status_now == [0,0,0,1,1]:
			step = c_step
		elif lt_status_now == [1,0,0,0,0] or lt_status_now == [0,0,0,0,1]:
			step = d_step

		# Direction calculate
		if	lt_status_now == [0,0,1,0,0]:
			off_track_count = 0
			fw.turn(90)
		# turn right
		elif lt_status_now in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
			off_track_count = 0
			turning_angle = int(90 - step)
		# turn left
		elif lt_status_now in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
			off_track_count = 0
			turning_angle = int(90 + step)
		elif lt_status_now == [0,0,0,0,0]:
			off_track_count += 1
			if off_track_count > max_off_track_count:
				#tmp_angle = -(turning_angle - 90) + 90
				tmp_angle = (turning_angle-90)/abs(90-turning_angle)
				tmp_angle *= fw.turning_max
				bw.speed = backward_speed
				bw.backward()
				fw.turn(tmp_angle)
				
				lf.wait_tile_center()
				bw.stop()

				fw.turn(turning_angle)
				time.sleep(0.2)
				bw.speed = forward_speed
				bw.forward()
				time.sleep(0.2)

				

		else:
			off_track_count = 0
	
		fw.turn(turning_angle)
		time.sleep(delay)

def cali():
	references = [0, 0, 0, 0, 0]
	print("cali for module:\n  first put all sensors on white, then put all sensors on black")
	mount = 100
	fw.turn(70)
	print("\n cali white")
	time.sleep(4)
	fw.turn(90)
	white_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	fw.turn(110)
	print("\n cali black")
	time.sleep(4)
	fw.turn(90)
	black_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	for i in range(0, 5):
		references[i] = (white_references[i] + black_references[i]) / 2
	lf.references = references
	print("Middle references =", references)
	time.sleep(1)

def destroy():
	bw.stop()
	fw.turn(90)

if __name__ == '__main__':
	try:
		try:
			while True:
				setup()
				main()
				#straight_run()
		except Exception as e:
			print(e)
			print('error try again in 5')
			destroy()
			time.sleep(5)
	except KeyboardInterrupt:
		destroy()
"""

def cali():
	references = [0, 0, 0, 0, 0]
	print("cali for module:\n  first put all sensors on white, then put all sensors on black")
	mount = 100
	fw.turn(70)
	print("\n cali white")
	time.sleep(4)
	fw.turn(90)
	white_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	fw.turn(110)
	print("\n cali black")
	time.sleep(4)
	fw.turn(90)
	black_references = lf.get_average(mount)
	fw.turn(95)
	time.sleep(0.5)
	fw.turn(85)
	time.sleep(0.5)
	fw.turn(90)
	time.sleep(1)

	for i in range(0, 5):
		references[i] = (white_references[i] + black_references[i]) / 2
	lf.references = references
	print("Middle references =", references)
	time.sleep(1)