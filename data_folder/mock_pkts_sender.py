import socket
import time

ip="127.0.0.1"
port=54816 + 25
to_send=54816 + 26
sendin=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sendin.bind((ip,port))
TM="8362779449732947244741960369298736354041856"
TL="4755809263979890948"

while True:
    sendin.sendto(TM,(ip,to_send))
    time.sleep(0.1)


