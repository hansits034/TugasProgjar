from socket import *
import socket
import time
import sys
import logging
from concurrent.futures import ThreadPoolExecutor
from http_server import HttpServer 

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    rcv_buffer = ""
    try:
        while True:
            data = connection.recv(4096) 
            if not data: 
                logging.info(f"Connection from {address} received no more data, client disconnected.")
                break

            rcv_buffer += data.decode('latin-1') 
            
            if "\r\n\r\n" in rcv_buffer:
                headers_part, body_part_candidate = rcv_buffer.split("\r\n\r\n", 1)
                
                content_length = 0
                for line in headers_part.split("\r\n"):
                    if line.lower().startswith("content-length:"):
                        try:
                            content_length = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            logging.warning(f"Malformed Content-Length header: {line}")
                            pass
                        break
                
                current_body_len = len(body_part_candidate.encode('latin-1'))
                
                if "POST" in headers_part and current_body_len < content_length:
                    while current_body_len < content_length:
                        extra_data = connection.recv(4096)
                        if not extra_data: 
                            logging.warning(f"Client {address} disconnected while sending POST body.")
                            break 
                        rcv_buffer += extra_data.decode('latin-1')
                        current_body_len = len(rcv_buffer.split("\r\n\r\n", 1)[1].encode('latin-1'))
                    
                if current_body_len >= content_length or "GET" in headers_part or "DELETE" in headers_part:
                    response_bytes = httpserver.proses(rcv_buffer)
                    connection.sendall(response_bytes)
                    break 

    except Exception as e:
        logging.error(f"Error processing client {address}: {e}", exc_info=True)
    finally:
        connection.close()
        logging.info(f"Connection from {address} closed.")

def Server():
    logging.basicConfig(level=logging.INFO, 
                        format='[%(asctime)s] %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)])

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ('0.0.0.0', 8889) 
    my_socket.bind(server_address)
    my_socket.listen(5) 

    logging.info(f"Thread Pool Server listening on {server_address[0]}:{server_address[1]}...")
    
    with ThreadPoolExecutor(max_workers=20) as executor: 
        while True:
            try:
                connection, client_address = my_socket.accept()
                logging.info(f"Connection from {client_address} received. Dispatching to thread.")
                
                executor.submit(ProcessTheClient, connection, client_address)
            
            except KeyboardInterrupt:
                logging.info("Server shutting down due to KeyboardInterrupt.")
                break 
            except Exception as e:
                logging.error(f"Error accepting connection: {e}", exc_info=True)
                continue 

def main():
    Server()

if __name__ == "__main__":
    main()
