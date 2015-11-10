import socket
import sys
import select
from struct import *


TCP_IP = '127.0.0.1'
TCP_PORT = int(sys.argv[1])
BUFFER = 1024
ack0 = "ack0"
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((TCP_IP, TCP_PORT))


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




# TCP_OPEN = False


UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#just a placeholder for tcp_socket
# tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
expected_seq_num = 0
received_packets = []
message = []


while True:
    # Add try here
    try:
        data, addr = sock.recvfrom(576)
    except:
        pass

    if data:
        received_packets.append(data)
        tcp_header = unpack('!HHLLBBHHH' , data[:20])
        print tcp_header
        seq_number = tcp_header[2]
        fin_number = tcp_header[5]
        packet_checksum = tcp_header[7]
        print "Sequence number = " + str(seq_number)
        print "FIN_number = " + str(fin_number)
        message.append(data[20:])





        #TODO Check to see if corrupt by using checksum function
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

        # pseudo header fields
        # source_address = socket.inet_aton( source_ip )
        # dest_address = socket.inet_aton(dest_ip)
        # placeholder = 0
        # protocol = socket.IPPROTO_TCP
        # tcp_length = len(tcp_header) + len(user_data)
        #
        # psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
        # psh = psh + tcp_header + user_data;

        new_checksum = checksum(tcp_header + user_data)

        print new_checksum
        print packet_checksum
        if new_checksum != packet_checksum:
            print "checksum does not match, corruption detected."
            break

        #TODO Check to see if in order
        if seq_number == expected_seq_num:
            expected_seq_num += 1
        else:
            break

        # if correct packet is received in order, then pack ACK and send
        # now start constructing the packet
        packet = '';

        source_ip = '127.0.0.1'
        dest_ip = '127.0.0.1' # or socket.gethostbyname('www.google.com')

        # tcp header fields
        tcp_source = 1234   # source port
        tcp_dest = 4444   # destination port
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

        # pseudo header fields
        source_address = socket.inet_aton(source_ip)
        dest_address = socket.inet_aton(dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header)

        psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
        psh = psh + tcp_header;

        tcp_check = checksum(psh)
        #print tcp_checksum

        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('!H' , tcp_check) + pack('!H' , tcp_urg_ptr)

        # final full packet - syn packets dont have any data
        packet = tcp_header





        print "received message:"

        print sys.getsizeof(tcp_header)
        print sys.getsizeof(data[20:])
        # print "data:", data[20:]


        tcp_sock.send(packet)
        if fin_number == 1:
            print "Delivery completed successfully"
            # write message to logfile
            # if message is stdout, just print the output
            exit()

        # if FIN == 1, set expected_seq_num = 0 (ready for next message)




    # check to see if packet is FIN
    # return sequence number
