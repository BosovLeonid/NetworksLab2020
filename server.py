import socket
import threading as th
from datetime import datetime
import sys

clients = {}

HEADER = 10
ENCODE = 'utf-8'

def setup_server():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"Choose where the server will be deployed:"
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

    server(ip_address, port) 

def server(IP, PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    th.Thread(target = accept_thread, args = (server_socket, )).start()

def accept_thread(server_socket):
    server_socket.listen()
    print(f"Waiting for new connections...")
    while True:
        client_socket, client_addr = server_socket.accept()
        print('{:*<30}'.format("*"))
        print(f"Connection with {client_addr[0]}:{client_addr[1]} established.")
        username = recv_package(client_socket)
        if username:
            clients[client_socket] = username
            print(f"Authorization on {client_addr[0]}:{client_addr[1]} complete.") 
            print(f"Username - {username['data'].decode(ENCODE)}.")
            print('{:*<30}'.format("*"))
            th.Thread(target = client_handler, args = (client_socket, )).start()

def recv_package(client_socket):
    while True:
        try:
            msg_header = client_socket.recv(HEADER)
            if not len(msg_header):
                return False
            msg_len = int(msg_header.decode(ENCODE).strip())
            return {'header':msg_header, 'data':client_socket.recv(msg_len)}
        except:
            return False

def client_handler(client_socket):
    while True:
        user = clients[client_socket]
        message = recv_package(client_socket)
        if not message:
            try:
                print(f"Connection was closed by user {user['data'].decode(ENCODE)}.")
                del clients[client_socket]
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                return
            except:
                continue
        time = datetime.now().strftime("%H:%M").encode(ENCODE)
        time_header = f"{len(time):<{HEADER}}".encode(ENCODE)
        message_time = {'header':time_header, 'data': time}
        print('{:-<30}'.format("-"))
        print(f"Received message from {user['data'].decode(ENCODE)}: \"<{time.decode(ENCODE)}> {message['data'].decode(ENCODE)}\"")
        print("Sending to other users.")

        for client in clients:
            if client == client_socket: continue
            client.send(user['header'] + user['data'] + message['header'] + message['data'] + message_time['header'] + message_time['data'])

        print("Sending done.")
        print('{:-<30}'.format("-"))    

setup_server()