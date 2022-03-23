import os
import sys

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




 



def main(modus):
    
    car = BaseCar()

    print('------ Fahrparcours --------------------')
    modi = {
        1: 'Fahrparcours 1 - Vorwärts und Rückwärts',
        2: 'Fahrparcours 2 - Kreisfahrt mit max. Lenkwinkel',
        3: 'Fahrparcours 3 - Vorwärtsfahrt bis Hindernis',
        4: 'Fahrparcours 4 - Erkundungstour',
        5: 'Fahrparcours 5 - Linienverfolgung',
        6: 'Fahrparcours 6 - Erweiterte Linienverfolgung',
        7: 'Fahrparcours 7 - 6. + Hinderniserkennung',
        0: 'Ende'
    }

    if modus == None:
        print('--' * 20)
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while True:

        while modus == None:
            modus = input('Wähle  (Andere Taste für Abbruch): ? ')
            if modus in ['1', '2', '3', '4', '5', '6', '7', '0']:
                break
            else:
                modus = None
                print('Getroffene Auswahl nicht möglich.')
                #quit()
        modus = int(modus)

        if modus == 1:
            print(modi[modus])
            car.drive(50,1)
            time.sleep(3)
            car.stop()
            time.sleep(1)
            car.drive(50,-1)
            time.sleep(3)
            car.stop()

        elif modus == 2:
            print(modi[modus])

        elif modus == 3:
            print(modi[modus])

        elif modus == 4:
            print(modi[modus])
        
        elif modus == 5:
            print(modi[modus])
        
        elif modus == 6:
            print(modi[modus])
        
        elif modus == 7:
            print(modi[modus])
        
        elif modus == 0:
            print("Ende")
            quit()
        
        modus = None
        break
    
if __name__ == '__main__':
    
    try:
        modus = sys.argv[1]
    except:
        modus = None

    main(modus)