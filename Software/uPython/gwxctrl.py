# gwxcontroller main core
"""
this code is intended to run on a esp32light with 2x13 pins

used pins:
pins 12,14,25,26,27,33 are all output and go to a buffer ic
pins 4,5 are for i2c1
pins 2.15 are for i2c2
pins 16,17 are for UART to wifi-esp32
pins 18,19,23 are for future usage (water-valves / heating / general purpose usage)
pin 13 windsensor
pin 22 on board led, used for heartbeat
pin 39 is used to measure battery voltage
pin 36 is used to measure power supply

unused:
pin 0,34,35

explanation for config parameter 'mot_openpersec1' and 'mot_openpersec2' for haus1/haus2 
 the value is, how far the window opens in one second. value in percent.
 
}
"""

import time
import json
import os
if not "ESP" in os.uname().machine:
    import sys
    sys.path.append("upyemu")
import machine, esp32
from machine import Pin, RTC, deepsleep, WDT
# from ucryptolib import aes
# from os import urandom
from binascii import hexlify
# from hashlib import sha256

# local libs:
import windsensor
import HYT221 
import comu
import docrypt

try:
    import revisionfile
except:
    class revisionfile:
        revision = "0000000"
        buildnumber = "0"

__revision__ = revisionfile.revision
__buildnumber__ = revisionfile.buildnumber
__version__ = "0.5.2-" + __revision__ + "-Build:" + str(revisionfile.buildnumber)

# ALLOWED_UART_VARS_W = ("loop_sleep","verbosity")
SECRET_GLOBS = ("ak", "watertables")   # don't display this value to public
DO_NOT_UPDATE = ("test_activated", "illegal")
DURATION_PER_LOOP_MAX = 9
MODE_CBC = 2
MOTOR_END_DELAY = 2  # delay motor switch off, if pos0 reached

USE_END_SWITCHES = 0
DIRECTION_SWITCH_DELAY_MS = 200 # if direction switches, motorpower must be securely off
POWER_SWITCH_DELAY_MS = 200

# pinning for esp32-lite
PIN_WIND = 13   # Pin(35, Pin.IN, pull=Pin.PULL_UP)    # pin35 is also ADC1_7
PIN_SCL1 = 5
PIN_SDA1 = 4
PIN_SCL2 = 2
PIN_SDA2 = 15
PIN_LED1 = Pin(22, Pin.OUT)  # on bigger boards it's pin2

PIN_WATER1 = Pin(27, Pin.OUT)
PIN_WATER2 = Pin(33, Pin.OUT)
PIN_WATER3 = Pin(32, Pin.OUT)
PIN_WATER4 = Pin(18, Pin.OUT)

PIN_MOTOR1 = Pin(25, Pin.OUT)   # hi=on
PIN_MOTOR1D = Pin(26, Pin.OUT)  # hi=up
PIN_MOTOR2 = Pin(12, Pin.OUT)   # hi=on
PIN_MOTOR2D = Pin(14, Pin.OUT)  # hi=up

PIN_END1UP = Pin(34, Pin.IN)
PIN_END1DOWN = Pin(23, Pin.IN, pull=Pin.PULL_UP)
PIN_END2UP = Pin(35, Pin.IN)    # pin35 can only be input
PIN_END2DOWN = Pin(19, Pin.IN, pull=Pin.PULL_UP)

DOSE1 = Pin(18, Pin.OUT)
DOSE2 = Pin(18, Pin.OUT)
DOSE3 = Pin(18, Pin.OUT)
DOSE4 = Pin(18, Pin.OUT)
DOSEN = [DOSE1, DOSE2, DOSE3, DOSE4]

ADC_BATT = machine.ADC(39)      # VN
PINNUM_POWER = 36   # needed for wakeup
ADC_POWER = machine.ADC(PINNUM_POWER)     # VP
# pins 32+33 are xtal32
# 22,21: scl/sda esp8266?
# esp32: scl/sda: 25/26 ; 18/19


