import paho.mqtt.client as mqtt
import logging
import socket
import tqdm
import os
import time
from globals import *

class Cliente(object):
    #DAHM Metodo constructor del objeto de la clase servidor
    def __init__(self, ip = HOST, portMQTT = MQTT_PORT, portTCP = TCP_HOST, user = MQTT_USUARIO, passwd = MQTT_KEY, x = mqtt.Client(clean_session=True)):
        self.ip = ip
        self.portMQTT = portMQTT
        self.portTCP = portTCP
        self.user = user
        self.passwd = passwd
        self.x = x

    #DAHM Configuracion inicial para que el servidor se vuelva subscriptor y publicador en el broker
    def configMQTT(self):
        client = self.x

        #Configuracion inicial de logging
        logging.basicConfig(
        level = logging.DEBUG, 
        format = '[%(levelname)s] (%(processName)-10s) %(message)s'
        )

        #Handler en caso suceda la conexion con el broker MQTT
        def on_connect(client, userdata, flags, rc): 
            connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
            logging.info(connectionText)

        #Handler en caso se publique satisfactoriamente en el broker MQTT
        def on_publish(client, userdata, mid): 
            publishText = "Publicacion satisfactoria"
            logging.debug(publishText)

        #Callback que se ejecuta cuando llega un mensaje al topic suscrito
        def on_message(client, userdata, msg):
            #Se muestra en pantalla informacion que ha llegado
            logging.info('mensaje recibido: ' + str(msg.payload))

        client.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
        client.on_message = on_message #Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
        client.on_publish = on_publish
        client.username_pw_set(self.user, self.passwd) #Credenciales requeridas por el broker

    #DAHM metodos del servidor
    def subscripcion(self, topico, qos=0):
        client = self.x
        client.subscribe((topico, qos))
        client.loop_start()

    def publicar(self, topico, mensaje, qos=0):
        client = self.x
        client.publish(topico, mensaje, qos, retain = False)

    def  conectar(self):
        client = self.x
        client.connect(host = self.ip, port = self.portMQTT) #DAHM Conectar al servidor remoto

    def desconectar(self):
        client = self.x
        client.disconnect()
    #-----------------------------------------------------------------------------------
    #------------JDCP TCP----------------
    #JDCP creando el TCP socket
    def est_connect(self):
        #JDCP se crea el socket a utilizar
        sock = socket.socket()
        #JDCP se indica se que esta intentando conectar al servidor
        logging.debug(f"[+] Intentando conectar al servidor y puerto {host}:{port}")
        sock.connect((host= self.ip, sel.portTCP))
        # si no hay errores entonces se conecta 
        logging.debug("[+] Conectado con el servidor.")
        return sock
    def Envio_TCP_Client (self):
        filename='audio.wav'
        filesize=os.path.getsize(filename)
        #se manda la informacion del comando FTR , destino y peso del archivo
        SEPARATOR = "<SEPARATOR>" # solamente servira para dierencia la informacion comandos 
        sock= est_connect(host= self.ip ,port= self.portTCP)

        sock.send(f"{filename}{SEPARATOR}{filesize}".encode())
        filesize=int(filesize)
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

   def Recp_TCP_Client (self):
        #JDCP ESTABLECIENDO COMUNICAICOND CON EL SERVIDOR PARA RECIBIR ARCHIVOS
        time.sleep(0.05)
        sock= est_connect(host=self.ip,port=self.portTCP)
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
        logging.info('inicia reproduccion')
        os.system('aplay '+filename)
        logging.info('termina reproduccion')
        #JDCP se desconecta de cliente TCP al recibir el archivo
        sock.close()
    
    #-----------------------------------------------------------------------------------


def Audio_create(filename='audio.wav',duracion=3):
    logging.info('inicia grabacion')
    os.system('arecord -d '+str(duracion)+' -f U8 -r 8000 '+filename)
    logging.info('termina grabacion')
    #JDCP se obtiene el tamano del archivo de grabacion
    filesize = os.path.getsize(filename)
    return filename , filesize

