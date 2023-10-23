from clientCV import camera
from tcp_client import Client

def main():
    c = Client("192.168.1.26",5900)
    cam = camera()
    while True:
        frame = cam.readCam()
        c.send_msg(frame)


if __name__ == "__main__":
    main()