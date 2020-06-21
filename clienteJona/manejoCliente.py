import paho.mqtt.client as mqtt
import logging
import socket
import tqdm
import os
import time
from globals import *

class Cliente(object):
    #DAHM ------------------------------------------    DAHM MQTT   ----------------------------------------------
    #DAHM Metodo constructor del objeto de la clase cliente que toma como parametros las constantes del archivo
    #DAHM globals.py, toma todos los parametros necessarios para crear una instancia de mqtt.Client y una de socket
    #DAHM tambien toma como parametros los archivos de texto a los cuales se va a subscribir el cliente y el qos.  
    def __init__(self, ip = HOST, portMQTT = MQTT_PORT, portTCP = TCP_HOST,
                user = MQTT_USUARIO, passwd = MQTT_KEY, qos = QOS_LEVEL,
                x = mqtt.Client(clean_session=True),
                usuario = USER_FILE, salas = ROOMS_USER_FILE,
                grupo = GROUP_ID):
        #DAHM atributos de la clase servidor para crear instancia de mqtt.Client y de socket
        self.ip = ip
        self.portMQTT = portMQTT
        self.portTCP = portTCP
        self.user = user
        self.passwd = passwd
        self.qos = qos
        #DAHM la instancia tambien es un atributo sobre el cual se trabaja todo el protocolo MQTT
        self.x = x
        #DAHM Estos son los archivos de texto donde se lleva el control de las salas y del usuario
        self.usuario = usuario
        self.salas = salas
        #DAHM Datos del grupo
        self.grupo = grupo

    #DAHM Configuracion inicial para que el servidor se vuelva subscriptor y publicador en el broker
    def configMQTT(self):
        client = self.x

        #DAHM Se configura el logging en modo DEBUG para observar mensajes desde este nivel
        logging.basicConfig(
        level = logging.DEBUG, 
        format = '[%(levelname)s] (%(processName)-10s) %(message)s'
        )

        #DAHM Funcion handler que configura el evento on_connect (cuando se logra conectar al broker el cliente)
        def on_connect(client, userdata, flags, rc): 
            connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
            logging.info(connectionText)

        #DAHM Funcion handler que configura el evento on_publish (cuando se logra publicar con exito en el topico seleccionado)
        def on_publish(client, userdata, mid): 
            publishText = "Publicacion satisfactoria"
            logging.debug(publishText)

        #DAHM Funcion handler que configura el evento on_message (cuando llega un mensaje a alguno de los topicos que se esta subscrito)
        def on_message(client, userdata, msg):
            logging.info('mensaje recibido: ' + str(msg.payload) + 'del topico: ' + str(msg.topic))

        #DAHM Se le atribuyen a nuestra instancia estos handlers
        client.on_connect = on_connect 
        client.on_message = on_message 
        client.on_publish = on_publish
        #DAHM le seteamos el usuario y contraseña de la cuenta del broker mosquitto
        client.username_pw_set(self.user, self.passwd) 

    #DAHM metodos del servidor
    def subscripcion(self):
        client = self.x
        topicos_l = self.topicos()
        #DAHM Ya que se tiene una lista de tuplas con todos los elementos de los archivos de texto se subscribe el cliente
        client.subscribe(topicos_l[:])
        #DAHM Se comienza el thread demonio que ve si llega algun mensaje a alguno de estos topicos
        client.loop_start()

    def topicos(self):
        topicos = []
        #DAHM Se abren los archivos en modo lectura
        archivo_usuario = open(self.usuario, 'r')
        archivo_salas = open(self.salas, 'r')
        #DAHM Se lee la primera linea del archivo usuario 
        usuario = archivo_usuario.readline()
        #DAHM Se crean las tuplas con los topicos del usuario y su qos
        topicos.append(('comandos/' + self.grupo + '/' + usuario, self.qos))
        topicos.append(('usuarios/' + usuario, 0))
        #DAHM cerramos el archivo
        archivo_usuario.close()

        #DAHM Se recorre el archivo salas con un bucle
        for sala in archivo_salas:
            #DAHM quitamos los caracteres de nueva linea de cada linea
            sala = sala.split('\n')
            #DAHM se crea una tupla con el formato de salas y el qos
            topico = ('salas' + '/' + self.grupo + '/' + sala[0][2:], self.qos)
            topicos.append(topico)
        #DAHM cerramos el archivo
        archivo_salas.close()

        #DAHM esta funcion retorna una lista de tuplas con los topicos a los que se subscribe el cliente y el qos
        return topicos

    #DAHM Esta funcion es la analogia de publish de paho
    def publicar(self, topico, mensaje):
        client = self.x
        client.publish(topico, mensaje, self.qos, retain = False)

    #DAHM conecta al broker la instancia creada en __init__
    def  conectar(self):
        client = self.x
        client.connect(host = self.ip, port = self.portMQTT) #DAHM Conectar al servidor remoto

    #DAHM Desconecta del broker la instancia creada en __init__
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
        logging.debug(f"[+] Intentando conectar al servidor y puerto {self.ip}:{self.portTCP}")
        sock.connect((self.ip, self.portTCP))
        # si no hay errores entonces se conecta 
        logging.debug("[+] Conectado con el servidor.")
        return sock
    def Envio_TCP_Client (self):
        filename='audio.wav'
        filesize=os.path.getsize(filename)
        #se manda la informacion del comando FTR , destino y peso del archivo
        SEPARATOR = "<SEPARATOR>" # solamente servira para dierencia la informacion comandos 
        sock= self.est_connect()

        sock.send(f"{filename}{SEPARATOR}{filesize}".encode())
        filesize=int(filesize)
        progress = tqdm.tqdm(range(filesize),f"Sending {filename}",total=1,miniters=0.01,mininterval=0.001 ,unit="B", unit_scale=False, unit_divisor=1024)
        with open(filename, "rb") as f:
            for _ in progress:
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
        sock= self.est_connect()
        received = sock.recv(64*1024).decode()
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

#---------------------solo para prueba-----------------------------
'''Audio_create()

cli=Cliente()

cli.Envio_TCP_Client()
time.sleep(5)
cli.Recp_TCP_Client'''
#-------------------------------------------------------------------