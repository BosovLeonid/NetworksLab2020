import socket
import threading as th
from datetime import datetime
import sys

HEADER = 10
ENCODE = 'utf-8'

AUTHORIZATION = '1'
DISCONNECT = '2'
SEND = '3'
CHANGE_NICK = '4'

def setup_client():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"Choose where the server deployed:"
    f"\n1 - Enter manually"
    f"\n2 - localhost(127.0.0.1)"
    f"\n3 - {hostname}({ip_address})")
    while True:
        mode = input()
        if (mode != '1') & (mode != '2') & (mode != '3'): 
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

    # Port input
    while True:
        try:
            port = int(input("Enter port(1024 - 65535):"))
            break
        except ValueError:
            print("Bad input")

    if(1024 > port):
        print("Warning! Reserved port. Port will be 1024.")
        port = 1024
    elif(port > 65535):
        print("Warning! Out of range. Port will be 65535.")
        port = 65535

    client(ip_address, port)

def client(IP, PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect((IP, PORT))

    print(f"Connection with {IP}:{PORT} established.")

    while True:
        username = input("Enter username:")
        if username != '':
            client_socket.send(f'{len(AUTHORIZATION):<{HEADER}}'.encode(ENCODE) + AUTHORIZATION.encode(ENCODE))
            client_socket.send(f'{len(username.encode(ENCODE)):<{HEADER}}'.encode(ENCODE) + username.encode(ENCODE))
            print(f"Authorization complete.")
            break

    th.Thread(target = recv_handler, args = (client_socket, )).start()
    th.Thread(target = send_handler, args = (client_socket, )).start()

def convert_time(_time):
    return datetime.fromtimestamp(float(_time)).strftime("%H:%M:%S")

def length_control(client_socket, data, length):
    if (len(data) != length):
        data_tmp = client_socket.recv(length - len(data))
        data += data_tmp
    return {'data_recived': len(data) == length, 'data': data}

def read_package(client_socket, buffer):
    try:
        # header recive
        if not buffer['header_recived']:
            msg_header = buffer['header']
            data = length_control(client_socket, msg_header, HEADER)
            
            buffer['header_recived'] = data['data_recived']
            buffer['header'] = data['data']
            if not data['data_recived']:
                return False, buffer

        # msg reciver
        msg = buffer['data']
        msg_len = int(buffer['header'].strip())
        data = length_control(client_socket, msg, msg_len)
        buffer['data_recived'] = data['data_recived']
        buffer['data'] = data['data']
        if not data['data_recived']:
            return False, buffer

        data_recv = buffer['data'].decode(ENCODE)
        buffer = {'header_recived': False, 'header': ''.encode(ENCODE),'data_recived': False, 'data':''.encode(ENCODE)}
        return data_recv, buffer
    except:
        return False

def recv_handler(client_socket):
    flags = {'username_recived': False, 'message_recived': False, 'time_recived': False}
    buffer = {'header_recived': False, 'header': ''.encode(ENCODE),'data_recived': False, 'data':''.encode(ENCODE)}
    while True:      
        try:
            #Username reciving
            if not flags['username_recived']:
                data, buffer = read_package(client_socket, buffer)
                if not data:
                    continue
                else:
                    username = data
                    flags['username_recived'] = True
            #Message reciving        
            if not flags['message_recived']:
                data, buffer = read_package(client_socket, buffer)
                if not data:
                    continue
                else:
                    message = data
                    flags['message_recived'] = True
            #Time reciving
            if not flags['time_recived']:
                data, buffer = read_package(client_socket, buffer)
                if not data:
                    continue
                else:
                    time = data
                    flags['time_recived'] = True
            #Display message
            if False in flags.values():
                continue
            else:
                print(f"<{convert_time(time)}> [{username}]: {message}")
                flags = {'username_recived': False, 'message_recived': False, 'time_recived': False}
                buffer = {'header_recived': False, 'header': ''.encode(ENCODE),'data_recived': False, 'data':''.encode(ENCODE)}
        except OSError:
            print(f"Connection was closed.")
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            return
        except EOFError:
            print(f"Connection was closed.")
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            return

def send_handler(client_socket):
    print(f"\nAvailable commands:\n"
    f"!disconnect - close connection and leave chat\n"
    f"!change - change current nickaname\n")
    while True:
        try:
            message = input()

            if message == '!disconnect':
                client_socket.send(f'{len(DISCONNECT):<{HEADER}}'.encode(ENCODE) + DISCONNECT.encode(ENCODE))
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                sys.exit()
            elif message == '!change': 
                username = input("Enter new username:")
                client_socket.send(f'{len(CHANGE_NICK):<{HEADER}}'.encode(ENCODE) + CHANGE_NICK.encode(ENCODE))
                client_socket.send(f"{len(username.encode(ENCODE)):<{HEADER}}".encode(ENCODE) + username.encode(ENCODE))
            elif message:
                client_socket.send(f'{len(SEND):<{HEADER}}'.encode(ENCODE) + SEND.encode(ENCODE))
                client_socket.send(f"{len(message.encode(ENCODE)):<{HEADER}}".encode(ENCODE) + message.encode(ENCODE))
        except OSError:
            print(f"Connection was closed.")
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            return
        except EOFError:
            print(f"Connection was closed.")
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            return
            
setup_client()