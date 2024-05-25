# gwxcontroller main core

import time
import windsensor
import HYT221 
import comu
from machine import Pin, RTC
import json

__version__ = "0.1.1a"

PIN_WIND = 35   # Pin(35, Pin.IN, pull=Pin.PULL_UP)    # pin35 is also ADC1_7
PIN_SCL1 = 5
PIN_SDA1 = 4
PIN_SCL2 = 19
PIN_SDA2 = 18
PIN_LED1 = Pin(22, Pin.OUT)
PIN_WATER1 = Pin(22, Pin.OUT)
PIN_WATER2 = Pin(23, Pin.OUT)
PIN_MOTOR1 = Pin(25, Pin.OUT)
PIN_MOTOR1D = Pin(26, Pin.OUT)
PIN_MOTOR2 = Pin(27, Pin.OUT)
PIN_MOTOR2D = Pin(14, Pin.OUT)
# pins 32+33 are xtal32
# 22,21: scl/sda

class globs:
    verbosity = 2
    cfgfile = "gwxctrl.cfg"
    ws, hy1, hy2 = None, None, None
    serv = None
    uart = None
    rx = []
    last_motorstate = [b"0",b"0"]   # possible: "u","d","0" // up, down, off
    last_waterstate = [0,0]     # possible: 0,1
    port = 80
    dorun = True
    cfg = None
    lasttime = 0
    todos = [("15:00","nop")]

def servCB(msg=None):
    if globs.verbosity:
        print("m:"+str(msg))
    globs.rx.append(msg)

def setMotor(num, direction):
    if globs.verbosity:
        print("m:",num,direction)
    if not isinstance(num,int):
        num = int(str(num)[-1])
    d = str(direction.strip()).replace("'","")[-1].lower()
    sw = {"0":[0,0],"d":[1,0],"u":[1,1],"o":[0,0]}  # pinoutput for: motor,direction
    sw2=sw.get(d,None)
    if not sw2 or num <1 or num >2:
        print("Warning: wrong values:", num, direction)
        return
    pd=[PIN_MOTOR1D, PIN_MOTOR2D][num-1]
    pm=[PIN_MOTOR1, PIN_MOTOR2][num-1]
    pm.value(0)
    pd.value(sw2[1])     # direction 1=up
    pm.value(sw2[0])     # motor on/off
    globs.last_motorstate[num-1] = sw.encode()

def setWater(num, onOff=None):
    if globs.verbosity:
        print("w:",num,onOff)
    if not isinstance(num,int):
        num = int(str(num)[-1])
    if not isinstance(onOff,int):
        onOff = int(str(onOff)[-1])
    p=[PIN_WATER1, PIN_WATER2][num-1]
    p.value(onOff)
    globs.last_waterstate[num-1] = onOff

def getMotor(num):
    pd=[PIN_MOTOR1D, PIN_MOTOR2D][num-1]
    pm=[PIN_MOTOR1, PIN_MOTOR2][num-1]
    m = pm.value()
    d = pd.value()
    status = ["0","d","?","u"][m|(d<<1)]
    return status

def toggleLed():
    PIN_LED1.value(not PIN_LED1.value())

def getTime(offset_m=None):
    "param: offset in minutes"
    d = RTC().datetime()
    if offset_m:
        if offset_m > 23*60:
            offset_m = 23 * 60
            print("Warnung! offset sehr gross:"+offset_m)
        d[5]+=offset_m
        while d[5]>59:
            d[5]-=60
            d[4] += 1   # next hour
        if d[4] >23:
            d[4] -= 24  # next day
    return  f"{d[4]:02}:{d[5]:02}:{d[6]:02}"

def dictLower(d):
    for k in list(d):
        if isinstance(d[k], dict):
            dictLower(d[k])
        if k.lower() != k:
            d[k.lower()] = d.pop(k)

def readConfig(filename="gwxctrl.cfg"):
    cfg = None
    msg = "Lese Einstellungen von:"+filename
    print(msg)
    comu.addTx(msg)
    with open(filename,"r") as f:
        cfg = json.load(f)
    if not cfg:
        msg = "Fehler! konnte config nicht laden!"
        print(msg)
        comu.addTx(msg)
        return
    dictLower(cfg)
    globs.cfg = cfg
    msg = "Einstellungen geladen"
    if "verbosity" in cfg:
        globs.verbosity = cfg["verbosity"]
    if globs.verbosity:
        msg += str(cfg)
    print(msg)
    comu.addTx(msg)

