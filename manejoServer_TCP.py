import paho.mqtt.client as mqtt
import logging
import socket
import tqdm
import os
import time
from globals import *

class Servidor():
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
    def est_servidor(self):
        #JDCP SE CREAR EL OBJETO TIPO SOCKET
        servidor = socket.socket()
        #JDCP SE LEVANTA EL SERVIDOR TCP LISTO PARA ESCUCHA
        servidor.bind((host = self.ip,port = self.portTCP))

        servidor.listen(5)
        logging.debug(f"[*] Esperando conexion en {SERVER_HOST}:{SERVER_PORT}")
        #JDCP se obtine la informacion del cliente que se conecto al servicio
        client_socket, address = servidor.accept() # datos el 
        #JDCP SE AVISA POR MEDIO DE LOGGING QUE SE HA CONECTADO AL SERVIDOR
        logging.debug(f"[+] {address} estado conectado")
        return servidor,client_socket,address

    def Recp_TCP_Server(self):
        #JDCP se obtiene todos los parametros y objetos de la funcion que levanta el servidor TCP
        server,cliente,direccion = self.est_servidor()
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
        
    def Envio_TCP_Server(self):

        servidor,cliente,direccion= self.est_servidor()
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
    
    #-----------------------------------------------------------------------------------






    
    



