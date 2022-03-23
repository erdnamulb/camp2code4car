import sys
import os

pfad = sys.path[0]
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(pfad)), "camp2code-project_phase_1", "Code"))
from basisklassen import *

bw = Back_Wheels()
fw = Front_Wheels()
usm = Ultrasonic()
irm = Infrared()


class BaseCar():

    def __init__(self):
        self.steering_angle = 90


    @property
    def steering_angle(self):
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = angle
        fw.turn(angle)


car = BaseCar()
car.steering_angle = 55
print("Erster Winkel")
time.sleep(5)
car.steering_angle = 90
print("Winkel zurück")
#time.sleep(5)
print("Ende Test")