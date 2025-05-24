import socket
import logging
import multiprocessing
import sys
from file_protocol import FileProtocol

fp = FileProtocol()

def handle_client(conn, addr):
    logging.warning(f"processing connection from {addr}")
    data_received = ""
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
    conn.close()

def main(worker_count):
    ip_address = '0.0.0.0'
    port = 6666
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip_address, port))
    sock.listen(5)

    logging.warning(f"server berjalan di {ip_address}:{port} dengan {worker_count} worker")

    # Gunakan proses pool (opsional) atau spawn manual
    while True:
        conn, addr = sock.accept()
        # spawn worker secara manual
        p = multiprocessing.Process(target=handle_client, args=(conn, addr))
        p.start()

if __name__ == '__main__':
    try:
        worker_count = int(sys.argv[1])
    except:
        worker_count = 1
    main(worker_count)

