import time
import select
import logging
import socket

import http_util

import ssl

from IPython import embed

"""
https://docs.python.org/3/howto/sockets.html
https://medium.com/@gdieu/build-a-tcp-proxy-in-python-part-1-3-7552cd5afdfe
https://www.geeks3d.com/hacklab/20190110/python-3-simple-http-request-with-the-socket-module/
"""

"""
How will this work?

1. Run (asynchronously) a ServerSocket always listening on localhost:8888
2. Any time a new request comes into the ServerSocket,
    1. Check if Intercept flag is set
    2. Apply any search/replace filters to the request
    3. Create a new ClientSocket (async)
    4. Wait for response
    5. Relay data back to client (browser/cURL)

"""

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

DEFAULT_SSOCK_ADDR = ("localhost", 8080)


class ClientSocket:

    def __init__(self):
        logging.debug("==============================")
        logging.debug("=== CREATING CLIENT SOCKET ===")
        logging.debug("==============================")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr):
        logging.debug("client socket connecting to addr: %s...", addr)
        self.sock.connect(addr)
        logging.debug("connected!")

    def send(self, data):
        logging.debug("client socket sending data: %s" % data)
        result = self.sock.send(data)
        logging.debug("sent %d bytes!" % result)

    def recv(self, decode=True):
        s_time = time.time()  # Should probably use `sock.settimeout(timeout)`
        chunk_size = 128
        timeout = 2
        data = b""

        logging.debug("socket receiving data... (client socket)")
        while True:
            chunk = self.sock.recv(chunk_size)
            if not chunk:
                break
            else:
                data += chunk
            if time.time() - s_time > timeout:
                logging.warning("recv() timed out while waiting for data (client socket)")
                break

        logging.debug("%d bytes of data received! (client socket)" % len(data))
        data = self._decode(data) if decode else data
        logging.debug("data[0:1000]:\n%s" % data[0:1000])
        return data

    def forward_http_request(self, req):
        logging.debug("forwarding http request...")
        self.connect((req.headers['Host'], 80))
        self.send(req.raw)
        logging.error("receive doesn't seem to be working correctly...")
        raise
        return self.recv()

    def _decode(self, data):
        logging.debug("decoding recv results... (client socket)")
        try:
            data = data.decode("ISO-8859-1")
            logging.debug("decoded with ISO-8859-1")
        except UnicodeError:
            logging.warning("decoding error (UnicodeError); return raw bytes instead")
            pass
        return data

    def _test(self, domain):
        # not working with HTTP/1.1
        # THANK YOU, curse you HTTP 1.1 - https://stackoverflow.com/a/56503783/2418744
        # the issue was the `Connection: close` header must be present
        # ^^^ also talks about TLS wrapping the socket
        logging.debug("_test run! (client socket)")
        self.connect((domain, 80))
        msg = "GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(domain)
        logging.debug("msg...:\n%s" % msg)
        self.send(msg.encode())
        return self.recv()



class ServerSocket:

    def __init__(self):
        logging.debug("==============================")
        logging.debug("=== CREATING SOCKET SERVER ===")
        logging.debug("==============================")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(0)
        self.MAX_REQUEST_SIZE = 1000000  # 1 MB

    def bind_and_listen(self, addr):
        logging.debug("socket binding to addr: %s... (server socket)", addr)
        self.sock.bind(addr)
        logging.debug("binded! (bound?)")
        self.sock.listen()
        logging.debug("socket is listening... (server socket)")

    def serve_forever(self):
        logging.debug("serving forever... (server socket)")
        while True:
            readable, writable, exceptional = select.select([self.sock], [], [])
            for s in readable:
                logging.debug("new readable socket: %r" % s)
                client, addr = self.sock.accept()
                logging.debug("accepted connection with client: {}".format(client))
                # it's readable so let's read it
                data = client.recv(self.MAX_REQUEST_SIZE)
                logging.debug("read %d bytes of data" % len(data))
                # todo: make it like...
                # r,w,e = select.select([self.sock, self.client_sockets_list], [self.writeable_sockets_list?])
                # Is this even necessary ^? Why does it work w/ Curl but not w/ the browser?
                # Is it worth looking at asyncio at this point?
                # embed()
                resp = self.handle_readable(client, data)
                logging.debug("got the response; sending back to client")
                client.send(resp.encode())
                logging.debug("closing connection")
                client.close()

            for s in writable:
                logging.debug("new writable socket: %r" % s)
                raise NotImplemented

            for s in exceptional:
                logging.debug("new exceptional socket: %r" % s)
                raise NotImplemented

    def handle_readable(self, client, data):
        logging.debug("handling data...")
        logging.info("data[0:100]: {}".format(data[0:100]))
        http_util.intercept_http_request(data)
        c_sock = ClientSocket()
        c_sock.connect(("example.com",80))
        msg = "GET / HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n".format(("example.com",80)[0])
        c_sock.send(msg.encode())
        resp = c_sock.recv()
        return resp
        # import sys
        # sys.exit("===TODO===")
