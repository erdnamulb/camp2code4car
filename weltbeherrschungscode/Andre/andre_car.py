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

    @property
    def steering_angle(self):
        return self._steering_angle()

    @property
    def direction(self):
        return self._direction

    @property
    def speed(self):
        return self._speed

    def stop(self):
        ha.stop()

    @steering_angle.setter
    def steering_angle(self, angle):
        self._steering_angle = angle
        va.turn(angle)

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

def parc1():
    print("Fahrparcours 1 - Vorwärts und Rückwärts")
    car.drive(30,1)
    time.sleep(3)
    car.stop()
    time.sleep(1)
    car.drive(30,-1)        
    time.sleep(3)
    car.stop()

def parc2():
    print("Fahrparcours 2 - Kreisfahrt mit maximalem Lenkwinkel")
    car.steering_angle = 90
    car.drive(30,1)
    time.sleep(1)
    car.steering_angle = 125
    time.sleep(3)
    car.stop()
    car.steering_angle = 125
    car.drive(30,-1)
    time.sleep(3)
    car.steering_angle = 90
    time.sleep(1)
    car.stop()
    # Wiederholung entgegen UZS
    car.drive(30,1)
    time.sleep(1)
    car.steering_angle = 55
    time.sleep(3)
    car.stop()
    car.steering_angle = 55
    car.drive(30,-1)
    time.sleep(3)
    car.steering_angle = 90
    time.sleep(1)
    car.stop()

def parc3(): 
    print("Fahrparcours 3 - Vorwärtsfahrt bis Hindernis")

def parc4(): 
    print("Fahrparcours 4 - Erkundungstour mit Hindernis")

def quit(): 
    print("Beende das Programm")
    
def handle_menu(menu):
    while True:
        for index, item in enumerate(menu, 1):
            print("{}  {}".format(index, item[0]))
        choice = int(input("Ihre Wahl? ")) - 1
        if 0 <= choice < len(menu):
            menu[choice][1]()
        else:
            print("Bitte nur Zahlen im Bereich 1 - {} eingeben".format(
                                                                    len(menu)))

menu = [
    ["- langsam Vorwärts und Rückwärts", parc1],
    ["- Kreisfahrt mit maximalem Lenkwinkel", parc2],
    ["- Vorwärtsfahrt bis Hindernis", parc3],
    ["- Erkundungstour", parc4],
    ["- Beenden", quit]
]

handle_menu(menu)