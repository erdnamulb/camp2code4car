from sqlite3 import dbapi2
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), 'camp2code-project_phase_1', 'Code'))
from basisklassen import *
import traceback
import loggingc2c as log
from random import randint 

db_path = f"{sys.path[0]}/andreasdb.sqlite"
#db_multi_w_path = f"{sys.path[0]}/andreas_db_multi.sqlite"
db_single_w_path = f"{sys.path[0]}/andreas_db_single.sqlite"
#log.makedatabase_multitable(db_multi_w_path)
log.makedatabase_singletable(db_single_w_path)
andreas_pdf = log.init_dataframe()

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

    def test_drive_2(self, name, sleep_secs: int=1, angles: list=[45, 135], speed: int=40):
        """Method for testdrive 2: driving forwards, stopping, setting steering angle 
        and driving in a circle. Driving backwards and forwards again

        Args:
            forward_secs (int, optional): Time in seconds for driving forwards. Defaults to 1.
            circle_secs (int, optional): Time in seconds for driving in a circle. Defaults to 8.
            sleep_secs (int, optional): Time in seconds for driving waiting. Defaults to 1.
            angles (list, optional): Angles for which the testdrive should be done. Defaults to [45, 135].
            speed (int, optional): Speed at which to drive. Defaults to 40.
        """
        print('Start')
        i = 0
        while i < 3:
            print ("Durchlauf {}", i)
            distance = self.distance
            self.drive(40,1)
            #auto fährt
            while distance > 7 or distance < 0:                
                distance = self.distance
                speed = self.speed
                direction = self.direction
                steering_angle = self.steering_angle
                print_data(distance, speed, direction, steering_angle)
                log.add_row_df(andreas_pdf, distance, [0, 0, 0, 0, 0], speed, direction, steering_angle)
                print(20*"--")
                time.sleep(.3)
            self.stop()
            print("Auto angehalten")
            #hindernis erkannt
            randbool = bool(randint(0,1)) 
            if randbool == 0:
                self.steering_angle = 45
            else:
                self.steering_angle = 135
            self.drive(40,-1)
            distance = self.distance
            speed = self.speed
            direction = self.direction
            steering_angle = self.steering_angle
            print_data(distance, speed, direction, steering_angle)
            log.add_row_df(andreas_pdf, distance, [0, 0, 0, 0, 0], speed, direction, steering_angle)
            print(20*"--")
            time.sleep(3)
            self.steering_angle = 90
            self.stop()
            distance = self.distance
            speed = self.speed
            direction = self.direction
            steering_angle = self.steering_angle
            print_data(distance, speed, direction, steering_angle)
            log.add_row_df(andreas_pdf, distance, [0, 0, 0, 0, 0], speed, direction, steering_angle)
            print(20*"--")
            
            conn = log.create_connection(db_single_w_path)
            andreas_pdf.to_sql('drivedata', conn, if_exists='append', index = False)            
            car.usm.stop() # Sensor ausschalten               
            self.stop()  
            i += 1              
        print('Ende')


    

def print_data(distance, speed, direction, steering_angle):
    print("Abstand zum Hindernis", distance)
    print("Geschwindigkeit:", speed)
    print("Fahrrichtung:", "vorwärts" if direction == 1 else "rückwärts")
    print("Lenkwinkel:", steering_angle)



def main(modus, car:SonicCar):




    car.test_drive_2(car)





if __name__ == '__main__':
    
    car = SonicCar()
    try:
        modus = sys.argv[1]
    except:
        modus = None

    main(modus, car)
    #print(car.usm.timeout)
    car.usm.stop()