import sys
from basisklassen import *
import loggingc2c as log
import cv2

class BaseCar():
    """Base Class to define the car movement
    """
    def __init__(self):
        self._steering_angle = 90
        self._speed = 0
        self._direction = 0
        self._bool_turn = True # bool für das setzen der Lenkendanschläge bei Aufgabe 4 (True = links -> 45°, False =  rechts -> 135°)
        
        # Load config.json part 1
        try:
            with open(sys.path[0] + "/config.json", "r") as f:
                data = json.load(f)
                turning_offset = data["turning_offset"]
                forward_A = data["forward_A"]
                forward_B = data["forward_B"]
                #print(f"Turning Offset: {turning_offset}; Forward A: {forward_A}; Forward B: {forward_B}")
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

        # Setup DataFrame and DataBase
        self.df = log.init_dataframe()
        self._db_path = f"{sys.path[0]}/logdata.sqlite"
        log.makedatabase(self._db_path)

        # Load config.json part 2: IR-references
        try:
            with open(sys.path[0] + "/config.json", "r") as f:
                data = json.load(f)
                ir_references = data["ir_references"]
                self.speed_fw = data["speed_fw"]
                self.speed_bw = data["speed_bw"]
                self.angle_fw = data["angle_fw"]
                self.angle_bw = data["angle_bw"]
                self.offtrack_fw = data["offtrack_fw"]
                self.offtrack_bw = data["offtrack_bw"]
                self.ir_intervall = data["ir_intervall"]
                print("Json-File: ", data)
        except:
            ir_references = [100, 100, 100, 100, 100]
            self.speed_fw = 30
            self.speed_bw = 30
            self.angle_fw = 30
            self.angle_bw = 45
            self.offtrack_fw = 8
            self.offtrack_bw = 30
            self.ir_intervall = 0.005
            print("config.json nicht gefunden")
        
        self.irm = Infrared(ir_references)
            
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
    def read_ir_analog(self) -> list:
        """Reads the value of the infrared module as analog.
        Returns:
            [list]: List of bytes of the measurement of each sensor read in as analog values. 
        """
        return self.irm.read_analog()
    
    @property
    def read_ir_digital(self) -> list:
        """Reads the value of the infrared module as digital.
        Returns:
            [list]: List of digitized measurement of the sensors using the reference as threshold. 
        """
        return self.irm.read_digital()
    
    def calibrate_ir(self):
        self.irm.cali_references()

        with open(sys.path[0] + "/config.json") as fin:
            data = json.load(fin)
            
        with open(sys.path[0] + "/config.json", "w") as fout:
            data['ir_references'] = list(self.irm._references)
            fout.write(json.dumps(data,indent = 6))
        print(data)

    def log(self):
        """Function to create log entries in the dataframe
        """
        log.add_row_df(self.df, self.distance, self.read_ir_digital , self.speed, self.direction, self.steering_angle)

    @property
    def log_and_read_values(self):
        """Function to read IR values, ultra sonic values and write log to dataframe
        """
        distance = self.distance
        ir_sensors = self.read_ir_digital
        log.add_row_df(self.df, distance, ir_sensors , self.speed, self.direction, self.steering_angle)
        return distance, ir_sensors
    
    def write_log_to_db(self):
        """Function to save log Information
        """
        log.write_log_to_db(self._db_path, self.df)

class CamCar(SensorCar):

    def __init__(self, skip_frame=2, cam_number=0):
        super().__init__()
        self.skip_frame = skip_frame
        self.VideoCapture = cv2.VideoCapture(cam_number)#, cv2.CAP_V4L)
        if not self.VideoCapture.isOpened():
            print("Cannot open camera")
            self.VideoCapture.release()
            exit()
        self.VideoCapture.set(cv2.CAP_PROP_FRAME_WIDTH,800)
        self.VideoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT,600)
        self.VideoCapture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._imgsize = (int(self.VideoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                         int(self.VideoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def get_frame(self, return_ret_value=False):
        """Returns current frame recorded by the camera

        Returns:
            numpy array: returns current frame as numpy array
        """
        if self.skip_frame:
            for i in range(int(self.skip_frame)):
                ret, frame = self.VideoCapture.read()
        ret, frame = self.VideoCapture.read()
        frame = cv2.flip(frame, -1)
        return frame, ret if return_ret_value else frame

    def testCam(self):
        """TEXT
        """
        # Schleife für Video Capturing
        while True:
            # Abfrage eines Frames
            frame, ret = self.get_frame(True)
            # Wenn ret == TRUE, so war Abfrage erfolgreich
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Bildmanipulation ----------
<<<<<<< HEAD:weltbeherrschungscode/auto_code.py
            #frame_to_display = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            #lower_blue = np.array([60,40,40])
            #upper_blue = np.array([150,255,255])
            #frame_to_display = cv2.inRange(frame_to_display, lower_blue,upper_blue)
=======
            #frame = cv2.flip(frame, -1)
            #frame_to_display = cv2.cvtColor(frame, cv.COLOR_BGR2RGB)# BGR2GRAY)
>>>>>>> 6973181d620db205ee946b5b5f9b9694c4223485:weltbeherrschungscode/JM112/Projektphase 2/auto_code.py
            frame_to_display = frame
            # ---------------------------
            # Display des Frames
            cv2.imshow("Display window (press q to quit)", frame_to_display)
            # Ende bei Drücken der Taste q
            if cv2.waitKey(1) == ord('q'):
                break
        # Kamera-Objekt muss "released" werden, um "später" ein neues Kamera-Objekt erstellen zu können!!!
        self.VideoCapture.release()
        cv2.destroyAllWindows()
    
    def release(self):
        """Releases the camera so it can be used by other programs.
        """
        self.VideoCapture.release()

C = CamCar()
C.testCam()
print("Ende")
