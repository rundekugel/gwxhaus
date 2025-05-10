#!/usr/bin/env python
"""
gwxcontroller config updater
usage: updateconfig.py -s=server[:port] -k=<key> -d=[data] [options]
      -cfg=<cfg-file>
      -q=<n>   qos=n
      -s=<server>  set servername
      -k=<key>     change/add this key
      -d=<data>    set data
      -dn=<number> set data as number, without quotes.
      -t=<text>    send this text. this must be json syntax!
      -js=<jsonfile>    send text from this file. file must contain json syntax!
      -u=<user>   
      -p=<passwd> 
      -ttx=<topic to send> 
      -trx=<topic to receive>
      -rs=1         reset after cmd
      -ro           read only
"""

import time,os,sys
import json
import paho.mqtt.client as mqtt

__version__ = "0.2.1"
__author__ = "rundekugel@github"

class globs:
    topicRx = "slw/gwx/tele/RESULT"
    topicTx = "slw/gwx/x/cmnd/SSerialSend"
    verbosity = 1
    key,data = None,None
    rx=0
    qos=0
    reset=0
    msg=None
    blocksize = 50

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(globs.topicRx)

def on_message(client, userdata, msg):
    p = str(msg.payload)
    if globs.verbosity:
        print(msg.topic + " " + p)
    if "SSerialReceived" in p:
        globs.rx=1
        if globs.verbosity: print("rx")
        globs.msg=msg.payload.decode()
        
def wait_for_rx(timeout=20):
    end = time.time()+timeout
    while time.time()< end:
        if globs.rx:
            globs.rx=0
            return True
    return False
    
def send(client, text):
    """    send the dictionary as text    """
    start = "modcfgs"
    add = "modcfga"
    end = "modcfg."
    blocksize = globs.blocksize
    p=0
    if isinstance(text, bytes):
        text=text.decode()
    m = start+"="+text[:blocksize]
    if globs.verbosity:
        print("mqtt: "+globs.topicTx+" ["+m+"]")
    client.publish(globs.topicTx, m, globs.qos, 0)
    time.sleep(10)
    while 1:
        p += blocksize
        if p>= len(text):
            break
        m = add+"="+text[p:p+blocksize]
        if globs.verbosity:
            print("mqtt: " + globs.topicTx + " [" + m + "]")
        client.publish(globs.topicTx, m, globs.qos, 0)
        time.sleep(10)
    client.publish(globs.topicTx, end, globs.qos, 0)
    if globs.verbosity:
        client.publish(globs.topicTx, "cfg?", globs.qos, 0)
    return

def getConfig(client, timeout=20):
    client.publish(globs.topicTx, "cfg?", globs.qos, 0)    
    end = time.time()+timeout
    while time.time()< end:
        if globs.msg:
            if "baudrate" in globs.msg.lower():                
                return globs.msg
    return None
    
def getFile(filename):
    with open(filename ,"r") as f:
        ret = f.read()
    # try json validity:
    json.loads(ret)
    return ret

def main():
    av=sys.argv
    if len(av)<2:
      print(__doc__)
      return 0

    server=None
    port=18883
    key=None
    rep=1
    retain = False
    user,pwd=None,None

    if len(av)>3:
      data=av[3]
    else:
      data=None
    datatype = "s"
    text = None
    configfile = None  # "updateconfig.cfg"
    readonly=0

    if len(av)>1:
      for p in av[1:]:
        if p[0] != "-":
          continue
        if "=" in p:
            p0,p1=p.split("=",1)
        else:
            p0,p1=p,None
        if p == "-r":
          retain=True
        if p[:2]=="-q":
          globs.qos = int(p[3:],10)
        if p[:2]=="-n":
          rep = int(p[3:],10)
        if p[:2]=="-v":
          globs.verbosity = int(p[3:],10)
        if p[:2]=="-s":
          server = p[3:]
        if p0=="-p":     pwd = p1
        if p0=="-u":     user = p1
        if p0=="-k":     key = p1
        if p0=="-d":     data,datatype = p1,"s"
        if p0=="-dn":    data,datatype = p1,"n"
        if p0=="-df":    data,datatype = float(p1), "f"
        if p0=="-dx":    data,datatype = float(p1), "f"
        if p0=="-t":     text = p1
        if p0=="-ttx":   globs.topicTx = p1
        if p0=="-trx":   globs.topicRx = p1
        if p0=="-cfg":   configfile=p1
        if p0=="-rs":     globs.reset=p1
        if p0=="-ro":     readonly=1
        if p0=="-bs":    globs.blocksize = int(p1)
        if p0=="-js":    text = getFile(p1).replace("\r",'').replace('\n','').strip()
        if p0 in ("-?","?","-h","--help"): print(__doc__) ; return 0

    # load config
    if configfile:
        with open(configfile, "r") as f:
            cfg = f.read().replace('\n','').replace('\r','')
            j = json.loads(cfg)
            v = j.get("topictx")
            if v: globs.topicTx= v
            v = j.get("topicrx")
            if v: globs.topicRx = v
            v = j.get("user")
            if v: user = v
            v = j.get("server")
            if v: server = v
            v = j.get("port")
            if v: port = v
            v = j.get("pwd")
            if v: pwd = v

    if server and ":" in server:
      sp=server.split(":")
      server=sp[0]
      p=int(sp[1],10)
      if p:
        port=p

    if globs.verbosity:
      print("r,q,n,v,s,t,port,key,data",
            retain,globs.qos,rep,globs.verbosity,server,port,key,data)

    client = mqtt.Client()
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(user,pwd)
    r=client.connect(server, port, 60)
    if r:
        print("connection error:",r)
        return r
    client.loop_start()

    if readonly:
        print("Read config...")
        r = getConfig(client)
        print(r)
        return 0

    rep-=1
    if key:
        if text is None:
            if datatype == 's': data = '"'+ str(data) + '"'
            text = '{"'+ key +'":'+str(data)+'}'
        send(client, text)
    else:
        print("No key given ==> nothing to do.")
    if globs.reset:
        if globs.verbosity:
            print("Init a reset...")
        client.publish(globs.topicTx, "reset!", globs.qos, 0)
    time.sleep(.5)
    #ssend(client, "cfg?")
    time.sleep(.5)
    print("done.")
    if not r:
        print("testwait")
        time.sleep(20)
    return 0

if __name__ == "__main__":
    sys.exit( main() )
#eof
