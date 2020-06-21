from manejoServer import Servidor
import logging
import time
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
        server.Recp_TCP_Server()
        time.sleep(2)
        server.Envio_TCP_Server()

except KeyboardInterrupt:
    logging.info('desconectado del broker!')
    server.desconectar()

