# do crypto stuff

from ucryptolib import aes
import os
from binascii import hexlify
from hashlib import sha256

__version__ = "0.0.2"
MODE_CBC = 2

class globs:
    filename = ""
    filehandle = None
    encoder = None
    decoder = None
    iv = b""
    verbosity = 3
    ak = b""
    
def init(ak):
    globs.iv = os.urandom(16)
    if ak:
        globs.ak = sha256(ak).digest()
        globs.decoder=aes(globs.ak, MODE_CBC, globs.iv).decrypt
        globs.encoder=aes(globs.ak, MODE_CBC, globs.iv).encrypt
        
def bin2str(btext):
    r=""
    for c in btext:
        r+=chr(c)
    return r
        
def parse(text):
    try:
        if globs.decoder:
            c=" "
            if not isinstance(text, bytes):
                c=b" "
            text += c * (16 - len(text) % 16)
            text=globs.decoder(text)
            if globs.verbosity>2:
                print(text)
        text = bin2str(text)
        c= text[0]
        t2=text[1:]
        if c=='w' and globs.filehandle:
            filehandle.write(t2)
            return "ok."
        if c=='o':
            if globs.filehandle:
                globs.filehandle.close()
                globs.filehandle = None
            c2,le=t2[0],ord(t2[1])
            t2=t2[2:2+le]
            globs.filehandle = open(t2.strip(),c2)
            return "ok."
        if c=='c' and globs.filehandle:
            globs.filehandle.close()
            globs.filehandle = None
            return "ok."
        if c=='r' and globs.filehandle and globs.encoder():
            r = globs.filehandle.read(128)
            r + " " * (16 - len(r) % 16)
            r = globs.encoder(r)
            return r
        if c=='l':
            if globs.encoder:
                r=str(os.listdir())
                r += " " * (16 - len(r) % 16)
                return hexlify(globs.encoder(r))
    except Exception as e:
        print("Error: "+str(e))
    return "nok!"
            
# eof
