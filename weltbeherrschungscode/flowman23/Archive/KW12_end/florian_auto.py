import os
import sys
import time
import loggingc2c as log

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


class BaseCar():
    
    def __init__(self):
        self._steering_angle = 90
        self._speed = 0
        self._direction = 0

        try:
            with open(sys.path[0] + "/config.json", "r") as f:
                data = json.load(f)
                turning_offset = data["turning_offset"]
                forward_A = data["forward_A"]
                forward_B = data["forward_B"]
                print("Turning Offset: ", turning_offset)
                #print("Forward A: ", forward_A)
                #print("Forward B: ", forward_B)
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
            self.bw.forward()
            self._direction = 1
        elif direction == -1: #rückwärts
            self.bw.backward()
            self._direction = -1
        else: # alles andere = stop
            self.stop()
            self._direction = 0

        self._speed = speed
        self.bw.speed = speed

class SonicCar(BaseCar):

    def __init__(self):
        super().__init__()
        self._distance = 0

    @property
    def distance(self):
        self._distance = self.usm.distance()
        return self._distance

"""def write_data(db_multi_w_path, db_single_w_path, distance, speed, direction, steering_angle):
    log.add_usm(db_multi_w_path, distance)
    log.add_driving(db_multi_w_path, speed, direction)                           
    log.add_steering(db_multi_w_path, steering_angle)                           
    log.add_data(db_single_w_path, distance, 0, 0, 0, 0, 0, speed, direction, steering_angle)
    print("data logged")
"""

def print_data(distance, speed, direction, steering_angle):
    print("Abstand zum Hindernis", distance)
    print("Geschwindigkeit:", speed)
    print("Fahrrichtung:", "vorwärts" if direction == 1 else "rückwärts")
    print("Lenkwinkel:", steering_angle)
    print(20*"--")


"""def write_log(car):
    distance = car.distance
    speed = car.speed
    direction = car.direction
    steering_angle = car.steering_angle"""


def main(modus, car: SonicCar):
    #db_multi_w_path = f"{sys.path[0]}/flo_db_multi.sqlite"
    db_single_w_path = f"{sys.path[0]}/flo_db_single.sqlite"
    #log.makedatabase_multitable(db_multi_w_path)
    log.makedatabase_singletable(db_single_w_path)
    flo_pdf = log.init_dataframe()

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
            car.drive(50, 1)
            time.sleep(1)
            car.stop()
            time.sleep(1)
            car.steering_angle = 135
            car.drive(50, 1)
            time.sleep(8)
            car.stop()
            car.steering_angle = 90

        elif modus == 3:
            print(modi[modus])
            car.drive(20,1)
            distance = car.distance
            while distance > 7 or distance < 0:
                distance = car.distance
                speed = car.speed
                direction = car.direction
                steering_angle = car.steering_angle
                print_data(distance, speed, direction, steering_angle)
                #write_data(db_multi_w_path, db_single_w_path, distance, speed, direction, steering_angle)
                log.add_row_df(flo_pdf, distance, [0, 0, 0, 0, 0], speed, direction, steering_angle)
                time.sleep(.3)
            car.stop()
            print("Auto angehalten")
            print(flo_pdf)
            conn = log.create_connection(db_single_w_path)
            flo_pdf.to_sql('drivedata', conn, if_exists='append', index = False)            
            car.usm.stop() # Sensor ausschalten

        elif modus == 4:
            print(modi[modus])
            
            i=0
            while i < 2:
                print(i)
                print("Los geht's")
                car.drive(20,1)
                distance = car.distance
                while distance > 7 or distance < 0:
                    distance = car.distance
                    speed = car.speed
                    direction = car.direction
                    steering_angle = car.steering_angle
                    print_data(distance, speed, direction, steering_angle)
                    log.add_row_df(flo_pdf, distance, [0, 0, 0, 0, 0], speed, direction, steering_angle)
                    time.sleep(.5)
                car.stop()
                print("Auto angehalten")
                time.sleep(1.0)

                car.drive(20, -1)
                print("Retour")
                while distance < 20:
                    distance = car.distance
                    speed = car.speed
                    direction = car.direction
                    steering_angle = car.steering_angle
                    print_data(distance, speed, direction, steering_angle)
                    log.add_row_df(flo_pdf, distance, [0, 0, 0, 0, 0], speed, direction, steering_angle)
                    time.sleep(.5)
                car.stop()
                print("Auto angehalten")
                time.sleep(1.0)

                car.steering_angle = 70
                print("links lenken")
                time.sleep(.5)
                i += 1

            car.steering_angle = 90 # Räder gerade stellen
            car.stop()              # Auto anhalten
            car.usm.stop()          # Sensor ausschalten


            # PandasDataFrame Daten anzeigen und schreiben
            print(flo_pdf)
            conn = log.create_connection(db_single_w_path)
            flo_pdf.to_sql('drivedata', conn, if_exists='append', index = False)            
            



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
    
    car = SonicCar()
    #car.usm.timeout = 0.06
    #print(car.usm.timeout)

    try:
        modus = sys.argv[1]
    except:
        modus = None

    main(modus, car)
    #print(car.usm.timeout)
    car.usm.stop()