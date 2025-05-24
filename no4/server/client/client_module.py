import socket
import base64

def send_command(command_str, port=6661):  # port default bisa diubah
    # Contoh koneksi sederhana ke server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.sendall(command_str.encode())
        data_received = ""
        while True:
            data = s.recv(4096)
            if not data:
                break
            data_received += data.decode()
            if data_received.endswith("\r\n\r\n"):
                break
        # parsing hasil contoh: harus disesuaikan dengan protokol servermu
        # Misal hasilnya dict-like JSON, kembalikan dict
        # Kalau kamu pakai format lain, parsing disini
        # Contoh dummy:
        return {"status": "OK", "data_namafile": "dummy_10mb.bin", "data_file": "base64string"}

def remote_get(filename, port=6661):
    command_str=f"GET {filename}\r\n\r\n"
    hasil = send_command(command_str, port)
    if hasil['status']=='OK':
        namafile= hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        with open(namafile, 'wb+') as fp:
            fp.write(isifile)
        return True
    else:
        print("Gagal mengambil file dari server")
        return False

def remote_upload(filename, port=6661):
    with open(filename, 'rb') as fp:
        isifile = base64.b64encode(fp.read()).decode()
    command_str=f"UPLOAD {filename} {isifile}\r\n\r\n"
    hasil = send_command(command_str, port)
    if hasil['status']=='OK':
        print(f"Upload File {filename} Ke Server Berhasil!!!")
        return True
    else:
        print("Gagal mengupload file ke server")
        print(f"error: {hasil.get('data', '')}")
        return False

