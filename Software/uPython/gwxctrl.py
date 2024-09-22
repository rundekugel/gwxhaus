# gwxcontroller main core

import time
import json

import machine, esp32
from machine import Pin, RTC, deepsleep, WDT
from ucryptolib import aes
from os import urandom
from binascii import hexlify
from hashlib import sha256

import windsensor
import HYT221 
import comu
import docrypt

__version__ = "0.3.1"

MODE_CBC = 2
# pinning for esp32-lite
PIN_WIND = 13   # Pin(35, Pin.IN, pull=Pin.PULL_UP)    # pin35 is also ADC1_7
PIN_SCL1 = 5
PIN_SDA1 = 4
PIN_SCL2 = 2
PIN_SDA2 = 15
PIN_LED1 = Pin(22, Pin.OUT)	 # on bigger boards it's pin2
PIN_WATER1 = Pin(27, Pin.OUT)
PIN_WATER2 = Pin(33, Pin.OUT)
PIN_MOTOR1 = Pin(25, Pin.OUT)
PIN_MOTOR1D = Pin(26, Pin.OUT)
PIN_MOTOR2 = Pin(12, Pin.OUT)
PIN_MOTOR2D = Pin(14, Pin.OUT)
PIN_END1UP = Pin(34, Pin.IN)
PIN_END1DOWN = Pin(35, Pin.IN)
PIN_END2UP = Pin(19, Pin.IN)
PIN_END2DOWN = Pin(23, Pin.IN)
DOSE1 = Pin(32, Pin.OUT)
# pin35 can only be input
# DOSE2 = Pin(35, Pin.OUT)
# PIN_POWER_GOOD = Pin(13, Pin.IN, Pin.PULL_DOWN)
ADC_BATT = machine.ADC(39)      # VN
PINNUM_POWER = 36
ADC_POWER = machine.ADC(PINNUM_POWER)     # VP
# pins 32+33 are xtal32
# 22,21: scl/sda esp8266?
# esp32: scl/sda: 25/26 ; 18/19

# ALLOWED_UART_VARS_W = ("loop_sleep","verbosity")
# ALLOWED_UART_VARS_R = ("loop_sleep","verbosity","globs","cfg","todos")
SECRET_GLOBS = ("ak")   # don't display this value to public

class globs:
    verbosity = 2
    cfgfile = "gwxctrl.cfg"
    ws, hy1, hy2 = None, None, None
    serv = None
    inited=False
    # uart = None
    rx = []
    # last_motorstate = [b"0",b"0"]   # possible: "u","d","0" // up, down, off
    # last_waterstate = [0,0]     # possible: 0,1
    port = 80
    dorun = True
    cfg = {"vccok":[4,30e3], "dsonbat":[[3.5,60e3],[3.3,300e3]], 
        "sensf1":50,"sensf2":50, "mot_openpersec1":1.2, "mot_openpersec2":1.3}
    lasttime = 0
    todos = [("15:00","nop")]
    loop_sleep = 2.5
    sturm = 0
    sturmdelay_on = 10
    sturmdelay_off = 100
    deepsleep_ms = 0
    lightsleep_ms = 0
    encoder = None
    decoder = None
    iv = b""
    modcfg = ""
    wdttime = 20
    manually_timeend = 0
    checkEndSwitch_lastTime = 0
    window_virtual_open1 = 0 # value in percent
    window_virtual_open2 = 0

def servCB(msg=None):
    if globs.verbosity:
        print("m:"+str(msg))
    globs.rx.append(msg)

def setMotor(num, direction):
    if globs.verbosity:
        print("m:", num, direction)
    if not isinstance(num, int):
        num = int(str(num).replace("'", "")[-1])
    d = str(direction).strip().replace("'", "")[-1].lower()
    if d=="u" and globs.sturm:
        return
    sw = {"0": [0, 0], "d": [1, 0], "u": [1, 1], "o": [0, 0]}  # pinoutput for: motor,direction
    sw2=sw.get(d, None)
    if not sw2 or num <1 or num >2:
        print("Warning: wrong values:", num, direction)
        return
    pd=[PIN_MOTOR1D, PIN_MOTOR2D][num-1]
    pm=[PIN_MOTOR1, PIN_MOTOR2][num-1]
    pm.value(0)
    pd.value(sw2[1])     # direction 1=up
    pm.value(sw2[0])     # motor on/off
    # globs.last_motorstate[num-1] = sw.encode()

