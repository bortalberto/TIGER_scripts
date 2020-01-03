import socket
import time

port_for_cloning = 58880 + 4
cloning_sending_port = 50000 + 4
address_for_cloning_sender = "127.0.0.1"
address_for_cloning_rcv = "127.0.0.1"
cloning_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cloning_sock.bind((address_for_cloning_sender, cloning_sending_port))
cloning_sock.setblocking(True)


with open("./data_for_packet_sender.dat", 'rb') as fi:
    full_data = fi.read()
    pacchetto=""
    for i in range(0, len(full_data) // 8):
        dato=full_data[i * 8:i * 8 + 8]
        print dato

        if dato!= "_spacer_":
            pacchetto+=dato
            time.sleep(0.01)
        else:
            cloning_sock.sendto(pacchetto, (address_for_cloning_rcv, port_for_cloning))
            time.sleep(0.5)
            pacchetto=""
