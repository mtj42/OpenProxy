import time
import select
import logging
import socket

from IPython import embed

"""
https://docs.python.org/3/howto/sockets.html
https://medium.com/@gdieu/build-a-tcp-proxy-in-python-part-1-3-7552cd5afdfe
https://www.geeks3d.com/hacklab/20190110/python-3-simple-http-request-with-the-socket-module/
"""

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

S_HOST = "localhost"  # Socket server host
S_PORT = 8080  # Socket server port


class HttpRequest:
    def __init__(self, data):
        self.raw = data
        headers, self.body = data.decode("latin-1").split("\r\n\r\n", 1)
        request_line, headers = headers.split("\r\n", 1)
        self.method, query, self.protocol = request_line.split(" ", 3)
        headers_dict = {}
        for line in headers.split("\r\n"):
            name, value = line.split(":", 1)
            headers_dict[name] = value.strip()
        self.headers = headers_dict
        if query.startswith("http://") or query.startswith("https://"):
            # for some reason the whole http://example.com/?a=b is in there
            logging.warning("request_line has protocol and FQDN in it; this will likely break the request")


class ClientSocket:

    def __init__(self):
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
        timeout = 5
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
        logging.debug("_test run! (client socket)")
        self.connect((domain, 80))
        self.send(b"GET / HTTP/1.0\r\n\r\n")
        return self.recv()



class ServerSocket:

    def __init__(self):
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
                embed()
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
        req = HttpRequest(data)
        client = ClientSocket()
        # resp = client.forward_http_request(req)  # HTTP response
        resp = client._test("google.com")
        return resp

    def _test(self, domain):
        logging.debug("_test run! (server socket)")
        self.bind_and_listen((domain, 8080))
        self.serve_forever()
        logging.debug("killing server...")


# test by running $ curl -X POST -d "Hello=World" -x localhost:8080 example.com
# then calling client.recv(1000) on line 103
s_sock = ServerSocket()
s_sock._test("localhost")

# c_sock = ClientSocket()
# c_sock._test("google.com")
