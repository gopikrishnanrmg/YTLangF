import socket
import variables
import time
import logging

def clientSend(hexDig):
    flag = False
    peer_ids = ipfsSwarmPeers()
    start_time = time.perf_counter()
    for peer_id in peer_ids:
        variables.logger.debug("Request sent to " + str(peer_id))
        functions.ipfsForward(peer_id)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", variables.sendPort))
        s.sendall(hexDig.encode())
        data = (s.recv(variables.socketBufferSize)).decode() #validate the data here, check if its of the right format, later can add signature schema
        variables.logger.debug("Recieved " + str(data) + " sent to "+ str(peer_id))
        try:
            if not (isinstance(data, (int)) and data == variables.socketRecordNA):
                langs = record.get("langs")
                flag = True
        except Exception as e:
            variables.logger.debug("Cannot parse " + str(data) + " received from "+ str(peer_id))
        
        s.close()
        functions.ipfsP2PClose(peerID)

        if time.time()-start_time > variables.waitTimeThreshold and flag:
            functions.add_record(hexDig,langs)
            return False
        elif time.time()-start_time > variables.waitTimeThreshold and not flag:
            return True

