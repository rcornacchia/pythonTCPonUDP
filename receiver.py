import socket
import sys
from struct import *

# TCP_IP = '127.0.0.1'
# TCP_PORT = 4444
# BUFFER = 1024
# ack0 = "ack0"
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((TCP_IP, TCP_PORT))
# s.send(ack0)
#
#
# data = s.recv(BUFFER)
# s.close()

TCP_OPEN = False

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((UDP_IP, UDP_PORT))

while True:
    # Add try here
    data, addr = sock.recvfrom(576)

    if TCP_OPEN == False:
        if data:
            # Once you receive first packet start TCP connection, return socket
            TCP_OPEN = True
    else:


        txt = unpack('!HHLLBBHHH' , data[:20])
        print "received message:", txt

        print sys.getsizeof(txt)
        print sys.getsizeof(data[20:])
        print "data:", data[20:]

# check to see if packet is FIN
# return sequence number
