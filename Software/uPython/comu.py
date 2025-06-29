# communication module
from machine import UART,RTC
import time

__version__ = "1.2.0"


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
    # ths = ""

def bytessplit(data, splitchar):
    for i in range(len(data)):
        if data[i]==ord(splitchar):  # datas[n] become int
            break
    return data[:i],data[i+1:]

def addTx(data):
    data = str(data)
    globs.tx.append(data)

def irq_handler():
    rx = globs.uart.read()
    if rx:
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

def init(portnum=None, baudrate=None):
    print("comu version:" + str(__version__))
    if baudrate in (300,600,1200,2400,4800,9600,19200,57600,115200,230400):
        globs.baud = baudrate
    if portnum is not None:
        globs.portnum = portnum
    globs.uart = UART(globs.uartport, globs.baud, bits=8, parity=None, stop=1,
        timeout=globs.timeout_ms, txbuf=1024)
    # globs.uart.irq(UART.RX_ANY, handler=irq_handler)
    globs.dorun = 1

def proc(msg=""):
            content = ""
            # globs.ths = ""
            while globs.tx:
                content += str(globs.tx.pop(0)) +"; "
            content += ";"+msg+";"
            try:
                globs.uart.flush()
            except:
                pass
            # todo: if esp8266, then wait for last character to be sents
            globs.uart.write(content.encode())
            content = ""
            # time.sleep(.1)
            # content += "---\r\n"
            d = RTC().datetime()
            content += (f"ts:{d[0]}-{d[1]:02}-{d[2]:02} {d[4]:02}:{d[5]:02}:{d[6]:02}\r\n")
            content = content.replace("'","") # tasmota can't deal with quotes
            globs.uart.write(content.encode())
            if globs.verbosity >1:
                print(content.encode())

            if globs.uart.any() or globs.rx:
                irq_handler()

# eof
