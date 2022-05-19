import cv2 
import matplotlib.pyplot as plt

class Camera():
    """A class for the camera

    Args:
    skip_frame: number of frames to skip while recording
    cam_number: which camera should be used. Defaults to 0. 

    Attributes
    --------
    
    VideoCapture: Class to get the video feed
    _imgsize: size of the image

    Methods
    --------
    get_frame(): returns current frame, recorded by the camera
    show_frame(): plots the current frame, recorded by the camera
    get_jpeg(): returns the current frame as .jpeg/raw bytes file
    save_frame(): saves the frame at the given path under the given name
    release(): releases the camera, so it can be used again and by other programs
    """

    def __init__(self, skip_frame=2, cam_number=0):
        self.skip_frame = skip_frame
        self.VideoCapture = cv2.VideoCapture(cam_number, cv2.CAP_V4L) #,
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

    def save_frame(self, path: str, name: str, frame=None):
        """Saves the current frame under the given path and filename

        Args:
            path (str): path where the file should be saved
            name (str): name under which the file should be saved
            frame (np.array, optional): frame which should be saved. 
                                        If None then the current frame recorded by the camera gets saved.
                                        Defaults to None.
        """
        if frame is None:
            frame = self.get_frame()
        cv2.imwrite(path + name, frame)

    def release(self):
        """Releases the camera so it can be used by other programs.
        """
        self.VideoCapture.release()    


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
# Schleife für Video Capturing
while True:
    # Abfrage eines Frames
    ret, frame = cap.read()
    height, width, _ = frame.shape
    frame = cv2.resize(frame,(int(width*1/3), int(height*1/3)), interpolation = cv2.INTER_CUBIC)
    # Wenn ret == TRUE, so war Abfrage erfolgreich
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Bildmanipulation
    frame_to_display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # ---------------------------
    # Display des Frames
    cv2.imshow("Display window (press q to quit)", frame_to_display)
    # Ende bei Drücken der Taste q
    if cv2.waitKey(1) == ord('q'):
        break
# Kamera-Objekt muss "released" werden, um "später" ein neues Kamera-Objekt erstellen zu können!!!
cap.release()
cv2.destroyAllWindows()