class globs:
    """global variables"""
    verbosity = 2
    cfgfile = "gwxctrl.cfg"
    ws, hy1, hy2 = None, None, None
    serv = None
    inited=False
    rx = []
    port = 80
    dorun = True
    cfg = {"vccok":[4,30e3], "dsonbat":[[3.5,60e3],[3.3,300e3]], 
        "sensf1":50,"sensf2":50, "mot_openpersec1":1.2, "mot_openpersec2":1.3,
        "sturm":10.1, "wind": {"max": 7.1}
        }
    lasttime = 0
    todos = [("15:00","nop")]
    loop_sleep = 1 # we are slow enough. 1 sec. is enough.
    sturm = 0
    sturmdelay_on = 3
    sturmdelay_off = 30
    deepsleep_ms = 0
    lightsleep_ms = 0
    iv = b""
    modcfg = ""
    wdttime = 90
    manually_timeend = 0
    # checkFensterPosition_lastTime = time.time()
    checkWindowPosition_lastTime = 0
    window_virtual_open = [0,0] # value in percent
    # window_virtual_open2 = 0
    watertables = [180*b"\0"]*4
    test_activated = False  # for debug don't change here, but in config-file!
    window_pos_dest = [None,None]
    windowpos_map = [{"d":0, "u":100, "h":50,"s":None},{"d":0, "u":100, "h":50,"s":None}]
    window_pos_toleranz = 10   # percent
    motor_delay = [0,0]
    alarms = []
    
def servCB(msg=None):
    """this is called for incoming data"""
    if globs.verbosity:
        print("m:"+str(msg))
    globs.rx.append(msg)

def doMotors():
    """
    switch motors,
    depending on globs.window_pos_dest and globs.window_virtual_open.
    
    globs.motor_delay is used to drive the motors to end-position, for the case, if
    virtual motor position is at the end, but not the physical position.
    until now, it's only used to close the windows properly.
    """
    for num in (0,1):
        if globs.window_pos_dest[num] is None: #stop!
            setMotor(num + 1, "0")
            continue
        motordir = getMotor(num+1)
        if globs.window_pos_dest[num] > globs.window_virtual_open[num]:
            # too less open
            if motordir == 'd' and globs.window_pos_dest[num] <100:
                # destination is somewhere in the middle. stop.
                globs.window_pos_dest[num] = None
                setMotor(num + 1, "s")
                continue
            setMotor(num +1, "u")
            globs.motor_delay[num] = MOTOR_END_DELAY
        if globs.window_pos_dest[num] < globs.window_virtual_open[num]:
            # too wide open
            if motordir == 'u' and globs.window_pos_dest[num] >0:
                # destination is somewhere in the middle. stop.
                globs.window_pos_dest[num] = None
                continue
            setMotor(num +1, "d")
            globs.motor_delay[num] = MOTOR_END_DELAY
        if globs.window_pos_dest[num] == globs.window_virtual_open[num]:
            if globs.motor_delay[num]:
                globs.motor_delay[num] -=1
            else:
                globs.window_pos_dest[num] = None


def setMotor(num, direction):
    """
    set the pins to control the motors
    direction: u=up; d=down; s=stop; 0=stop
    """
    if globs.verbosity:
        print("m:", num, direction)
    if not isinstance(num, int):
        num = int(str(num).replace("'", "")[-1])
    d = str(direction).strip().replace("'", "")[-1].lower()
    if d == "u" and globs.sturm >= globs.cfg.get("sturm",10):
        return
    sw = {"0": [0, 0], "d": [1, 0], "u": [1, 1], "o": [0, 0], "s": [0, 0]}  # pinoutput for: motor,direction
    sw2 = sw.get(d, None)
    if not sw2 or num <1 or num >2:
        print("Warning: wrong values:", num, direction)
        return
    pd = [PIN_MOTOR1D, PIN_MOTOR2D][num-1]
    pm = [PIN_MOTOR1, PIN_MOTOR2][num-1]
    pm.value(0)
    time.time_ms(POWER_SWITCH_DELAY_MS)
    pd.value(sw2[1])     # direction 1=up
    time.time_ms(DIRECTION_SWITCH_DELAY_MS)
    pm.value(sw2[0])     # motor on/off

