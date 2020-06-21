import binascii
import logging

logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    )

class instruccionS(object):
    def __init__(self, codigo, dest='', filesize=''):
        self.codigo='0'+ str(codigo)
        self.dest=str(dest)
        self.filesize=filesize
        self.codigohex=binascii.unhexlify(self.codigo)
        self.destbytes=self.dest.encode()
        self.filesizebytes=str(self.filesize).encode()
        self.trama=(self.codigohex+self.destbytes+self.filesizebytes)
        if self.codigo=='01' and self.filesize=='':
            raise FaltanArgumentos

    def __str__(self):
        return str(self.trama)

    def __repr__(self):
        return str(self)
    
    def enviar(self):
        pass

class FaltanArgumentos(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "No se especifico tamaño de archivo o destinatario"
    
    def __repr__(self):
        return str(self)

class instruccionR(object):
    def __init__(self, trama):
        self.trama=trama
        self.strama=trama.decode()
    def getCodigo(self):
        return self.trama[0]
    def getDest(self):
        if self.strama[3]=='S' or self.strama[3]=='s':
            return self.strama[1:6]
        else:
            return self.strama[1:9]

    def getFilesize(self):
        if self.getCodigo()==(1 or 2):
            if self.strama[3]=='S' or self.strama[3]=='s':
                return self.strama[6:]
            else:
                return self.strama[9:]
        else:
            return ''




        
