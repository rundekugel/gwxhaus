# communication module
from machine import UART
import time

__version__ = "0.0.1c"

class globs:
    verbosity = 2
    uartport = 2
    baud = 19200
    uart = None
    tx=[]
    callbackRx = None
    timeout_ms = 500
    dorun = 1
    rx=b""

def bytessplit(data, splitchar):
    for i in range(len(data)):
        if data[i]==ord(splitchar):  # datas[n] become int
            break
    return data[:i],data[i+1:]

def addTx(data):
    data = str(data).encode()
    globs.tx.append(data)

def irq_handler():
    rx = globs.uart.read()
    globs.rx += rx  # .decode()
    if globs.verbosity>5:
        print("ih:"+str(rx))
        print("ih2:" + str(globs.rx))
    globs.rx = globs.rx.replace(b'\r',b'\n')
    while b'\n\n' in globs.rx:
        globs.rx = globs.rx.replace(b'\n\n',b'\n')
    if globs.verbosity>5:
        print("ih.nn:" + str(globs.rx))
    if b"\n" in globs.rx:
        r1,globs.rx = bytessplit(globs.rx, b"\n")
        if globs.verbosity:
            print("ihs:" + str(r1)+":"+str(globs.rx))
        if globs.callbackRx:
            globs.callbackRx(r1)

def init(portnum=None):
    print("comu version:" + str(__version__))
    if portnum is not None:
        globs.portnum = portnum
    globs.uart = UART(globs.uartport, globs.baud, timeout=globs.timeout_ms)
    # globs.uart.irq(UART.RX_ANY, handler=irq_handler)
    globs.dorun = 1

def proc(msg=None):
            content = globs.ths
            globs.ths = ""
            if globs.tx:
                content += globs.tx.pop()+"\r\n"
            content += "<hr>\r\n"
            content += "ts:"+str(time.time())+"<hr>\r\n"
            globs.uart.write(content.encode())

            if globs.uart.any():
                irq_handler()

# eof