def setWater(num, onOff=None):
    """set the pins to control the water valves. onOff = 0|1"""
    if globs.verbosity:
        print("w:",num,onOff)
    if not isinstance(num,int):
        num = int(str(num).replace("'","")[-1])
    if not isinstance(onOff,int):
        onOff = int(str(onOff).replace("'","")[-1])
    p=[PIN_WATER1, PIN_WATER2, PIN_WATER3, PIN_WATER4][num-1]
    p.value(onOff)

def setDose(num, onOff=None):
    """set the pins to control general purpose output. onOff = 0|1"""
    if globs.verbosity:
        print("d:",num,onOff)
    if not isinstance(num,int):
        num = int(str(num).replace("'","")[-1])
    if not isinstance(onOff,int):
        onOff = int(str(onOff).replace("'","")[-1])
    p=DOSEN[num-1]
    p.value(onOff)

def getMotor(num, lang=""):
    """
     num: 1|2
     lang: if 'de' then return german texts
     retval: 0/aus, d/zu, u/auf
    """
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
    """
     num: 1|2
     lang: if 'de' then return german texts
     retval: 0/Zu, d/zu, u/Auf
    """
    p=[PIN_WATER1, PIN_WATER2, PIN_WATER3, PIN_WATER4][num-1]
    v=p.value()
    if lang == "de":
        return ["Zu", "Auf"][v]
    return v

def getDose(num, lang=""):
    p=DOSEN[num-1]
    v=p.value()
    if lang == "de":
        return ["Aus", "An"][v]
    return v

def toggleLed():
    """toggle the on-board-led"""
    PIN_LED1.value(not PIN_LED1.value())

def getTime(offset_m=None):
    """
    param: offset in minutes
    returns: time as string in format HH:MM:SS
    """
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
    """change keys in dict to lower case ==> keys are not case sensitive"""
    for k in list(d):
        if isinstance(d[k], dict):
            dictLower(d[k])
        if k.lower() != k:
            d[k.lower()] = d.pop(k)

def pubconfig(cfg):
    """return only config values, which are not private"""
    cfg_tmp = dict(cfg)
    for c in SECRET_GLOBS:
        cfg_tmp.pop(c ,None)  # remove secrets before show cfg
    return cfg_tmp

def readConfig(filename="gwxctrl.cfg"):
    """read config file and update globs.cfg with the result"""
    cfg = None
    msg = "Lese Einstellungen von:"+filename
    if globs.verbosity:
        print(msg)
        comu.addTx(msg)
    try:
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
        if globs.verbosity is None:
            globs.verbosity = 0
        if isinstance(globs.verbosity, str):
            try:
                globs.verbosity = int(globs.verbosity)
            except:
                globs.verbosity = 0
        if globs.verbosity:
            msg += str(pubconfig(cfg))
            print(msg)
            comu.addTx(msg)
    except Exception as e:
        msg = "!!! Fehler in readConfig !!!"+str(e)
        print(msg)
        comu.addTx(msg)
    return


def updateConfigFile(addcfg, filename="gwxctrl.cfg"):
    """update config file with new settings"""
    cfg = None
    with open(filename, "r") as f:
        cfg = json.load(f)
    if not cfg:
        msg = "Fehler! konnte config nicht laden!"
        print(msg)
        comu.addTx(msg)
        return False
    dictLower(cfg)
    dictLower(addcfg)
    for k in DO_NOT_UPDATE:
        addcfg.pop(k,0)
    if not addcfg:
        comu.addTx("empty cfg!")
        return False
    cfg.update(addcfg)
    with open(filename, "w") as f:
        json.dump(cfg, f)
    return True

