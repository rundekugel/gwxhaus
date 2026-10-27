'''
read pins from motor direction sensors
'''

import pcf8574
from machine import SoftI2C as I2C
from machine import Pin

#import  hw-blackpill.hwspec
import  hwspec

LEFT =1
RIGHT = 2
OFF = 0
ERROR = 3

class MotorDirections():
    freq = 10e3
    i2c_port = 1
    i2c_adr = 0x21
    i2c = None
    pcf = None

    def __init__(self, i2c_adr=None, i2c_port_num=None, frequence=None):
        if frequence:
            self.freq = frequence
        if i2c_port_num is not None:
            self.i2c_port = i2c_port_num
        if i2c_adr is not None:
            self.i2c_adr = i2c_adr

        if self.i2c_port_num == 1:
            pinSCK = Pin(PIN_SCL1, Pin.PULL_UP)
            pinSDA = Pin(PIN_SDA1, Pin.PULL_UP)
        elif i2c_port_num ==2:
            pinSCK = Pin(PIN_SCL2, Pin.PULL_UP)
            pinSDA = Pin(PIN_SDA2, Pin.PULL_UP)
        else:
            return None
        self.i2c = I2C(scl=pinSCK, sda=pinSDA, freq=self.freq)
        self.pcf = pcf8574.PCF8574(self.i2c, self.i2c_adr)

    def getPcf(self):
        return self.pcf

    def getPin(self, pin):
        return self.pcf.pin(pin)

    def getPort(self):
        return self.pcf.port()
    
    # def setPin(self, pin, value):
    #     self.pcf.pin = value

    def getDirById(self, id):
        # num is 0..3
        p = self.pcf.port()
        p >>= id *2
        p &= 0b11
        return p

#eof
