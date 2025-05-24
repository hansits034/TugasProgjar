from socket import socket, SOL_SOCKET, SO_REUSEADDR, AF_INET, SOCK_STREAM
import logging
from concurrent.futures import ThreadPoolExecutor
from file_protocol import FileProtocol

fp = FileProtocol()

def process_client(connection, address):
    logging.warning(f"connection from {address}")
    data_received = ""
    try:
        while True:
            data = connection.recv(32)
            if data:
                d = data.decode()
                data_received += d
                if data_received.endswith("\r\n\r\n"):
                    hasil = fp.proses_string(data_received[:-4])
                    hasil += "\r\n\r\n"
                    connection.sendall(hasil.encode())
                    data_received = ""
            else:
                break
    except Exception as e:
        logging.warning(f"error handling client {address}: {str(e)}")
    finally:
        connection.close()

def main():
    server_address = ('0.0.0.0', 6666)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(server_address)
    sock.listen(5)

    logging.warning(f"server berjalan di ip address {server_address}")

    # Gunakan thread pool untuk mengelola klien
    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            connection, client_address = sock.accept()
            executor.submit(process_client, connection, client_address)

if __name__ == '__main__':
    main()

