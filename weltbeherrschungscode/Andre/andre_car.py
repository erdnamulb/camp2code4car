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

    def __init__(self) -> None:
        self.angle = 90
        self.direction = 0
        self.speed = 0

    @property
    def angle(self):
        return self.get_angles()

    @property
    def direction(self):
        return self.direction

    @stop.setter
    def stop(self, stop):
        self._stop = stop

    @speed.setter
    def speed(self, speed):
        self._speed = speed

    def drive(self, speed: int, dir: int)
        self.direction = dir
        if dir == 1:
            bw.forward()
            self.direction = 1
        elif dir == -1:
            bw.backward()
            self.direction = -1
        else:
            self.stop()
            self.direction = 0
        
        self.speed = speed
        bw.speed = speed

car = BaseCar()
car.drive(20,1)
time.sleep(3)
car.drive(20,-1)        
time.sleep(3)
car.stop()



