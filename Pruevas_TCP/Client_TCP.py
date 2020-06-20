import socket
import tqdm
import os
import time
import logging


BUFFER_SIZE = 64*1024 # send 4096 bytes each time step
host = 'localhost'#'167.71.243.238'

port = 9800
#Configuracion inicial para logging. logging.DEBUG muestra todo.
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

def est_connect(host='167.71.243.238',port=9804):
    #JDCP se crea el socket a utilizar
    sock = socket.socket()
    #JDCP se indica se que esta intentando conectar al servidor
    logging.debug(f"[+] Intentando conectar al servidor y puerto {host}:{port}")
    sock.connect((host, port))
    # si no hay errores entonces se conecta 
    logging.debug("[+] Conectado con el servidor.")
    return sock
    

def Audio_create(filename='audio.wav',duracion=3):
    
    os.system('arecord -d '+str(duracion)+' -f U8 -r 8000 '+filename)
    #JDCP se obtiene el tamano del archivo de grabacion
    filesize = os.path.getsize(filename)
    return filename , filesize
    
def Envio_TCP_Client (filename='audio.wav',filesize=1024,host='167.71.243.238',port=9804):
 
    #se manda la informacion del comando FTR , destino y peso del archivo
    SEPARATOR = "<SEPARATOR>" # solamente servira para dierencia la informacion comandos 
    sock= est_connect(host,port)

    sock.send(f"{filename}{SEPARATOR}{filesize}".encode())
    # if comando ok 
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
            sock.sendall(bytes_read)
            #time.sleep(delay)
            # update the progress bar
            progress.update(len(bytes_read))         
    # close the socket
    sock.close()

def Recp_TCP_Client (host='167.71.243.238',port=9804):
    #JDCP ESTABLECIENDO COMUNICAICOND CON EL SERVIDOR PARA RECIBIR ARCHIVOS
    time.sleep(0.05)
    sock= est_connect(host,port)
    received = sock.recv(BUFFER_SIZE).decode()
    SEPARATOR = "<SEPARATOR>" 
    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = 'REB_CLIENTE.wav'#os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", total=1,unit="B", unit_scale=True, unit_divisor=0.1)
    with open(filename, "wb") as f:
        for i in progress:
            # read 1024 bytes from the socket (receive)
            bytes_read = sock.recv(filesize)
            
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                
                break
            #JDCP SE ESCRIBE EL ARCHVIO QUE ES RECIBIDO
            f.write(bytes_read)
           
        progress.update(i)
    #JDCP se desconecta de cliente TCP al recibir el archivo
    sock.close()

#nombre,tamano=Audio_create('audio.wav',5)

#Envio_TCP_Client(nombre,tamano,host,port)

while True:
    logging.debug('ingrese 1 para envio, 2 para recepcion')
    entrada = int(input('ingrese su seleccion: '))
    if (entrada ==1):
        nombre,tamano=Audio_create('audio.wav',5)
        Envio_TCP_Client(nombre,tamano,host,port)
    elif (entrada == 2):
        Recp_TCP_Client(host,port)   
    else:
        break