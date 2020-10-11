import socket
import threading as th
import sys

HEADER = 10
ENCODE = 'utf-8'

clients = {}

def setup_client():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"Choose where the server deployed:"
    f"\n1 - Enter manually"
    f"\n2 - localhost(127.0.0.1)"
    f"\n3 - {hostname}({ip_address})")
    while True:
        mode = input()
        if (mode != '1') & (mode != '2'): 
            print("Bad input")
            continue
        elif mode == '1':
                while True:
                    ip_address = input("Format - x.x.x.x: ")
                    try:
                        socket.inet_aton(ip_address)
                        break
                    except socket.error:
                        print("Bad input")
                        continue
                break
        elif mode == '2':
                ip_address = 'localhost'
                break
        else: 
            break
    while True:
        port = int(input("Enter port(1024 - 65535):"))
        if(1024 > port) | (port > 65535):
            print("Bad input")
            continue
        else: break

    client(ip_address, port)

def client(IP, PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect((IP, PORT))

    print(f"Connection with {IP}:{PORT} established.")

    username = input("Enter username:").encode(ENCODE)
    client_socket.send(f"{len(username):<{HEADER}}".encode(ENCODE) + username)
    print(f"Authorization complete.")

    th.Thread(target = recv_handler, args = (client_socket, )).start()
    th.Thread(target = send_handler, args = (client_socket, )).start()

def read_package(client_socket):
    header = client_socket.recv(HEADER)
    if not len(header):
        print(f"Connection was closed by server.")
        sys.exit()
    data_len = int(header.decode(ENCODE))
    return client_socket.recv(data_len).decode(ENCODE)

def recv_handler(client_socket):
    while True:
        try:
            username = read_package(client_socket)
            message = read_package(client_socket)
            time = read_package(client_socket)
            
            print(f"<{time}> [{username}]: {message}")
        except OSError:
            print(f"Connection was closed by server.")
            return
        except:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            sys.exit()

def send_handler(client_socket):
    while True:
        try:
            message = input().encode(ENCODE)

            if message == 'qq'.encode(ENCODE):
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                sys.exit()
            if message:
                client_socket.send(f"{len(message):<{HEADER}}".encode(ENCODE) + message)
        except OSError:
            return
            
setup_client()