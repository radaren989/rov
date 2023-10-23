from tcp_client import Client

c = Client('192.168.1.36',1234)
print(c.rec_msg().decode())
c.send_msg(b'send from client')
