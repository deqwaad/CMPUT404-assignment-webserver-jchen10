#  coding: utf-8 
import socketserver
import re
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
document_root = "./www"

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        request = self.data.decode('utf-8')
        request_lines = request.splitlines()
        ret = re.match(r"([^/]*)([^ ]+)",request_lines[0])
        if ret:
            path = ret.group(2)
            if path.endswith("/"):
                path += "index.html"
        if not request.startswith("GET"):
            # Handle unsupported methods with a 405 error
            response_header = "HTTP/1.1 405 Method Not Allowed\r\n"
            response_header += "\r\n"
            response_body = "405 Method Not Allowed!"
            self.request.send(response_header.encode('utf-8'))
            self.request.send(response_body.encode('utf-8'))
            return
        elif not path.endswith((".html", ".css", "/")):
            path += "/"
            response_header = f"HTTP/1.1 301 Moved Permanently\r\n"
            response_header += f"Location: {path}\r\n"
            self.request.send(response_header.encode('utf-8'))
            return
        else:
            try:
                with open(document_root + path, "rb") as f_n:
                    content = f_n.read()
                    # Determine MIME type
                    mime_type, _ = mimetypes.guess_type(path)
                    if mime_type is not None:
                        response_header = f"HTTP/1.1 200 OK\r\n"
                        response_header += f"Content-Type: {mime_type}\r\n"
                        response_header += "\r\n"
                        self.request.send(response_header.encode('utf-8'))
                        self.request.send(content)
                        f_n.close()
            except BaseException:
                # Handle 404 Not Found
                response_header = "HTTP/1.1 404 Not Found\r\n"
                response_header += "\r\n"
                response_body = "404 Not Found!"
                self.request.send(response_header.encode('utf-8'))
                self.request.send(response_body.encode('utf-8'))

        self.request.close()

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()