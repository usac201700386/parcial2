import paho.mqtt.client as mqtt
import logging
import socket
import tqdm
import os
import time
from globals import *
#JICM se importa para el manejo de mensajes a mostrar
import threading #JICM Concurrencia con hilos
#JICM se importan las librerías necesarias
import binascii
#JICM se importan las librerías para manejar hilos
import threading #Concurrencia con hilos
import sys       #Requerido para salir (sys.exit())

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
        #JICM se lee el usuario del archivo txt
        archivo=open(self.usuario, 'r')
        self.usuarioPropio=archivo.readline()
        archivo.close()


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
            #configurarhiloALIVE()
            logging.debug(connectionText)#no quiero que se lo muestre al usuario, solo para debug

        #DAHM Funcion handler que configura el evento on_publish (cuando se logra publicar con exito en el topico seleccionado)
        def on_publish(client, userdata, mid): 
            publishText = "Publicacion satisfactoria"
            logging.debug(publishText)

        #DAHM Funcion handler que configura el evento on_message (cuando llega un mensaje a alguno de los topicos que se esta subscrito)
        def on_message(client, userdata, msg):
            logging.info('mensaje recibido: ' + str(msg.payload) + 'del topico: ' + str(msg.topic))
            #JICM se evalúa si lo que se recibe es un comando o un mensaje normal
            Instruccion=instruccionR(msg.payload)
            codigo=Instruccion.getCodigo()
            logging.debug(type(Instruccion.getCodigo()))
            #JICM acción cuando se recibe un FRR
            if (codigo==2):
                i2=instruccionS(6,str(self.usuarioPropio))
                #user.publicar('comandos/04/'+str(self.usuarioPropio), i2.trama)
                logging.debug(i2.trama)
                user.publicar('salas/04/S3', i2.trama)
            #JICM accion cuando se recibe un ok    
            elif (codigo==6):
                logging.info('reconoció el código 6')
                #JICM se incializa el hilo de TCP
                configurarhiloTCP()
            #JICM accion cuando se recibe un ack
            elif (codigo==5):
                logging.debug('se recibió un ack')


                

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
    #JICM codigo que se manda a llamar del hilo de alive
    def envioAlive(self):
        alive=instruccionS(4,self.usuarioPropio)
        #while True:
        self.publicar('comandos/04/'+ str(self.usuarioPropio), alive.trama)
        #time.sleep(2)
            
    
    #-----------------------------------------------------------------------------------


#JICM se crea la clase de instrucciones a enviar
class instruccionS(object):
    #JICM se inicializa el objeto, filseize es un argumento opcional
    def __init__(self, codigo, dest, filesize=''):
        self.codigo='0'+ str(codigo)#JICM se crea el código de la instrucción para que sea un str con dos numeros
        self.dest=str(dest)
        self.filesize=filesize
        #JICM se codifica en hexadecimal y en lista de bytes
        self.codigohex=binascii.unhexlify(self.codigo)
        self.destbytes=self.dest.encode()
        self.filesizebytes=str(self.filesize).encode()
        self.trama=(self.codigohex+self.destbytes+self.filesizebytes)
        #JICM Se envía error si desean crear la instrucción 01 pero no añaden filesize
        if self.codigo=='01' and self.filesize=='':
            raise FaltanArgumentos
    #JICM se sobreescriben los metodos str y repr para facilitar la comprensión de los objetos        
    def __str__(self):
        return str(self.trama)

    def __repr__(self):
        return str(self)
#JICM se crea la excepción para cuando faltan argumentos
class FaltanArgumentos(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "No se especifico tamaño de archivo o destinatario"
    
    def __repr__(self):
        return str(self)
#JICM se crea una clase de instrucciones recibidas, para obtener sus parámetros de manera facil con getters
class instruccionR(object):
    def __init__(self, trama):
        self.trama=trama
        self.strama=trama.decode()
    def getCodigo(self):
        return self.trama[0]
    #JICM el destino depende de si es una sala o un usuario
    def getDest(self):
        if self.strama[3]=='S' or self.strama[3]=='s':
            return self.strama[1:7]
        else:
            return self.strama[1:9]
    #JICM el filesize solo retorna un valor si el comando era 1 o 2, pues los demás no llevan ese parámetro
    def getFilesize(self):
        #JICM que digitos corresponden al filsize depende de si el destinatario era una sala o un usuario
        if self.getCodigo()==(2):
            if self.strama[3]=='S' or self.strama[3]=='s':
                return self.strama[7:]
            else:
                return self.strama[9:]
        else:
            logging.info('esta trama no incluye tamaño de archivo')
        









def Audio_create(filename='audio.wav',duracion=3):
    logging.info('inicia grabacion')
    os.system('arecord -d '+str(duracion)+' -f U8 -r 8000 '+filename)
    logging.info('termina grabacion')
    #JDCP se obtiene el tamano del archivo de grabacion
    filesize = os.path.getsize(filename)
    return filename , filesize


#---------------------MAIN----------------------
########################################333333
############################################


#JICM se inicializa el cliente creando un objeto de esa clase
user = Cliente()
#JICM se llaman los métodos para configurar MQTT, conectar y suscribirse a los tópicos para este user
user.configMQTT()
user.conectar()
user.subscripcion()
#imprime al usuario los usuarios que son sus contactos
destinos = user.topicos()
print('----------   CONTACTOS   -------- \n')
for destino in destinos:
    logging.info('está suscrito a ' + str(destino))
print('--------------------------------- \n')
#time.sleep(1)

#JICM se configura el hilo para enviar con TCP
def configurarhiloTCP():
    time.sleep(3)
    t1 = threading.Thread(name = 'Envío TCP',
                            target = user.Envio_TCP_Client(),
                            args = (()),
                            daemon = True
                            )
    t1.start()
#JICM Se configura el hilo para enviar los alive cada dos segundos
def sendAlive():
    while True:
        user.envioAlive()
        time.sleep(2)
#def configurarhiloALIVE():

t2 = threading.Thread(name = 'enviar ALIVE',
                    target = sendAlive(),
                    args = (()),
                    daemon = True
                    )

t2.start()

try:
    while True:
        inst=input('si desea enviar un mensaje, ingreselo ahora, si desea enviar un archivo, ingrese "3" \n')
        topico = input('A donde desea enviar su mensaje o archivo? \n')
        if inst==('3'):
            logging.info('a continuación iniciará la grabación')
            Audio_create()
            tamaño = input("ingrese el tamaño del archivo \n")
            i1=instruccionS(3,topico,tamaño)
            user.publicar('comandos/04/'+ str(user.usuarioPropio), i1.trama)
            
        else:
            user.publicar(topico, inst)


except KeyboardInterrupt:
    user.desconectar()
    logging.info('desconectado del broker!')