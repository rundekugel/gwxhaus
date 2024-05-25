# simple server
import socket
import time
import timer
import windsensor
import HYT221 
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

def main(port=80):
    print("simpleserv version:" + str(__version__))
    ws = windsensor.Windsensor(14)
    hy1 = HYT221.HYT221(PIN_SCL1, PIN_SDA1)
    hy2 = HYT221.HYT221(PIN_SCL2, PIN_SDA2)

    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(addr)
    except Exception as e:
        if globs.verbosity:
            print("eB:" + str(e))

    s.listen(1)
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
        try:
            while True:
                line=""
                try:
                    line = cl_file.readline()   # do this in extra thread!
                    line=str(line)
                    if globs.verbosity:
                        print("L:"+line)
                except Exception as e:
                    if globs.verbosity:
                        print("eL:"+str(e))
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
                    if globs.verbosity:
                        print("doclose.")
                if "eof!" in line:
                    doeof = 1
                    print("eof enabled.")
                if "listen=" in line:
                    dolisten = 0
                    print("listen disabled.")
                if "interv=" in line:
                    globs.interval_rx = int(line.split("=",1).strip())
                if line.strip() != "":    # read all server msg 1st, then respond
                    continue
                time.sleep(.5)
                speed = round(ws.getValue())
                print("s:"+str(speed))
                content = "Wind:"+str(speed)+"m/s.\r\n"
                content += "Sensor1:\r\n"
                try:
                    ht = str(hy1.getValues())
                except:
                    ht="Temp und Luft ausgefallen."
                content += ht+"\r\n"
                content += "Sensor2:\r\n"
                try:
                    ht = str(hy2.getValues())
                except:
                    ht="Temp und Luft ausgefallen."
                content += ht +"\r\n"
                # content += "Temperatur:"+str(round(ht.temperature,1))+"°C.\r\n"
                # content += "Luftfeuchte:" + str(round(ht.humidity, 1)) + "%.\r\n"
                content += "Motor: ?.\r\n"
                content += "<hr>\r\n"
                # cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html;charset=utf-8\r\n')
                cl.send('Content-type: text/html;charset=utf-8\r\n')
                cl.send("Content-Length: "+str(len(content)))
                cl.send('Connection: close\r\n\r\n')
                cl.send(content)
                if doclose:
                    cl.send('xxxxxx')
                    time.sleep(.1)
                    break
                time.sleep(.5)
            print("br.close.")
            time.sleep(.1)
            cl.close()
            # time.sleep(2)
        except Exception as e:
            print("eRun:" + str(e))
        cl.close()
    cl.close()
    ws=None
    print("siserv-fin.")
# eof
