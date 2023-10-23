from tcp_server import Server

t = Server('192.168.1.36',5900)
t.wait_connection()
t.send_msg(b'send from server')
print(t.rec_msg().decode())