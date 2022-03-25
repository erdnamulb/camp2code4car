from sqlite3 import dbapi2
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

class SensorCar(SonicCar):

    def __init__(self):
        super().__init__()
        self.irm = Infrared()
        # Setup DataFrame and DataBaseDatenbank anlegen und Dataframe initialisieren
        self.df = log.init_dataframe()
        self._db_path = f"{sys.path[0]}/logdata.sqlite"
        log.makedatabase_singletable(self._db_path)
        

    def drive(self, speed: int, direction: int):
        """Overloaded function from BaseCar. Added loggin
        """
        super().drive(speed, direction)
        self.log()
    
    @property
    def steering_angle(self):
        """Overloaded property from BaseCar.
        """
        return super().steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        """Overloaded setter from BaseCar. Added loggin 
        """
        super(SensorCar, self.__class__).steering_angle.fset(self,angle)
        self.log()

    def stop(self):
        """Overloaded function from BaseCar. Added loggin
        """
        super().stop()
        self.log()

    
    @property
    def read_ir_sensors(self) -> list:
        """Reads the value of the infrared module as analog.
        Returns:
            [list]: List of bytes of the measurement of each sensor read in as analog values. 
        """
        return self.irm.read_analog()

    def log(self):
        """Function to create log entries in the dataframe
        """
        log.add_row_df(self.df, self.distance, self.read_ir_sensors , self.speed, self.direction, self.steering_angle)

    def write_log_to_db(self):
        """Function to save log Dataframe to sqlite DB
        """
        conn = log.create_connection(self._db_path)
        self.df.to_sql('drivedata', conn, if_exists='append', index = False)


    

def print_data(distance, speed, direction, steering_angle):
    print("Abstand zum Hindernis", distance)
    print("Geschwindigkeit:", speed)
    print("Fahrrichtung:", "vorwärts" if direction == 1 else "rückwärts")
    print("Lenkwinkel:", steering_angle)

def main(modus, car:SonicCar):
    
    #db_multi_w_path = f"{sys.path[0]}/andreas_db_multi.sqlite"
    db_single_w_path = f"{sys.path[0]}/andreas_db_single.sqlite"
    #log.makedatabase_multitable(db_multi_w_path)
    log.makedatabase_singletable(db_single_w_path)
    andreas_pdf = log.init_dataframe()

    #car = SonicCar()
    #log.makedatabase_multitable(db_path)
    #log.makedatabase_singletable(db_single_w_path)

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
                speed = car.speed
                direction = car.direction
                steering_angle = car.steering_angle
                print_data(distance, speed, direction, steering_angle)
                #write_data(db_multi_w_path, db_single_w_path, distance, speed, direction, steering_angle)
                log.add_row_df(andreas_pdf, distance, [0, 0, 0, 0, 0], speed, direction, steering_angle)
                print(20*"--")
                time.sleep(.3)
            car.stop()
            print("Auto angehalten")
            print(andreas_pdf)
            conn = log.create_connection(db_single_w_path)
            andreas_pdf.to_sql('drivedata', conn, if_exists='append', index = False)            
            car.usm.stop() # Sensor ausschalten

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
    
    car = SensorCar()
    try:
        modus = sys.argv[1]
    except:
        modus = None

    main(modus, car)
    #print(car.usm.timeout)
    car.usm.stop()