from manejoServer import *

server = Servidor()

server.configMQTT()
server.conectar()
server.subscripcion('201700804')

try:
    while True:
        mensaje = input('ingrese mensaje: ')
        server.publicar('201701042', mensaje)

except KeyboardInterrupt:
    logging.info('desconectado del broker!')
    server.desconectar()

