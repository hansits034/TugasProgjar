import time
import base64
import argparse
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from client_module import remote_get, remote_upload  # asumsikan sudah update agar terima port parameter
import os

def upload_task(args):
    filename, port = args
    start = time.time()
    success = remote_upload(filename, port=port)
    end = time.time()
    return (success, end - start)

def download_task(args):
    filename, port = args
    start = time.time()
    success = remote_get(filename, port=port)
    end = time.time()
    return (success, end - start)

def run_stress(op, filename, pool_type, num_workers, port):
    task_fn = upload_task if op == "upload" else download_task
    tasks = [(filename, port)] * num_workers

    print(f"Running {op} on {filename} with {num_workers} {pool_type} workers at port {port}...")
    
    if pool_type == "thread":
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = list(executor.map(task_fn, tasks))
    elif pool_type == "process":
        with Pool(processes=num_workers) as p:
            results = p.map(task_fn, tasks)
    else:
        raise ValueError("Invalid pool type. Use 'thread' or 'process'.")

    # Rekap hasil
    success_count = sum(1 for r in results if r[0])
    fail_count = num_workers - success_count
    total_time = sum(r[1] for r in results) / num_workers
    file_size = os.path.getsize(filename)
    throughput = file_size / total_time if total_time > 0 else 0

    return {
        "total_time": total_time,
        "throughput": throughput,
        "success": success_count,
        "fail": fail_count
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--op', choices=['upload', 'download'], required=True)
    parser.add_argument('--file', required=True)
    parser.add_argument('--pool', choices=['thread', 'process'], required=True)
    parser.add_argument('--workers', type=int, required=True)
    parser.add_argument('--port', type=int, required=True)  # tambahkan port

    args = parser.parse_args()
    result = run_stress(args.op, args.file, args.pool, args.workers, args.port)
    print(result)

