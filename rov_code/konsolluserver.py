from tcp_server import Server
import cv2
import pickle
import numpy as np
import struct
import time
import imutils
import random
import pygame

pygame.init()
j = pygame.joystick.Joystick(0)
j.init()


# check your windows ip and type both server and client
#HOST = '169.254.79.44'
#HOST = '169.254.235.16'
#HOST = '169.254.79.44'
#HOST = '192.168.137.1'
HOST = '192.168.1.36' # tugrul host

PORT = 5900
s = Server(HOST,PORT)
s.wait_connection()
s.send_msg(b'sent server')
print(s.rec_msg(1024).decode())
data = b''

payload_size = struct.calcsize(">L")

leftxaxis = 0
leftyaxis = 0
rightxaxis = 0
rightyaxis = 0
hatx = 0
haty = 0
kademe = 25
kademe_2 = 25
cnt_i = 1  # used to save frame

# deneme kaydi okunur
prev_frame_time = 0
new_frame_time = 0

# video recording
codec = cv2.VideoWriter_fourcc(*'XVID')
# output = cv2.VideoWriter('capture.avi', codec, 30, (800, 600))
recording_flag = False  # recording variable
vid_i = 0  # count number of captured videos

print("satır 54 ")
while True:
    yuvarlak = 0
    ucgen = 0
    L1 = 0
    R1 = 0
    L2 = 0
    R2 = 0
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                leftxaxis = event.value
            if event.axis == 1:
                leftyaxis = event.value
            if event.axis == 2:
                rightxaxis = event.value
            if event.axis == 3:
                rightyaxis = event.value
        if event.type == pygame.JOYHATMOTION:
            if event.value == (0, 1):
                haty = 1
            elif event.value == (0, -1):
                haty = -1
            elif event.value == (1, 0):
                hatx = 1
            elif event.value == (-1, 0):
                hatx = -1
            if event.value == (0, 0):
                hatx = 0
                haty = 0
        if event.type == pygame.JOYBUTTONDOWN:
            if j.get_button(1):
                yuvarlak = 1
            if j.get_button(2):
                ucgen = 1
            if j.get_button(4):
                L1 = 1
            if j.get_button(5):
                R1 = 1
            if j.get_button(6):
                L2 = 1
            if j.get_button(7):
                R2 = 1
            

    if R1 == 1 and kademe != 100:
        kademe = kademe + 25
    if R2 == 1 and 25 != kademe:
        kademe = kademe - 25
    if L1 == 1 and kademe_2 != 100:
        kademe_2 = kademe_2 + 25
    if L2 == 1 and 25 != kademe_2:
        kademe_2 = kademe_2 - 25
    print("kademe: ", kademe)
    # print("Yük Kaldırma: ", kademe_2)
    analogBytes = bytearray(
        struct.pack("12f", leftxaxis, leftyaxis, rightxaxis, rightyaxis, hatx, haty, yuvarlak, ucgen, L1, R1, L2, R2))
    
    s.send_msg(analogBytes)

    # print(s.rec_msg(1024))
    while len(data) < payload_size:
        data += s.rec_msg(4096)

    packed_msg_size = data[:payload_size]
    data = data[payload_size:]

    msg_size = struct.unpack(">L", packed_msg_size)[0]
    print("msg:", msg_size)

    while len(data) <= msg_size:
        data += s.rec_msg(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    print("video")
    # print(data)
    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
    frame = imutils.resize(frame, height=600, width=800, inter=cv2.INTER_LINEAR)
    # h, w, ret = frame.shape
    # print(frame.shape)
    # print(h, w, ret)
    # frame = cv2.flip(frame,0) # do not flip here, results a delay
    cv2.imshow("KAMERA", frame)

    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    fps = int(fps)

    if cv2.waitKey(1) & 0xFF == ord('p'):
        cv2.imwrite("image%d.jpg" % cnt_i, frame)
        print("image saved")
        cnt_i = cnt_i + 1
    print(fps)
    # record video if "space" is pressed
    if cv2.waitKey(1) % 256 == 32:
        if recording_flag == False:
            # we are transitioning from not recording to recording

            # you can record here by seperated files
            recorded_file_name = "capture_" + str(vid_i) + ".avi"
            output = cv2.VideoWriter(recorded_file_name, codec, fps, (800, 600))
            print("recording video" + str(vid_i))
            vid_i = vid_i + 1

            # or just continue to write on the captured video
            # output.write(frame)
            # print("only recording on the same video")
            recording_flag = True
        else:
            # transitioning from recording to not recording
            print("stopped!")
            recording_flag = False

    # keep recording...
    if recording_flag:
        output.write(frame)

    print("Recording Flag", recording_flag)
    cv2.waitKey(1)

s.close()