def deleteFromConfigFile(key, filename="gwxctrl.cfg"):
    """delete one entry from configfile"""
    cfg = None
    with open(filename,"r") as f:
        cfg = json.load(f)
    if not cfg:
        msg = "Fehler! konnte config nicht laden!"
        print(msg)
        comu.addTx(msg)
        return
    dictLower(cfg)
    cfg.pop(key.lower())
    with open(filename,"w") as f:
        json.dump(cfg,f)
    return

def init():
    print("GwxControl version:" + str(__version__))
    # globs.checkWindowPosition_lastTime = time.time()
    readConfig(globs.cfgfile)
    diameter=globs.cfg.get("windsensordia",None)
    if diameter is not None:
        diameter=float(diameter) 
    globs.ws = windsensor.Windsensor(PIN_WIND, 
                    diameter=diameter)
    globs.ws.verbosity = globs.verbosity

    addr1 = globs.cfg.get("sensoraddr1")      # this is None, if not given
    f=globs.cfg.get("sensf1")
    globs.hy1 = HYT221.HYT221(PIN_SCL1, PIN_SDA1, addr1, freq=f)    # if addr1 is None, default is used
    addr2 = globs.cfg.get("sensoraddr2")
    f=globs.cfg.get("sensf2")
    globs.hy2 = HYT221.HYT221(PIN_SCL2, PIN_SDA2, addr2, freq=f)
    globs.hy1.verbosity = globs.verbosity
    globs.hy2.verbosity = globs.verbosity

    comu.globs.callbackRx = servCB
    comu.globs.verbosity = globs.verbosity
    ADC_BATT.atten(machine.ADC.ATTN_11DB)    # set to 3.3V range
    ADC_POWER.atten(machine.ADC.ATTN_11DB)
    esp32.wake_on_ext0(pin=PINNUM_POWER, level=esp32.WAKEUP_ANY_HIGH)

    ak = globs.cfg.get("ak")  # this key used for updates over the air, or critical config-values
    if ak:
        docrypt.init(ak = ak)

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
    for i in range(1,5):
        try:
          with open(f"watertimetable{i}.dat","rb") as f:
            globs.watertables[i-1] = f.read()
        except Exception as e:
            print(f"error wt{i}: "+str(e))

    globs.lasttime = getTime()
    
    pinsReset()
    
    if globs.cfg.get("test_activated"):
        globs.hy1.testremotecontrol=(0,41,21)
        globs.hy2.testremotecontrol=(0,42,22)
        PIN_END1UP.on()  # for simulator only
        PIN_END1DOWN.on()
        PIN_END2UP.on()
        PIN_END2DOWN.on()

    if globs.verbosity:
        print("init done.")
    globs.inited = True

def pinsReset():
    PIN_WATER1.value(0)
    PIN_WATER2.value(0)
    PIN_WATER3.value(0)
    PIN_WATER4.value(0)
    for d in DOSEN:
        d.value(0)
    PIN_MOTOR1.value(0)
    PIN_MOTOR1D.value(0)
    PIN_MOTOR2.value(0)
    PIN_MOTOR2D.value(0)

def getTH(sensor,num):
    """Sensor for temperature and humidity"""
    try:
        s=sensor.getValues(postdec=1)
        t,h = s.temperature, s.humidity
    except Exception as e:
        t,h = "-", "-"
        if globs.verbosity:
            print("err.Th:"+str(e))
    return f"T{num}:{t};H{num}:{h}"

