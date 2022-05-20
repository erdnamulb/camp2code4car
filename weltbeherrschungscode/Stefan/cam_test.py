import sys 
from auto_code import CamCar



if __name__ == '__main__':
    # car anlegen
    car = CamCar()
    car.testCam()
    car.release()
    

    """# Erstellen eines Objektes für den Kamerazugriff
    cap = cv.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640);
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480);
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    # Schleife für Video Capturing
    while True:
        # Abfrage eines Frames
        ret, frame = cap.read()
        height, width, _ = frame.shape
        #print(f"h = {height}, w = {width}")
        #frame = cv.resize(frame,(int(width*1/3), int(height*1/3)), interpolation = cv.INTER_CUBIC)
        #frame = cv.resize(frame,(640, 480))
        # Wenn ret == TRUE, so war Abfrage erfolgreich
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        # Bildmanipulation ----------
        frame = cv.flip(frame, -1)
        #frame_to_display = cv.cvtColor(frame, cv.COLOR_BGR2RGB)# BGR2GRAY)
        frame_to_display = frame
        # ---------------------------
        # Display des Frames
        cv.imshow("Display window (press q to quit)", frame_to_display)
        # Ende bei Drücken der Taste q
        if cv.waitKey(1) == ord('q'):
            break
    # Kamera-Objekt muss "released" werden, um "später" ein neues Kamera-Objekt erstellen zu können!!!
    cap.release()
    cv.destroyAllWindows()"""