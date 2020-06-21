from manejoServer import Servidor
import logging

server = Servidor()

server.configMQTT()
server.conectar()
server.subscripcion()

topics = server.topicos()
for topic in topics:
    print(topic[0])

try:
    while True:
        destino = input('Ingrese destinatario: ')
        mensaje = input('Ingrese mensaje: ')
        server.publicar(destino, mensaje)


except KeyboardInterrupt:
    logging.info('desconectado del broker!')
    server.desconectar()

