import os
import io
import mimetypes 
import cgi
from datetime import datetime
from email.message import Message 

class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.png'] = 'image/png'
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers=None):
        if headers is None:
            headers = {}
        tanggal = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT') 
        resp = []
        resp.append(f"HTTP/1.0 {kode} {message}\r\n")
        resp.append(f"Date: {tanggal}\r\n")
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append(f"Content-Length: {len(messagebody)}\r\n")
        for kk in headers:
            resp.append("{}:{}\r\n" . format(kk,headers[kk]))
        resp.append("\r\n")
        
        response_headers = ''.join(resp).encode('latin-1') 
        if (type(messagebody) is not bytes):
            messagebody = messagebody.encode() 
        
        response = response_headers + messagebody
        return response

    def proses(self, data):
        requests = data.split("\r\n")
        
        try:
            empty_line_index = requests.index('')
        except ValueError:
            empty_line_index = len(requests)

        header_lines = requests[:empty_line_index]
        body_str = "\r\n".join(requests[empty_line_index + 1:])

        if not header_lines:
            return self.response(400, 'Bad Request', 'Empty Request', {})

        baris = header_lines[0]
        all_headers_raw = [n for n in header_lines[1:] if n]

        parsed_headers = {}
        for header_line in all_headers_raw:
            if ':' in header_line:
                key, value = header_line.split(':', 1)
                parsed_headers[key.strip()] = value.strip()
        
        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if method == 'GET':
                return self.http_get(object_address, parsed_headers)
            elif method == 'POST':
                return self.http_post(object_address, parsed_headers, body_str)
            elif method == 'DELETE':
                return self.http_delete(object_address, parsed_headers)
            else:
                return self.response(400, 'Bad Request', 'Method Not Supported', {})
        except IndexError:
            return self.response(400, 'Bad Request', 'Malformed Request Line', {})

    def http_get(self, object_address, headers):
        if object_address == '/':
            return self.response(200,'OK','Ini Adalah web Server percobaan',dict())

        if object_address == '/video':
            return self.response(302, 'Found', '', dict(Location='https://youtu.be/katoxpnTf04'))
        if object_address == '/santai':
            return self.response(200, 'OK', 'santai saja', dict())

        if object_address == '/list':
            try:
                current_dir_files = [f for f in os.listdir('./') if os.path.isfile(f) or os.path.isdir(f)]
                upload_dir_files = []
                if os.path.exists('uploads') and os.path.isdir('uploads'):
                    upload_dir_files = [f for f in os.listdir('uploads') if os.path.isfile(os.path.join('uploads', f))]

                list_html = "<html><body><h1>Server Files</h1>"
                list_html += "<h2>Current Directory:</h2><ul>"
                for item in sorted(current_dir_files):
                    if item.startswith('.'):
                        continue
                    if os.path.isfile(item):
                        list_html += f"<li>{item} (File)</li>"
                    elif os.path.isdir(item):
                        list_html += f"<li>{item} (Directory)</li>"
                list_html += "</ul>"
                
                list_html += "<h2>Uploaded Files (in 'uploads' directory):</h2>"
                if upload_dir_files:
                    list_html += "<ul>"
                    for item in sorted(upload_dir_files):
                        list_html += f"<li>{item}</li>"
                    list_html += "</ul>"
                else:
                    list_html += "<p>No files uploaded yet.</p>"

                list_html += "</body></html>"
                return self.response(200, 'OK', list_html, {'Content-Type': 'text/html'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Error listing files: {e}', {})

        object_path = object_address[1:]

        file_to_serve = None
        if os.path.exists(object_path) and os.path.isfile(object_path):
            file_to_serve = object_path
        elif os.path.exists(os.path.join('uploads', object_path)) and os.path.isfile(os.path.join('uploads', object_path)):
            file_to_serve = os.path.join('uploads', object_path)
        
        if not file_to_serve:
            return self.response(404, 'Not Found', f'File "{object_path}" not found.', {})

        try:
            with open(file_to_serve, 'rb') as fp:
                isi = fp.read()
            
            fext = os.path.splitext(file_to_serve)[1]
            content_type = self.types.get(fext.lower(), 'application/octet-stream')

            headers = {'Content-type': content_type}
            return self.response(200, 'OK', isi, headers)
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error reading file: {e}', {})

    def http_post(self, object_address, incoming_headers, request_body_str):
        if object_address == '/upload':
            upload_dir = 'uploads'
            os.makedirs(upload_dir, exist_ok=True)

            mock_headers_obj = Message()
            for k, v in incoming_headers.items():
                mock_headers_obj.add_header(k, v)

            body_bytes_io = io.BytesIO(request_body_str.encode('latin-1'))

            environ = {
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': incoming_headers.get('Content-Type', 'application/x-www-form-urlencoded'),
                'CONTENT_LENGTH': incoming_headers.get('Content-Length', str(len(request_body_str.encode('latin-1')))),
                'QUERY_STRING': '', 
            }

            try:
                form = cgi.FieldStorage(
                    fp=body_bytes_io,
                    headers=mock_headers_obj, 
                    environ=environ,
                    keep_blank_values=1 
                )

                if 'file' in form:
                    file_item = form['file']
                    if file_item.filename:
                        fn = os.path.basename(file_item.filename)
                        filepath = os.path.join(upload_dir, fn)
                        
                        with open(filepath, 'wb') as f:
                            f.write(file_item.file.read())
                        return self.response(200, 'OK', f'File "{fn}" uploaded successfully to {upload_dir}.', {})
                    else:
                        return self.response(400, 'Bad Request', 'No file name provided for upload.', {})
                else:
                    return self.response(400, 'Bad Request', 'No "file" field found in the form data. Ensure the input field name is "file".', {})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Error processing file upload via cgi.FieldStorage: {e}', {})
        else:
            return self.response(404, 'Not Found', '', {})

    def http_delete(self, object_address, headers):
        if object_address.startswith('/delete/'):
            filename = object_address[8:]
            
            filepath_to_delete = os.path.join('uploads', filename)
            
            if not os.path.exists(filepath_to_delete):
                return self.response(404, 'Not Found', f'File "{filename}" not found in uploads directory.', {})
            
            if not os.path.isfile(filepath_to_delete):
                return self.response(400, 'Bad Request', f'"{filename}" is not a file or is not in the uploads directory.', {})

            try:
                os.remove(filepath_to_delete)
                return self.response(200, 'OK', f'File "{filename}" deleted successfully from uploads directory.', {})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Error deleting file: {e}', {})
        else:
            return self.response(400, 'Bad Request', 'Invalid DELETE request format. Use /delete/<filename>.', {})
