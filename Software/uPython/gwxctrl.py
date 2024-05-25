# gwxcontroller main core

import time
import network
import windsensor
import HYT221 
import simpleserv

__version__ = "0.0.1b"

PIN_WIND = 14
PIN_SCL1 = 5
PIN_SDA1 = 4
PIN_SCL2 = 19
PIN_SDA2 = 18
PIN_WATER1 = 26
PIN_WATER2 = 27

class globs:
    verbosity = 2
    cfgfile = "gwxc.cfg"
    ws, hy1, hy2 = None, None, None
    serv = None
    uart = None
    rx = []
    last_motorstate = ["0","0"]   # possible: "u","d","0" // up, down, off
    last_waterstate = [0,0]     # possible: 0,1

def servCB(msg=None):
    if globs.verbosity:
        print("m:"+str(msg))
    globs.rx.append(msg)

def setMotor(num, direction):
    if globs.verbosity:
        print("m:",num,direction)

def setWater(num, direction):
    if globs.verbosity:
        print("w:",num,direction)

def init():
    print("GwxControl version:" + str(__version__))
    globs.ws = windsensor.Windsensor(14)
    globs.hy1 = HYT221.HYT221(PIN_SCL1, PIN_SDA1)
    globs.hy2 = HYT221.HYT221(PIN_SCL2, PIN_SDA2)
    simpleserv.globs.callbackRx = servCB
    globs.serv = simpleserv.init(80)
    globs.uart = None
    print("init done.")

def getTH(sensor):
    try:
        s=sensor.getValues(round=1)
        t,h = s.temperature, s.humidity
    except Exception as e:
        t,h = None, None
    return "Temperatur: "+str(t)+"°C\r\nLuftfeuchte: "+str(h)+"%"

def parseMsg():
    try:
        msg = globs.rx.pop()
        if "motor" in msg:
            num = msg.split("motor", 1)[1].strip()
            num,direction = num.split("=", 1)
            if globs.last_motorstate[num] != direction:
                setMotor(num, direction)
        if "wasser" in msg:
            num = msg.split("wasser", 1)[1].strip()
            num,direction = num.split("=", 1)
            setWasser(num, direction)
        if "testalarm" in msg:
            sendAlarm("test:"+msg)
    except Exception as e:
        print("error in parseMsg:"+str(e))

def sendAlarm(msg):
    if globs.verbosity:
        print("Alarm:",msg)

def main():
    while True:     # do forever
        if globs.ws:
            speed = round(globs.ws.getValue())
        simpleserv.windspeed = speed
        print("sp:"+str(speed)+"\r\n")
        ths = "th1:" + getTH(globs.hy1)+"\r\n" + \
              "th2:" + getTH(globs.hy2)
        simpleserv.ths = ths
        print(ths+"\r\n")
        motors = "Motoren: "+str(globs.last_motorstate)+"\r\n"
        fenster = "Fenster: ?\r\n"
        simpleserv.tx.append(motors)
        simpleserv.proc()
        if globs.rx:
            parseMsg()
        else:
            time.sleep(.5)

# eof
