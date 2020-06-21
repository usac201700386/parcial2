import paho.mqtt.client as mqtt
import logging
from globals import *

class Servidor():
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
        topicos = []
        #DAHM Ahora que ya hay certeza de que existen los archivos se ponen en modo lectura.
        archivo_usuarios = open(self.usuarios, 'r')
        archivo_salas = open(self.salas, 'r')
        #DAHM Un bucle separa las comas de cada linea del archivo usuarios.
        for usuario in archivo_usuarios:
            t = usuario.split(',')
            topico = ('usuarios' + '/' + t[0], self.qos)
            topicos.append(topico)
        archivo_usuarios.close()
        #DAHM Este otro bucle toma cada linea del archivo salas y guarda cada topico en el formato indicado
        for sala in archivo_salas:
            sala = sala.split('\n')
            topico = ('salas' + '/' + self.grupo + '/' + sala[0][2:], self.qos)
            topicos.append(topico)
        archivo_salas.close()
        #DAHM Ya que se tiene una lista de tuplas con todos los elementos de los archivos de texto se subscribe el servidor
        client.subscribe(topicos[:])
        #DAHM Se comienza el thread demonio que ve si llega algun mensaje a alguno de estos topicos
        client.loop_start()

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

    






    
    



