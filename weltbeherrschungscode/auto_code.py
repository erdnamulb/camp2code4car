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
    
    def region_of_interest(self, edges):
        height, width = edges.shape
        mask = np.zeros_like(edges)

        # only focus bottom half of the screen
        polygon = np.array([[
            (0, 4/5 * height),
            (1/4 * width, 1/3 * height),
            (3/4 * width, 1/3 * height),
            (width, 4/5 * height),
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        cropped_edges = cv2.bitwise_and(edges, mask)
        return cropped_edges

    def detect_line_segments(self, cropped_edges):
        # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
        rho = 1  # distance precision in pixel, i.e. 1 pixel
        angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
        min_threshold = 10  # minimal of votes
        line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4)
        return line_segments

    def draw_line_segments(self, line_segments, img):
        img2 = img.copy()
        for line in line_segments:
            x1,y1,x2,y2 = line[0]
            cv2.line(img2,(x1,y1),(x2,y2),(0,0,255),4)
        return img2
    
    def average_slope_intercept(self, frame, line_segments):
        """
        This function combines line segments into one or two lane lines
        If all line slopes are < 0: then we only have detected left lane
        If all line slopes are > 0: then we only have detected right lane
        """
        lane_lines = []
        if line_segments is None:
            print('No line_segment segments detected')
            return lane_lines

        height, width, _ = frame.shape
        left_fit = []
        right_fit = []

        boundary = 1/3
        left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 1/3 of the screen
        right_region_boundary = width * boundary # right lane line segment should be on right 1/3 of the screen

        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:
                if x1 == x2:
                    print('skipping vertical line segment (slope=inf): %s' % line_segment)
                    continue
                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]
                if slope < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((slope, intercept))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((slope, intercept))

        left_fit_average = np.average(left_fit, axis=0)
        if len(left_fit) > 0:
            lane_lines.append(self.make_points(frame, left_fit_average))

        right_fit_average = np.average(right_fit, axis=0)
        if len(right_fit) > 0:
            lane_lines.append(self.make_points(frame, right_fit_average))

        #print('lane lines: %s' % lane_lines)  # [[[316, 720, 484, 432]], [[1009, 720, 718, 432]]]

        return lane_lines
    
    def make_points(self, frame, line):
        height, width, _ = frame.shape
        slope, intercept = line
        y1 = height  # bottom of the frame
        y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

        # bound the coordinates within the frame
        x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
        x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
        return [[x1, y1, x2, y2]]
    
    def display_lines(self, frame, lines, line_color=(0, 255, 0), line_width=2):
        line_image = np.zeros_like(frame)
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
        line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
        return line_image

    def compute_steering_angle(self, frame, lane_lines):
        """ Find the steering angle based on lane line coordinate
            We assume that camera is calibrated to point to dead center
        """
        if len(lane_lines) == 0:
            print('No lane lines detected, do nothing')
            return -90

        height, width, _ = frame.shape
        if len(lane_lines) == 1:
            print('Only detected one lane line, just follow it. %s' % lane_lines[0])
            x1, _, x2, _ = lane_lines[0][0]
            x_offset = x2 - x1
        else:
            _, _, left_x2, _ = lane_lines[0][0]
            _, _, right_x2, _ = lane_lines[1][0]
            camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
            mid = int(width / 2 * (1 + camera_mid_offset_percent))
            x_offset = (left_x2 + right_x2) / 2 - mid

        # find the steering angle, which is angle between navigation direction to end of center line
        y_offset = int(height / 2)

        angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

        print('new steering angle: %s' % steering_angle)
        return steering_angle

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
            #frame_blur=cv2.blur(frame,(5,5))
            
            frame_in_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_blue = np.array([60,40,40]) #([60,100,75])
            upper_blue = np.array([120,255,255])
            frame_hsv_in_color_range = cv2.inRange(frame_in_hsv, lower_blue,upper_blue)
            #frame_hsv_in_color_range=cv2.blur(frame_hsv_in_color_range,(5,5))
            frame_canny_edges = cv2.Canny(frame_hsv_in_color_range,200, 400)
            frame_cuted_regions = self.region_of_interest(frame_canny_edges)
            line_segments = self.detect_line_segments(frame_cuted_regions)
            
            # Display Frame with marks
            """frame_with_marks = self.draw_line_segments(line_segments, frame)
            cv2.imshow("Display window (press q to quit)", frame_with_marks)"""
            
            lane_lines = self.average_slope_intercept(frame, line_segments)
            lane_lines_image = self.display_lines(frame, lane_lines)
            angle = self.compute_steering_angle(frame, lane_lines)
            self.steering_angle = angle
            
            # ---------------------------
            # Display des Frames
            cv2.imshow("Display window (press q to quit)", lane_lines_image)
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

if __name__ == '__main__':
    # car anlegen
    car = CamCar()
    car.testCam()
    car.release()
