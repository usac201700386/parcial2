import socket
import tqdm
import os
import time
#delay=0.0025
# device's IP address
SERVER_HOST = "167.71.243.238"
SERVER_PORT = 9804#5001
# receive 4096 bytes each time
BUFFER_SIZE = 64 *1024

SEPARATOR = "<SEPARATOR>"

# create the server socket
# TCP socket
s = socket.socket()

s.bind((SERVER_HOST, SERVER_PORT))

s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

client_socket, address = s.accept() 
# if below code is executed, that means the sender is connected
print(f"[+] {address} is connected.")

received = client_socket.recv(BUFFER_SIZE).decode()
filename, filesize = received.split(SEPARATOR)
# remove absolute path if there is
filename = 'recibido.wav'#os.path.basename(filename)
# convert to integer
filesize = int(filesize)


progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", total=1,unit="B", unit_scale=True, unit_divisor=0.1)
with open(filename, "wb") as f:
    for i in progress:
        # read 1024 bytes from the socket (receive)
        bytes_read = client_socket.recv(filesize)
        
        if not bytes_read:    
            # nothing is received
            # file transmitting is done
            
            break
        # write to the file the bytes we just received
        f.write(bytes_read)
        #time.sleep(delay)
        # update the progress bar
    progress.update(i)
        

# close the client socket
client_socket.close()
# close the server socket
s.close()