def setWater(num, onOff=None):
    num = int(num)
    if globs.verbosity:
        print("w:",num,onOff)
    if not isinstance(num,int):
        num = int(str(num).replace("'","")[-1])
    if not isinstance(onOff,int):
        onOff = int(str(onOff).replace("'","")[-1])
    p=[PIN_WATER1, PIN_WATER2][num-1]
    p.value(onOff)
    # globs.last_waterstate[num-1] = onOff


def setDose(num, onOff=None):
    num = int(num)
    if globs.verbosity:
        print("d:",num,onOff)
    if not isinstance(num,int):
        num = int(str(num).replace("'","")[-1])
    if not isinstance(onOff,int):
        onOff = int(str(onOff).replace("'","")[-1])
    p=[DOSE1, DOSE2][num-1]
    p.value(onOff)
    # globs.last_waterstate[num-1] = onOff

def getMotor(num, lang=""):
    num=int(num)
    pd=[PIN_MOTOR1D, PIN_MOTOR2D][num-1]
    pm=[PIN_MOTOR1, PIN_MOTOR2][num-1]
    m = pm.value()
    d = pd.value()
    if lang == "de":
        status = ["Aus", "Zu", "?", "Auf"][m | (d << 1)]
    else:
        status = ["0","d","?","u"][m|(d<<1)]
    return status

def getWater(num, lang=""):
    p=[PIN_WATER1, PIN_WATER2][num-1]
    v=p.value()
    if lang == "de":
        return ["Zu", "Auf"][v]
    return v

def getDose(num, lang=""):
    p=[DOSE1, DOSE2][num-1]
    v=p.value()
    if lang == "de":
        return ["Aus", "An"][v]
    return v

def toggleLed():
    PIN_LED1.value(not PIN_LED1.value())

def getTime(offset_m=None):
    """param: offset in minutes"""
    d = RTC().datetime()
    if offset_m:
        d = list(d)	
        if offset_m > 23*60:
            offset_m = 23 * 60
            print("Warnung! offset sehr gross:"+str(offset_m))
        d[5]+=offset_m
        while d[5]>59:
            d[5]-=60
            d[4] += 1   # next hour
        if d[4] >23:
            d[4] -= 24  # next day
    return f"{d[4]:02}:{d[5]:02}:{d[6]:02}"

def dictLower(d):
    for k in list(d):
        if isinstance(d[k], dict):
            dictLower(d[k])
        if k.lower() != k:
            d[k.lower()] = d.pop(k)

def pubconfig(cfg):
    cfg_tmp = dict(cfg)
    for c in SECRET_GLOBS:
        cfg_tmp.pop(c ,None)  # remove secrets before show cfg
    return cfg

def readConfig(filename="gwxctrl.cfg"):
    cfg = None
    msg = "Lese Einstellungen von:"+filename
    if globs.verbosity:
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
    globs.cfg.update(cfg)
    msg = "Einstellungen geladen"
    if "verbosity" in cfg:
        globs.verbosity = cfg["verbosity"]
    if globs.verbosity:
        msg += str(pubconfig(cfg))
        print(msg)
        comu.addTx(msg)
        
def updateConfigFile(addcfg, filename="gwxctrl.cfg"):
    cfg = None
    with open(filename,"r") as f:
        cfg = json.load(f)
    if not cfg:
        msg = "Fehler! konnte config nicht laden!"
        print(msg)
        comu.addTx(msg)
        return
    dictLower(cfg)
    dictLower(addcfg)
    cfg.update(addcfg)
    with open(filename,"w") as f:
        json.dump(cfg,f)
    return

