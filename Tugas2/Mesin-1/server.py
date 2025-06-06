from socket import *
import socket
import threading
import logging
import sys
from datetime import datetime

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        while True:
            data = self.connection.recv(1024)
            if not data:
                break

            request = data.decode('utf-8')
            logging.warning(f"Request from {self.address}: {request.strip()}")

            if request == "TIME\r\n":
                now = datetime.now()
                waktu = now.strftime("%H:%M:%S")
                response = f"JAM {waktu}\r\n"
                self.connection.sendall(response.encode('utf-8'))
            elif request == "QUIT\r\n":
                break
            else:
                # Jika tidak sesuai permintaan TIME/QUIT, abaikan
                continue

        self.connection.close()

class Server(threading.Thread):
    def __init__(self):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', 45000))
        self.my_socket.listen(5)
        logging.warning("Server is listening on port 45000...")

        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning(f"Connection from {self.client_address}")

            client_thread = ProcessTheClient(self.connection, self.client_address)
            client_thread.start()
            self.the_clients.append(client_thread)

def main():
    logging.basicConfig(level=logging.WARNING)
    svr = Server()
    svr.start()

if __name__ == "__main__":
    main()
