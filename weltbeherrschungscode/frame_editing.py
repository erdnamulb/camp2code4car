import numpy as np
import cv2
#from auto_code import CamCar

def detect_color_in_frame(car: CamCar, frame):
    frame_in_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_blue = np.array(car.hsv_low)  #([60,40,40]) #([60,100,75])
    upper_blue = np.array(car.hsv_high)   #([120,255,255])
    frame_in_color_range = cv2.inRange(frame_in_hsv, lower_blue,upper_blue)
    return frame_in_color_range

def cutout_region_of_interest(car: CamCar, frame):
        height, width = frame.shape
        mask = np.zeros_like(frame)

        # define frame for cutout
        w1, h1 = car.point_1
        w2, h2 = car.point_2
        w3, h3 = car.point_3
        w4, h4 = car.point_4

        polygon = np.array([[
            (w1*width/100, h1*height/100),
            (w2*width/100, h2*height/100),
            (w3*width/100, h3*height/100),
            (w4*width/100, h4*height/100),
        ]], np.int32)

        """polygon = np.array([[
            (0, 4/5 * height),
            (1/4 * width, 1/3 * height),
            (3/4 * width, 1/3 * height),
            (width, 4/5 * height),
        ]], np.int32)
        """

        cv2.fillPoly(mask, polygon, 255)
        cuted_frame = cv2.bitwise_and(frame, mask)
        return cuted_frame

def detect_line_segments(car: CamCar, frame):
        rho = 1  # distance precision in pixel, i.e. 1 pixel
        angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
        min_threshold = car.hough_min_threshold  # minimal of votes (tested between 10-100)
        line_segments = cv2.HoughLinesP(frame, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4)
        return line_segments

def draw_line_segments(line_segments, frame):
    if line_segments is None: # go on, if there is no line
        return frame
    frame2 = frame.copy()
    for line in line_segments:
        x1,y1,x2,y2 = line[0]
        cv2.line(frame2,(x1,y1),(x2,y2),(0,0,255),4)
    return frame2

def generate_lane_lines(frame, line_segments):
    #out of all line segments

    """
    This function combines line segments into one or two lane lines
    If all line slopes are < 0: then we only have detected left lane
    If all line slopes are > 0: then we only have detected right lane
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
        lane_lines.append(calculate_lane_lines(frame, left_fit_average))

    right_fit_average = np.average(right_fit, axis=0)
    if len(right_fit) > 0:
        lane_lines.append(calculate_lane_lines(frame, right_fit_average))

    #print('lane lines: %s' % lane_lines)  

    return lane_lines

def calculate_lane_lines(frame, line):
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

def add_lane_lines_to_frame(frame, lane_lines, line_color=(0, 255, 0), line_width=2):
    line_image = np.zeros_like(frame)
    if lane_lines is not None:
        for line in lane_lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
    line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
    return line_image