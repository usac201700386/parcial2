from manejoCliente import Cliente
from manejoCliente import InvalidUser
from manejoCliente import Seleccion_invalida
import logging
from globals import *
#JDCP A MI ME TOCO TCP POR ESO NO HAY MUCHOS COMENTARIOS DE MI PARTE EN ESTE CODIGO XD
#JICM A MI ME TOCO MANEJO DE INSTRUCCIONES, POR ESO TAMPOCO MUCHOS COMENTARIOS MIOS EN ESTE CODIGO XD
grupo = GROUP_ID
audio = FILENAME
user = Cliente()

user.configMQTT()
user.conectar()
user.subscripcion()

destinos = user.topicos()
logging.info(('----------   TOPICOS A LOS QUE SE ESTA SUBSCRITO   -------- '))
for destino in destinos:
    logging.info((destino[0]))

try:
    while True:
        opcion1 = input('1) Enviar texto\n2) Enviar mensaje de voz\n')
        if opcion1 == '1':
            opcion2 = input('a. Enviar a usuario\nb. Enviar a sala\n')
            if opcion2 == 'a':
                #JICM levantar excepcion si el usuario es invalido
                try:
                    usuario = input('A que usuario desea enviar el mensaje?\n')
                    int(usuario)
                    if len(usuario)!=9:
                        raise InvalidUser
                    mensaje = input('Escriba su mensaje:\n')
                    user.publicar('usuarios/' + usuario, mensaje)
                #JICM manejo de la excepción si el usuario es invalido, para que se reinicie el programa
                #en vez de cerrarse por completo                   
                except (InvalidUser, ValueError):
                    logging.exception('el usuario debe de ser de 9 números')

            elif opcion2 == 'b':
                sala = input('A que sala desea enviar el mensaje?\n')
                mensaje = input('Escriba su mensaje:\n')
                user.publicar('salas/' + grupo + '/S' + sala, mensaje)

            else:
                raise Seleccion_invalida

        elif opcion1 == '2':
            opcion2 = input('a. Enviar a usuario\nb. Enviar a sala\n')
            if opcion2 == 'a':
                #JICM levantar excepción si el usuario es invalido
                try:
                    #JDCP LE DICE AL USUARIO QUE INGRESE LOS PARAMETROS DEL AUDIO
                    usuario = input('A que usuario desea enviar el audio?\n')
                    int(usuario)
                    if (len(usuario)!=9):
                        raise InvalidUser
                    duracion = input('Ingrese duracion del audio: \n')
                    user.grabarAudio(audio, duracion)
                    user.enviarAudio(audio, usuario)
                #JICM manejo de la excepción si el usuario es invalido, para que se reinicie el programa
                #en vez de cerrarse por completo
                except (InvalidUser, ValueError):
                    logging.exception('el usuario debe de ser de 9 números')

            elif opcion2 == 'b':
                sala = input('A que sala desea enviar el audio?\n')
                duracion = input('Ingrese duracion del audio: \n')
                user.grabarAudio(audio, duracion)
                #JICM se configura para que envíe correctamente a las salas
                user.enviarAudio(audio, "S"+sala)
            else:
                raise Seleccion_invalida
        else:
            #JDCP LEVANTA ERRO SI EL USUARIO NO SELECCIONA LA OPCIONES PROPUESTAS
            raise Seleccion_invalida

except KeyboardInterrupt:
    user.desconectar()
    logging.info('desconectado del broker!')

