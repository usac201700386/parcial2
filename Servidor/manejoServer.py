import paho.mqtt.client as mqtt
import socket
import tqdm
import logging
import os
from globals import *

class Servidor():
    #----------------------------------------------   DAHM MQTT   -------------------------------------------------
    #DAHM Metodo constructor del objeto de la clase servidor, este metodo toma las constantes globales necesarias para:
    #DAHM crear una instancia del tipo mqtt.Client, una de tipo socket y los archivos de texto donde se va a llevar el
    #DAHM control de usuarios y salas.
    def __init__(self, ip = HOST, portMQTT = MQTT_PORT, portTCP = TCP_HOST, 
                user = MQTT_USUARIO, passwd = MQTT_KEY, qos = QOS_LEVEL,
                x = mqtt.Client(clean_session=True),
                usuarios = USERS_FILE, salas = ROOMS_FILE,
                grupo = GROUP_ID):
        #DAHM Se pasan los parametros de la clase los cuales son constantes de globals.py
        self.ip = ip
        self.portMQTT = portMQTT
        self.portTCP = portTCP
        self.user = user
        self.passwd = passwd
        self.qos = qos
        #DAHM Llamamos x a la instancia de la clase mqtt.Client
        self.x = x
        #DAHM Estos son los archivos de texto donde se lleva el control de las salas y los usuarios
        self.usuarios = usuarios
        self.salas = salas
        #DAHM Datos del grupo
        self.grupo = grupo
        

    #DAHM Configuracion inicial para que el servidor se vuelva subscriptor y publicador en el broker
    def configMQTT(self):
        client = self.x

        #DAHM Se configura el logging para que muestre todo desde nivel DEBUG hacia arriba
        logging.basicConfig(
        level = logging.DEBUG, 
        format = '[%(levelname)s] (%(processName)-10s) %(message)s'
        )

        #DAHM La funcion Handler que atiende el evento on_connect (cuando se logra conectar al broker mosquitto)
        def on_connect(client, userdata, flags, rc): 
            connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
            logging.info(connectionText)

        #DAHM La funcion Handler que atiende el evento on_publish (cuando se publica en algun topic)
        def on_publish(client, userdata, mid): 
            publishText = "Publicacion satisfactoria"
            logging.debug(publishText)

        #DAHM La funcion Handler que atiende el evento on_message (cuando llega algun mensaje a algun topic que esta subscrito el servidor)
        def on_message(client, userdata, msg):
            #Se muestra en pantalla informacion que ha llegado
            logging.info('mensaje recibido: ' + str(msg.payload) + ' del topico: ' + str(msg.topic))

        #DAHM Se le asignan estos handlers a la instancia x
        client.on_connect = on_connect 
        client.on_message = on_message 
        client.on_publish = on_publish

        #DAHM Se configura el usuario y la contraseña de la cuenta del broker al cual nos queremos conectar
        client.username_pw_set(self.user, self.passwd) 

    #DAHM metodos del servidor
    def subscripcion(self):
        client = self.x
        topicos_l = self.topicos()
        #DAHM Ya que se tiene una lista de tuplas con todos los elementos de los archivos de texto se subscribe el servidor
        client.subscribe(topicos_l[:])
        #DAHM Se comienza el thread demonio que ve si llega algun mensaje a alguno de estos topicos
        client.loop_start()

    def topicos(self):
        topicos_lista = []
        #DAHM Ahora que ya hay certeza de que existen los archivos se ponen en modo lectura.
        archivo_usuarios = open(self.usuarios, 'r')
        archivo_salas = open(self.salas, 'r')
        #DAHM Un bucle separa las comas de cada linea del archivo usuarios.
        for usuario in archivo_usuarios:
            t = usuario.split(',')
            topico = ('usuarios' + '/' + t[0], self.qos)
            topicos_lista.append(topico)
        archivo_usuarios.close()
        #DAHM Este otro bucle toma cada linea del archivo salas y guarda cada topico en el formato indicado
        for sala in archivo_salas:
            sala = sala.split('\n')
            topico = ('salas' + '/' + self.grupo + '/' + sala[0][2:], self.qos)
            topicos_lista.append(topico)
        archivo_salas.close()
        #DAHM Se agrega comandos a la lista de tuplas
        topicos_lista.append(('comandos/' + self.grupo + '/#', self.qos))

        return topicos_lista


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
    def est_servidor(self):
        #JDCP SE CREAR EL OBJETO TIPO SOCKET
        servidor = socket.socket()
        #JDCP SE LEVANTA EL SERVIDOR TCP LISTO PARA ESCUCHA
        servidor.bind((self.ip,self.portTCP))

        servidor.listen(5)
        logging.debug(f"[*] Esperando conexion en {self.ip}:{self.portTCP}")
        #JDCP se obtine la informacion del cliente que se conecto al servicio
        client_socket, address = servidor.accept() # datos el 
        #JDCP SE AVISA POR MEDIO DE LOGGING QUE SE HA CONECTADO AL SERVIDOR
        logging.debug(f"[+] {address} estado conectado")
        return servidor,client_socket,address

    def Recp_TCP_Server(self):
        #JDCP se obtiene todos los parametros y objetos de la funcion que levanta el servidor TCP
        server,cliente,_ = self.est_servidor()
        #SE ESTA ATENTO A LA INFORMACION QUE SE RECIBE DEL TCP SOBRE EL TAMANO DEL ARCHIVO
        received = cliente.recv(64*1024).decode()
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

        servidor,cliente,_= self.est_servidor()
        filename= 'Recp_server.wav'
        SEPARATOR = "<SEPARATOR>"
        filesize = os.path.getsize(filename)
        cliente.send(f"{filename}{SEPARATOR}{filesize}".encode())
        
        progress = tqdm.tqdm(range(filesize),f"Sending {filename}",total=1,miniters=0.01,mininterval=0.001 ,unit="B", unit_scale=False, unit_divisor=1024)
        with open(filename, "rb") as f:
            for _ in progress:
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

    






    
    



