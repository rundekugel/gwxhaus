# simple server
import socket
import time
import timer
import windsensor
import HYT221 
import network

__version__ = "0.0.1b"

class globs:
    verbosity = 2
    sock = None
    sockr = None
    sockf = None
    line = ""
    interval_rx=1
    dorx=1
    tL = None

def wifiap():
    ap = network.WLAN(network.AP_IF)  # create access-point interface
    ap.config(ssid='ESP-AP')  # set the SSID of the access point
    ap.config(max_clients=10)  # set how many clients can connect to the network
    ap.active(True)

def sockread():
    if globs.verbosity:
        print("sr...")
        print(globs.__dict__)
    if not globs.dorx:
        return
    globs.dorx = False
    try:
        line = globs.sockf.readline()  # do this in extra thread!
    except:
        return
    if globs.verbosity >1:
        print("L:" + str(line))
    globs.line += str(line)


def main(port=80):
    print("simpleserv version:" + str(__version__))
    ws = windsensor.Windsensor(4)
    # hy = HYT221.HYT221(5,4)

    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(5)

    print('listening on', addr)
    dorun = 1
    cl = None
    while dorun:
        dolisten = 1
        doclose = 0
        cl, addr = s.accept()
        print('client connected from', addr)
        cl.settimeout(1)
        cl_file = cl.makefile('rwb', 0)
        # globs.sockf = cl_file
        # globs.tL = timer.Timer(globs.interval_rx, sockread)
        try:
            while True:
                line=""
                try:
                    if dolisten:
                        # line = globs.line
                        # globs.line = ""
                        # globs.dorx = 1
                        line = cl_file.readline()   # do this in extra thread!
                        print("L:"+str(line))
                        line=str(line)
                except Exception as e:
                    print("e:"+str(e))
                    pass
                if "stopall" in line:
                    dorun = 0
                    break
                if "stop" in line:
                    break
                if "test" in line:
                    print("test")
                    cl.send(line)
                if " HTTP/" in line:
                    doclose = True
                if "eof!" in line:
                    doeof = 1
                    print("eof enabled.")
                if "listen=" in line:
                    dolisten = 0
                    print("listen disabled.")
                if "interv=" in line:
                    globs.interval_rx = int(line.split("=",1).strip())
                speed = ws.getValue()
                print("s:"+str(speed))
                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n')
                cl.send('Connection: close\r\n\r\n')
                cl.send("wind:"+str(speed))
                cl.send('<hr>\r\n')
                time.sleep(1)
                if doclose:
                    break
            print("br.close.")
            cl.close()
        except Exception as e:
            print("e:" + str(e))
        globs.tL.stop()
        cl.close()
    cl.close()
    ws=None
    globs.tL.stop()
    print("siserv-fin.")
# eof
