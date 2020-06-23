from manejoCliente import Cliente
import logging
from globals import *

grupo = GROUP_ID
audio = FILENAME
user = Cliente()

user.configMQTT()
user.conectar()
user.subscripcion()

destinos = user.topicos()
print('----------   TOPICOS A LOS QUE SE ESTA SUBSCRITO   -------- ')
for destino in destinos:
    print(destino[0])

try:
    while True:
        opcion1 = input('1) Enviar texto\n2) Enviar mensaje de voz\n')
        if opcion1 == '1':
            opcion2 = input('a. Enviar a usuario\nb. Enviar a sala\n')
            if opcion2 == 'a':
                usuario = input('A que usuario desea enviar el mensaje?\n')
                mensaje = input('Escriba su mensaje:\n')
                user.publicar('usuarios/' + usuario, mensaje)
            elif opcion2 == 'b':
                sala = input('A que sala desea enviar el mensaje?\n')
                mensaje = input('Escriba su mensaje:\n')
                user.publicar('salas/' + grupo + '/S' + sala, mensaje)
            else:
                print('opcion incorrecta\n')
        elif opcion1 == '2':
            opcion2 = input('a. Enviar a usuario\nb. Enviar a sala\n')
            if opcion2 == 'a':
                usuario = input('A que usuario desea enviar el audio?\n')
                duracion = input('Ingrese duracion del audio: \n')
                user.grabarAudio(audio, duracion)
                user.enviarAudio(audio, usuario)
            elif opcion2 == 'b':
                sala = input('A que sala desea enviar el audio?\n')
                duracion = input('Ingrese duracion del audio: \n')
                user.grabarAudio(audio, duracion)
                user.enviarAudio(audio, "S"+sala)
            else:
                print('opcion incorrecta\n')
        else:
            print('opcion incorrecta\n')

except KeyboardInterrupt:
    user.desconectar()
    logging.info('desconectado del broker!')

