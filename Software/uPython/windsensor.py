# uPython windsensor
"""
Runs with esp-32 and uPython.
calculate wind speed from pulse-sensor
Written by rundekugel @github 2024
"""

from machine import Pin
import utime
# from machine import Timer

__version__ = "0.1.3"
PI = 3.141592653589793
WINDSENSOR_DIAMETER = 110e-3    # diameter in m


class Filter:
    lastval = None
    size = 2

    def __init__(self, size, initvalue=None):
        if initvalue is not None:
            self.lastval = initvalue
        size = int(size)
        if size <1:
            print("Warning: size must be integer and >0, but is:"+str(size))
            size=1
        self.size = size

    def feed(self, value):
        if self.lastval is None:
            self.lastval = value
            return value
        self.lastval = (self.lastval *self.size + value)/(self.size+1)
        return self.lastval

    def getValue(self, rounded=1):
        return round(self.lastval, rounded)

class FilterWindowed:
    lastvals = []
    size = 7
    lastav = 0

    def __init__(self, size, initvalue=None):
        if initvalue is not None:
            self.lastval = initvalue
        size = int(size)
        if size <1:
            print("Warning: size must be integer and >0, but is:"+str(size))
            size=1
        self.size = size

    def feed(self, value):
        self.lastvals.append(value)
        if self.size <2:
            return value
        while len(self.lastvals) > self.size:
            self.lastvals.pop(0)
        b = list(self.lastvals)
        b.sort()
        if len(b)>2: b.pop() # remove biggest value
        av = 0
        for i in b:
            av += i
        av /= len(b)
        self.lastav = av
        return av
        
    def getValue(self, rounded=1):
        return round(self.lastav, rounded)

class Windsensor:
    pin = None
    lasttime = None
    lastdelta = None
    speed = None
    diameter = WINDSENSOR_DIAMETER # diameter in m
    proportionalityfactor = 2.6
    circumference = None
    filter = None
    verbosity = 1
    testremotecontrol = None
    

    def __init__(self, pin, diameter=None, filtersize=None):
        """param: pinnumber for data input"""
        self.pin = Pin(pin, Pin.IN, pull=Pin.PULL_UP)
        self.lasttime = utime.ticks_ms()/1e3
        self.pin.irq(trigger=Pin.IRQ_RISING, handler = self.pinhandler)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler = self.pinhandler)
        if diameter:
            self.diameter = diameter
        self.circumference = self.diameter * PI
        if filtersize is None: filtersize = 7
        self.filter = FilterWindowed(filtersize)

    def __del__(self):
        print("del"+str(self))
        self.pin.irq(handler=None)
        print("fin.")

    def pinhandler(self, pin):
        min_delta = 1e-3    # avoid divide by zero
        d = utime.ticks_ms()/1e3 - self.lasttime
        # debouncing
        if d < min_delta:
            if self.verbosity>1:
                print("invalid d:", d)
            self.lasttime = utime.ticks_ms()/1e3
            return
        self.lastdelta = d
        self.lasttime = utime.ticks_ms()/1e3
        self.speed = self.filter.feed(
                                self.circumference /
                                (self.lastdelta * self.proportionalityfactor)
                            )
        if self.verbosity>1:
            print("d:",self.lastdelta)
            print("m/s:",self.speed)

    def getValue(self, rounded=1):
        """wind m/s"""
        # print(utime.time(), self.lasttime, self.lastdelta)
        # after 1 second asume no wind
        if self.testremotecontrol is not None:
            print("Warnung: windsensor liefert nur testwerte!")
            return self.testremotecontrol
        if utime.ticks_ms()/1e3 > self.lasttime + 1:
            self.speed = 0
        if self.verbosity >1:
            print("d:",self.lastdelta)
            print("m/s:",self.speed)
        return round(self.speed, rounded)


if __name__ == "__main__":
    print("Windsensor Version:"+__version__)
    ws = Windsensor(4)
    for i in range(100):
        val = ws.getValue()
        print("m/s:",val)
        utime.sleep(1)

# eof
