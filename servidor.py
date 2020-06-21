from manejoServer import Servidor
import logging

server = Servidor()

server.configMQTT()
server.conectar()
server.subscripcion()

try:
    while True:
        pass

except KeyboardInterrupt:
    logging.info('desconectado del broker!')
    server.desconectar()

