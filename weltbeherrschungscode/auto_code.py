import sys
import matplotlib.pyplot as plt
from basisklassen import *
import loggingc2c as log
import cv2
from frame_editing import *
from datetime import datetime

take_image = False

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
                self.frame_width = data["frame_width"] # Bildbreite
                self.frame_height = data["frame_height"] # Bildhöhe
                self.hsv_low = data["hsv_low"]
                self.hsv_high = data["hsv_high"]
                self.point_1 = data["point_1"]
                self.point_2 = data["point_2"]
                self.point_3 = data["point_3"]
                self.point_4 = data["point_4"]
                self.hough_min_threshold = data["hough_min_threshold"]
                self.max_angle_change_1 = data["max_angle_change_1"]
                self.max_angle_change_2 = data["max_angle_change_2"]
                self.zoom_factor = data["zoom_factor"]
                self.pic_folder = data["pic_folder"]
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

    take_image = False

    def __init__(self, skip_frame=2, cam_number=0):
        super().__init__()
        self.skip_frame = skip_frame
        self.VideoCapture = cv2.VideoCapture(cam_number)#, cv2.CAP_V4L)
        if not self.VideoCapture.isOpened():
            print("Cannot open camera")
            self.VideoCapture.release()
            exit()
        self.VideoCapture.set(cv2.CAP_PROP_FRAME_WIDTH,self.frame_width)
        self.VideoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT,self.frame_height)
        self.VideoCapture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._imgsize = (int(self.VideoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                         int(self.VideoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def get_frame(self):
        """Returns current frame recorded by the camera

        Returns:
            numpy array: returns current frame as numpy array
        """
        if self.skip_frame:
            for i in range(int(self.skip_frame)):
                _, frame = self.VideoCapture.read()
        _, frame = self.VideoCapture.read()
        frame = cv2.flip(frame, -1)
        return frame
    
    def show_frame(self):
        """Plots the current frame
        """
        plt.imshow(self.get_frame())
    
    def get_jpeg(self, frame=None):
        """Returns the current frame as .jpeg/raw bytes file

        Args:
            frame (list): frame which should be saved.

        Returns:
            bytes: returns the frame as raw bytes
        """
        if frame is None:
            frame = self.get_frame()
        _,x = cv2.imencode('.jpeg', frame)
        return x.tobytes()

    def get_steering_angle_from_cam(self):
         # Abfrage eines Frames
        frame, ret = self.get_frame(True)
        # Wenn ret == TRUE, so war Abfrage erfolgreich
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            return

        # Bildauswertung ----------
        #Frame in HSV wandeln und auf Blau filtern 
        frame_in_color_range = detect_color_in_frame(car, frame)
        #Kanten im Frame finden 
        frame_canny_edges = cv2.Canny(frame_in_color_range,200, 400)
        #Bild beschneiden auf intersssanten Bildausschnitt
        frame_cuted_regions = cutout_region_of_interest(car, frame_canny_edges)
        #Liniensegmente mit HoughLinesP finden
        line_segments = detect_line_segments(car, frame_cuted_regions)
        #Fahrbahnbegrenzung erzeugen
        lane_lines = generate_lane_lines(frame, line_segments)
        #Lenkwinkel berechnen
        angle = self.compute_steering_angle(frame, lane_lines)

        return angle, frame, lane_lines
    
    def lane_lines_on_frame(self, frame, lane_lines, line_color=(0, 255, 0), line_width=2):
        return add_lane_lines_to_frame(frame, lane_lines, line_color, line_width)
        
    def compute_steering_angle(self, frame, lane_lines):
        """ Find the steering angle based on lane line coordinate
            We assume that camera is calibrated to point to dead center
        """
        if len(lane_lines) == 0:
            #print('No lane lines detected, do nothing')
            return car.steering_angle

        height, width, _ = frame.shape
      
        if len(lane_lines) == 1: # only one line
            max_delta = self.max_angle_change_1
            #print('Only detected one lane line, just follow it. %s' % lane_lines[0])
            x1, y1, x2, y2 = lane_lines[0][0]
            line =  np.polyfit((x1, x2), (y1, y2), 1)
            #y = mx + n
            m = line[0]
            if m < 0: #left line
                x_offset = x2 - int(width / 4)
            else:
                x_offset = x2 - int( width * 3 / 4)
            print(f"Only one lane line detected. {lane_lines[0]}") #, offset {x_offset}, m {m}")

        else: # two lines
            max_delta = self.max_angle_change_2
            _, _, left_x2, _ = lane_lines[0][0]
            _, _, right_x2, _ = lane_lines[1][0]
            #camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
            #mid = int(width / 2 * (1 + camera_mid_offset_percent))
            mid = int(width / 2)
            x_offset = (left_x2 + right_x2) / 2 - mid

        # find the steering angle, which is angle between navigation direction to end of center line
        y_offset = int(height / 2)

        angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
        calc_steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

        #limt steering angle
        angle_delta = calc_steering_angle - self.steering_angle
        if abs(angle_delta) > max_delta:
            set_delta = max_delta * angle_delta / abs(angle_delta)
            steering_angle = int(self.steering_angle + set_delta)
        else:
            set_delta = 0
            steering_angle = calc_steering_angle

        print(f"calculated angle: {calc_steering_angle}, returned angle: {steering_angle}, angle_delta {angle_delta}, set_delta {set_delta}")
        return steering_angle
    
    def testCam(self):
        """TEXT
        """
        # Schleife für Video Capturing
        modulo_counter = 0
        while True:
            # Abfrage eines Frames
            frame, ret = self.get_frame(True)
            # Wenn ret == TRUE, so war Abfrage erfolgreich
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Bildmanipulation ----------
            frame_blur=cv2.blur(frame,(5,5))
             
            #Frame in HSV wandeln und auf Blau filtern 
            frame_in_color_range = detect_color_in_frame(car, frame_blur)

            #Kanten im Frame finden 
            frame_canny_edges = cv2.Canny(frame_in_color_range,200, 400)
            
            #Bild beschneiden auf intersssanten Bildausschnitt
            frame_cuted_regions = cutout_region_of_interest(car, frame_canny_edges)
            #cv2.imshow("Display window (press q to quit)", frame_cuted_regions)

            #Liniensegmente mit HoughLinesP finden
            line_segments = detect_line_segments(car, frame_cuted_regions)
            # Display Frame with marks
            frame_with_marks = draw_line_segments(line_segments, frame)
            #cv2.imshow("Display window (press q to quit)", frame_with_marks)"""
            
            #Fahrbahnbegrenzung erzeugen
            lane_lines = generate_lane_lines(frame, line_segments)

            #Lenkwinkel berechnen
            angle = self.compute_steering_angle(frame, lane_lines)
            self.steering_angle = angle

            #Fahrbahnbegrenzung einzeichnen
            frame_lane_lines = add_lane_lines_to_frame(frame, lane_lines)
            
            # Frames zumsammen bauen
            frame_1 = cv2.cvtColor(frame_in_color_range, cv2.COLOR_GRAY2RGB)
            frame_2 = cv2.cvtColor(frame_cuted_regions, cv2.COLOR_GRAY2RGB)
            frame_left = np.hstack((frame_1,frame_2))
            frame_right = np.hstack((frame_with_marks, frame_lane_lines))
            frame_total = np.vstack((frame_left, frame_right))

            height, width, _ = frame_total.shape
            frame_total = cv2.resize(frame_total,(int(width*self.zoom_factor), int(height*self.zoom_factor)), interpolation = cv2.INTER_CUBIC)

            # ---------------------------
            # Display des Frames
            cv2.imshow("Display window (press q to quit)", frame_total)
            #Bilder speichern
            time_stamp = datetime.now()
            
            if modulo_counter % 4 == 0: #Modulo --> jedes vierte Bild
                cv2.imwrite(f"{self.pic_folder}{time_stamp}_{angle:03d}.png", frame)
            modulo_counter += 1
            

            # Ende bei Drücken der Taste q
            if cv2.waitKey(1) == ord('q'):
                break
        # Kamera-Objekt muss "released" werden, um "später" ein neues Kamera-Objekt erstellen zu können!!!
        cv2.destroyAllWindows()
    
    def test_cuted_frame(self):
        # Schleife für Video Capturing
        while True:
            # Abfrage eines Frames
            frame, ret = self.get_frame(True)
            # Wenn ret == TRUE, so war Abfrage erfolgreich
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Bildmanipulation ----------
            
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_cut = cutout_region_of_interest(self,frame_gray)
            cv2.imshow("Display window (press q to quit)", frame_cut)

            # ---------------------------
            # Display des Frames
            #cv2.imshow("Display window (press q to quit)", lane_lines_image)
            # Ende bei Drücken der Taste q
            if cv2.waitKey(1) == ord('q'):
                break
        # Kamera-Objekt muss "released" werden, um "später" ein neues Kamera-Objekt erstellen zu können!!!
        cv2.destroyAllWindows()

    def release_cam(self):
        """Releases the camera so it can be used by other programs.
        """
        self.VideoCapture.release()

if __name__ == '__main__':
    # car anlegen
    car = CamCar()
    #car.drive(30 ,1)
    car.testCam()
    car.stop()
    #car.test_cuted_frame()
    car.release_cam()
