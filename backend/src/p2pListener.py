import socket
import variables
import functions
import logging

def serverListen():
    functions.ipfsListen()
    server_socket = socket.socket()
    server_socket.bind(("localhost",variables.listenPort))
    while True:
        server_socket.listen()
        (client_socket, address) = server_socket.accept()
        data = client_socket.recv(variables.socketBufferSize)
        variables.logger.debug("Recieved request for " + str(data.decode()))
        record = functions.find_record(data.decode())
        if record:
            variables.logger.debug("Found record for " + str(data.decode()) + " : " + str(record))
            client_socket.send(record.encode())
        else:
            variables.logger.debug("Cannot find record for " + str(data.decode()))
            client_socket.send(variables.socketRecordNA.encode())
        client_socket.close()

serverListen()