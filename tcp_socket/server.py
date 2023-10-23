import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('192.168.1.14',1234))
s.listen(5)

while True:
    client_socket, addr = s.accept()
    print(f'connection from {addr} has been established!')
    client_socket.send(b'message received by server')