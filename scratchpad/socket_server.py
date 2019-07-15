import time
import logging
import socket
from IPython import embed

# https://docs.python.org/3/howto/sockets.html
# https://medium.com/@gdieu/build-a-tcp-proxy-in-python-part-1-3-7552cd5afdfe
# https://www.geeks3d.com/hacklab/20190110/python-3-simple-http-request-with-the-socket-module/


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

S_HOST = "localhost"  # Socket server host
S_PORT = 8080  # Socket server port


class ClientSocket:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr):
        logging.debug("socket connecting to addr: %s...", addr)
        self.sock.connect(addr)
        logging.debug("connected!")

    def send(self, data):
        logging.debug("socket sending data: %s" % data)
        result = self.sock.send(data)
        logging.debug("sent %d bytes!" % result)

    def recv(self, decode=True):
        s_time = time.time()
        chunk_size = 128
        timeout = 5
        data = b""

        logging.debug("socket receiving data...")
        while True:
            chunk = self.sock.recv(chunk_size)
            if not chunk:
                break
            else:
                data += chunk
            if time.time() - s_time > timeout:
                logging.warning("recv timed out while waiting for data")
                break

        logging.debug("%d bytes of data received!" % len(data))
        data = self._decode(data) if decode else data
        logging.debug("data[0:1000]:\n%s" % data[0:1000])
        return data

    def _decode(self, data):
        logging.debug("decoding recv results...")
        try:
            data = data.decode("ISO-8859-1")
            logging.debug("decoded with ISO-8859-1")
        except UnicodeError:
            logging.warning("decoding error (UnicodeError); return raw bytes instead")
            pass
        return data

    def _test(self, domain):
        logging.debug("_test run!")
        s.connect((domain, 80))
        s.send(b"GET / HTTP/1.0\r\n\r\n")
        s.recv()


s = ClientSocket()
s._test("google.com")


# Client socket:
#
# # create an INET, STREAMing socket
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # now connect to the web server on port 80 - the normal http port
# s.connect(("www.python.org", 80))
#
#
# Server socket:
#
# # create an INET, STREAMing socket
# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 
# # bind the socket to a public host, and a well-known port
# serversocket.bind((S_HOST, S_PORT))
# 
# # become a server socket
# serversocket.listen()
# 
