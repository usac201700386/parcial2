#JICM se importa la clase para el manejo de clientes
from manejoCliente import Cliente
#JICM se importa la clase para el manejo de comandos a enviar y recibidos
from comandos import *
#JICM se importa para poder llevar tiempo
import time
#JICM se importa para el manejo de mensajes a mostrar
import threading #JICM Concurrencia con hilos


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
time.sleep(1)

try:
    while True:
        inst=input('si desea enviar un mensaje, ingreselo ahora, si desea enviar un archivo, ingrese "1" \n')
        topico = input('A donde desea enviar su mensaje o archivo? \n')
        if inst!='1':
            user.publicar(topico, inst)
        else:
            tamaño = input("ingrese el tamaño del archivo \n")
            i1=instruccionS(1,topico,tamaño)
            user.publicar('comandos/04/201701042', i1.trama)

except KeyboardInterrupt:
    user.desconectar()
    logging.info('desconectado del broker!')
