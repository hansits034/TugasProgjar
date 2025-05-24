import subprocess
import csv
from itertools import product

# Konfigurasi kombinasi
operations = ['upload', 'download']
files = {
    '10MB': 'dummy_10mb.bin',
    '50MB': 'dummy_50mb.bin',
    '100MB': 'dummy_100mb.bin'
}
client_workers = [1, 5, 50]
server_workers = [1, 5, 50]
pool_type = 'process'  # bisa diganti 'thread'

# Mapping server worker ke port
port_map = {
    1: 6661,
    5: 6662,
    50: 6663
}

# CSV setup
csvfile = open("stress_test_results.csv", "w", newline="")
csvwriter = csv.writer(csvfile)
csvwriter.writerow([
    "No", "Operasi", "Volume", "Client Workers", "Server Workers",
    "Port Server", "Waktu Total/Client (s)", "Throughput (bytes/s)",
    "Client Sukses", "Client Gagal"
])

no = 1
for op, (vol_label, file), cworker, sworker in product(operations, files.items(), client_workers, server_workers):
    port = port_map[sworker]
    print(f"▶️ [{no}/54] Testing: {op}, {vol_label}, {cworker} client workers, {sworker} server workers at port {port}")

    # (opsional) restart server sesuai jumlah sworker jika kamu mau automatisasi server juga

    # Panggil client stress test dengan port yang sesuai
    proc = subprocess.run(
        ['python3', 'stress_client.py',
         '--op', op,
         '--file', file,
         '--pool', pool_type,
         '--workers', str(cworker),
         '--port', str(port)],
        capture_output=True, text=True
    )

    # Parsing hasil output JSON-like (hasil dict dari `stress_client.py`)
    try:
        exec("result = " + proc.stdout.strip())  # insecure, hanya untuk testing
        waktu_total = round(result['total_time'], 4)
        throughput = round(result['throughput'], 2)
        sukses = result['success']
        gagal = result['fail']
    except Exception as e:
        waktu_total = 0
        throughput = 0
        sukses = 0
        gagal = cworker

    csvwriter.writerow([
        no, op, vol_label, cworker, sworker,
        port, waktu_total, throughput, sukses, gagal
    ])
    no += 1

csvfile.close()
print("✅ Stress test selesai, hasil disimpan di stress_test_results.csv")

