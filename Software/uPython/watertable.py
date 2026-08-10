# watertable tools
"""
this code is intended to run on a embedded system with micropython

holds 5min-granular tables for watervalves power on/off

set and  get marks, for switch on or off with resolution of 5min.
data is arranged in 6bits per byte for easy handling of data to send via uart
2 bytes per hour
24 hours per table = 48 bytes per table

for storage as file and/or communication via UART only the
chars 0x20 to 0x70 (=32 to 112) are used.
"""

import time
import json

__version__ = "0.0.1-" 


OFFSET = 32
BYTES_PER_TABLE = 2*24 
#FILE_PREFIX = "watertimetable"
#FILE_POSTFIX = ".dat"
FILENAME_TEMPLATE = "watertimetable{n}.dat"

class watertables:    
    """
    holds a 5min-granular table for watervalves power on/off
    """
    tables = None
    number_of_tables = None

    def __init__(self, number_of_tables=2) -> None:
          # init with zero
          self.tables = [[0]*BYTES_PER_TABLE] * number_of_tables
          self.number_of_tables = number_of_tables

    def setData(self, id, hour, minute, onOff):
        """
        set one of the 5minute intervals to on or off
        returns None for error; 0 for ok
        """
        if id <0 or id >= self.number_of_tables:
            return None
        pos = hour *2
        if minute>=30:
            pos+=1
            minute-=30
        minute /= 6
        if onOff:
            self.tables[id][pos] |= (1<<int(minute))
        else:
            self.tables[id][pos] &= 0xff-(1<<int(minute))
        return 0         

    def getData(self, id, hour, minute):
        """
        get one of the 5minute intervals: 
        False for off; True for on 
        None for error.
        """
        if id <0 or id >= self.number_of_tables:
            return None
        pos = hour * 2
        if minute >= 30:
            pos +=1
            minute -= 30
        bitshift = int(minute/5)
        b = self.watertables[id][pos]
        r = b & (1<<bitshift)
        return r >0

    def packData(self, id) -> str: 
        """
        return table as packed ascii data
        returns None for error
        """
        if id <0 or id >= self.number_of_tables:
            return None
        text = ""
        for hour in range(24):
             b0,b1 = self.tables[id][hour*2:hour*2 +2] # get 2 bytes
             b0,b1 = b0 &0x3f, b1 &0x3f
             text += chr(b0 +OFFSET) + chr(b1 +OFFSET)
        return text

    def unpackData(self, id, text):
        """
        unpack table from ascii data and store internal
        returns None for error ; 0 for ok
        """
        if id <0 or id >= self.number_of_tables:
            return None
        pos = 0
        for hour in range(24):
             b0,b1 = text[hour*2:hour*2+2]
             self.tables[id][pos]   = ord(b0) -OFFSET
             self.tables[id][pos+1] = ord(b1) -OFFSET
             pos += 2
        return 0

    #todo:
    def storeAsFile(self, id):
        if id <0 or id >= self.number_of_tables:
            return None
        try:
            text = self.packData(id)
            if text is None:
                return None
            with open(FILENAME_TEMPLATE.replace("{n}", str(id)),"w") as f:
                f.write(text)
            return 0
        except:
            return None
        
    def readFromFile(self, id):
        if id <0 or id >= self.number_of_tables:
            return None
        try:
            with open(FILENAME_TEMPLATE.replace("{n}", str(id)),"r") as f:
                data = f.read()
        except:
            return None
        if len(data) < BYTES_PER_TABLE:
            return None
        return self.unpackData(id, data)
        
        

#eof
