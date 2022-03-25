import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), 'camp2code-project_phase_1', 'Code'))
from basisklassen import *
import loggingc2c as log


class BaseCar():
    """Base Class to define the car movement
    """
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
        self.bw.stop() # stop motion (if vehicle ist driving)

    @property
    def speed(self):
        """Returns the actual speed
        """
        return self._speed

    @property
    def direction(self):
        """Returns the actual direction
        """
        return self._direction

    @property
    def steering_angle(self):
        """Returns the actual steering angle
        """
        return self._steering_angle

    @steering_angle.setter
    def steering_angle(self, angle):
        """Set new steering_angle
        """
        self._steering_angle = angle
        self.fw.turn(angle)

    def stop(self):
        """Stop the car
        """
        self._direction = 0
        self.bw.stop()

    def drive(self, speed: int, direction: int):
        """Function to set speed and motion direction 
        """
        self._direction = direction
        if direction == 1: #move forward
            self._direction = 1
            self.bw.forward()
        elif direction == -1: #move backward
            self._direction = -1
            self.bw.backward()
        else: # all other values = stop
            self._direction = 0
            self.stop()

        self._speed = speed
        self.bw.speed = speed
    
    def wait_angle(self,  waitTime: float, angle: int):
        """Function to drive with minimal steering changes over a given time 
        """
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
        """The function alternately returns the two end stops of the steering
        """
        if self._bool_turn:
            angle = 45
        else:
            angle = 135
        self._bool_turn = not self._bool_turn
        return angle

    def avoid_crash(self):
        """The function is intended to avoid a crash. 
        By driving backwards for 1s and then driving away for another 2s with full steering angle (left or right).
        The vehicle then continues straight ahead.
        """
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
        self.usm = Ultrasonic()

    @property
    def distance(self):
        """Returns the actual distance to ultra sonic sensor
        """
        return self.usm.distance()

class SensorCar(SonicCar):

    def __init__(self):
        super().__init__()
        self.irm = Infrared()
        # Setup DataFrame and DataBase
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
