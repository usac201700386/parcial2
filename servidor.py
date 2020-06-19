import logging
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

'''
Config. inicial del cliente MQTT
'''
server_MQTT = mqtt.Client(clean_session=True) #Nueva instancia de cliente
server_MQTT.on_connect = on_connect #Se configura la funcion "Handler" cuando suceda la conexion
server_MQTT.on_publish = on_publish #Se configura la funcion "Handler" que se activa al publicar algo
server_MQTT.username_pw_set(MQTT_USUARIO, MQTT_KEY) #Credenciales requeridas por el broker
server_MQTT.connect(host = HOST, port = MQTT_PORT) #Conectar al servidor remoto

server_MQTT.publish('comandos/04', "Mensaje inicial de prueba", qos = 0, retain = False)

server_MQTT.disconnect()
logging.info("Se ha desconectado del broker. Saliendo...")