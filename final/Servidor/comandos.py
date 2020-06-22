#JICM se importan las librerías necesarias
import binascii
import logging
from manejoServer_instrucciones import *

#JICM se configura el logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    )
#JICM se crea la clase de instrucciones a enviar
class instruccionS(object):
    #JICM se inicializa el objeto, filseize es un argumento opcional
    def __init__(self, codigo, dest, filesize=''):
        self.codigo='0'+ str(codigo)#JICM se crea el código de la instrucción para que sea un str con dos numeros
        self.dest=str(dest)
        self.filesize=filesize
        #JICM se codifica en hexadecimal y en lista de bytes
        self.codigohex=binascii.unhexlify(self.codigo)
        self.destbytes=self.dest.encode()
        self.filesizebytes=str(self.filesize).encode()
        self.trama=(self.codigohex+self.destbytes+self.filesizebytes)
        #JICM Se envía error si desean crear la instrucción 01 pero no añaden filesize
        if self.codigo=='01' and self.filesize=='':
            raise FaltanArgumentos
    #JICM se sobreescriben los metodos str y repr para facilitar la comprensión de los objetos        
    def __str__(self):
        return str(self.trama)

    def __repr__(self):
        return str(self)
#JICM se crea la excepción para cuando faltan argumentos
class FaltanArgumentos(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "No se especifico tamaño de archivo o destinatario"
    
    def __repr__(self):
        return str(self)
#JICM se crea una clase de instrucciones recibidas, para obtener sus parámetros de manera facil con getters
class instruccionR(object):
    def __init__(self, trama, origen):
        self.trama=trama
        self.strama=trama.decode()
        self.origen= origen
    def getCodigo(self):
        return self.trama[0]
    #JICM el destino depende de si es una sala o un usuario
    def getDest(self):
        if self.strama[3]=='S' or self.strama[3]=='s':
            return self.strama[1:7]
        else:
            return self.strama[1:9]
    #el filesize solo retorna un valor si el comando era 1 o 2, pues los demás no llevan ese parámetro
    def getFilesize(self):
        #que digitos corresponden al filsize depende de si el destinatario era una sala o un usuario
        if self.getCodigo()==(1 or 2):
            if self.strama[3]=='S' or self.strama[3]=='s':
                return self.strama[7:]
            else:
                return self.strama[9:]

        else:
            logging.info('esta trama no incluye tamaño de archivo')







        
