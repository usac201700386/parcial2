import logging
import os
import paho.mqtt.client as mqtt
from credenciales import *

#Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
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

'''
Config. inicial del cliente MQTT
'''
server_MQTT = mqtt.Client(clean_session=True) #Nueva instancia de cliente
server_MQTT.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
server_MQTT.on_publish = on_publish #Se configura la funcion "Handler" que se activa al publicar algo
server_MQTT.on_message = on_message #Se configura la funcion "Handler" que se activa al llegar un mensaje a un topic subscrito
server_MQTT.username_pw_set(MQTT_USUARIO, MQTT_KEY) #Credenciales requeridas por el broker
server_MQTT.connect(host = HOST, port = MQTT_PORT) #Conectar al servidor remoto

topico = 'comandos/04'
mensaje = b'/x01'

#Publicacion simple
server_MQTT.publish(topico, mensaje, qos = 0, retain = False)

#Subscripcion simple con tupla (topic,qos)
server_MQTT.subscribe((topico, 0))

#Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
server_MQTT.loop_start()


try:
    while True:
        pass

except KeyboardInterrupt:
    logging.info('Desconectando...')

finally:
    server_MQTT.disconnect()
    logging.info('Se ha desconectado!')