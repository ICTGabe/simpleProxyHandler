import sys
import socket
import threading

# HEXFILTER with string ASCII printable characters
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range (256)])

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):              # Piece of string to dump and put it into the word variable
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):    # Translate build-in function to substitute the string
        word = str(src[i:i+length])
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append(f'{i:04X} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results
    
def receive_from(connection):
    buffer = b""                            # Empty byte string
    connection.settimeout(5)                # 5 Second time-out
    try:
        while True:                         # Loop to read response data into the buffer
            data = connection.recv(4096)    # Set connection recv (4096 bit)
            if not data:                    # If there is no more data BREAK
                break
            buffer += data                  # Buffer adds data
    except Exception as e:
        pass 
    return buffer                           # Return the buffer with inserted data

def request_handler(buffer):
    # Perform packet modifications (Optional)
    return buffer

def response_handler(buffer):
    # Perform packet modifications, for example: fuzzing tasks and checks for authentication
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):  # Connect to a remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Define TCP connection using AF_INET and SOCK_STREAM
    remote_socket.connect((remote_host,remote_port))                        # Check for first initiate connection to remote side and request data before going in the main loop
    remote_buffer = b""                                                     # Define remote_buffer outside the if block and initialize it with an empty value
    if receive_first:                                                       # Server daemons will expect you to do this
        remote_buffer = receive_from(remote_socket)                         # Accepts connected socket object and performs a receive 
        hexdump(remote_buffer)                                              # Sends remote_buffer value to hexdump for decoding 
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):                                                  # If length of remote_buffer 
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)                                   # Sends remote_buffer to client_socket
    while True:                                                             # Setup loop for continually read from the local client, process the data and send it
        local_buffer = receive_from(client_socket)                          # Giving local_buffer the value of the client_socket
        if len(local_buffer):                                               
            line = "[==>]Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)                                           # Send local_buffer to hexdump

            local_buffer = request_handler(local_buffer)                    # Send local_buffer to request_handler
            remote_socket.send(local_buffer)                                # Socket send local_buffer 
            print("[==>] Sent to remote. ")
        remote_buffer = receive_from(remote_socket)                         # Receive packet from remote_socket
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)                                          # Send remote_buffer to hexdump

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)                               # Send remote_buffer to client_socket
            print("[<==] Sent to localhost.")
        if not len(local_buffer) or not len(remote_buffer):                 # If there is no data close both the local and remote sockets and break out of the loop
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

def server_loop(local_host, local_port,
                remote_host,remote_port, receive_first):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)               # Server loop function creates a socket               
    try:
        server.bind((local_host,local_port))                                # Binds to local hosts and listens
    except Exception as e:
        print('problem on bind: %r' % e)
        print("[!!] Failed to listen on %s:%d" % (local_host,local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
    print("[*] Listening on %s:%d" % (local_host,local_port))
    server.listen(5)
    while True:                                                             # Main loop 
        client_socket, addr = server.accept()
        # Print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # Start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket,remote_host,
            remote_port,receive_first))
        proxy_thread.start()
            
def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] ", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]
    
    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()

    





    
