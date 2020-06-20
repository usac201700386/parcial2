import socket
import tqdm
import os
import time
#delay= 0.0025
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 64*1024 # send 4096 bytes each time step
host = '167.71.243.238'#"localhost"
# the port, let's use 5001
port = 9804
# the name of file we want to send, make sure it exists
#filename = "texto.txt"
# get the file size
duracion=3
filename='audio.wav'
os.system('arecord -d '+str(duracion)+' -f U8 -r 8000 '+filename)

filesize = os.path.getsize(filename)

# create the client socket
s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

s.send(f"{filename}{SEPARATOR}{filesize}".encode())

progress = tqdm.tqdm(range(filesize),f"Sending {filename}",total=1,miniters=0.01,mininterval=0.001 ,unit="B", unit_scale=False, unit_divisor=1024)
with open(filename, "rb") as f:
    for i in progress:
        # read the bytes from the file
        bytes_read = f.read(filesize)
        
        if not bytes_read:
            # file transmitting is done
           
            break
        # we use sendall to assure transimission in 
        # busy networks
        s.sendall(bytes_read)
        #time.sleep(delay)
        # update the progress bar
        progress.update(len(bytes_read))
        
        
# close the socket
s.close()