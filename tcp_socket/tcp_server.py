import socket

class Server:
    def __init__(self, HOST, PORT):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.HOST = HOST
            self.PORT = PORT
            
            self.s.bind((self.HOST, self.PORT))
            self.s.listen(1024)
        except: 
            raise Exception("TCP Server Set Up Error!")

        self.client_socket = None
        self.client_addr = None

    def wait_connection(self):
        self.client_socket, self.client_addr = self.s.accept()
        print(f'connection from {self.client_addr} has been established!')
        self.client_socket.send(b'Test Message Received')
        print(self.client_socket.recv(1024).decode())
    
    def send_msg(self, msg):
        self.client_socket.send(msg)
    
    def rec_msg(self,size):
        return self.client_socket.recv(size)
    
    def close(self):
        self.s.close()
