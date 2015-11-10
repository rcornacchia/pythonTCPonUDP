
    # conn.send(data)
    #if ack = base
# send all packets in window
# window = base + WINDOW_SIZE

# send packets from base to window or to last packet

#when you receive an ACK
# 1 - remove packet from packets and add to confirmed
# 2 - if ACK = base, increment base
# 3 - else if ACK != base resend packets from base to window

# if timeout occurs, resend packets from base to window

# packets - contains all packets
# base = 0
# basePacket = packets[base]
# window = []
# while len(packets) != 0:
#     if WINDOW_SIZE < len(packets):
#         window.append(packets[base:WINDOW_SIZE])
#         packets.remove(packets[base:WINDOW_SIZE])
#     else:
#         window.append(packets[base:])
#         packets.remove(packets[base:])
#
#     for pkt in window:
#         sock.sendto(pkt, (UDP_IP, UDP_PORT))
#         #wait for ACK
#
#         while True:
#             data = conn.recv(BUFFER)
#             if not data: break
#             print "received data:", data
#             conn.send(data)
#         conn.close()










# open TCP connection to receiver



# create packets

# send packets in window

# wait certain interval

# wait for ACK

# if timer runs out before ACK, resend whole Window

# if you receive ACK for base packet, increase window by 1
    #if you receive ACK for

# log to log_file








# timestamp, source, destination, Sequence #, ACK #, and the flags,

# """
# % sender <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size> %
# sender file.txt 128.59.15.38 20000 20001 logfile.txt 1152
# Delivery completed successfully
# Total bytes sent = 1152
# Segments sent = 2 Segments retransmitted = 0 %
#
#
# but with a FIN request to signal the end of the transmission.
#
# You need to implement the 20?byte TCP header format, without options.
#
#
# The window_size is a parameter and window_size is measured in terms of the number of packets.
# Your sender should support variable window size, and it will be specified as the last parameter on command line.
# If no parameter is specified, the default window size value should be 1.
#
# The TCP checksum is computed over the TCP header and data; this does not quite
# correspond to the correct way of doing it (which includes parts of the IP header), but is close enough.
# If no parameter is specified, the default window size value should be 1.
# """





# # open UDP socket connection to proxy
#
#
# #tcp server code (Waiting for ACKS)
# TCP_IP = '127.0.0.1'
# TCP_PORT = 4444
# BUFFER = 1024
#
#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((TCP_IP, TCP_PORT))
#
# s.listen(1)
#
# conn, addr = s.accept()
#
# while True:
#     data = conn.recv(BUFFER)
#     if not data: break
#     print "received data:", data
#     conn.send(data)
# conn.close()


# split text file by 556 bytes

#
# for i in range(0, len(txt), 556):
#     packet_txt.append(txt[i: i+556])
# print "SIZE OF PACKET 0"
# print len(packet_txt[0])
#
# print len(packet_txt[1])

# print packet_txt


import socket, sys, struct



# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w

    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);

    #complement and mask to 4 byte short
    s = ~s & 0xffff

    return s

#create a raw socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
except socket.error , msg:
    print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

# tell kernel not to put in headers, since we are providing it, when using IPPROTO_RAW this is not necessary
# s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# now start constructing the packet
packet = '';

source_ip = socket.gethostbyname()
dest_ip = '192.168.1.1' # or socket.gethostbyname('www.google.com')

# ip header fields
ip_ihl = 5
ip_ver = 4
ip_tos = 0
ip_tot_len = 0  # kernel will fill the correct total length
ip_id = 54321   #Id of this packet
ip_frag_off = 0
ip_ttl = 255
ip_proto = socket.IPPROTO_TCP
ip_check = 0    # kernel will fill the correct checksum
ip_saddr = socket.inet_aton ( source_ip )   #Spoof the source ip address if you want to
ip_daddr = socket.inet_aton ( dest_ip )

ip_ihl_ver = (ip_ver << 4) + ip_ihl

# the ! in the pack format string means network order
ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)

# tcp header fields
tcp_source = 1234   # source port
tcp_dest = 80   # destination port
tcp_seq = 454
tcp_ack_seq = 0
tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
#tcp flags
tcp_fin = 0
tcp_syn = 1
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

user_data = 'Hello, how are you'

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
tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('H' , tcp_check) + pack('!H' , tcp_urg_ptr)

# final full packet - syn packets dont have any data
packet = ip_header + tcp_header + user_data






#Send the packet finally - the port specified has no effect
s.sendto(packet, (dest_ip , 0 ))    # put this in a loop if you want to flood the target
