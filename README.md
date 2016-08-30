The program is a basic implementation of a distance-vector (RIP-like) protocol over UDP. Each node in the network runs an instance of the program. Each node, or router, listens for incoming routing messages on a given node and sends update messages to neighboring nodes designated on the command line. In this program, we are only using one socket to send and receive messages. Due to this, we can only handle IP addresses and not hostnames since we would have to create sockets for every node in the command line. Each router will send data every 5 seconds.

Packet format:
<IP address>:<Port>:<distance/weight>|<IP address>:<Port>:<distance/weight>|[…]

Usage:
python router.py <listen_port> <interface1> <interface2> […]

Sample:
python router.py 2000 128.59.15.38:2001:4 128.59.15.38:2002:6
python router.py 2001 128.59.15.38:2000:4 128.59.15.38:2002:1
python router.py 2002 128.59.15.38:2000:6 128.59.15.38:2001:1 128.59.15.38:2003:3
python router.py 2003 128.59.15.38:2002:3