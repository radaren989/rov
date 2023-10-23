# Bu kod doğru kod
# 10.02.2021
from tcp_client import Client
import imutils
from imutils.video import VideoStream
import argparse
import time
import cv2
import struct
import pickle
import time
import Adafruit_PCA9685
import RPi.GPIO as GPIO
import sys


timeStamp=time.time()
fpsFilt=1
font=cv2.FONT_HERSHEY_SIMPLEX

GPIO.setmode(GPIO.BCM) #anahtarlama
S_GPIO=12
GPIO.setup(S_GPIO, GPIO.OUT)
a = 1
#HOST = '169.254.24.15'
#HOST = '169.254.41.134'
#HOST = '169.254.226.61' 
#HOST = '192.168.137.141'
#HOST = '169.254.117.8'
#HOST = '169.254.192.8'
#HOST = '192.168.137.1'
#HOST = '169.254.92.173'
#HOST = '169.254.235.16'
HOST = '169.254.35.177'

PORT = 5900

if len(sys.argv)>=2:
    PORT = int(sys.argv[2])
    HOST = sys.argv[1]

try:
    c = Client(HOST,PORT)
    print(c.rec_msg().decode())
    c.send_msg(b'send from client')
except:
    raise Exception('TCP Connection Error!')

print('connected to', HOST, PORT)



ap = argparse.ArgumentParser()
print('3')
ap.add_argument("-p", "--picamera", type=int, default=-1)
print('2')
args = vars(ap.parse_args())
print('1')
#Usb = VideoStream(usePiCamera=args["picamera"] > 0).start()
PiCamera=cv2.VideoCapture(0)
#try:
    # src = 1 veya src = 2
#except:
    # PiCamera=cv2.VideoCapture(1) # src = 1 veya src = 2

print("x")

time.sleep(0.2)
pwm =Adafruit_PCA9685.PCA9685()
yanal=0
dikey=0
donme=0
Guc=0
j=0
i=0
gripper_kapali=0
gripper_eksen_sayac=150
kamera_servo_sayac=0
pwm.set_pwm_freq(60)
Camera_Switch=1

kademe=25
kademe_2=25
while True:
    #if Camera_Switch==1:
    ret, frame = PiCamera.read()
    #if Camera_Switch==0:
    #   frame = Usb.read()
    if ret==True:    
        dt=time.time()-timeStamp
        timeStamp=time.time()
        fps=1/dt
        fpsFilt=.9*fpsFilt + .1*fps
        #cv2.putText(frame,str(round(fpsFilt,1))+' fps',(0,30),font,1,(0,0,255),2)
        frame = cv2.flip(frame, 1)
        frame = cv2.flip(frame, 0)
        #####frame = imutils.resize(frame, width=600)
        result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        data = pickle.dumps(frame, 0)
        size = len(data)
        
        
        
        #print(size)
        
        # Receive the response from the client
        received_data = b""
        remaining_data = size
        while remaining_data > 0:
            chunk = c.rec_msg(min(remaining_data, 1024))
            if not chunk:
                # Client closed the connection prematurely
                raise ConnectionError("Connection closed by the client.")
            received_data += chunk
            remaining_data -= len(chunk)

        # Unpack the received data
        axis = struct.unpack("12f",received_data)
        frame = pickle.loads(received_data)
        # c.sendall(struct.pack(">L", size) + data)
        # axis = struct.unpack("12f", c.recv(48))
        leftxaxis = round(axis[0],3)+0.039
        leftyaxis = round(axis[1],3)+0.039
        rightyaxis = round(axis[2],3)+0.039
        rightxaxis = round(axis[3],3)+0.039
        hatx = axis[4]
        haty = axis[5]
        yuvarlak=axis[6]
        ucgen = axis[7]
        L1=axis[8]
        R1=axis[9]
        L2=axis[10]
        R2=axis[11]
        kademe_yuzde=kademe/100
        kademe_2_yuzde=kademe_2/100
        print(haty,hatx,yuvarlak,leftxaxis,leftyaxis,rightxaxis,rightyaxis)
        #c.sendall(b'heyyyoo')
        yanal=100*leftyaxis*kademe_yuzde
        dikey=100*rightyaxis*kademe_yuzde
        donme=75*leftxaxis*kademe_yuzde
        kayma=100*hatx*kademe_yuzde
        yuk_kaldırma=100*rightxaxis
        #---------------------------------Kamera değiştirme-----------------
        if L1==1:
            Camera_Switch=1
        if L2==1:
            Camera_Switch=0
        #-----------------------------------------------Bitti-------------
        #-----------------------------------------------Güç aç kapa---------------------------------
        if ucgen==1 and Guc==1:
            
            GPIO.output(S_GPIO,GPIO.LOW)
            Guc=0
        elif ucgen==1 and Guc==0:
            GPIO.output(S_GPIO,GPIO.HIGH)
            Guc=1
            for i in range(8,16):
                pwm.set_pwm(i,0,500)
            time.sleep(1)
            for i in range(8,16):
                pwm.set_pwm(i,0,0)
            time.sleep(4)
        #----------------------------------------------Bitti------------------------------------
            
        if Guc==1:
            #---------------------------------------KADEME---------------------------------------
            if R1==1 and kademe!=75:
                kademe=kademe + 25
            if R2==1 and 25!=kademe:
                kademe=kademe - 25
            #-----------------------------------------Kademe Bitti--------------------------------
                    
            #--------------------------------------------motor yön-------------------------------
            pwm.set_pwm(15,0,int(380-dikey*0.80+yuk_kaldırma))
            pwm.set_pwm(14,0,int(380-dikey*0.80+yuk_kaldırma))
            pwm.set_pwm(13,0,int(380-dikey))
            pwm.set_pwm(12,0,int(380-dikey))
            pwm.set_pwm(11,0,int(380-yanal+donme-kayma))
            pwm.set_pwm(10,0,int(380-yanal+kayma))
            pwm.set_pwm(9,0,int(380-yanal+kayma))
            pwm.set_pwm(8,0,int(380-yanal-donme-kayma))
            #-------------------------------------------Motor Kodu Biter---------------------------------------------------
            

        #----------------------------------------gripper yönlendirme ve aç kapa----------------------------------------
            if yuvarlak==1:    
                if gripper_kapali==0:
                    pwm.set_pwm(2,0,300)
                    gripper_kapali=1
                elif gripper_kapali==1:
                    pwm.set_pwm(2,0,150)
                    gripper_kapali=0

    #####
    #         if rightxaxis==1 and gripper_eksen_sayac<450:
    #             gripper_eksen_sayac=gripper_eksen_sayac+5
    #         if rightxaxis==-1 and 150<gripper_eksen_sayac:
    #             gripper_eksen_sayac=gripper_eksen_sayac-5
    #         pwm.set_pwm(9,0,gripper_eksen_sayac)
            #-----------------------------------------------Gripper kodu biter--------------------------------------------------
            #--------------------------------------------------Kamera Servo-----------------------------------------------------
            if haty==1 and kamera_servo_sayac<250:
                kamera_servo_sayac=kamera_servo_sayac+5
            if haty==-1 and 0<kamera_servo_sayac:
                kamera_servo_sayac=kamera_servo_sayac-5
            print(kamera_servo_sayac)
            pwm.set_pwm(0,0,210+kamera_servo_sayac)
            #----------------------------------------------------Kamera servo bitti---------------------------------------------
cv2.destroyAllWindows()
vs.stop()               
c.close()
