import socket
import sys
import time
import select
from struct import *

#usage: sender <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>

# # argv[1] = file_to_send
# # argv[2] = remote_ip
# REMOTE_IP = sys.argv[2]
#
# # argv[3] = remote_port
# REMOTE_PORT = sys.argv[3]
#
# # argv[4] = ack_port_num
# ACK_PORT_NUM = sys.argv[4]
#
# # argv[5] = log_filename
#
# # argv[6] = window_size
# WINDOW_SIZE = sys.argv[6]
WINDOW_SIZE = 3




# TCP connection occurs at startup
TCP_IP = '127.0.0.1'
TCP_PORT = int(sys.argv[2])
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

    source_ip = '127.0.0.1'
    dest_ip = '127.0.0.1' # or socket.gethostbyname('www.google.com')

    # tcp header fields
    tcp_source = 1234   # source port
    tcp_dest = 4444   # destination port
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

    # pseudo header fields
    source_address = socket.inet_aton( source_ip )
    dest_address = socket.inet_aton(dest_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(user_data)

    psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
    psh = psh + tcp_header + user_data;

    tcp_check = checksum(psh)
    #print tcp_checksum

    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('!H' , tcp_check) + pack('!H' , tcp_urg_ptr)

    # final full packet - syn packets dont have any data
    packet = tcp_header + user_data

    # increment seq_number
    seq_number += 1



    packets.append(packet)

last_message = packet_txt[-1]
print "checksum: ", tcp_check
print sys.getsizeof(tcp_header)

#Send the packet finally - the port specified has no effect
# s.sendto(packet, (dest_ip , 0 ))    # put this in a loop if you want to flood the target
# base

# window

# final

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

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

# print "WINDOW"
# print window
# I use 3 seconds as initial RTO, as per RFC standards.
# If RTT >2, increase RTO to 5 seconds.
RTO = 3

# start timer
start = time.time()

# send packets
for packet in window:
    print "sending packet number" + str(base)
    sock.sendto(packet, (UDP_IP, UDP_PORT))



now = time.time()

time.sleep(1)

later = time.time()
ready = []

print "Difference is "+ str(later-now)

while(len(packets) != 0):
    now = time.time()
    print "NOW " + str(now)
    print "start " + str(start)
    print "now - start" + str(now - start)
    if now - start <= RTO:
        ready = select.select([conn], [], [], 3)
        print "before recv"

        if ready[0]:
            data = conn.recv(BUFFER)

        print "after recv"
        if not data:
            # timeout += 1
            # time.sleep(1)
            break
        print "STILL SENDING"

        #stop timer
        print "received data:", data

        tcp_header = unpack('!HHLLBBHHH' , data[:20])
        seq_number = tcp_header[2]
        ack_seq_number = tcp_header[3]
        fin_number = tcp_header[5]
        print "ack sequence number: " + str(ack_seq_number)
        if(base == ack_seq_number):
            print "testasdkfjalskdfj"
            # received the correct ack
            acknowledged_packets.append(window[0])
            del window[0]
            # add next packet to window
            window.append(packets[0])
            base += 1
    else:
        print "TIMEOUT"
        # resend the packets
        start = time.time()
        for packet in window:
            sock.sendto(packet, (UDP_IP, UDP_PORT))



print "END OF FILE"
