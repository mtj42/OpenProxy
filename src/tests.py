import sockets


def setup():
    ssock = sockets.ServerSocket()
    ssock.bind_and_listen(sockets.DEFAULT_SSOCK_ADDR)
    ssock.serve_forever()


def teardown():
    ssock.sock.close()


setup() # how do I run stuff after this? serve_forever() never ends
teardown()