def parseMsg():
    """execute cmds in globs.rx"""  # all or one
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
            cmd, val = cmd.split(b"=", 1)
            val = val.decode().strip() ; cmd = cmd.strip()
        if globs.verbosity > 1:
            print("pM:", cmd, val)
        if cmd[:-1] in (b"motor",b"fenster"):
            num = int(cmd[-1:])-1
            direction = val
            if direction == "?":
                msg = "M1:"+getMotor(1)+". M2:"+getMotor(2)
                if globs.verbosity:
                    print(msg)
                comu.addTx(msg)
            else:
                if val in ('u','d','h',"s"):
                    val = globs.windowpos_map[num].get(val,None)
                else:
                    val = int(val)
                globs.window_pos_dest[num] = val
                # setMotor(num, direction)
            return
        if b"wasser" in cmd:
            num = cmd[-1:]
            direction = val
            if direction == "?":
                comu.addTx(f"W1:{getWater(1)}, W2:{getWater(2)}, W3:{getWater(3)}, W4:{getWater(4)}")
            else:
                setWater(num, direction)
            return
        if b"dose" in cmd:
            num = cmd[-1:]
            direction = val
            if direction == "?":
                comu.addTx(f"D1:{getDose(1)}, D2:{getDose(2)}, D3:{getDose(3)}, D4:{getDose(4)}")
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
            if b"grfx" in val:
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
            ti = val.split(',')
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
            if not val: val=""
            globs.modcfg = val
        if b"modcfga" in cmd:
            globs.modcfg += val
        if b"modcfg." in cmd:
            globs.modcfg += val
            globs.modcfg = globs.modcfg.replace("'", '"')
            try:
                if globs.verbosity: print(globs.modcfg)
                j=json.loads(globs.modcfg)
                if globs.verbosity: print(str(j))
                if updateConfigFile(j):
                    comu.addTx("updated: "+str(j))
                else:
                    comu.addTx("not updated")
            except Exception as e:
                if globs.verbosity:
                    print("error in parseMsg:" + str(e))
            globs.modcfg = ""
        if b"delcfg" in cmd:
            if globs.verbosity: print("del:",val)
            deleteFromConfigFile(val)
            comu.addTx("deleted: "+str(j))
        if b"ws" in cmd:
            if globs.ws.testremotecontrol is not None:
                globs.ws.testremotecontrol = float(val)
        if b"version" in cmd:
            comu.addTx("Version: "+str(__version__))
                
    except Exception as e:
        if globs.verbosity:
            print("error in parseMsg:"+str(e))

def sendAlarm(msg):
    if globs.verbosity:
        print("Alarm:",msg)
    comu.addTx("Alarm:"+str(msg))

def checkTemp(hausnum):
    """
    check temperature and humidity and set window destination position
    switch on water, if too dry
    """
    try:
        sensor = [globs.hy1, globs.hy2][hausnum-1]
        s = sensor.getValues(postdec=1)
        if not s:
            return
        cfg = globs.cfg["haus"+str(hausnum)]

        if cfg.get("talarm"):
            tmaxFlag ="tmax"+str(hausnum)
            if s.temperature > cfg.get("talarm",40):
                if not tmaxFlag in globs.alarms:
                    globs.alarms.append(tmaxFlag)
                    sendAlarm(f"Temperatur in Haus{hausnum}:{s.temperature}°C")
            else:
                if tmaxFlag in globs.alarms:
                    globs.alarms.remove(tmaxFlag)
        
        tm = cfg.get("tminalarm")
        if tm:
            tminFlag ="tmin"+str(hausnum)
            if s.temperature < tm:
                if not tminFlag in globs.alarms:
                    globs.alarms.append("tmin"+str(hausnum))
                    sendAlarm(f"Temperatur in Haus{hausnum}:{s.temperature}°C")
            else:
                if tminFlag in globs.alarms:
                    globs.alarms.remove(tminFlag)

        # 'manually control' set?
        if globs.manually_timeend > time.time():
            return
        globs.manually_timeend = 0  # if RTC will be reset after power-loss. This helps.

        if s.temperature > cfg["tmax"]:
            #setMotor(hausnum,"u")
            globs.window_pos_dest[hausnum-1] = 100
        if s.temperature < cfg["tmin"]:
            globs.window_pos_dest[hausnum-1] = 0
        else:
            if s.humidity > cfg["hmax"]:
                globs.window_pos_dest[hausnum-1] = 100
                setWater(hausnum, 0)
        if s.humidity < cfg["hmin"]:
            if getWater(hausnum) == 0:
                setWater(hausnum,1)
                globs.todos.append((getTime(1), "wasser"+str(hausnum)+"=0"))
    except:
        print("fehler in check temp")

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
    # 'manually control' set?
    if globs.manually_timeend > time.time():
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
    d = RTC().datetime()
    minute = d[4]*60 + d[5]
    bitmask = 1<<(minute%8)
    mi = int(minute/8)
    for wt in range(1,5):
        try:
            byte = globs.watertables[wt-1][mi]
            m = (byte & bitmask)
            if m:
                setWater(wt, 1)
            else:
                setWater(wt, 0)
        except Exception as e:
            print(f"err in checkTimer.watertable{wt}: "+str(e))
            
