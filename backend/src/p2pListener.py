import socket
import variables
import functions

def serverListen():
    # functions.ipfsListen()
    while True:
        server_socket = socket.socket()
        server_socket.bind(("localhost",variables.listenPort))
        server_socket.listen()
        (client_socket, address) = server_socket.accept()
        data = client_socket.recv(variables.socketBufferSize)
        print(data.decode())
        message = "enc conn"
        client_socket.send(message.encode())
        client_socket.close()
