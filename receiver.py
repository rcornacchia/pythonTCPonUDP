import socket
import sys
import select
import time
import datetime
from struct import *


# usage: receiver <filename> <listening_port> <sender_IP> <sender_port> <log_filename>
of = open(sys.argv[1], "wb")
LISTENING_PORT = int(sys.argv[2])
TCP_IP = sys.argv[3]
TCP_PORT = int(sys.argv[4])
log_file = sys.argv[5]


BUFFER = 1024
ack0 = "ack0"
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((TCP_IP, TCP_PORT))

time_stamps = []

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

UDP_IP = socket.gethostname()
UDP_PORT = LISTENING_PORT


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((UDP_IP, UDP_PORT))
expected_seq_num = 0
received_packets = []
message = []
time_stamps = []
stamp = ""

packet_in_order = False
packet_corrupt = False

while True:
    # Add try here
    packet_corrupt = False
    try:
        data, addr = sock.recvfrom(576)
    except:
        break

    if data is not None:
        now = time.time()

        received_packets.append(data)
        tcp_header = unpack('!HHLLBBHHH' , data[:20])
        seq_number = tcp_header[2]
        fin_number = tcp_header[5]

        p_time = datetime.datetime.fromtimestamp(now).strftime('%H:%M:%S')
        stamp = p_time, seq_number
        time_stamps.append(stamp)


        packet_checksum = tcp_header[7]
        message.append(data[20:])
        of.write(data[20:])
        # Check to see if corrupt by using checksum function
        # now start constructing the packet
        packet = '';


        # tcp header fields
        tcp_source = tcp_header[0]   # source port
        tcp_dest = tcp_header[1]   # destination port
        tcp_seq = seq_number # multiply by size of data
        tcp_ack_seq = 0
        tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        tcp_fin = fin_number
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

        user_data = data[20:]
        new_checksum = checksum(tcp_header + user_data)
        if new_checksum != packet_checksum:
            print "checksum does not match, corruption detected."
            packet_corrupt = True
        # Check to see if in order
        print expected_seq_num
        if seq_number == expected_seq_num and packet_corrupt == False:
            expected_seq_num += 1
        else:
            packet_in_order = False
        print "expected: " + str(expected_seq_num-1)
        print "Got pack: " + str(seq_number)        
        # if correct packet is received in order, then pack ACK and send
        # now start constructing the packet
        packet = '';
        # tcp header fields
        tcp_source = LISTENING_PORT   # source port
        tcp_dest = LISTENING_PORT # destination port
        tcp_seq = int(seq_number) # multiply by size of data
        tcp_ack_seq = int(seq_number)
        tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        tcp_fin = 0
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


        tcp_check = checksum(tcp_header)

        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('!H' , tcp_check) + pack('!H' , tcp_urg_ptr)

        # final full packet - syn packets dont have any data
        packet = tcp_header
        print seq_number

        if packet_corrupt == False:
            print packet
            tcp_sock.send(packet)
            if fin_number == 1:
                print "Delivery completed successfully"
                # write message to logfile
                # if message is stdout, just print the output
                lf = open(log_file, "wb")
                lf.write("timestamp\tsource\t\tdestination\tSequence #\tACK #\n")
                for stamp in time_stamps:
                    lf.write(str(stamp[0]) + "\t" + socket.gethostname() + "\t\t" + str(TCP_IP) + "\t" + str(stamp[1]) + "\tACK#" + str(stamp[1]) + "\n")


                exit()

