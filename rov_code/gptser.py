from tcp_server import Server
import cv2
import pickle
import numpy as np
import struct
import time
import imutils
import random
import pygame

class VideoStream:
    def __init__(self, host, port):
        self.HOST = host
        self.PORT = port
        self.server = Server(self.HOST, self.PORT)
        self.server.wait_connection()
        self.server.send_msg(b'sent server')
        print(self.server.rec_msg(1024).decode())

        self.payload_size = struct.calcsize(">L")

        pygame.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        self.leftxaxis = 0
        self.leftyaxis = 0
        self.rightxaxis = 0
        self.rightyaxis = 0
        self.hatx = 0
        self.haty = 0
        self.kademe = 25
        self.kademe_2 = 25
        self.cnt_i = 1

        self.prev_frame_time = 0
        self.new_frame_time = 0

        self.codec = cv2.VideoWriter_fourcc(*'XVID')
        self.recording_flag = False
        self.vid_i = 0

    def update_joystick_values(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.JOYAXISMOTION:
                self.leftxaxis = event.value if event.axis == 0 else self.leftxaxis
                self.leftyaxis = event.value if event.axis == 1 else self.leftyaxis
                self.rightxaxis = event.value if event.axis == 2 else self.rightxaxis
                self.rightyaxis = event.value if event.axis == 3 else self.rightyaxis
            elif event.type == pygame.JOYHATMOTION:
                self.hatx, self.haty = event.value if event.value != (0, 0) else (0, 0)

    def update_kademe_values(self):
        if self.joystick.get_button(4) and self.kademe != 100:
            self.kademe += 25
        if self.joystick.get_button(5) and 25 != self.kademe:
            self.kademe -= 25
        if self.joystick.get_button(6) and self.kademe_2 != 100:
            self.kademe_2 += 25
        if self.joystick.get_button(7) and 25 != self.kademe_2:
            self.kademe_2 -= 25

    def send_joystick_data(self):
        analog_bytes = bytearray(
            struct.pack("12f", self.leftxaxis, self.leftyaxis, self.rightxaxis, self.rightyaxis, 
                        self.hatx, self.haty, 0, 0, 0, 0, 0, 0)
        )
        self.server.send_msg(analog_bytes)

    def receive_and_display_frame(self):
        data = b''
        while len(data) < self.payload_size:
            data += self.server.rec_msg(4096)

        packed_msg_size = data[:self.payload_size]
        data = data[self.payload_size:]

        msg_size = struct.unpack(">L", packed_msg_size)[0]

        while len(data) <= msg_size:
            data += self.server.rec_msg(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        frame = imutils.resize(frame, height=600, width=800, inter=cv2.INTER_LINEAR)

        cv2.imshow("KAMERA", frame)
        return frame

    def record_video(self,frame):
        if self.recording_flag:
            self.output.write(frame)

    def run(self):
        while True:
            self.update_joystick_values()
            self.update_kademe_values()

            self.send_joystick_data()
            frame = self.receive_and_display_frame()

            if cv2.waitKey(1) % 256 == 32:
                self.toggle_recording()

            self.record_video(frame)

            cv2.waitKey(1)

    def toggle_recording(self):
        if not self.recording_flag:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.recording_flag = True
        self.output = cv2.VideoWriter(f"capture_{self.vid_i}.avi", self.codec, 30, (800, 600))
        print(f"Recording video {self.vid_i}")
        self.vid_i += 1

    def stop_recording(self):
        self.recording_flag = False
        self.output.release()
        print("Stopped recording!")

    def close_connection(self):
        self.server.close()

# Usage
if __name__ == "__main__":
    video_stream = VideoStream('192.168.1.36', 5900)
    try:
        video_stream.run()
    finally:
        video_stream.close_connection()