import logging


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)

sample_http_request = """GET / HTTP/1.1
Host: example.com
Connection: Close
"""

def intercept_http_request(data):
    data = sample_http_request

    from IPython import embed
    embed()

    return data