import socket
import variables

def clientSend():
    # functions.ipfsForward()
    client_socket = socket.socket()
    host = socket.gethostname()
    client_socket.connect((host, variables.listenPort))

    message = client_socket.recv(variables.socketBufferSize)

    client_socket.close()
    print(message.decode('ascii'))