def init():
    print("GwxControl version:" + str(__version__))
    globs.checkEndSwitch_lastTime = time.time()
    readConfig(globs.cfgfile)
    globs.ws = windsensor.Windsensor(PIN_WIND, diameter=globs.cfg.get("windsensordia",None))
    globs.ws.verbosity = globs.verbosity
    addr1 = globs.cfg.get("sensoraddr1")      # this is None, if not given
    #freq = 50
    f=globs.cfg.get("sensf1")
    #if f: freq=f
    globs.hy1 = HYT221.HYT221(PIN_SCL1, PIN_SDA1, addr1, freq=f)    # if addr1 is None, default is used
    addr2 = globs.cfg.get("sensoraddr2")
    #freq = 50
    f=globs.cfg.get("sensf2")
    #if f: freq=f
    globs.hy2 = HYT221.HYT221(PIN_SCL2, PIN_SDA2, addr2, freq=f)
    globs.hy1.verbosity = globs.verbosity
    globs.hy2.verbosity = globs.verbosity
    comu.globs.callbackRx = servCB
    comu.globs.verbosity = globs.verbosity
    ADC_BATT.atten(machine.ADC.ATTN_11DB)    # set to 3.3V range
    ADC_POWER.atten(machine.ADC.ATTN_11DB)
    esp32.wake_on_ext0(pin=PINNUM_POWER, level=esp32.WAKEUP_ANY_HIGH)
    ak = globs.cfg.get("ak")
    if ak:
        docrypt.init(ak = ak)
    # globs.uart = comu
    comu.init(2, globs.cfg.get("baudrate"))
    rc = machine.reset_cause()
    comu.addTx("resetcause:"+str(rc))
    if globs.verbosity:
        print("resetcause:"+str(rc))
    if machine.DEEPSLEEP_RESET == rc:
        if globs.verbosity:
            print("wake up from deepsleep...")
        # read values from nvr
        cfg = RTC().memory()
        RTC().memory(b"")  # erase, don't use this values next time
        comu.addTx(cfg)
        time.sleep(1)  # time for client to send infos, before goto deep sleep again
        try:
            cfg = json.loads(cfg)
            globs.lasttime = cfg.get("t")
            if cfg.get("deepsleeprepeat"):
                globs.deepsleep_ms = int(cfg.get("ds") * 1000)
        except Exception as e:
            # cfgok=0
            comu.addTx("Fehler: Lesen von RTC-RAM:"+str(e))
        # if voltage is back, clear deepsleep
        if getVCCVolt() >4:
            globs.deepsleep_ms = 0

    globs.lasttime = getTime()
    
    pinsReset()
    
    test_activated = 0
    if test_activated:
        globs.hy1.testremotecontrol=(0,40,20)
        globs.hy2.testremotecontrol=(0,42,22)

    if globs.verbosity:
        print("init done.")
    globs.inited = True

def pinsReset():
    PIN_WATER1.value(0)
    PIN_WATER2.value(0)
    PIN_MOTOR1.value(0)
    PIN_MOTOR1D.value(0)
    PIN_MOTOR2.value(0)
    PIN_MOTOR2D.value(0)

def getTH(sensor,num):
    try:
        s=sensor.getValues(postdec=1)
        t,h = s.temperature, s.humidity
    except Exception as e:
        t,h = "-", "-"
        if globs.verbosity:
            print("err.Th:"+str(e))
    return f"T{num}:{t};H{num}:{h}"

