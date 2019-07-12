import re
import socket
import requests
import threading
import socketserver

from IPython import embed

def parse_http_request(r):
    method = re.search(r'^([A-Z]+?) .*?\r\n', r)
    host = re.search(r'Host: (.*)\r\n', r)
    if not method:
        raise MethodNotFoundException
    if not host:
        raise HostNotFoundException
    embed()
    
class HostNotFoundException(Exception):
    pass

class MethodNotFoundException(Exception):
    pass

# https://docs.python.org/3/library/socketserver.html#asynchronous-mixins
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        parse_http_request(data)    
        # cur_thread = threading.current_thread()
        # response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        response = bytes("{}".format(data), 'ascii')
        self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))


if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 8080

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        # client(ip, port, "Hello World 1")
        # client(ip, port, "Hello World 2")
        # client(ip, port, "Hello World 3")

        server.serve_forever()
        # server.shutdown()
