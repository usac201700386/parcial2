from manejoCliente import Cliente
import logging

user = Cliente()

user.configMQTT()
user.conectar()
user.subscripcion()

destinos = user.topicos()
print('----------   CONTACTOS   -------- \n')
for destino in destinos:
    print(destino[0])

try:
    while True:

        topico = input('A donde desea enviar un mensaje? ')
        mensaje = input('Ingrese mensaje: ')
        user.publicar(topico, mensaje)

except KeyboardInterrupt:
    user.desconectar()
    logging.info('desconectado del broker!')