def getBatVolt(rounded=2):
    """return battery voltage"""
    v, n = 0, 10
    for i in range(n):
       v += ADC_BATT.read_uv()*2/1e6
    return round(v / n, rounded)

def getVCCVolt(rounded=2):
    """return power input voltage"""
    v, n = 0, 10
    if globs.cfg.get("test_activated",0):
        return 5.67
    for i in range(n):
       v += ADC_POWER.read_uv()*2/1e6
    return round(v / n, rounded)

def checkWind():
    """
    if too much wind, wait a little, before storm-alarm.
    if there is very strong wind, it's storm ==> close windows immediately
    if storm is over, wait some time, for really end of storm.
    """
    # not used for now:  globs.sturmdelay_on
    # for test: globs.ws.testremotecontrol=0

    speed = globs.ws.getValue()
    if speed is None:
        print("Warning! No windspeed")
    try:
        if speed > globs.cfg["wind"]["max"]:
                globs.sturm = globs.sturmdelay_on
        if globs.sturm >= globs.sturmdelay_on:
            if globs.verbosity:
                print("Wind > max! Offene Fenster werden etwas abgesenkt.")
            for n in (0,1):
                if globs.window_virtual_open[n] > globs.windowpos_map[n].get('h',0):
                    globs.window_pos_dest[n] = globs.windowpos_map[n].get('h',0)
                    doMotors()   # fast! no time to wait for next automatic cycle
        if speed > globs.cfg.get("sturm",10):
            globs.sturm += globs.sturmdelay_on
            if globs.verbosity:
                print("Sturm. Alle Fenster werden geschlossen.")
            globs.window_pos_dest[0]=0
            globs.window_pos_dest[1]=0
            doMotors()   # fast! no time to wait for next automatic cycle
        else:
            if globs.sturm > globs.sturmdelay_off:
                globs.sturm = globs.sturmdelay_off
            if globs.sturm:
                globs.sturm -= 1

    except Exception as e:
        print(str(e))

def checkWindowPosition():
    """
    update the virtual model of window position,
    depending on time and motor status
    """
    if not globs.checkWindowPosition_lastTime:
        checkWindowPosition_lastTime = time.time()
    timedelta = time.time() - globs.checkWindowPosition_lastTime
    globs.checkWindowPosition_lastTime = time.time()

    PIN_END_DOWN = (PIN_END1DOWN, PIN_END2DOWN)
    # PIN_END_UP = (PIN_END1UP, PIN_END2UP)
    for housenum in (1,2):
        try:
            step = timedelta * float(globs.cfg["mot_openpersec"+str(housenum)])
            if getMotor(housenum) == "d":
                globs.window_virtual_open[housenum-1] -= step
                if USE_END_SWITCHES:
                    if PIN_END_DOWN[housenum-1].value() :
                        globs.window_virtual_open[housenum-1] = 0
            if getMotor(housenum) in "u":
                globs.window_virtual_open[housenum-1] += step
        except Exception as e:
            print(str(e))
        if globs.window_virtual_open[housenum - 1] < 0:
            globs.window_virtual_open[housenum - 1] = 0
        if globs.window_virtual_open[housenum - 1] > 100:
            globs.window_virtual_open[housenum - 1] = 100
            globs.window_pos_dest[housenum - 1] = None
    return

