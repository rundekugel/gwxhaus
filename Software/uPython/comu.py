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
    rx=""

def bytessplit(data, splitchar):
    for i in range(len(data)):
        if data[i]==splitchar:
            break
    return data[:i],data[i+1:]

def irq_handler():
    rx = globs.uart.read()
    globs.rx += rx.decode()
    globs.rx.replace('\r','\n')
    while '\n\n' in globs.rx:
        globs.rx = globs.rx.replace('\n\n','\n')
    if "\n" in globs.rx:
        r1,globs.rx = bytessplit(globs.rx, "\n")
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
