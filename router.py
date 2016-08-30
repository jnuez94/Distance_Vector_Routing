import sys
import signal
import socket
import time
import threading
import datetime

UDP_IP = ""
SLEEP_TIME = 5
NET_GRAPH = {} # keeps track of every node except for the host node
NEIGH_NODE = {} # keeps track of neighboring nodes

# handling control+c gracefully
def exit_handler(signal, frame):
	 print 'Exiting...'
	 sys.exit(0)

# creating udp socket
def create_socket(args):
	nodeSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	global UDP_IP
	UDP_IP = socket.gethostbyname(socket.gethostname())
	nodeSock.bind((UDP_IP, args))
	print 'node starting up on %s:%d' % (UDP_IP, args)
	return nodeSock

# creating routing table
def routing_table(args):
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	date, tstamp = st.split(' ')
	table = "-------------- Routing Table ---------------\n"
	table += "Node %s:%s @ %s\n" % (UDP_IP, args, tstamp)
	table += "host\t\tport\tdistance\tinterface\n"
	for (ip, port), node in NET_GRAPH.items():
		table += "%s\t%d\t%d\t\t%d\n" % (ip, port, node[0], node[1])
	table += "----------- End Routing Table --------------\n\n"
	return table

# updating routing table based on message received from neighboring nodes
def update_table(sock, listen_port):
	while True: 
		info, (ip, port) = sock.recvfrom(2048)
		# print info
		table = info.split('|')
		for i in table:
			if i == '':
				print "receiving empty table... from %s:%d\n" % (ip, port)
				continue
			(node_ip, node_port, node_distance) = i.split(':')
			if node_ip != UDP_IP or node_port != listen_port:
				try:
					# print i
					(n_distance, n_interface) = NEIGH_NODE[(ip, port)]
					(prev_distance, prev_interface) = NET_GRAPH[(node_ip, int(node_port))]
					sum_distance = int(n_distance)+int(node_distance)
					# print "previous distance: %s" % (prev_distance)
					# print "new path distance: %d" % (sum_distance)
					if int(prev_distance) > sum_distance:
						NET_GRAPH[(node_ip, int(node_port))] = (sum_distance, n_interface)
				except:
					try:
						(n_distance, n_interface) = NEIGH_NODE[(ip, int(port))]
						NET_GRAPH[(node_ip, int(node_port))] = (n_distance+int(node_distance), n_interface)
					except:
						print "Unreachable node... \n\n"
		print routing_table(listen_port)

# handling sending distance informations
def send_distanceInfo(sock):
	info = ''
	for (ip, port), node in NET_GRAPH.items():
		info += "%s:%d:%d|" % (ip, port, node[0])
	for (ip, port), node in NEIGH_NODE.items():
		sock.sendto(info, (ip, port))

# handling command line arguments and multithreading update and sending message
def main(args):
	if (len(args) < 3):
		message = 'usage: %s <listen_port> <interface1> <interface2> [...]' % (args[0])
		sys.exit(message)
		
	sock = create_socket(int(args[1]))

	for i in range(2, len(args)):
		nodeInfo = args[i].split(':')
		ip = nodeInfo[0]
		port = int(nodeInfo[1])
		distance = int(nodeInfo[2])
		interface = i - 1
		NEIGH_NODE[(ip, port)] = (distance, interface)
		NET_GRAPH[(ip, port)] = (distance, interface)

	print routing_table(args[1])

	update = threading.Thread(target=update_table, args=(sock, args[1]))
	update.daemon = True
	update.start()
	
	while True:
		send_distanceInfo(sock)
		time.sleep(SLEEP_TIME)

	sys.exit(sock.close())

if __name__ == '__main__':
	signal.signal(signal.SIGINT, exit_handler)
	main(sys.argv)