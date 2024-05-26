# HYT221
"""
Runs with esp-32 and uPython.
Read humidity and temperature from HYT-221 sensor via i2c
Written by rundekugel @github 2024
"""

from machine import SoftI2C as I2C
from machine import Pin
import binascii
import utime

__version__ = "1.0.2"

HYT_Addr = 0x28
DHT10_Addr = 0x70
FREQ_DEFAULT = int(1e3)


class Result:
    status = None
    humidity = None
    temperature = None
    verbosity = 0
    postdec = 1
    
    def __init__(self, status, humidity=None, temperature=None):
        """params: if status is tuple, then all values are read from this tuple"""
        if isinstance(status, (tuple,list)):
            status, humidity, temperature = status
        self.status, self.humidity, self.temperature = (
                            status, humidity, temperature)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return ("Status, Luftfeuchte, Temperatur: "
                +str(self.status)+"/"+str(self.humidity)+"/"+str(self.temperature))
    

class HYT221:
    """
    read humidity, temperature and status from HYT221-sensor
    params: pins as object from Pin or as integer
    """
    i2c = None
    address = None
    verbosity = 0
    testremotecontrol = None

    def __init__(self, pinSCK, pinSDA, address=HYT_Addr,
                 freq=FREQ_DEFAULT, verbosity=0):
        self.verbosity = verbosity
        if isinstance(pinSCK, int):
            pinSCK = Pin(pinSCK, Pin.PULL_UP, Pin.OPEN_DRAIN)
        if isinstance(pinSDA, int):
            pinSDA = Pin(pinSDA, Pin.PULL_UP, Pin.OPEN_DRAIN)
        self.pinSCK = pinSCK
        self.pinSDA = pinSDA
        self.address = address
        self.i2c = I2C(scl=self.pinSCK, sda=self.pinSDA, freq=freq)
    
    def __str__(self):
        return self.__unicode__()
        
    def __unicode__(self):
        s, h, t = self.getValues()
        return ("Status, Luftfeuchte, Temperatur: "
                +str(s)+"/"+str(h)+"/"+str(t))
  
    def getValues(self, postdec=1):
        """from: AHHYTM_E2.3.6"""
        utime.sleep(.15)
        if self.testremotecontrol is not None:
            print("Warning: Testmodus. Werte sind nur Testwerte!")
            return Result(self.testremotecontrol)
        try:
            self.i2c.readfrom_mem(self.address, 0x1c, 2)  # needed to initialize the next data measuring
            utime.sleep(.01)
            r = self.i2c.readfrom(self.address, 4)
            if self.verbosity:
                print(binascii.hexlify(r, ' '))
        except:
            return None
        status = r[0] >> 6
        h = r[0] & 0b111111
        h <<= 8
        h |= r[1]
        h *= (100/(2**14-1))
        t = (r[2] << 6) | (r[3] >> 2)
        t *= (165/16383)
        t -= 40
        h = round(h,postdec)
        t = round(t,postdec)
        return Result(status, h, t)

    def scan(self):
        devs = self.i2c.scan()
        if self.verbosity:
            print("I2C devices found: ", devs, " = ",
                  binascii.hexlify(bytes(devs), " "))
        return devs
    

if __name__ == "__main__":
    print("HYT221 Version:"+__version__)
    sensor = HYT221(5, 4)
    sensor.scan()
    hyt = sensor.getValues()
    print("Status, Luftfeuchte, Temperatur: ",
          hyt.status, hyt.humidity, hyt.temperature)
    # or simply:
    print(hyt)
    
# eof
