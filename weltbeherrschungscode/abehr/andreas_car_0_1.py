import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), 'camp2code-project_phase_1', 'Code'))
from basisklassen import *
import traceback
import loggingc2c as log

db_path = f"{sys.path[0]}/andreasdb.sqlite"

class BaseCar():

    def __init__(self):
        self._steering_angle = 90
        self._speed = 0
        self._direction = 0
        
        try:
            path= os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), 'camp2code-project_phase_1', 'Code')
            with open(path +"/config.json", "r") as f:
                data = json.load(f)
                turning_offset = data["turning_offset"]
                forward_A = data["forward_A"]
                forward_B = data["forward_B"]
                print("Turning Offset: ", turning_offset)
                print("Forward A: ", forward_A)
                print("Forward B: ", forward_B)
        except:
            print("config.json nicht gefunden")
            turning_offset = 0
            forward_A = 0
            forward_B = 0

        self.bw = Back_Wheels(forward_A=forward_A, forward_B=forward_B)
        self.fw = Front_Wheels(turning_offset=turning_offset)
        self.usm = Ultrasonic()
        self.irm = Infrared()
        self.bw.stop()

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
        self.fw.turn(angle)

    def stop(self):
        self.bw.stop()

    def drive(self, speed: int, direction: int):
        self._direction = direction
        if direction == 1: #vorwärts
            self._direction = 1
            self.bw.forward()
        elif direction == -1: #rückwärts
            self.bw.backward()
            self._direction = -1
        else: # alles andere = stop
            self.stop()
            self._direction = 0

        self._speed = speed
        self.bw.speed = speed
    
    def wait_angle(self,  waitTime: float, angle: int):
        now = 0
        while now < waitTime:
            self.steering_angle = angle
            time.sleep(.5)
            now += .5
            print(f"time= {now:.1f} set_angle = {angle}")


class SonicCar(BaseCar):

    def __init__(self):
        super().__init__()
        self._distance = 0

    @property
    def distance(self):
        self._distance = self.usm.distance()
        return self._distance

class Fahrdaten():

    def __init__(self) -> None:
        self.speed = 0


def main(modus):
    """Main Function for Executing the tasks


    Args:
        modus (int): The mode that can be choosen by the user
    """

    car = SonicCar()

    print('-- Fahrparcours --------------------')
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
            time.sleep(1)
            car.drive(50,-1)
            time.sleep(1)
            car.stop()

        elif modus == 2:
            print(modi[modus])
            car.drive(50,1)
            time.sleep(1)
            car.steering_angle = 135
            time.sleep(8)
            car.stop()
            car.steering_angle = 45
            time.sleep(1)
            car.drive(50,-1)
            time.sleep(8)
            car.stop()
            car.steering_angle = 90

        elif modus == 3:
            print(modi[modus])
            distance = car.distance
            car.drive(40,1)
            while distance > 7 or distance < 0:
                distance = car.distance
                log.add_driving(db_path, car.speed, car.direction)
                log.add_usm(db_path,distance)
                print(distance)
                time.sleep(.1)
            car.stop()
            log.add_driving(db_path, car.speed, car.direction)
            #Schleife mit USM Distance
            """freigabe = car.distance
            print(freigabe)
            while freigabe > 10 or freigabe < 0:
                print(freigabe)
                car.drive(50,1)
                print("fahre vorwärts")
                time.sleep(1)
            print(freigabe)
            car.stop()
            print("Fahrt gestoppt")"""
            
            

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

