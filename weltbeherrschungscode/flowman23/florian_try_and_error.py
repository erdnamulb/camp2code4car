import os
import sys
import time

# aktuellen Pfad herausfinden:
path_to_myproject = sys.path[0]
# mit dirname zweimal nach oben springen und dann mit join in die unterordner wechseln
# anschliessend mit sys.path.append den zu durchsuchenden Systempfad erweitern auf diesen ordner
# dieser wird dann auch nach dem basisklassen.py durchsucht
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(path_to_myproject)), "camp2code-project_phase_1", "Code"))

from basisklassen import *


# print(sys.path[0])
# path_to_myproject = os.path.abspath(__file__)
# print(path_to_myproject)
# print(os.path.join(os.path.dirname(os.path.dirname(path_to_myproject)), "camp2code-project_phase_1", "Code"))

# ----------------- init --------------------
bw = Back_Wheels()
fw = Front_Wheels()
usm = Ultrasonic()
irm = Infrared()

class BaseCar():
    
    def __init__(self):
        self._steering_angle = 90
        self._speed = 0
        self._direction = 0
        
    @property
    def speed(self):
        return self._speed
        
    @property
    def direction(self):
        return self._direction

    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = angle
        fw.turn(angle)

    def stop(self):
        bw.stop()
    
    def drive(self, speed: int, direction: int):
        self._direction = direction
        if direction == 1: #vorwärts
            bw.forward()
            self._direction = 1
        elif direction == -1: #rückwärts
            bw.backward()
            self._direction = -1
        else: # alles andere = stop
            self.stop()
            self._direction = 0

        self._speed = speed
        bw.speed = speed

car = BaseCar()
"""car.drive(20, 1)
time.sleep(3)
car.stop()"""

car.drive(50, 1)
time.sleep(1)
car.stop()
time.sleep(1)
car.steering_angle = 135
car.drive(50, 1)
time.sleep(8)
car.stop()
car.steering_angle = 90
