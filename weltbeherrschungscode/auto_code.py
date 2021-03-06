import sys
from basisklassen import *
import loggingc2c as log
import cv2
import numpy as np
from datetime import datetime
import time
from tensorflow import keras

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
    
    def get_frame_dash(self):
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
    
    def detect_color_in_frame(self, frame):
        """Converts frame to HSV and filter out all colores which are not in range
        Args:
            frame: camera picture
        Returns:
            frame_in_color_range: filtered frame
        """
        frame_in_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_blue = np.array(self.hsv_low)  
        upper_blue = np.array(self.hsv_high)   
        frame_in_color_range = cv2.inRange(frame_in_hsv, lower_blue,upper_blue)
        return frame_in_color_range
    
    def cutout_region_of_interest(self, frame):
        """Cut out defined area from frame
        Args:
            frame: camera picture
        Returns:
            cuted_frame: cuted frame
        """
        height, width = frame.shape
        mask = np.zeros_like(frame)
        # define frame for cutout
        w1, h1 = self.point_1
        w2, h2 = self.point_2
        w3, h3 = self.point_3
        w4, h4 = self.point_4
        polygon = np.array([[
            (w1*width/100, h1*height/100),
            (w2*width/100, h2*height/100),
            (w3*width/100, h3*height/100),
            (w4*width/100, h4*height/100),
        ]], np.int32)
        cv2.fillPoly(mask, polygon, 255)
        cuted_frame = cv2.bitwise_and(frame, mask)
        return cuted_frame

    def detect_line_segments(self, frame):
        """detect line segments with Hough transformation
        Args:
            frame: camera picture
        Returns:
            line_segments: lsit of line segments
        """
        rho = 1  # distance precision in pixel, i.e. 1 pixel
        angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
        min_threshold = self.hough_min_threshold  # minimal of votes (tested between 10-100)
        line_segments = cv2.HoughLinesP(frame, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4)
        return line_segments
    
    def draw_line_segments(self, line_segments, frame):
        """draw line segments from Hough transformation in frame
        Args:
            frame: camera picture
            line_segments: lsit of line segments
        Returns:
            frame2: frame with line segments
        """
        if line_segments is None: # go on, if there is no line
            return frame
        frame2 = frame.copy()
        for line in line_segments:
            x1,y1,x2,y2 = line[0]
            cv2.line(frame2,(x1,y1),(x2,y2),(0,0,255),4)
        return frame2

    def calculate_lane_lines(self, frame, line):
        """
        sub function to calculate lane lines
        Args:
            frame: camera picture
            line: information for one line
        Returns:
            coordinates for one line
        """
        height, width, _ = frame.shape
        # y = mx + n
        m, n = line
        y1 = height  # bottom of the frame
        y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

        # bound the coordinates within the frame
        # x = ( y - n ) / m
        x1 = max(-width, min(2*width, int((y1 - n) / m)))
        x2 = max(-width, min(2*width, int((y2 - n) / m)))
        return [[x1, y1, x2, y2]]

    def generate_lane_lines(self, frame, line_segments):
        """
        This function combines line segments into one or two lane lines
        Args:
            frame: camera picture
            line_segments: lsit of line segments
        Returns:
            lane_lines: one or two lane lines
        """
        lane_lines = []
        if line_segments is None:
            print('No line_segment segments detected')
            return lane_lines

        _ , width, _ = frame.shape
        left_fit = []
        right_fit = []

        boundary = 1/3
        left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
        right_region_boundary = width * boundary # right lane line segment should be on right 2/3 of the screen

        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:
                if x1 == x2:
                    #print('skipping vertical line segment (slope=inf): %s' % line_segment)
                    continue
                fit =  np.polyfit((x1, x2), (y1, y2), 1)
                #y = mx + n
                m = fit[0]
                n = fit[1]
                if m < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((m, n))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((m, n))

        left_fit_average = np.average(left_fit, axis=0)
        if len(left_fit) > 0:
            lane_lines.append(self.calculate_lane_lines(frame, left_fit_average))

        right_fit_average = np.average(right_fit, axis=0)
        if len(right_fit) > 0:
            lane_lines.append(self.calculate_lane_lines(frame, right_fit_average))

        #print('lane lines: %s' % lane_lines)  
        return lane_lines


    def add_lane_lines_to_frame(self, frame, lane_lines, line_color=(0, 255, 0), line_width=2):
        """
        This function adds lane lines to a frame
        Args:
            frame: camera picture
            lane_lines: one or two lane lines
        Returns:
            line_image: frame with lines
        """
        line_image = np.zeros_like(frame)
        if lane_lines is not None:
            for line in lane_lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
        line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
        return line_image
    
    def compute_steering_angle(self, frame, lane_lines):
        """ 
        Find the steering angle based on lane line coordinate
        Args:
            frame: camera picture
            lane_lines: one or two lane lines
        Returns:
            steering_angle: steering angle which should be set to steering (with limited angle change)
            calc_steering_angle: steering angle which is calculated by frame
        """
        if len(lane_lines) == 0:
            print('No lane lines detected, do nothing')
            return car.steering_angle, car.steering_angle

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
            #print(f"Only one lane line detected. {lane_lines[0]}") #, offset {x_offset}, m {m}")

        else: # two lines
            max_delta = self.max_angle_change_2
            _, _, left_x2, _ = lane_lines[0][0]
            _, _, right_x2, _ = lane_lines[1][0]
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

        #print(f"calculated angle: {calc_steering_angle}, returned angle: {steering_angle}, angle_delta {angle_delta}, set_delta {set_delta}")
        return steering_angle, calc_steering_angle
    
    def testCam(self):
        """ 
        Testfuction for camera pictures
        Args:
            -
        Returns:
            -
        """
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
            frame_in_color_range = self.detect_color_in_frame(frame_blur)
            #Kanten im Frame finden 
            frame_canny_edges = cv2.Canny(frame_in_color_range,200, 400)
            #Bild beschneiden auf intersssanten Bildausschnitt
            frame_cuted_regions = self.cutout_region_of_interest(frame_canny_edges)
            #Liniensegmente mit HoughLinesP finden
            line_segments = self.detect_line_segments(frame_cuted_regions)
            # Display Frame with marks
            frame_with_marks = self.draw_line_segments(line_segments, frame)
            #Fahrbahnbegrenzung erzeugen
            lane_lines = self.generate_lane_lines(frame, line_segments)
            
            #Lenkwinkel berechnen
            angle, calc_angle = self.compute_steering_angle(frame, lane_lines)
            print(f"calc angle: {calc_angle:3d}, ret angle: {angle:3d}, delta {(abs(calc_angle - angle)):3d}")
            self.steering_angle = angle

            #Fahrbahnbegrenzung einzeichnen
            frame_lane_lines = self.add_lane_lines_to_frame(frame, lane_lines)
            
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
            
            # Ende bei Drücken der Taste q
            if cv2.waitKey(1) == ord('q'):
                break
        # Kamera-Objekt muss "released" werden, um "später" ein neues Kamera-Objekt erstellen zu können!!!
        cv2.destroyAllWindows()
    
    def test_cuted_frame(self):
        """ 
        Testfuction for frame cutting
        Args:
            -
        Returns:
            -
        """
        while True:
            # Abfrage eines Frames
            frame, ret = self.get_frame(True)
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Bildmanipulation ----------
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_cut = self.cutout_region_of_interest(frame_gray)
            # Display des Frames
            cv2.imshow("Display window (press q to quit)", frame_cut)
            # Ende bei Drücken der Taste q
            if cv2.waitKey(1) == ord('q'):
                break
        # Kamera-Objekt muss "released" werden, um "später" ein neues Kamera-Objekt erstellen zu können!!!
        cv2.destroyAllWindows()

    def take_pictures_fast(self, num_pics):
        """ 
        Function to take a number of pictures for CNN calculation
        Args:
            num_pics: number of pictures to save
        Returns:
            -
        """
        angle_max = 0
        angle_min = 180
        time_intervall = time.time() 
        count = 0
        while count < num_pics:
            # Abfrage eines Frames
            frame, ret = self.get_frame(True)
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Bildmanipulation ----------
            frame_edit=cv2.blur(frame,(5,5))
            #Frame in HSV wandeln und auf Blau filtern 
            frame_edit = self.detect_color_in_frame(frame_edit)
            #Kanten im Frame finden 
            frame_edit = cv2.Canny(frame_edit,200, 400)
            #Bild beschneiden auf intersssanten Bildausschnitt
            frame_edit = self.cutout_region_of_interest(frame_edit)
            #Liniensegmente mit HoughLinesP finden
            line_segments = self.detect_line_segments(frame_edit)
            #Fahrbahnbegrenzung erzeugen
            lane_lines = self.generate_lane_lines(frame, line_segments)
        
            #Lenkwinkel berechnen
            angle, calc_angle = self.compute_steering_angle(frame, lane_lines)
            #Lenkwinkel setzen
            self.steering_angle = angle        

            #Bilder speichern
            time_stamp = datetime.now()      
            cv2.imwrite(f"{self.pic_folder}{time_stamp}_{angle:03d}.png", frame)
            
            #Loging
            angle_max = max(angle_max, angle)
            angle_min = min(angle_min, angle)
            count += 1
            print(f"{count:5d} calc angle: {calc_angle:3d}, ret angle: {angle:3d}, delta {(abs(calc_angle - angle)):3d}, min: {angle_min:3d}, max: {angle_max:3d}, calc time {(time.time() - time_intervall)*1000:5.2f}")
            time_intervall = time.time() 
            
    def frame_process_cnn(self, frame):
        """
        This function prepares the frame for cnn evaluation
        Args:
            frame: camera picture
        Returns:
            frame: processed frame
        """
        height, _, _ = frame.shape
        frame = frame[int(height*0.3):int(height*0.8),:,:]  # remove top and botom of the image, as it is not relavant for lane following
        frame = cv2.resize(frame, (200,75)) # input image size (200,75) in model
        #frame = frame / 255 # normalizing
        return frame

    def test_cnn(self):
        """
        Testfunction for CNN
        Args:
            -
        Returns:
            -
        """
        cnn_path = fr"weltbeherrschungscode/Stefan/angle5s_110.h5" 
        model = keras.models.load_model(cnn_path)
   
        time_intervall = time.time()
        while True:
            # Abfrage eines Frames
            frame, ret = self.get_frame(True)
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Bildmanipulation ----------
            frame_processed = self.frame_process_cnn(frame)
            frame_np = np.asarray([frame_processed])
            #Lenkwinkel berechnen
            angle_predict = int(model.predict(frame_np)[0])
            print(f"predicted angle = {angle_predict:3d}°, duration = {(time.time()-time_intervall)*1000:.0f}ms")
            time_intervall = time.time()
            
            #angle = self.compute_steering_angle(frame, lane_lines)
            self.steering_angle = angle_predict
            
            frame_total =  frame
            height, width, _ = frame_total.shape
            frame_total = cv2.resize(frame_total,(int(width*self.zoom_factor), int(height*self.zoom_factor)), interpolation = cv2.INTER_CUBIC)

            # ---------------------------
            # Display des Frames
            cv2.imshow("Display window (press q to quit)", frame_total)

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
    #car.drive(25 ,1)
    car.testCam()
    #time_start = time.time()
    #car.take_pictures_fast(100)
    #print(f"Dauer: {(time.time() - time_start):.3f}")
    #car.test_cnn()
    #car.test_cuted_frame()
    car.stop()
    car.release_cam()
