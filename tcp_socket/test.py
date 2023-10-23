from tcp_server import Server

t = Server('hostip',1234)
t.wait_connection()
t.send_msg(b'send from server')
print(t.rec_msg().decode())