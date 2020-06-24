from manejoCliente import Cliente
from manejoCliente import InvalidUser
from manejoCliente import Seleccion_invalida
import logging
from globals import *

#JDCP A MI ME TOCO TCP POR ESO NO HAY MUCHOS COMENTARIOS DE MI PARTE EN ESTE CODIGO XD
#JICM A MI ME TOCO MANEJO DE INSTRUCCIONES, POR ESO TAMPOCO MUCHOS COMENTARIOS MIOS EN ESTE CODIGO XD

#DAHM Constantes a utilizar en la interfaz importadas de globals.py
grupo = GROUP_ID
audio = FILENAME

#DAHM Creacion de instancia de la clase Cliente la cual tiene ya todos los argumentos por defecto importados de globals.py
user = Cliente()
#DAHM Se configura para que se pueda conectar a un broker MQTT
user.configMQTT()
#DAHM Se conecta al broker
user.conectar()
#DAHM Se subscribe a los topicos detectados de los .txt
user.subscripcion()

#DAHM El metodo topicos retorna una lista de tuplas con los topicos y el QoS entonces lo desplegamos al inicio del menu
destinos = user.topicos()
logging.info(('----------   TOPICOS A LOS QUE SE ESTA SUBSCRITO   -------- '))
for destino in destinos:
    #DAHM Desplegamos solo el primer argumento ya que a un usuario final no  le interesa el QoS, de esta manera
    #DAHM el usuario sabe de donde puede recibir mensajes o audios 
    logging.info((destino[0]))

try:
    while True:
        opcion1 = input('1) Enviar texto\n2) Enviar mensaje de voz\n')
        try:#JDCP VERIFICA QUE SE INGRESE UNA OPCION CORRECTA , EN CASO CONTRARIO REINICIA EL PROGRAMA
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
                        logging.error('el usuario debe de ser de 9 números')

                elif opcion2 == 'b':
                    sala = input('A que sala desea enviar el mensaje?\n')
                    #JDCP ESTO VERIFICA QUE EL FORMATO DE LA SALA INGRESADA SEA VALIDA
                    try:
                        #JDCP SE VERIFICA QUE ESTE INGRESANDO UN NUMERO Y NO LETRAS 
                        if(sala.isdigit()):
                            mensaje = input('Escriba su mensaje:\n')
                            user.publicar('salas/' + grupo + '/S' + sala, mensaje)
                        else:
                            raise Seleccion_invalida
                        #JDCP SI EL USUARIO COMETE EL ERROR DE INGRESAR CARACTERES NO NUMERICOS
                    except (Seleccion_invalida,ValueError):
                        logging.error('solo se admiten valores numericos en la direccion de la sala \n')
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
                        #JDCP hilo para grabar y enviar
                        user.hilo_enviarAudio(audio, duracion, usuario)
                    #JICM manejo de la excepción si el usuario es invalido, para que se reinicie el programa
                    #en vez de cerrarse por completo
                    except (InvalidUser, ValueError):
                        logging.error('el usuario debe de ser de 9 números')

                elif opcion2 == 'b':
                    try:
                        sala = input('A que sala desea enviar el audio?\n')
                        if (sala.isdigit()):
                            duracion = input('Ingrese duracion del audio: \n')
                            #JICM se configura para que envíe correctamente a las salas
                            user.hilo_enviarAudio(audio, duracion,"S"+sala)
                        else:
                            raise Seleccion_invalida
                        #JDCP SI EL USUARIO COMETE EL ERROR DE INGRESAR CARACTERES NO NUMERICOS
                    except (Seleccion_invalida,ValueError):
                        logging.error('solo se admiten valores numericos en la direccion de la sala \n')
                else:
                    raise Seleccion_invalida
                    
            else:
                #JDCP LEVANTA ERRO SI EL USUARIO NO SELECCIONA LA OPCIONES PROPUESTAS
                raise Seleccion_invalida
        except (Seleccion_invalida,ValueError):
            #JDCP SE MUESTRA AL USUARIO QUE HA INGRESADO UN DATO INVALIDO
            logging.error('data invalido, Ingrese una de las siguiente opciones : \n')

#DAHM El usuario solo puede finalizar el programa con interrupcion ctrl+c
except KeyboardInterrupt:
    #DAHM Se llama el metodo que desconecta del broker MQTT a la instancia
    user.desconectar()
    logging.info('desconectado del broker!')