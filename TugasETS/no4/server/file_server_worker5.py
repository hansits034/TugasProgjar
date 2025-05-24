from socket import *
import socket
import multiprocessing
import logging
from file_protocol import FileProtocol

fp = FileProtocol()

def handle_client(conn_addr):
    conn, addr = conn_addr
    logging.warning(f"processing connection from {addr}")
    data_received = ""
    try:
        while True:
            data = conn.recv(32)
            if not data:
                break
            d = data.decode()
            data_received += d
            if data_received.endswith("\r\n\r\n"):
                hasil = fp.proses_string(data_received[:-4])
                hasil += "\r\n\r\n"
                conn.sendall(hasil.encode())
                data_received = ""
    except Exception as e:
        logging.warning(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

def main():
    ip_address = '0.0.0.0'
    port = 6662
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip_address, port))
    sock.listen(5)

    logging.warning(f"server berjalan di {ip_address}:{port} dengan 5 worker")

    pool = multiprocessing.Pool(processes=5)

    while True:
        conn, addr = sock.accept()
        # Kirim tuple (conn, addr) ke pool worker
        pool.apply_async(handle_client, args=((conn, addr),))

if __name__ == '__main__':
    main()
