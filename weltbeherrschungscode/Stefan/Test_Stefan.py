from datetime import datetime
import sys, os

import numpy as np
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), 'camp2code-project_phase_1', 'Code'))
from basisklassen import *
import loggingc2c as log

import traceback


class BaseCar():

    def __init__(self):
        self._steering_angle = 90
        self._speed = 0
        self._direction = 0
        self._bool_turn = True
        
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
        self._direction = 0
        self.bw.stop()

    def drive(self, speed: int, direction: int):
        self._direction = direction
        if direction == 1: #vorwärts
            self._direction = 1
            self.bw.forward()
        elif direction == -1: #rückwärts
            self._direction = -1
            self.bw.backward()
        else: # alles andere = stop
            self._direction = 0
            self.stop()

        self._speed = speed
        self.bw.speed = speed
    
    def wait_angle(self,  waitTime: float, angle: int):
        now = 0
        while now < waitTime:
            self.steering_angle = angle
            time.sleep(.25)
            
            if angle > 90:
                offset = -5
            else:
                offset = 5
            self.steering_angle = angle + offset
            time.sleep(.25)

            now += .5
            print(f"time= {now:.1f} set_angle = {angle}")
    
    def turn_direction(self):
        if self._bool_turn:
            angle = 45
        else:
            angle = 135
        self._bool_turn = not self._bool_turn
        return angle

    def avoid_crash(self):
        self.stop()
        time.sleep(.5)
        self.drive(self._speed,-1)
        time.sleep(1)
        self.steering_angle = self.turn_direction()
        time.sleep(2)
        self.stop()
        time.sleep(.5)
        self.steering_angle = 90
        self.drive(self._speed, 1)



class SonicCar(BaseCar):

    def __init__(self):
        super().__init__()

    @property
    def distance(self):
        return self.usm.distance()

class SensorCar(SonicCar):

    def __init__(self):
        super().__init__()
        self.df = log.init_dataframe()

    def drive(self, speed: int, direction: int):
        super().drive(speed, direction)
        self.log()
    
    @property
    def steering_angle(self):
        #return BaseCar.steering_angle.fget(self)
        return super().steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        super(SensorCar, self.__class__).steering_angle.fset(self,angle)
        self.log()

    def stop(self):
        super().stop()
        self.log()

    def get_average(self):
        """Returns the mean value of the measurements.
        Args:
            mount (int): Number of measurements taken. Defaults to 10.
        Returns:
            [float]: List of measurement as mean of 'mount' individual measurements.
        """
        return self.irm.get_average(50)

    def cali_references(self) -> None:
        """Recording the reference
        """
        self.irm.cali_references()
    
    @property
    def read_analog(self) -> list:
        """Reads the value of the infrared module as analog.
        Returns:
            [list]: List of bytes of the measurement of each sensor read in as analog values. 
        """
        return self.irm.read_analog()

    def log(self):
        log.add_row_df(self.df, self.distance, self.read_analog , self._speed, self._direction, self._steering_angle)



