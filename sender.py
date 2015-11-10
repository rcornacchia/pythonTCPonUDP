import socket
import sys
import time
import select
import datetime
from struct import *

#usage: sender <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>

# argv[1] = file_to_send
# argv[2] = remote_ip
REMOTE_IP = str(sys.argv[2])

# argv[3] = remote_port
REMOTE_PORT = int(sys.argv[3])

# argv[4] = ack_port_num
ACK_PORT_NUM = int(sys.argv[4])

# argv[5] = log_filename
log_file = sys.argv[5]

WINDOW_SIZE = 1
# argv[6] = window_size
if sys.argv[6] is not None:
    WINDOW_SIZE = int(sys.argv[6])


# TCP connection occurs at startup
TCP_IP = socket.gethostbyname(socket.gethostname())

print TCP_PORT
TCP_PORT = ACK_PORT_NUM
BUFFER = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))

s.listen(1)

conn, addr = s.accept()

# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        try:
            w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        except:
            if s > 65535:
                s = s % 65535
            s = abs(s)
            return s
        s = s + w

    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);

    #complement and mask to 4 byte short
    s = ~s & 0xffff

    #accounting for overflow
    if s > 65535:
        s = s % 65535
    if s < 0:
        s = abs(s)
    return s

packet_txt = []

# read text file
if not sys.argv[1]:
    print "Incorrect usage"
else:
    f = open(sys.argv[1], "r")

    try:
        text = f.read(556)
        print len(text)
        packet_txt.append(text)
        while text != "":
            text = f.read(556)
            if text != "":
                packet_txt.append(text)
    finally:
        f.close()

num_packets = len(packet_txt)

# List to hold all packets
packets = []
seq_number = 0

for text in packet_txt:

    # now start constructing the packet
    packet = '';


    # tcp header fields
    tcp_source = 5005   # source port
    tcp_dest = REMOTE_PORT   # destination port
    tcp_seq = seq_number # multiply by size of data
    tcp_ack_seq = 0
    tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
    #tcp flags

    if seq_number == (num_packets-1):
        # last packet
        tcp_fin = 1
    else:
        tcp_fin = 0

    #not using any of these flags
    tcp_syn = 0
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 0
    tcp_urg = 0


    tcp_window = socket.htons (5840)    #   maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)

    # the ! in the pack format string means network order
    tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)

    user_data = text

    tcp_check = checksum(tcp_header + user_data)

    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('!H' , tcp_check) + pack('!H' , tcp_urg_ptr)

    # final full packet - syn packets dont have any data
    packet = tcp_header + user_data

    # increment seq_number
    seq_number += 1

    packets.append(packet)



UDP_IP = REMOTE_IP
UDP_PORT = REMOTE_PORT

timeout = 0
# standard RTO = 3 according to RFC docs
RTO = 3

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

base = 0
# fill window with packets
window = []
acknowledged_packets = []

window = packets[0:WINDOW_SIZE]
del packets[0:WINDOW_SIZE]

# I use 3 seconds as initial RTO, as per RFC standards.
# If RTT >2, increase RTO to 5 seconds.
RTO = 3

# start timer
start = time.time()

#last_base
last_base = 0

time_stamps = []

# send packets
for packet in window:
    sock.sendto(packet, (UDP_IP, UDP_PORT))
    base + 1

base = 0
data = None

ready = []
print "Packets is size " + str(len(packets))

retransmit_counter = 0

while(len(acknowledged_packets) != num_packets):
    now = time.time()
    if now - start <= RTO:
        ready = select.select([conn], [], [], 0.00001)
        if ready[0]:
            data = conn.recv(BUFFER)
            ready = []

        if data is not None:

            tcp_header = unpack('!HHLLBBHHH' , data[:20])
            seq_number = tcp_header[2]
            ack_seq_number = tcp_header[3]
            fin_number = tcp_header[5]

            now = time.time()
            RTT = now - start

            #Increase RTO if RTT comes close to RTO
            if RTT >= RTO-1:
                RTO = RTO*2


            p_time = datetime.datetime.fromtimestamp(now).strftime('%H:%M:%S')
            stamp = p_time, ack_seq_number, RTT
            time_stamps.append(stamp)

            data = None
            if(base == ack_seq_number):
                # received the correct ack
                acknowledged_packets.append(window[0])
                del window[0]
                # add next packet to window
                if base < 8:
                    window.append(packets[0])
                    del packets[0]
                else:
                    start = time.time()
                    for packet in window:
                        sock.sendto(packet, (UDP_IP, UDP_PORT))
                base += 1
            else:
                retransmit_counter += 1
    else:
        if base == last_base:
            retransmit_counter += 1
        else:
            last_base = base
        # resend the packets
        start = time.time()
        for packet in window:
            sock.sendto(packet, (UDP_IP, UDP_PORT))



print "Delivery completed successfully"
print "Total bytes sent = " + str(num_packets*576)
print "Segments sent = " + str(num_packets)
print "Segments retransmitted = " + str(retransmit_counter)


# timestamp, source, destination, Sequence #, ACK #, RTT
lf = open(log_file, "wb")
lf.write("timestamp\tsource\t\tdestination\tSequence #\tACK #\tRTT\n")
for stamp in time_stamps:
    lf.write(str(stamp[0]) + "\t" + socket.gethostname() + "\t\t" + str(REMOTE_IP) + "\t" + str(stamp[1]) + "\tACK#" + str(stamp[1]) + "\t" + str(stamp[2]) + "\n")
