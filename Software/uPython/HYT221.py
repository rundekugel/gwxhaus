# upython read i2c

from machine import SoftI2C as I2C
from machine import Pin
import binascii
import utime
import struct

# gpio: 0,4,5 ==> D3,D2,D1

HYT_Addr = 0x28
DHT10_Addr = 0x70

p5=Pin(5,Pin.PULL_UP,Pin.OPEN_DRAIN)
p4=Pin(4,Pin.PULL_UP,Pin.OPEN_DRAIN)

#
i2c=I2C(scl=p5, sda=p4, freq=int(1e3))
i2c2=I2C(scl=p5, sda=p4, freq=int(1e3), timeout=int(10e3))

def setOff():
    p4.off()
    p5.off()

def setOn():
    p4=Pin(4,Pin.PULL_UP,Pin.OUT)
    p4.on()
    # p5=Pin(5,Pin.PULL_UP,Pin.OUT)
    p5.on()
    

setOn()
print(i2c)
utime.sleep(.1)
devs = i2c.scan()
print("found:",devs, binascii.hexlify(bytes(devs)," "))

class Result:
    status=None
    hygro=None
    thermo=None
    
    def __init__(self,s,h,t):
        self.status, self.hygro, self.thermo = s,h,t
    
    def toString(self):
        return "Status, Luftfeuchte, Temperatur: "+str(self.status)+"/"+str(self.hygro)+"/"+str(self.thermo)
    def __str__(self):
        return "Status, Luftfeuchte, Temperatur: "+str(self.status)+"/"+str(self.hygro)+"/"+str(self.thermo)
    def __unicode__(self):
        return "Status, Luftfeuchte, Temperatur: "+str(self.status)+"/"+str(self.hygro)+"/"+str(self.thermo)
    
def softreset(i2c=i2c):
    # todo
    i2c.readfrom_mem(0x28,0x1c,2)  # needed to initialize the next data sampling
    return
    
def getHYT(i2c=i2c, verbosity=1):
    """from: AHHYTM_E2.3.6"""
    # setOn() # in case, it's switched off during pause
    utime.sleep(.15)
    i2c.readfrom_mem(0x28,0x1c,2)  # needed to initialize the next data measuring
    utime.sleep(.01)
    r = i2c.readfrom(HYT_Addr,4)
    setOff();
    if verbosity:
        print(binascii.hexlify(r,' '))
    status=r[0]>>6
    h=r[0]&0b111111
    h<<=8
    h|=r[1]
    h*=(100/(2**14-1))
    # t=((r[2]&0b11111100))<<6 | (r[3]>>2)
    t=(r[2]<<6) | (r[3]>>2)
    t*=(165/16383)
    t-=40
    return Result(status,h,t)

if __name__ == "__main__":
    hyt = getHYT(i2c, verbosity=0)
    print("Status, Luftfeuchte, Temperatur: ",hyt.status, hyt.hygro, hyt.thermo)
    # or simply:
    print(hyt)
    
    