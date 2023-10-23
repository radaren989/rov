from tcp_server import Server
import cv2 as cv
import numpy as np

s = Server("192.168.1.26",5900)
s.wait_connection()

while True:
    frame = s.rec_msg()
    np.frombuffer(frame, dtype=np.uint8)
    frame.reshape(480,640,3)
    cv.imshow("frame",frame)
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()