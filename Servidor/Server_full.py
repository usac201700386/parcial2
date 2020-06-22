import paho.mqtt.client as mqtt
import socket#PARA COMUNICACION DE TCP
import tqdm #JDCP PARA MANEJOS VISUALES
import logging
import os
from globals import *
#JICM se importan las librerías necesarias
import binascii
import time
#JDCP libreria de Hilos
import threading #Concurrencia con hilos
import sys       #Requerido para salir (sys.exit())


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
        self.publish_status = False
        self.lista_actual = []      #JDCP ESTA LISTA ALMACENA LOS ALIVES DE TODOS LOS USAURIO ACTUALES
        self.lista_conectados = []  #JDCP ESTA LISTAL ALMACENA LOS USUARIOS CONECTADOS EN 3 CICLOS DE ALIVE

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
            logging.debug(publishText + str(self.publish_status))
            if (self.publish_status):
                    self.publish_status=False
                    configurar_hilo()
            self.publish_status= False
            

        #DAHM La funcion Handler que atiende el evento on_message (cuando llega algun mensaje a algun topic que esta subscrito el servidor)
        def on_message(client, userdata, msg):
            #self.publish_status=False
            #Se muestra en pantalla informacion que ha llegado
            logging.info('mensaje recibido: ' + str(msg.payload) + 'del topico: ' + str(msg.topic))
            #JICM se lee el usuario del archivo txt

            #JICM se evalúa si lo que se recibe es un comando o un mensaje normal
            Instruccion=instruccionR(msg.payload)
            ID= str(msg.topic)[-10:]
            logging.debug(ID)
            codigo=Instruccion.getCodigo()
            #logging.debug(type(Instruccion.getCodigo()))
            if (codigo==3):
                #JDCP ESTA FLAG ACTIVA EL OK PARA RECIBIR ARCHIVOS
                self.publish_status=True
                #JDCP ESTE OBJETO MANDA LA TRAMA PARA EL OK
                i6=instruccionS(6,ID)
                logging.debug(i6.trama)
                #JDCP SE PUBLICA EL OK
                server.publicar('usuarios/'+ID, i6.trama)
                logging.debug('valor de flag ->'+str(self.publish_status))
                #JDCP ACK
                i5=instruccionS(5,ID)
                #JDCP SE PUBLICA EL ACK
                server.publicar('usuarios/'+ID, i5.trama)
            elif(codigo==4):
                #JDCP ESTA FUNCION MANEJA EL ALVIE
                #JDCP ESTE ES UN OBJETO PARA CONTROLAR EL ESTATUS DE ALIVE
                i5 =instruccionS(5,ID)
                if (ID not in self.lista_actual):
                    self.lista_actual.append(ID)
                else:
                    pass
                    

                #JDCP PUBLICAR ACK PARA EL ALIVE
                server.publicar('usuarios/'+ID, i5.trama)
                
            else:

                logging.debug('la condición codigo=2 no se cumple')

            # esta funcion me tiene que devolver trama codificada
        
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
        logging.debug(f"[*] Esperando conexion TCP en {self.ip}:{self.portTCP}")
        #JDCP se obtine la informacion del cliente que se conecto al servicio
        client_socket, address = servidor.accept() # datos el 
        #JDCP SE AVISA POR MEDIO DE LOGGING QUE SE HA CONECTADO AL SERVIDOR
        logging.debug(f"[+] {address} estado conectado")
        return servidor,client_socket,address

    def Recp_TCP_Server(self):
        #JDCP se obtiene todos los parametros y objetos de la funcion que levanta el servidor TCP
        server,cliente,_ = self.est_servidor()
        #SE ESTA ATENTO A LA INFORMACION QUE SE RECIBE DEL TCP SOBRE EL TAMANO DEL ARCHIVO
        logging.debug('inicia la recepcion del archivo')
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

#-----------------------------------------------------------------------------------
#            inicia clase de comandos
# -----------------------------------------------------------------------------------
   #JICM se configura el logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    )
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
    #el filesize solo retorna un valor si el comando era 1 o 2, pues los demás no llevan ese parámetro
    def getFilesize(self):
        #que digitos corresponden al filsize depende de si el destinatario era una sala o un usuario
        if self.getCodigo()==(1 or 2):
            if self.strama[3]=='S' or self.strama[3]=='s':
                return self.strama[7:]
            else:
                return self.strama[9:]
        else:
            logging.info('esta trama no incluye tamaño de archivo')
    

def configurar_hilo():
    time.sleep(3)
    t1 = threading.Thread(name = 'Servidor TCP',
                        target = server.Recp_TCP_Server(),
                        args = (()),
                        daemon = True
                        )
    t1.start()
    
def control_alive(lista_conectados=[],lista_actual=[]):
    while True:
        if(len(lista_conectados)==3):
            lista_conectados.remove(lista_conectados[0])
        lista_conectados.append(lista_actual)
        lista_actual=[]
        logging.debug('lista de conectados -> '+str(lista_conectados))
        time.sleep(2)
    
    



#------------------------------------------------------------------------------------ 


server = Servidor()
server.configMQTT()
server.conectar()
server.subscripcion()
#JDCP esta es la lista de topicos a los que esta suscrito el servidor
topics = server.topicos()
for topic in topics:
    print(topic[0])

Hilo_conectados = threading.Thread(name = 'Refresca la lista de Conectaods',
                        target = control_alive(),
                        args = ((server.lista_conectados,server.lista_actual)),
                        daemon = True
                        )

Hilo_conectados.start()


try:
    while True:
        pass
        #server.evaluar()
        
       # server.Recp_TCP_Server()
        #time.sleep(2)
        #server.Envio_TCP_Server()

except KeyboardInterrupt:
    logging.info('desconectado del broker!')
    server.desconectar()




    
    