def formTime(text):
    """return well formated timestring from given text. format: HH:MM. adds a 0 as prefix, if neccessary"""
    h=text.split(":",1)[0]
    if len(h)<2:
        text="0"+text
    return text

def main():
    """
    the main loop starts the watchdog and calls all used functions
    """
    globs.wdt=None
    # wdt=WDT(timeout=globs.wdttime*1000)
    speed = -1
    if not globs.inited:
        # wdt.feed()
        init()
        a=10
        while a:
            a-=1
            time.sleep(.5)
            # allow a cfg message before anything else can hang
            if globs.rx:
                parseMsg() 
    if globs.wdttime <30:
        globs.wdttime = 30    
    globs.wdt=WDT(timeout=int(globs.wdttime*1000))
       
    while globs.dorun:     # do forever
        globs.wdt.feed()
        loopstart = time.time()
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
        motors += ";F1:"+str(round(globs.window_virtual_open[0]))+"; F2:"+str(round(globs.window_virtual_open[1]))
        water = f"W1:{getWater(1, 'de')}; W2:{getWater(2, 'de')}; W3:{getWater(3, 'de')}; W4:{getWater(4, 'de')}"
        dosen = f"D1:{getDose(1, 'de')}; D2:{getDose(2, 'de')}; D3:{getDose(3, 'de')}; D4:{getWater(4, 'de')}"
        # fenster = "Fenster: ?\r\n"  # todo. need 8 gpios first.
        comu.addTx(motors)
        comu.addTx(water)
        comu.addTx(dosen)
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
            if not "ESP" in os.uname().machine: # this is for the emulator
                PIN_LED1.doGuiupdate()  # this updates all pins
            time.sleep(.5)
            end -= .5
        parseMsg()

        # check for command which must be executed at a specific time.
        checkTemp(1)
        checkTemp(2)
        checkTimer()

        if not "ESP" in os.uname().machine:  # this is for the emulator
            PIN_LED1.doGuiupdate()  # this updates all pins

        for todo in globs.todos:
            t=formTime(todo[0])
            if t<globs.lasttime:
                continue
            if t<getTime():     # do it
                globs.todos.remove(todo)  # remove from queue
                m=todo[1]
                globs.rx.append(m)  # will be done in parseMsg()
                continue

        checkWindowPosition()
        doMotors()
        if not "ESP" in os.uname().machine:  # this is for the emulator
            PIN_LED1.doGuiupdate()  # this updates all pins
        checkWind()
        if not "ESP" in os.uname().machine:  # this is for the emulator
            PIN_LED1.doGuiupdate()  # this updates all pins


        if globs.rx and (time.time() -loopstart) < DURATION_PER_LOOP_MAX:
            parseMsg() 

        globs.lasttime = getTime()  # this line must be after all checks !

        # sleep on power loss
        vccVal = globs.cfg.get("vccok")
        if vccVal:
            if getVCCVolt() > vccVal[0]:
                globs.lightsleep_ms = 0
            else:
                battV = getBatVolt()
                sendAlarm(f"gwxctrl Spannung zu klein: USB={getVCCVolt()}V ; Batt={battV}V.")
                globs.lightsleep_ms = int(vccVal[1])
                batSets = globs.cfg.get("dsonbat")      # deepsleep on low bat
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
    # globs.rx.append(b"deepsleep=2")
    if "test_activated" in sys.argv:
        globs.test_activated = True
    parseMsg()
    main()
# eof
