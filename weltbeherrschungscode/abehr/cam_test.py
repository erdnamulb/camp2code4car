import numpy as np
import cv2 as cv

def draw_line_segments(line_segments,img):
    img2 = img.copy()
    #img2 = cv.cvtColor(img2, cv.COLOR_GRAY2RGB)
    if line_segments is not None: # Könnte None sein, wenn Hough keine Linie erkennt!
        for line in line_segments:
            x1,y1,x2,y2 = line[0]
            cv.line(img2,(x1,y1),(x2,y2),(255,0,0),1)
    return img2

# Erstellen eines Objektes für den Kamerazugriff
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Schleife für Video Capturing
while True:
    # Abfrage eines Frames
    ret, frame = cap.read()
    height, width, _ = frame.shape
    frame = cv.resize(frame,(int(width*2/3), int(height*2/3)), interpolation = cv.INTER_CUBIC)
    # Wenn ret == TRUE, so war Abfrage erfolgreich
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Bildmanipulation ----------
    frame_to_display = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # ---------------------------
    # Display des Frames
    cv.imshow("Display window (press q to quit)", frame_to_display)
    # Ende bei Drücken der Taste q
    if cv.waitKey(1) == ord('q'):
        break
# Kamera-Objekt muss "released" werden, um "später" ein neues Kamera-Objekt erstellen zu können!!!
cap.release()
cv.destroyAllWindows()