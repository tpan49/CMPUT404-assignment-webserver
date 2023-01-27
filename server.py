#  coding: utf-8 
import socketserver
import re

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


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        s = (self.data.decode("utf-8").split())   
        
        header = 'HTTP/1.1 '
        status_code = '200 OK'
        
        # Method type
        method = s[0]
        
        # Just the path 
        path = s[1]
        
        # If there are redundant / -> make it only one / -> Moved to only 1 slash 
        if(re.search("/{2,}", path) != None):
            status_code = '301 Moved Permanently'
            single_slash_path = re.sub("/{2,}", "/", path)
            bytearray_content1 = header + status_code + '\r\n' + 'Location: '+ single_slash_path + '\r\n\r\n'
            self.request.sendall(bytearray(bytearray_content1, 'utf-8')) 
            return
        
        print ("Got a request of: %s\n" % self.data)
        
        if(method != 'GET'):
            status_code = '405 Method Not Allowed'
            bytearray_content1 = header + status_code + '\r\n\r\n'
            self.request.sendall(bytearray(bytearray_content1, 'utf-8')) 
        
        path_splitted_byslash = path.split('/')
        
        # Only file deeper than ./www is allowed to be served
        num_allowed_go_back = 0
        for i in range (1,len(path_splitted_byslash)) :
            if(path_splitted_byslash[i]=='..'):
                num_allowed_go_back -=1
            else:
                num_allowed_go_back +=1
                
        # Get file to be served name
        file_served_name = path_splitted_byslash[len(path_splitted_byslash)-1]
        
        # Get file type
        file_served_name_split = file_served_name.split('.')
        
        # Check if the file/folder has an extension
        if(len(file_served_name_split)>1):
            content_type = file_served_name_split[len(file_served_name_split)-1]
        else:
            content_type = 'plain'
        
        # Check if it exist or not. 
        # Is it file or folder?  
        # If file, serve the content of that file. 
        # If folder, look for index.html inside. 
        # If has index, serve that. 
        # If no, return 404
       
        try:
            # When path is not allowed -> FileNotFoundError 
            if(num_allowed_go_back<0):
                raise FileNotFoundError
            
            # Check if file/folder exists #if not -> FileNotFoundError
            status = open('./www'+path, 'rb')
 
            # File exists -> response
            bytearray_content1 = header + status_code + '\r\n' + 'Content-Type: text/' + content_type + '\r\n\r\n'
            self.request.sendall(bytearray(bytearray_content1, 'utf-8')) 
            self.request.sendfile(status)
            status.close()
            
        except IsADirectoryError:
            # Folder exits but without the / -> redirect with added /
            if (path[-1] != '/'):
                status_code = '301 Moved Permanently'
                slash = '/'
                bytearray_content1 = header + status_code + '\r\n' + 'Location: '+ path + slash + '\r\n\r\n'
                self.request.sendall(bytearray(bytearray_content1, 'utf-8')) 
        
            else:                
                # Look for index.html file in this folder 
                # If exists = able to open -> response
                # If not exists -> FileNotFound
                index_html_status = open('./www'+path+'index.html', 'rb')
                content_type = 'html'
                
                bytearray_content1 = header + status_code + '\r\n' + "Content-Type: text/" + content_type + '\r\n\r\n'
                self.request.sendall(bytearray(bytearray_content1, 'utf-8')) 
                self.request.sendfile(index_html_status)
                index_html_status.close()
                
        except FileNotFoundError:
            status_code = '404 Not Found'
            bytearray_content1 = header + status_code + '\r\n' + 'Content-Type: text/' + content_type + '\r\n\r\n'
            self.request.sendall(bytearray(bytearray_content1, 'utf-8')) 
            
        except:
            status_code = '500 Internal Server Error'
            bytearray_content1 = header + status_code + '\r\n\r\n'
            self.request.sendall(bytearray(bytearray_content1, 'utf-8')) 
           

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