def main(modus, car: SensorCar):
    """Main Function for Executing the tasks


    Args:
        modus (int): The mode that can be choosen by the user
    """
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
        print('Auswahl:')
        for m in modi.keys():
            print('{i} - {name}'.format(i=m, name=modi[m]))
        print('--' * 20)

    while True:

        while modus == None:
            modus = input("Wähle  (Abbruch mit '0'): ? ")
            if modus in ['1', '2', '3', '4', '5', '6', '7', '8', '0']:
                break
            else:
                modus = None
                print('Getroffene Auswahl nicht möglich.')
                #quit()
        modus = int(modus)

        if modus == 1:
            print(modi[modus])
            car.steering_angle = 90
            print("vorwärts")
            car.drive(30,1)
            time.sleep(3)
            print("stopp")
            car.stop()
            time.sleep(1)
            print("rückwärts")
            car.drive(30,-1)
            time.sleep(3)
            print("stopp")
            car.stop()

        elif modus == 2:
            print(modi[modus])
            car.steering_angle = 90
            time.sleep(.3)
            print("vorwärts")
            car.drive(40,1)
            time.sleep(1)
            car.stop()
            time.sleep(.5)
            print("Uhrzeigersinn")
            car.steering_angle = 135
            time.sleep(.3)
            car.drive(40,1)
            car.wait_angle(10, 135)
            car.stop()
            car.steering_angle = 90
            time.sleep(1)
            print("Zurück")
            car.steering_angle = 135
            time.sleep(.3)
            car.drive(40,-1)
            car.wait_angle(10, 135)
            car.stop()
            time.sleep(.5)
            print("Rückwärts")
            car.steering_angle = 90
            car.drive(30,-1)
            time.sleep(1)
            car.stop()
            

        elif modus == 3:
            print(modi[modus])
            distance = car.distance
            car.drive(40,1)
            while distance > 7 or distance < 0:
                distance = car.distance
                car.log()
                print(distance)
                time.sleep(.3)
            car.stop()

        elif modus == 4:
            print(modi[modus])
            loop_count = 0
            while loop_count < 2:
                car.steering_angle = 90
                car.drive(40,1)
                distance = car.distance
                while distance > 12 or distance < 0:
                    distance = car.distance
                    print(f"{distance} , {car.steering_angle}")
                    car.log()
                    time.sleep(.3)
                car.avoid_crash()
                loop_count += 1
            car.stop()
        
        elif modus == 5:
            print(modi[modus])
            high_value = 140
            line_value = 100
            car.steering_angle = 90
            #print(car.get_average(50))
            #car.cali_references()
            while True:
                ir_data = car.read_analog()
                print(f"{ir_data}")
                # Prüfen, ob Linie noch da ist
                line_found = False
                for ir in ir_data:
                    if ir < line_value:
                        line_found = True
                        time_start = 0
                if not line_found:
                    if time_start == 0:
                        time_start = datetime.timestamp(datetime.now())
                    time_now = datetime.timestamp(datetime.now())
                    print(time_now - time_start)
                    if time_now - time_start < 2:
                        ir_data = car.read_analog()
                        for ir in ir_data:
                            if ir < line_value: #line found
                                time_start = 0
                        time.sleep(.1)
                        continue
                    car.steering_angle = 90
                    car.stop()
                    break
                # Lenken
                analog = np.array(ir_data)
                min_ir = np.min(analog)
                min_pos = np.where(analog == min_ir)[0][0]
                print(f"min = {min_ir} Position: {min_pos}")
                if min_pos == 0:
                    car.steering_angle = 45
                    car.drive(30,1)
                elif min_pos == 1:
                    car.steering_angle = 65
                    car.drive(35,1)
                elif min_pos == 2:
                    car.steering_angle = 90
                    car.drive(40,1)
                elif min_pos == 3:
                    car.steering_angle = 115
                    car.drive(35,1)
                elif min_pos == 4:
                    car.steering_angle = 135
                    car.drive(30,1)
                time.sleep(.1)
        
        elif modus == 6:
            print(modi[modus])
        
        elif modus == 7:
            print(modi[modus])

        elif modus == 8:
            #print(modi[modus])
            run_loop = True
            while run_loop:
                for a in range(45, 136, 5):
                    time.sleep(.1)
                    car.steering_angle = a
                    print(f"angle : {car.steering_angle}")
                for a in range(135, 44, -5):
                    time.sleep(.1)
                    car.steering_angle = a
                    print(f"angle : {car.steering_angle}")
                run_loop = True
        
        elif modus == 0:
            print("Ende")
            quit()
        
        modus = None
        break

if __name__ == '__main__':
    
    car = SensorCar()

    # Datenbank anlegen und Dataframe initialisieren
    db_path = f"{sys.path[0]}/logdata.sqlite"
    log.makedatabase_singletable(db_path)
    try:
        modus = sys.argv[1]
    except:
        modus = None

    main(modus, car)
    car.stop()
    car.usm.stop()
    conn = log.create_connection(db_path)
    car.df.to_sql('drivedata', conn, if_exists='append', index = False)  
    print(car.df)

