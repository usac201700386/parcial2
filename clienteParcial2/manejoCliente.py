import paho.mqtt.client as mqtt
import logging
import os
import threading
from globals import *

class Cliente(object):
    #DAHM ------------------------------------------    DAHM MQTT   ----------------------------------------------
    #DAHM Metodo constructor del objeto de la clase cliente que toma como parametros las constantes del archivo
    #DAHM globals.py, toma todos los parametros necessarios para crear una instancia de mqtt.Client
    #DAHM tambien toma como parametros los archivos de texto a los cuales se va a subscribir el cliente y el qos.  
    def __init__(self, ip = HOST, portMQTT = MQTT_PORT,
                user = MQTT_USUARIO, passwd = MQTT_KEY, qos = QOS_LEVEL,
                x = mqtt.Client(clean_session=True),
                usuario = USER_FILE, salas = ROOMS_USER_FILE,
                grupo = GROUP_ID, direccion = FILENAME_R):
        #DAHM atributos de la clase servidor para crear instancia de mqtt.Client
        self.ip = ip
        self.portMQTT = portMQTT
        self.user = user
        self.passwd = passwd
        self.qos = qos
        #DAHM la instancia tambien es un atributo sobre el cual se trabaja todo el protocolo MQTT
        self.x = x
        #DAHM Estos son los archivos de texto donde se lleva el control de las salas y del usuario
        self. usuario = usuario
        self.salas = salas
        #DAHM Datos del grupo
        self.grupo = grupo
        #DAHM Parametros para manejar el audio
        self.direccion = direccion

    #DAHM Configuracion inicial para que el servidor se vuelva subscriptor y publicador en el broker
    def configMQTT(self):
        client = self.x

        #DAHM Se configura el logging en modo DEBUG para observar mensajes desde este nivel
        logging.basicConfig(
        level = logging.DEBUG, 
        format = '[%(levelname)s] %(message)s'
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
            #DAHM Revisa si el topico es un archivo para recibirlo con el metodo especifico para esto
            #JICM generaliza para que si se encuentra la palagra archivos reciba el audio
            if ('audio' in str(msg.topic)) :
                logging.debug('Recibiendo audio...')
                #DAHM Se manda a llamar el metodo para recibir audio y guardarlo en el nombre de la carpeta que aparece en globals
                self.hilo_audio(msg.payload)
                logging.info('Audio recibido de: ' + str(msg.topic))
            #DAHM Cuando el topico es de un chat de usuario o sala lo desplega
            else:
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
        topicos.append(('audio/' + self.grupo + '/' + usuario, self.qos))
        #DAHM cerramos el archivo
        archivo_usuario.close()

        #DAHM Se recorre el archivo salas con un bucle
        for sala in archivo_salas:
            #DAHM quitamos los caracteres de nueva linea de cada linea
            sala = sala.split('\n')
            #DAHM se crea una tupla con el formato de salas y el qos
            topico = ('salas' + '/' + self.grupo + '/' + sala[0][2:], self.qos)
            topicos.append(topico)
            #JICM se añaden la suscripcion a las salas de archivos
            topico = ('audio' + '/' + self.grupo + '/' + sala[0][2:], self.qos)
            topicos.append(topico)
        #DAHM cerramos el archivo
        archivo_salas.close()

        #DAHM esta funcion retorna una lista de tuplas con los topicos a los que se subscribe el cliente y el qos
        return topicos

    #DAHM Este metodo graba audio del cliente para luego enviarlo
    def grabarAudio(self, file, duracion):
        os.system('arecord -d ' +  str(duracion) + ' -f U8 -r 8000 ' + str(file))

    #JICM Este metodo envia archivos de audio por MQTT
    def enviarAudio(self, file, destino):
        f = open(file, 'rb')
        binario = f.read()
        f.close()
        byteArray = bytearray(binario)
        self.publicar('audio/' + self.grupo + '/' + destino, byteArray)

    #JICM Este metodo recibe el archivo de audio por y lo decodifica
    def recibirAudio(self, bytearrayR):
        dir = self.direccion
        audioR = open(dir, 'wb')
        audioR.write(bytearrayR)
        audioR.close()
        logging.info('inicia reproduccion')
        #JDCP ESTA FUNCION REPODUCE EL AUDIO AUTOMATICAMENTE
        os.system('aplay '+ dir)
        logging.info('termina reproduccion')
    def hilo_audio(self,nombre):
        audio = threading.Thread(name = 'loquesea',
                            target = self.recibirAudio,
                            args = ((nombre)),
                            daemon = False
                            )
        audio.start()

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
#JICM se crea el error para cuando el carnet no es valido
class InvalidUser(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "El usuario debe de contener nueve números"
    
    def __repr__(self):
        return str(self)
#JDCP este error se levanta si el usario no ingreso un caracter valido de la insturcciones
class Seleccion_invalida(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "Porfavor ingrese un numero o letra valida"
    def __repr__(self):
        return str(self)
#JDCP este error se levanta si el usuario quiere mandar algo a una sala no valida por ejemplo salas/04/a
class sala_invalida(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "Formato de sala invalido"
    def __repr__(self):
        return str(self)


