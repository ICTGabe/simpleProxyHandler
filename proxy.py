import sys
import socket
import threading
#HEXFILTER with string ASCII printable characters
HEX_FILTER = ''.join(
	[(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
	if isinstance(src, bytes): #piece of string to dump and put it into the word variable
		src = src.decode()
	results = list()
	for i in range(0, len(src), length): #translate build-in function to substitute the string
		word = str(src[i:i+length])
		printable = word.translate(HEX_FILTER)
		hexa = ' '.join([f'{ord(c):02X}' for c in word])
		hexwidth = length*3
		results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
	if show:
		for line in results:
			print(line)
	else:
		return results
	
def receive_from(connection):
	buffer = b"" #empty byte string
	connection.settimeout(10) #10 second time-out 
	try:
		while True: #loop to read response data into the buffer 
			data = connection.recv(4096) #set connection recv (4096 bit)
			if not data: #if there is no more data BREAK
				break
			buffer += data #buffer + data 
	except Exception as e:
		pass
	return buffer #return the buffer with inserted data

def request_handler(buffer):
	# perform packet modifications
	return buffer

def response_handler(buffer):
	#perform packet modifications
	return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
	remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #connect to remote host using standard values for tcp connection 
	remote_socket.connect((remote_host, remote_port)) #setting host and port

	if receive_first: #checking to make sure remote side doesn't initiate connection and request data
		remote_buffer = receive_from(remote_socket) #accepts connected socket object and perfoms a receive
		hexdump(remote_buffer)

	remote_buffer = response_handler(remote_buffer) #send received buffer to the local client
	if len(remote_buffer):
		print("[<==] Sending %d bytes to localhost." %len (remote_buffer))
		client_socket.send(remote_buffer)#send the received buffer to the local client

	while True: #continually read from the local client, process the data send it to the remote client
		local_buffer = receive_from(client_socket) #accepts connected socket object and perfoms a receive
		if len(local_buffer):
			line = "[==>] Received %d bytes from localhost." %len(local_buffer)
			print(line)
			hexdump(local_buffer)

			local_buffer = request_handler(local_buffer)
			remote_socket.send(local_buffer)
			print("[==>] Sent to remote.")
		
		remote_buffer = receive_from(remote_socket) #accepts connected socket object and perfoms a receive
		if len(remote_buffer):
			print("[<==] Received %d bytes from remote." %len(remote_buffer))
			hexdump(remote_buffer)

			remote_buffer = response_handler(remote_buffer)
			client_socket.send(remote_buffer)
			print("[<==] Sent to localhost.")

		if not len(local_buffer) or not len(remote_buffer):
			client_socket.close()
			remote_socket.close()
			print("[*] No more data. Closing connections.")
			break

	
