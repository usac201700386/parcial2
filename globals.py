'''
--------------------------   GRUPO 04    -----------------------------
PARCIAL 2: Implementar una aplicacion de mensajeria instantanea con
mensajes de texto, audio y salas de chat TODO BASADO EN MQTT.

INSTRUCCIONES DE USO: En usuarios.txt se escribe el carnet del cliente,
en salas.txt se ingresan las salas a las que va a pertenecer.

Integrantes:    Diego Andres Herrera Morales        201700804
                Jose Daniel Campos Pol              201700386
                Jonathan Israel Cobar Mendoza       201701042

Curso: Proyectos de computacion aplicados a I.E
Catedratico: M.Sc Ivan Morales
'''



#DAHM direccion IP del servidor
HOST = '167.71.243.238'
#DAHM puerto de conexion para MQTT
MQTT_PORT = 1883
#DAHM credenciales del broker MQTT
MQTT_USUARIO = 'proyectos'
MQTT_KEY = 'proyectos980'

#DAHM archivos de texto que utilizara para subscripciones el servidor
#USERS_FILE = 'usuarios.txt'
#ROOMS_FILE = 'salas.txt'

#DAHM archivos de texto que utilizara para subscripciones el cliente
USER_FILE = 'usuario.txt'
ROOMS_USER_FILE = 'salas.txt'

#DAHM datos del grupo
GROUP_ID = '04'

#DAHM Mas parametros de MQTT:
QOS_LEVEL = 1

#DAHM constantes para la grabacion
FILENAME = 'nuevaGrabacion.wav'
FILENAME_R = 'grabacionRecibida.wav'