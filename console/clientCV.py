import numpy as np
import cv2 as cv

class camera:
    def __init__(self):
        print("Camera is turning on!")
        self.cap = cv.VideoCapture(0)
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()
    
    def readCam(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...") 
        
        return frame.tobytes()

    def capture(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...") 
        
        cv.imshow('frame', frame)
        
        if cv.waitKey(1) == ord('q'):
            self.finalize()

    def finalize(self):
        print("Camera is turning off!")
        self.cap.release()
        cv.destroyAllWindows()