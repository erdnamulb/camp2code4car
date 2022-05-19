from basisklassen import * 
import datetime
import pandas as pd 
import time 
import json

class BaseCar():
    """Class for a basic car.

    Args:
    config: config file for the car
    
    Attributes
    --------
    turning_offset : offset for computing the angle
    forward_A : rotating direction of wheel A
    forward_B : rotating direction of wheel B
    speed : speed of the car
    direction : driving direction of the car
    steering_angle : steering angle of the car
    logDict : dict for logging

    Methods
    --------
    drive(): method for driving the car straight forwards or backwards
    stop(): method for stoping the car
    _log(): method for logging data collected while driving
    get_log(): method for getting the logged data
    save_log(): method for saving the logged data
    get_status(): method for getting current speed, direction and angle
    shake_front_wheels(): method for testing the basic steering
    test_drive_1(): method for a test drive
    test_drive_2(): method for a test drive
    """
    def __init__(self, config="config.json"):

        #Einlesen config-File
        with open(config, "r") as f:
            data = json.load(f)
            turning_offset = data["turning_offset"]
            forward_A = data["forward_A"]
            forward_B = data["forward_B"]

        # Auto-Einstellungen
        self._turning_offset = turning_offset
        self._forward_A = forward_A
        self._forward_B = forward_B
        self._back_wheels = Back_Wheels(forward_A=self.forward_A, forward_B=self.forward_B)            # präsentiert Klasse Back_Wheels
        self._front_wheels = Front_Wheels(turning_offset=self.turning_offset)  # präsentiert Klasse Front_Wheels

        #Fahrt-Einstellungen
        self._speed = 0
        self._direction = 0
        self._steering_angle = 90

        #Log-Variablen und andere
        self._logDict = {"time": [], "speed": [], "direction": [], "angle": []}

    @property
    def turning_offset(self):
        return self._turning_offset
    
    @turning_offset.setter
    def turning_offset(self, value):
        try:
            self._turning_offset = int(value)
            self._front_wheels._turning_offset = value
        except ValueError:
            print("Turning-Offset muss eine Zahl sein!")

    @property
    def forward_A(self):
        return self._forward_A
    
    @forward_A.setter
    def forward_A(self, value):
        try:
            self._forward_A = int(value)
            self._back_wheels.forward_A = value
        except ValueError:
            print("Forward A muss eine Zahl sein!")

    @property
    def forward_B(self):
        return self._forward_B
    
    @forward_B.setter
    def forward_B(self, value):
        try:
            self._forward_B = int(value)
            self._back_wheels.forward_B = value
        except ValueError:
            print("Forward B muss eine Zahl sein!")

    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self, value):
        try:
            self._speed = int(value)
            self._back_wheels.speed = int(value)
        except ValueError:
            print("Speed muss eine Zahl sein!")

    @property
    def direction(self):
        return self._direction
    
    @direction.setter
    def direction(self, value):
        try:
            if int(value) not in [-1, 0, 1]:
                raise ValueError("Direction muss -1, 0 oder 1 sein!")
            self._direction = int(value)
        except ValueError:
            print("Direction muss eine Zahl sein!")

    @property
    def steering_angle(self):
        return self._steering_angle
    
    @steering_angle.setter
    def steering_angle(self, angle, alpha=0.0):
        try:
            self._steering_angle = float(angle)
            if angle == None:
                self._front_wheels.turn(self._steering_angle)
            else:
                # Front_Wheels.turn() erlaubt keine zu großen Lenkwinkel und verwendet in diesem Fall maximale Winkel
                # daher wird hier der gesetzte Winkel neu abgefragt
                self._steering_angle = self._front_wheels.turn(self._steering_angle*alpha+angle*(1-alpha))
        except ValueError:
            print("Steering Angle muss eine Zahl sein!")

    def drive(self, speed: int, direction: int=1):
        """Method for start driving

        Args:
            speed (int): speed at which to drive
            direction (int, optional): Driving direciton. 1 for forwards, -1 for backwards. Defaults to 1.
        """
        self.speed = speed 
        self.direction = direction
        self.is_driving = True
        if direction == 1:
            self.is_driving = True
            self._back_wheels.forward()
        elif direction == -1:
            self.is_driving = True
            self._back_wheels.backward()
        elif direction == 0:
            self.stop()
            print("Richtung wurde auf 0 gesetzt. Das Auto hält an!")
        else:
            self.stop()
            print("Unbekannte Richtung! Alle Parameter werden auf Null gesetzt!") 

    def stop(self):
        """Method for stopping the car. 
        """
        self.speed = 0
        self.direction = 0 
        self._back_wheels.stop()
        self.is_driving = False 
    
    def _log(self, additional_dict: dict=None, **kwargs):
        """Method for logging of data collected while driving. By default
        time, speed, direction and angle are being logged. You either can pass 
        a dict for further values or keyword arguments

        Args:
            additional_dict (dict, optional): Dict with further values for logging. Defaults to None.
        """

        self._logDict["time"].append(datetime.datetime.now())
        self._logDict["speed"].append(self.speed)
        self._logDict["direction"].append(self.direction)
        self._logDict["angle"].append(self.steering_angle)

        if isinstance(additional_dict, dict):
            for key, value in additional_dict.items():
                if key in self._logDict:
                    self._logDict[key].append(value)
                else:
                    self._logDict[key] = [value]
            
        for key, value in kwargs.items():
            if key in self._logDict:
                self._logDict[key].append(value)
            else:
                self._logDict[key] = [value]

    def get_log(self):
        """Returns the logged data as a pandas dataframe

        Returns:
            pandas dataframe: dataframe of logged data collected while driving
        """
        df = pd.DataFrame(self._logDict)
        return df

    def _save_log(self):
        """Method for saving the logged data as .csv file
        """
        self.get_log().to_csv(f"log_of_trip.csv")
        print(f"log_of_trip.csv wurde erfolgreich gespeichert!")

    def test_drive_1(self, forward_secs: int=3, sleep_secs: int=1, backward_secs: int=3, speed: int=40):
        """Method for testdrive 1: driving forwards, stopping and driving backwards again.

        Args:
            forward_secs (int, optional): Time in seconds for driving forwards. Defaults to 3.
            sleep_secs (int, optional): Time in seconds for stopping and waiting. Defaults to 1.
            backward_secs (int, optional): Time in seconds for driving backwards. Defaults to 3.
            speed (int, optional): Speed at which to drive. Defaults to 40.
        """
        print('Start')
        self.steering_angle = 90       
        self.drive(speed=speed, direction=1)      
        time.sleep(forward_secs)                    
        self.stop()                 
        time.sleep(sleep_secs)                    
        self.drive(speed=speed, direction=-1)     
        time.sleep(backward_secs)                    
        self.stop()                 
        print('Ende')

    def test_drive_2(self, forward_secs: int=1, circle_secs: int=8, 
                     sleep_secs: int=1, angles: list=[45, 135], speed: int=40):
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
        for a in angles:
            self.steering_angle = 90     
            self.drive(speed=speed)  
            time.sleep(forward_secs)                  
            self.steering_angle = a       
            time.sleep(circle_secs)                  
            self.stop()                
            time.sleep(sleep_secs)                   
            self.drive(speed=speed, direction=-1)  
            time.sleep(circle_secs)                  
            self.steering_angle = 90      
            time.sleep(forward_secs)                  
            self.stop()                
        print('Ende')


    # Weitere Methoden. Diese sind nicht Teil des Projektes.
    def get_status(self):
        """Method which returns a dict of current speed, direction and angle.

        Returns:
            dict: Dictionary with current speed, direction and angle
        """
        return {
            'speed': self.speed,
            'direction': self.direction,
            'angle': self.steering_angle,
        }

    def shake_front_wheels(self, tw=.2):
        """Method for testing if basic steering is working.

        Args:
            tw (float, optional): Time waiting between changes in steering angle. Defaults to .2.
        """
        self.steering_angle = 90
        time.sleep(tw)
        self.steering_angle = 45
        time.sleep(tw)
        self.steering_angle = 135
        time.sleep(tw)
        self.steering_angle = 90