def parseMsg():
    """execute all cmds in globs.rx"""
    try:
        msg=None
        if globs.verbosity > 1:
            print("PM.")
        while globs.rx and not msg:
            msg = globs.rx.pop().strip()
            if globs.verbosity>1:
                print("pM:"+str(msg))
        if not msg:
            return
        cmd, val = msg, ""
        if isinstance(cmd, str):
            cmd = cmd.encode()
        if b"=" in cmd:
            cmd, val = cmd.split(b"=",1)
            val=val.strip() ; cmd=cmd.strip()
        if globs.verbosity > 1:
            print("pM:", cmd, val)
        if b"motor" in cmd:
            num = cmd[-1:]
            direction = val
            if direction == b"?":
                msg = "Motor1:"+getMotor(1)+". Motor2:"+getMotor(2)
                if globs.verbosity:
                    print(msg)
                comu.addTx(msg)
            else:
                setMotor(num, direction)
            return
        if b"wasser" in cmd:
            num = cmd[-1:]
            direction = val
            if direction == "?":
                comu.addTx(f"Wasser1:{getWater(1)}, Wasser2:{getWater(2)}")
            else:
                setWater(num, direction)
            return
        if b"dose" in cmd:
            num = cmd[-1:]
            direction = val
            if direction == "?":
                comu.addTx(f"dose1:{getDose(1)}, dose:{getDose(2)}")
            else:
                setDose(num, direction)
            return
        if b"testalarm" in cmd:
            sendAlarm("test:"+str(msg))
            return
        if b"fwupdate!!" in cmd:
            sendAlarm("pause für fw-update:"+str(msg))
            # globs.dorun = False
            for i in range(40):
                toggleLed()
                time.sleep(.5)
            print("back.")
        if b"fwmainstop!!" in cmd:
            sendAlarm("stop für fw-update:"+str(msg))
            globs.dorun = False
        if b"todos?" in msg:
            comu.addTx(str(globs.todos))
        elif b"todo" in msg:
            if "grfx" in val:
                val = val.replace("grfx","")
                if globs.verbosity: print("todo:"+str(val))
                globs.todo.append(val)
        if b"globs?" in msg:
            g = dict(globs.__dict__)    # make a copy
            g.pop("cfg", None)
            comu.addTx(str(pubconfig(g)))
        if b"cfg?" in msg:
            comu.addTx(str(pubconfig(globs.cfg)))
        if b"verbosity" in cmd:
            globs.verbosity = int(val)
            comu.globs.verbosity = int(val)
        if b"interval" in cmd:
            globs.loop_sleep = int(val)/10
            comu.addTx(f"loop sleep:{globs.loop_sleep}s")
        if b"rtc" == cmd:
            ti = val.split(b',')
            tii=[]
            for t in ti:
                tii.append(int(t))
            while len(tii)<8:
                tii.append(0)
            RTC().init(tii)
        if b"reset!" == cmd:
            machine.reset()
        if b"deepsleep" in cmd:
            globs.deepsleep_ms = int(val)*1000
            if globs.verbosity:
                print(f"deepsleep {globs.deepsleep_ms} sec.")
            return
        if b"bat?" in cmd:
            m = f"Battery: {ADC_BATT.read_uv()*2/1e6} V."
            comu.addTx(m)
            if globs.verbosity:
                print(m)
        if b"power?" in cmd:
            m = f"Power: {ADC_POWER.read_uv()*2/1e6} V."
            comu.addTx(m)
            if globs.verbosity:
                print(m)
        if b"iv?" in cmd:
            m = f"iv: {hexlify(globs.iv)}."
            comu.addTx(m)
            if globs.verbosity:
                print(m)
        if b"i2cscan" in cmd:
            hy = [globs.hy1, globs.hy2][int(val)]
            devs = hy.scan()
            m= b"I2C devices found: "+str(devs).encode() +b" = "+hexlify(bytes(devs), " ")
            if globs.verbosity: print(m)
            comu.addTx(m)
        if b"manually" in cmd:
            globs.manually_timeend = time.time() + int(val)
        if b"am:" in cmd[:3]:
                encrypted = cmd[3:]
                m = docrypt.parse(dec)
                if globs.verbosity:
                    print(m)
                comu.addTx(m)
        if b"modcfgs" in cmd:
            if not val: val=b""
            globs.modcfg = val
        if b"modcfga" in cmd:
            globs.modcfg += val
        if b"modcfg." in cmd:
            globs.modcfg += val
            globs.modcfg = globs.modcfg.decode()
            if globs.verbosity: print(globs.modcfg)
            j=json.loads(globs.modcfg)
            if globs.verbosity: print(str(j))
            updateConfigFile(j)
            globs.modcfg=""
            comu.addTx("updated: "+str(j))
                
    except Exception as e:
        if globs.verbosity:
            print("error in parseMsg:"+str(e))

