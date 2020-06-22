from manejoServer import *
import logging
import time
import binascii
#------------------------------------------------------------------------------
#JDCP                   AQUI INICIA LA EJECUCION DE PROGRMA
#------------------------------------------------------------------------------
server = Servidor()
server.configMQTT()
server.conectar()
server.subscripcion()
#JDCP esta es la lista de topicos a los que esta suscrito el servidor
topics = server.topicos()
for topic in topics:
    print(topic[0])


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
