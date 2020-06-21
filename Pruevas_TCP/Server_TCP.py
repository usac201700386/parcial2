import socket
import tqdm
import os
import time
import logging
#JDCP  estos datos se tienen que importar desde un archivo de texto plano
SERVER_HOST = "167.71.243.238" #host a conectar
SERVER_PORT = 9804#9804# numero de puerto a utlizar
BUFFER_SIZE = 64 *1024

#JDCP Configuracion inicial para logging. logging.DEBUG muestra todo.
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
    #JDCP se obtine la informacion del cliente que se conecto al servicio
    client_socket, address = servidor.accept() # datos el 
    #JDCP SE AVISA POR MEDIO DE LOGGING QUE SE HA CONECTADO AL SERVIDOR
    logging.debug(f"[+] {address} estado conectado")
    return servidor,client_socket,address

def Recp_TCP_Server(host='167.71.243.238',port=9804):
    #JDCP se obtiene todos los parametros y objetos de la funcion que levanta el servidor TCP
    server,cliente,direccion = est_servidor(host,port)
    #SE ESTA ATENTO A LA INFORMACION QUE SE RECIBE DEL TCP SOBRE EL TAMANO DEL ARCHIVO
    received = cliente.recv(BUFFER_SIZE).decode()
    SEPARATOR = "<SEPARATOR>"
    #SE ESTABLECE EL NOMBRE DEL ARCHIVO QUE SE ALMACENA EN EL servido
    filename, filesize = received.split(SEPARATOR)
   
    filename = 'Recp_server.wav'#os.path.basename(filename)
    #JDCP CONVERITR EL VALOR DEL TAMANO DE STRING A ENTERO
    filesize = int(filesize)

    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", total=1,unit="B", unit_scale=True, unit_divisor=0.1)
    with open(filename, "wb") as f:
        for i in progress:
            #JDCP LEE LA CANTIDA DE BYTES DEL TAMANO DEL ARCHIVO
            bytes_read = cliente.recv(filesize)
            
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                
                break
            # JDCP SE ESCRIBE EL EL ARCHIVO QUE SE ESTA RECIBIENDO
            f.write(bytes_read)
            
        progress.update(i)
            

    #JDCP SE CIERRA LA COMUNICACION CON EL CLIENTE
    cliente.close()
    #JDCP SE CIERRA EL SERVIDOR
    server.close()
def Envio_TCP_Server(host='167.71.243.238',port=9804):
    servidor,cliente,direccion= est_servidor(host,port)
    filename= 'Recp_server.wav'
    SEPARATOR = "<SEPARATOR>"
    filesize = os.path.getsize(filename)
    cliente.send(f"{filename}{SEPARATOR}{filesize}".encode())
    
    progress = tqdm.tqdm(range(filesize),f"Sending {filename}",total=1,miniters=0.01,mininterval=0.001 ,unit="B", unit_scale=False, unit_divisor=1024)
    with open(filename, "rb") as f:
        for i in progress:
            #JDCP SE LEE LOS BYTES DEL ARCHIVO DE AUDIO
            bytes_read = f.read(filesize)
            if not bytes_read:
                #JDCP ESTO SUCEDE CUANDO FINALIZA EL ENVIO 
            
                break
            #JDCP ESTO SUCEDE MINETRA SE ENVIA CADA BYTE DE AUDIO
            cliente.sendall(bytes_read)
           # JDCP SE ACTULIZA EL VALOR DE LA BARRA QUE SE ESTA MOSTRANDO
            progress.update(len(bytes_read))         
    # JDCP SE CORTA COMUNICACION CON EL CLIENTE Y SE CIERRA EL SERVIDOR TCP
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