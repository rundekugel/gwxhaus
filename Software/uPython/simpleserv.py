# simple server
import socket
import time
import network

__version__ = "0.0.1b"
PIN_WIND = 14
PIN_SCL1 = 5
PIN_SDA1 = 4
PIN_SCL2 = 19
PIN_SDA2 = 18

class globs:
    verbosity = 2
    sock = None
    sock_client = None
    sockf = None
    line = ""
    interval_rx=1
    dorx=1
    tL = None
    tx=[]
    callbackRx = None
    windspeed = None
    ths=""
    connectionclose = 0
    port = 80


def wifiap():
    ap = network.WLAN(network.AP_IF)  # create access-point interface
    ap.config(ssid='ESP-AP')  # set the SSID of the access point
    ap.config(max_clients=10)  # set how many clients can connect to the network
    ap.active(True)

def close():
    globs.sock_client.close()
    globs.sock.close()

def proc(msg=None):
    try:
        if not globs.sock:
            init(globs.port)
        if not globs.sock_client:
            if globs.verbosity:
                print("init sise...")
            globs.sock.settimeout(1)
            cl, addr = globs.sock.accept()
            print('client connected from', addr)
            cl.settimeout(1)
            globs.sockf = cl.makefile('rwb', 0)
            globs.sock_client = cl

        line = ""
        while 1:
            try:
                line = globs.sockf.readline()  # do this in extra thread!
                line = str(line)
                if globs.verbosity:
                    print("L:" + line)
            except Exception as e:
                if globs.verbosity:
                    print("eL:" + str(e))
            if "stopall" in line:
                globs.dorun = 0
                globs.callbackRx("stopall")
                break
            if "stop" in line:
                break
            if "test" in line:
                print("test")
                globs.sock_client.send(line)
                if globs.callbackRx:
                    callbackRx(msg=line)
            if " HTTP/" in line:
                globs.connectionclose = True
                if globs.verbosity:
                    print("doclose.")
            if "listen=" in line:
                print("listen disabled.")
            if "interv=" in line:
                globs.interval_rx = int(line.split("=", 1).strip())
            if line.strip() != "":  # read all server msg 1st, then respond
                continue
            time.sleep(.5)
            ths = globs.ths
            globs.ths = ""
            globs.sock_client.send(ths)
            if globs.tx:
                t=globs.tx.pop()
                globs.sock_client.send(t)+"\r\n"
            content += "<hr>\r\n"
            # cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html;charset=utf-8\r\n')
            globs.sock_client.send('Content-type: text/html;charset=utf-8\r\n')
            globs.sock_client.send("Content-Length: " + str(len(content)))
            globs.sock_client.send('Connection: close\r\n\r\n')
            globs.sock_client.send(content)
            if globs.connectionclose:
                globs.sock_client.send('xxxxxx')
                time.sleep(.1)
            time.sleep(.5)
            break
        if globs.verbosity:
            print("proc ok.")
    except Exception as e:
        if globs.verbosity:
            print("esiseProc:" + str(e))
    print("br.close.")
    time.sleep(.1)
    globs.sock_client.close()
    close()


def init(port=80):
    print("simpleserv version:" + str(__version__))

    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    globs.sock = s
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(addr)
        s.listen(1)
        print('listening on', addr)
    except Exception as e:
        if globs.verbosity:
            print("eB:" + str(e))

    globs.dorun = 1

# eof
