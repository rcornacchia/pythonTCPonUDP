README.txt



Copyright:
I used TCP_packet creation from the following site:
http://www.binarytides.com/raw-socket-programming-in-python-linux/

Professor sanctioned this use


I tested with the following commands, run in this order:

1) ./newudpl -isofia:3333 -odelhi:7766 -s50 -d2.004 -L7 -B5 -O9

2) python sender.py words.txt vanilla 41192 39832 sender_log.txt 3

3) python receiver.py file.txt 7766 128.59.15.30 39832 receiver_log.txt





a) TCP Header:
From RFC 793

0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |          Source Port          |       Destination Port        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                        Sequence Number                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Acknowledgment Number                      |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |  Data |           |U|A|P|R|S|F|                               |
   | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
   |       |           |G|K|H|T|N|N|                               |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |           Checksum            |         Urgent Pointer        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Options                    |    Padding    |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                             data                              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

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



b) States

Sender:
    On startup, it only enters SENDING STATE after receiving a connection:
    NO_TCP_CONNECTION -------> SENDING STATE

    after sending a message:
    SENDING STATE -------> RECEIVING STATE

    after receiving an ACK or Timeout:
    RECEIVING STATE -------> SENDING STATE

Receiver:

    On startup, it enters RECEIVING STATE after receiving a connection:
    NO_TCP_CONNECTION -------> RECEIVING STATE

    after receiving a message:
    RECEIVING STATE -------> SEND_ACK

    after sending an ACK:
    SEND_ACK ----> RECEIVING STATE

c) The loss recovery Mechanism

I used a simple Go-Back-N with a sliding window.
The sender will send all the packets in a window and wait for acks.
It will only slide the window, once it receives an ACK for the base packet.
The base packet is the one with the lowest seq_number.
If a timeout occurs it will resend all of the packets.

If it receives an ACK it will send the next window of packets.

After extensive testing on CLIC, the program runs as specified in the instructions.
I encountered a lot of trouble once I started to incorporate the proxy, but I've
worked out the kinks, and the app works well now. :)


-TCP Packet size = 576
    -20 byte tcp_header + 556 byte data segment
    -RFC --> RTO initially set to 3 seconds
        -If RTT comes within 1 second of the RTO, then the RTO will be
        increased

HOW TO RUN:
1) sender is run first
#usage: sender <filename> <remote_IP> <remote_port> <ac_port_num>
<log_filename> <window_size>

2) newudpl is run

3) receiver is run



First, the sender and receiver establish a tcp connection.
Then, the sender parses the text file into packets.
After, it starts to send the packages via UDP.
When the receiver gets a packet, it first unpacks it, then checks it
checksum.
If correct and in order, it will send an ACK to the sender via TCP.
The sender will unpack the ACK and adjust the window accordingly.




The checksum accounts for large numbers of packets, by using modulus
to ensure a small checksum number.


Specify to stdout works as described in the specifications.
Use stdout as the file and both the sender and receiver will print the log
file to console.


TESTING:

I tested with the following commands, run in this order:

1) ./newudpl -isofia:3333 -odelhi:7766 -s50 -d2.004 -L7 -B5 -O9
2) python sender.py words.txt vanilla 41192 39832 sender_log.txt 3
3) python receiver.py file.txt 7766 128.59.15.30 39832 receiver_log.txt




SENDER output:
Delivery completed successfully
Total bytes sent = 6336
Segments sent = 11
Segments retransmitted = 4


newudpl proxy output:
rlc2160@vanilla:~/x/pythonTCPonUDP/newudpl-1.4$ ./newudpl
-isofia:3333 -odelhi:7766 -s50 -d2.004 -L7 -B5 -O9

Network Emulator With UDP Link
Copyright (c) 2001 by Columbia University; all rights reserved

Link established:
sofia.clic.cs.columbia.edu(128.59.15.30)/3333 ->
 vanilla(128.59.10.226)/41192
   /41193 ->
             delhi.clic.cs.columbia.edu(128.59.15.41)/7766

emulating speed  : 50(kb/s)
delay            : 2.004000(sec)
ether net        : 10M(b/s)
queue buffer size: 8192(bytes)

error rate
random packet loss: 7(1/100 per packet)
bit error         : 5(1/100000 per
bit)
out of order      : 9(1/100 per
packet)


Receiver output:
Delivery completed successfully


sender_log.txt

SENDER_LOG:i
timestamp source    destination   Sequence #  ACK #   RTT
05:26:24  vanilla   128.59.15.33  0           ACK#0   0.002277135849
05:26:24  vanilla   128.59.15.33  1           ACK#1   0.00428605079651
05:26:24  vanilla   128.59.15.33  2           ACK#2   0.0044949054718
05:26:27  vanilla   128.59.15.33  3           ACK#3   0.00101709365845
05:26:27  vanilla   128.59.15.33  4           ACK#4   0.00167608261108
05:26:27  vanilla   128.59.15.33  5           ACK#5   0.0017101764679
05:26:30  vanilla   128.59.15.33  6           ACK#6   0.00132203102112
05:26:30  vanilla   128.59.15.33  7           ACK#7   0.00366497039795
05:26:30  vanilla   128.59.15.33  8           ACK#8   0.00370001792908
05:26:30  vanilla   128.59.15.33  9           ACK#9   0.0016610622406
05:26:30  vanilla   128.59.15.33  10          ACK#10  0.00022292137146


RECEIVER_LOG:
timestamp source  destination   Sequence #  ACK
19:22:02  delhi   128.59.15.30  1           ACK#1
19:22:08  delhi   128.59.15.30  0           ACK#0
19:22:08  delhi   128.59.15.30  1           ACK#1
19:22:08  delhi   128.59.15.30  2           ACK#2
19:22:14  delhi   128.59.15.30  3           ACK#3
19:22:14  delhi   128.59.15.30  4           ACK#4
19:22:14  delhi   128.59.15.30  5           ACK#5
