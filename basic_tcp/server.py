import socket
import threading

from os import urandom

from utils2 import bf_decrypt

IP = '0.0.0.0'
PORT = 9998

BUFF_SIZE = 16

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')
    while True:
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}: {address[1]})')
        client_handler = threading.Thread (target = handle_client, args = (client,))
        client_handler.start()

def handle_client(client_socket):
    with client_socket as sock:
        data = urandom(BUFF_SIZE) 
        while len(data) == BUFF_SIZE:
            data = sock.recv(BUFF_SIZE)
            print(f'[*] Received: {data} of length {len(data)}')

if __name__ == '__main__':
    main()

