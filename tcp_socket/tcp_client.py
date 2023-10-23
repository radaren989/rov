import socket

class Client:
	def __init__(self, Host, Port):
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.HOST = Host
			self.PORT = Port

			self.s.connect((self.HOST, self.PORT))
			
			print(self.s.recv(1024).decode())
			self.s.send(b'Test Message Recieved')
		except:
			raise Exception("TCP Connection Error!")

	def rec_msg(self,size):
		return self.s.recv(size)

	def send_msg(self, msg):
		self.s.send(msg)

	def close(self):
		self.s.close()
