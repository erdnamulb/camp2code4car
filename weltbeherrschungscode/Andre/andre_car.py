import os
import sys
import time

# working directory ermitteln und durchhangeln
absolutepath = os.path.abspath(__file__)
file_dir = os.path.dirname(absolutepath)
parent_dir = os.path.dirname(file_dir)
parent_dir = os.path.dirname(parent_dir)
new_path = os.path.join(parent_dir, 'camp2code-project_phase_1')   
new_path = os.path.join(new_path, 'Code')   
sys.path.append(new_path)
print(new_path)

import basisklassen as bk

# getter: steering_angle, speed, direction
# setter: drive(int,int), stop()

va = bk.Front_Wheels()
ha = bk.Back_Wheels()

class BaseCar:

    def __init__(self):
        self._steering_angle = 90
        self._direction = 0
        self._speed = 0

    def steering_angle(self):
        return self._steering_angle()

    @property
    def direction(self):
        return self._direction

    def stop(self):
        ha.stop()

    @property
    def speed(self):
        return self._speed

    def drive(self, speed: int, dir: int):
        self._direction = dir
        if dir == 1:
            ha.forward()
            self._direction = 1
        elif dir == -1:
            ha.backward()
            self._direction = -1
        else:
            self.stop()
            self._direction = 0
        
        self._speed = speed
        ha.speed = speed

car = BaseCar()
car.drive(0,1)
time.sleep(3)
car.drive(20,-1)        
time.sleep(3)
car.stop()



