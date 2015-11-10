README.txt


Size of packets


sender
#usage: sender <filename> <remote_IP> <remote_port> <ac_port_num> <log_filename> <window_size>

001
00


checksum append byte over for large files

Calculate RTO:

RFC --> RTO initially set to 3 seconds
RTT_Var --> 1.5 * RTT_AVG


receiver

QUESTIONS
-Does packet need to be exact size? Difference between length and size
-Can sequence number be 0, 1, 2, 3... or must it be seq # * size of packet?
-should I use fin flag for FIN signal, or just send a separate signal at the end

-How to calculate RTO
Factor in RTT for outliers
Use RTT to calculate average RTT

initialize RTO = 3 seconds
if RTT passes 2 seconds then increase RTO


-am I packing the tcp header correctly, psh
-how to account for checksum overflow
-do I have to use ack field in header or just send separate acks based off of sequence number


TODO
-construct all packets
-send packets that are in the window
-wait for acks/resend if necessary
-once acks are received
-account for overflow
-stdout
-cite binary tides






576 bytes

UDP sockets

20 byte header that is the same as header described in book.
so data section = 576-20bytes = 556 bytes



python struct module




Send python char over UDP socket will be considered 1 byte
