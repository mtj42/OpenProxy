import sockets
import time
import logging

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


default_test_domain = ("example.com",80)
default_test_proxy_addr = ("localhost",8080)


def test_client_socket():
    c_sock = sockets.ClientSocket()
    c_sock.connect(default_test_domain)
    msg = "GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(default_test_domain[0])
    c_sock.send(msg.encode())
    c_sock.recv()

def test_server_socket():
    s_sock = sockets.ServerSocket()
    s_sock.bind_and_listen(default_test_proxy_addr)
    s_sock.serve_forever()


