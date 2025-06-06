import sys
import socket
import logging
import threading

def kirim_data(nama="kosong"):
    logging.warning(f"[CLIENT-{nama}] mulai koneksi")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('172.16.16.101', 45000)
    logging.warning(f"[CLIENT-{nama}] membuka socket ke {server_address}")
    sock.connect(server_address)

    try:
        # Kirim permintaan waktu
        request = 'TIME\r\n'
        logging.warning(f"[CLIENT-{nama}] mengirim: {request.strip()}")
        sock.sendall(request.encode())

        # Terima respon waktu
        data = sock.recv(1024)
        logging.warning(f"[CLIENT-{nama}] menerima: {data.decode().strip()}")

        # Kirim perintah QUIT
        quit_cmd = 'QUIT\r\n'
        logging.warning(f"[CLIENT-{nama}] mengirim: {quit_cmd.strip()}")
        sock.sendall(quit_cmd.encode())

    finally:
        logging.warning(f"[CLIENT-{nama}] menutup koneksi")
        sock.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    threads = []
    for i in range(3):
        t = threading.Thread(target=kirim_data, args=(i,))
        threads.append(t)

    for thr in threads:
        thr.start()
