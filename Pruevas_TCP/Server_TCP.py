import socket
import tqdm
import os
import time
import logging
#JDCP  estos datos se tienen que importar desde un archivo de texto plano
SERVER_HOST = "167.71.243.238" #host a conectar
SERVER_PORT = 9804#9804# numero de puerto a utlizar
BUFFER_SIZE = 64 *1024
#este carcter es propio del prama para obtener informacion

#Configuracion inicial para logging. logging.DEBUG muestra todo.
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )
#JDCP creando el TCP socket
def est_servidor(host='167.71.243.238',port=9804):
    #JDCP SE CREAR EL OBJETO TIPO SOCKET
    servidor = socket.socket()
    #JDCP SE LEVANTA EL SERVIDOR TCP LISTO PARA ESCUCHA
    servidor.bind((host,port))

    servidor.listen(5)
    logging.debug(f"[*] Esperando conexion en {SERVER_HOST}:{SERVER_PORT}")

    client_socket, address = servidor.accept() # datos el 
    # if below code is executed, that means the sender is connected
    logging.debug(f"[+] {address} estado conectado")
    return servidor,client_socket,address

def Recp_TCP_Server(host='167.71.243.238',port=9804):

    server,cliente,direccion = est_servidor(host,port)

    received = cliente.recv(BUFFER_SIZE).decode()
    SEPARATOR = "<SEPARATOR>"

    filename, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = 'Recp_server.wav'#os.path.basename(filename)
    # convert to integer
    filesize = int(filesize)

    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", total=1,unit="B", unit_scale=True, unit_divisor=0.1)
    with open(filename, "wb") as f:
        for i in progress:
            # read 1024 bytes from the socket (receive)
            bytes_read = cliente.recv(filesize)
            
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
    cliente.close()
    # close the server socket
    server.close()
def Envio_TCP_Server(host='167.71.243.238',port=9804):
    servidor,cliente,direccion= est_servidor(host,port)
    filename= 'Recp_server.wav'
    SEPARATOR = "<SEPARATOR>"
    filesize = os.path.getsize(filename)
    cliente.send(f"{filename}{SEPARATOR}{filesize}".encode())
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
            cliente.sendall(bytes_read)
            #time.sleep(delay)
            # update the progress bar
            progress.update(len(bytes_read))         
    # close the socket
    cliente.close()
    servidor.close()
while True:
    logging.debug('ingrese 1 para recibir, 2 para enviar')
    entrada = int(input('ingrese su seleccion: '))
    if (entrada ==1):
        Recp_TCP_Server(SERVER_HOST,SERVER_PORT)
    elif (entrada == 2):
        Envio_TCP_Server(SERVER_HOST,SERVER_PORT)
    else:
        break