#!/usr/bin/env python
"""
get mqtt message and copy it to a file, to be read by the webpage.
"""
import os,sys
import threading
import time
import json
import configparser

__version__ = "0.1.1"

class globs:
    doit = 1
    verbosity = 1
    

def mqttbuf(name, user, pwd, topic, filename,sleep=1,count=1,timeout=0):
    print("start "+sys.argv[0]+" thread: "+ name +" / "+topic)
    if timeout:
        timeout=" -W "+str(timeout)
    else:
        timeout = ""
    while globs.doit:
        try:
            os.system("touch "+filename+".tmp")
            # os.system("echo \<?php header\(\\\'Content-type: application/json\\\'\)\; ?\> >"+filename+".tmp" )
            # os.system("echo \<?php header\(\\\'strict-transport-security: max-age=10\\\'\)\; ?\> >>"+filename+".tmp" )
            cmd = "mosquitto_sub -h mq.qc9.de -p 18883 --tls-use-os-certs -u " + \
               user+" -P "+pwd+" -t " +topic + timeout +" -C "+str(count)+" >"+filename+".tmp 2>&1"
            if globs.verbosity>2:
                    print(cmd)
            os.system(cmd)
            d=""
            with open(filename+".tmp") as f:
                d=f.read()
            if d:
                os.rename(filename+".tmp", filename)
                if globs.verbosity>1:
                    print("in:"+filename+":"+d)
            time.sleep(sleep)    
        except Exception as e:
            print(f"Error in {name}: "+str(e))
        
# --- main ---
def main():
    print("PID:",os.getpid())
    pw = ""
    configfile = "mqttbuf.cfg"
    path=""
    config = configparser.ConfigParser()
    threads=[]
    
    # args overrides config
    for p in sys.argv[1:]:
        if p[0] != "-": configfile = p; continue
        if "=" in p:
            p0,p1 = p.split("=",1)
        else:
            p0,p1 = p,None
        if p0=="-pw": pw=p1
        if p0=="-path": path=p1
        if p0=="-cfg": configfile = p1
        if p0=="-v": globs.verbosity = int(p1)
        
    if not config.read(configfile):
        raise Exception("No configfile given! Provide a config file. See example mqttbuf.cfg")
    
    if not path:
        path = config["DEFAULT"].get("destpath")
    if path:
        os.chdir(path)
        
    for name in config.sections():
        try:
            c=config[name]
            filename,user,pw,topic,sleep,count,timeout = c["file"],c["user"],c["pw"],\
                        c["topic"],c.getfloat("interval",1),c.getint("count",1),c.getint("timeout",0)
            t = threading.Thread(target=mqttbuf, args=(name, user, pw, topic, filename, sleep, count, timeout))
            t.start()
            threads.append(t)
        except Exception as e:
            print("Error: "+str(e))
    try:     
        while globs.doit:
            time.sleep(1)
    except: # catch a kill and stop the threads
        globs.doit=0
        time.sleep(1)
    print("end.")

if __name__ == "__main__":
    main()