def sendAlarm(msg):
    if globs.verbosity:
        print("Alarm:",msg)
    comu.addTx("Alarm:"+str(msg))

def checkTemp(hausnum):
    sensor = [globs.hy1, globs.hy2][hausnum-1]
    s = sensor.getValues(postdec=1)
    if not s:
        return
    cfg = globs.cfg["haus"+str(hausnum)]

    if s.temperature > cfg.get("talarm",40):
        sendAlarm(f"Temperatur in Haus{hausnum}:{s.temperature}°C")

    # 'manually control' set?
    if globs.manually_timeend > time.time():
        return
    globs.manually_timeend = 0  # if RTC will be reset after power-loss. This helps. 

    if s.temperature > cfg["tmax"]:
        setMotor(hausnum,"u")
    if s.temperature < cfg["tmin"]:
        setMotor(hausnum,"d")
        
    if s.humidity > cfg["hmax"]:
        setMotor(hausnum,"u")
        setWater(hausnum, 0)
    if s.humidity < cfg["hmin"]:
        if getWater(hausnum) == 0:
            setWater(hausnum,1)
            globs.todos.append((getTime(1), "wasser"+str(hausnum)+"=0"))

def checkTimer():
    """
    go through all timer elements.
    element: "name":["timeStart","timeStop"]
      name: device to switch
      timeStart: "HH:MM". if no start time, use empty string: ""
      timeStop: "HH:MM". (optional)
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
        z = formTime(z)
        if z < globs.lasttime:
            continue
        if z <= getTime():
            globs.rx.append(t + on)
        if zEnd:
            zEnd = formTime(zEnd)
            if zEnd < globs.lasttime:
                continue
            if zEnd <= getTime():
                globs.rx.append(t + off)

def getBatVolt(rounded=2):
    v, n = 0, 10
    for i in range(n):
       v += ADC_BATT.read_uv()*2/1e6
    return round(v / n, rounded)

def getVCCVolt(rounded=2):
    v, n = 0, 10
    for i in range(n):
       v += ADC_POWER.read_uv()*2/1e6
    return round(v / n, rounded)

def checkWind():
    """
    if too much wind, wait a little, before storm-alarm.
    if storm is over, wait some time, for really end of storm.
    """
    speed = globs.ws.getValue()
    if not speed:
        return
    try:
        if speed > globs.cfg["wind"]["max"]:
            globs.sturm +=1
            if speed > globs.cfg["wind"]["max"] *2:
                globs.sturm += globs.sturmdelay_on
            if globs.sturm > globs.sturmdelay_on:
                if globs.verbosity:
                    print("Sturm. Alle Fenster werden geschlossen.")
                setMotor(1,"d")
                setMotor(2,"d")
        else:
            if globs.sturm > globs.sturmdelay_off:
                globs.sturm = globs.sturmdelay_off
            if globs.sturm:
                globs.sturm -= 1

    except:
        pass
        
def checkEndSwitch():
    #if not hasattr(checkEndSwitch, "lastTime"):
    #    checkEndSwitch.setattr("lastTime", time.time())
    timedelta = time.time() - globs.checkEndSwitch_lastTime
    checkEndSwitch_lastTime = time.time()
    try:
        step = timedelta * float(globs.cfg["mot_openpersec1"])
        if getMotor(1) == "d":
            globs.motor1_virtual_open -= step
            if PIN_END1DOWN.value ==0:
                globs.motor1_virtual_open = 0
                setMotor(1,0)
        if getMotor(1) == "u":
            globs.motor1_virtual_open += step
    except Exception as e:
        print(str(e))
        
    try:
        step = timedelta * float(globs.cfg["mot_openpersec2"])
        if getMotor(2) == "d":
            globs.motor1_virtual_open -= step
            if PIN_END2DOWN.value ==0:
                globs.motor2_virtual_open = 0
                setMotor(2,0)
        if getMotor(2) == "u":
            globs.motor1_virtual_open += step
    except Exception as e:
        print(str(e))
        
    return        

def formTime(text):
    h=text.split(":",1)
    if len(h)<2:
        text="0"+text
    return text

def main():
    globs.wdt=None
    # wdt=WDT(timeout=globs.wdttime*1000)
    speed = -1
    if not globs.inited:
        # wdt.feed()
        init()
    globs.wdt=WDT(timeout=int(globs.wdttime*1000))
    
    while globs.dorun:     # do forever
        globs.wdt.feed()
        toggleLed()     # heartbeat
        try:
            speed = -1
            if globs.ws:
                speed = globs.ws.getValue()
        except Exception as e:
            if globs.verbosity:
                print("eWs:"+str(e))
        ths ="sp:"+str(speed)+ "; " 
        ths += getTH(globs.hy1,1) +"; "+ getTH(globs.hy2,2)
        comu.addTx(ths)
        if globs.verbosity:
            # print(ths)
            pass
        motors = "M1:"+getMotor(1, 'de')+"; M2:"+getMotor(2, 'de')
        motors += ";F1:"+str(globs.window_virtual_open1)+"; F2:"+str(globs.window_virtual_open2)
        water = f"W1:{getWater(1, 'de')}; W2:{getWater(2, 'de')}"
        # fenster = "Fenster: ?\r\n"  # todo. need 8 gpios first.
        comu.addTx(motors)
        comu.addTx(water)
        if globs.sturm:
            comu.addTx(f"Sturm:{globs.sturm}")
        comu.addTx(f"USB={getVCCVolt()}V ; Bat.={getBatVolt(2)}V.")
        d=globs.manually_timeend - time.time()
        if d<0:d=0
        comu.addTx(f"mn:{d}");
        if globs.verbosity:
            print(comu.globs.tx)
        comu.proc()
        end=globs.loop_sleep *2
        while end >0:
            if globs.rx:
                break
            time.sleep(.5)
            end -= .5
        parseMsg()

        # check for command which must be executed at a specific time.
        checkTemp(1)
        checkTemp(2)
        checkTimer()

        for todo in globs.todos:
            t=formTime(todo[0])
            if t<globs.lasttime:
                continue
            if t<getTime():     # do it
                globs.todos.remove(todo)  # remove from queue
                m=todo[1]
                globs.rx.append(m)  # will be done in parseMsg()
                continue

        checkWind()
        globs.lasttime = getTime()  # this line must be after all checks !

        checkEndSwitch()
        
        # sleep on power loss
        vccVal = globs.cfg.get("vccok")
        if vccVal:
            if getVCCVolt() > vccVal[0]:
                globs.lightsleep_ms = 0
            else:
                battV = getBatVolt()
                sendAlarm(f"gwxctrl Spannung zu klein: USB={getVCCVolt()}V ; Batt={battV}V.")
                globs.lightsleep_ms = int(vccVal[1])
                batSets = globs.cfg.get("dsonbat")  	# deepsleep on low bat
                if batSets:
                    for setting in batSets:
                        if battV < setting[0]:
                            globs.deepsleep_ms = int(setting[1])

        if globs.deepsleep_ms >0:  # if we run on battery. 
            msg = f"Goto deepsleep for {globs.deepsleep_ms/1000}s..."
            comu.addTx(msg)
            comu.proc()
            print(msg)
            pinsReset()
            time.sleep(.1)
            nv_info = {"t":globs.lasttime, "ds":globs.deepsleep_ms/1000}
            RTC().memory(json.dumps(nv_info))
            deepsleep(int(globs.deepsleep_ms))
        if globs.lightsleep_ms:
            comu.addTx(f"goto lightsleep for {globs.lightsleep_ms/1000}s.")
            comu.proc()
            time.sleep(.1)
            machine.lightsleep(globs.lightsleep_ms)
            comu.addTx(f"Woke up from lightsleep.")
    print("stopped.")
    return

if __name__ == "__main__":
    # test
    globs.rx.append(b"deepsleep=2")
    parseMsg()
# eof