def init():
    print("GwxControl version:" + str(__version__))
    globs.ws = windsensor.Windsensor(PIN_WIND)
    globs.hy1 = HYT221.HYT221(PIN_SCL1, PIN_SDA1)
    globs.hy2 = HYT221.HYT221(PIN_SCL2, PIN_SDA2)
    comu.globs.callbackRx = servCB
    globs.uart = comu
    comu.init(2)
    print("init done.")
    readConfig(globs.cfgfile)
    globs.lasttime = getTime()

def getTH(sensor):
    try:
        s=sensor.getValues(postdec=1)
        t,h = s.temperature, s.humidity
    except Exception as e:
        t,h = None, None
        print("eTh:"+str(e))
    return "Temperatur: "+str(t)+"°C\r\nLuftfeuchte: "+str(h)+"%"

def parseMsg():
    try:
        msg = globs.rx.pop()
        if "motor" in msg:
            num = msg.split(b"motor", 1)[1].strip()
            num,direction = num.split(b"=", 1)
            if direction == b"?":
                msg = "Motor1:"+getMotor(1)+". Motor2:"+getMotor(2)
                if globs.verbosity:
                    print(msg)
                comu.addTx(msg)
        if "wasser" in msg:
            num = msg.split(b"wasser", 1)[1].strip()
            num,direction = num.split(b"=", 1)
            setWasser(num, direction)
        if "testalarm" in msg:
            sendAlarm("test:"+str(msg))
        if "fwupdate!!" in msg:
            sendAlarm("stop für fw-update:"+str(msg))
            # globs.dorun = False
            for i in range(40):
                toggleLed()
                time.sleep(.5)
            print("back.")
    except Exception as e:
        print("error in parseMsg:"+str(e))

def sendAlarm(msg):
    if globs.verbosity:
        print("Alarm:",msg)
    comu.addTx("Alarm:"+str(msg))

def checkTemp(hausnum):
    sensor = [globs.hy1, globs,hy2][hausnum-1]
    s = getTH(sensor)
    cfg = globs.cfg["haus"+str(hausnum)]
    if s.temperature > cfg["tmax"]:
        setMotor(hausnum,"u")
    if s.humidity > cfg["hmax"]:
        setMotor(hausnum,"u")
    if s.temperature < cfg["tmin"]:
        setMotor(hausnum,"d")
    if s.humidity < cfg["hmin"]:
        globs.todos.append((getTime(1), "wasser"+str(hausnum)+"=0"))
        setWater(hausnum,1)

def checkTimer():
    """
    go through all timer elements.

    """
    if not "timer" in globs.cfg:
        return
    ti = globs.cfg["timer"]
    for t in ti:
        z,zEnd = ti[t], None
        on, off = "=1","=0"
        t=t.replace("lueften","motor")
        t=t.replace("fenster","motor")
        if "motor" in t:
            on, off = "=u", "=d"
        if isinstance(z, (list,tuple)):
            z,zEnd = z[:2]
        z = z.replace("-","").strip()
        if not z:
            continue
        if z < globs.lasttime:
            continue
        if z <= getTime():
            globs.rx.append(t + on)
        if zEnd:
            if zEnd < globs.lasttime:
                continue
            if zEnd <= getTime():
                globs.rx.append(t + off)

def formTime(text):
    h=text.split(":",1)
    if len(h)<2:
        text="0"+text
    return text

def main():
    while True:     # globs.dorun:     # do forever
        toggleLed()     # heartbeat
        try:
            speed = -1
            if globs.ws:
                speed = round(globs.ws.getValue())
        except Exception as e:
            print("eWs:"+str(e))
        ths ="sp:"+str(speed)+"\r\n"
        ths += "th1:" + getTH(globs.hy1)+"\r\n" + \
              "th2:" + getTH(globs.hy2)
        comu.globs.ths = ths+"\r\n"
        print(ths)
        motors = "Motoren: "+str(globs.last_motorstate)+"\r\n"
        fenster = "Fenster: ?\r\n"
        comu.globs.tx.append(motors)
        comu.proc()
        if globs.rx:
            parseMsg()
        else:
            time.sleep(.5)

        checkTemp(1)
        checkTemp(2)
        checkTimer()

        for todo in todos:
            t=formTime(todo[0])
            if t<globs.lasttime:
                continue
            if t<getTime():     # do it
                todos.remove(todo)  # remove from queue
                m=todo[1]
                globs.rx.append(m)

        globs.lasttime = getTime()  # last line !
# eof
