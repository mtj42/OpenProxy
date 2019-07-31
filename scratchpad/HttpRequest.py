# old
# 
# class HttpRequest:
#     def __init__(self, data):
#         self.raw = data
#         headers, self.body = data.decode("latin-1").split("\r\n\r\n", 1)
#         request_line, headers = headers.split("\r\n", 1)
#         self.method, self.query, self.protocol = request_line.split(" ", 3)
#         headers_dict = {}
#         for line in headers.split("\r\n"):
#             name, value = line.split(":", 1)
#             headers_dict[name] = value.strip()
#         self.headers = headers_dict
# 