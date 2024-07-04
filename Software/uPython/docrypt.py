# do crypto stuff

from ucryptolib import aes
import os
from binascii import hexlify
from hashlib import sha256

__version__ = "0.1.0"

MODE_ECB = 1
MODE_CBC = 2
MODE_CTR = 6

class globs:
    filename = ""
    filehandle = None
    encr = None
    decr = None
    ive = b""
    ivd = b""
    verbosity = 3
    ak = b""
    
def init(ak):
    if globs.verbosity:
        print("docrypt version:"+__version__)
    globs.ive = os.urandom(16)
    globs.ivd = os.urandom(16)
    if ak:
        if not isinstance(ak, bytes):
            ak = str(ak).encode()
        globs.ak = sha256(ak).digest()
        globs.decr=aes(globs.ak, MODE_ECB, globs.ivd).decrypt
        globs.encr=aes(globs.ak, MODE_ECB, globs.ive).encrypt
        
def bin2str(btext):
    r=""
    for c in btext:
        r+=chr(c)
    return r
        
def encode(plain,iv=None):
    if iv: globs.ive = iv
    globs.encr=aes(globs.ak, MODE_ECB, globs.ive).encrypt
    if not isinstance(plain, bytes):
        plain=plain.encode()
    return
        
def parse(text):
    try:
        if globs.decr:
            c=" "
            if not isinstance(text, bytes):
                c=b" "
            text += c * (16 - len(text) % 16)
            text=globs.decr(text)
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
        if c=='r' and globs.filehandle and globs.encr():
            r = globs.filehandle.read(128)
            r + " " * (16 - len(r) % 16)
            r = globs.encr(r)
            return r
        if c=='l':
            if globs.encr:
                r=str(os.listdir())
                r += " " * (16 - len(r) % 16)
                return hexlify(globs.encr(r))
        if c=='t':
            if globs.encr:
                r="test!"
                r += " " * (16 - len(r) % 16)
                if globs.verbosity:
                    print(r)
                return hexlify(globs.encr(r))
    except Exception as e:
        print("Error parse: "+str(e))
    return "nok!"
            
# eof
