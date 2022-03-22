import sys 

sys.path.append('/home/pi/Projektphase1/camp2code4car/camp2code-project_phase_1/Code')
from basisklassen import *


bw = Back_Wheels()
fw = Front_Wheels()

class BaseCar():
    
    def __init__(self):
        self._steering_angle = 90
        self._speed = 0
        self._direction = 0
        
    @property
    def speed(self):
        return self._speed
        
    @property
    def direction(self, direct: int):
        return self._direction

    def steering_angle(self, angle):
        return self._steering_angle

    def stop(self):
        bw.stop()
    
    def drive(self, speed: int, direction: int):
        self._direction = direction
        if direction == 1: #vorwärts
            bw.forward()
        elif direction == -1: #rückwärts
            bw.backward()
        else: # alles andere = stop
            self.stop()

        self._speed = speed
        bw.speed = speed

car = BaseCar()

car.drive(50,1)
time.sleep(1)
car.drive(50,-1)
time.sleep(1)
car.stop()