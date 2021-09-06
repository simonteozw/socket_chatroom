# server can handle many clients,

import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# overcome the "Address already in use" error
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]

clients = {}

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header): # client has closed connection
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {
            "header": message_header,
            "data": client_socket.recv(message_length)
        }

    except:
        # something wrong like empty message or client exited abruptly
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket: # new connection
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print("Accepted new connection from {}:{}, username: {}".format(*client_address, user['data'].decode('utf-8')))
        # existing socket is sending a message
        else:
            message = receive_message(notified_socket)

            if message is False:
                print("Closed connection from {}".format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print("Received message from {}:{}".format(user["data"].decode("utf-8"), message["data"].decode("utf-8")))

            # broadcase message to all other clients
            for client_socket in clients:

                # but do not send to sender
                if client_socket == notified_socket:
                    continue

                # user['header'] and message['header'] are already encoded
                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
