#!/usr/bin/env python
"""
gwxcontroller config updater
usage: updateconfig.py server[:port] <key> [data] [options]
      -q=<n>   qos=n
      -s=<server>  set servername
      -k=<key>     change/add this key
      -d=<data>    set data
      -dn=<number> set data as number, without quotes.
      -t=<text>    send this text
      -u=<user>   
      -p=<passwd> 
      -ttx=<topic to send> 
      -trx=<topic to receive> 
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

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(globs.topicRx)

def on_message(client, userdata, msg):
    p = str(msg.payload)
    print(msg.topic + " " + p)
    if "SSerialReceived" in p:
        globs.rx=1
        if globs.verbosity: print("rx")
        
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
    blocksize = 20
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
    return

def main():
    av=sys.argv
    if len(av)<3:
      print(__doc__)
      return 0

    server=av[1]
    port=18883
    key=av[2]
    rep=1
    retain = False
    user,pwd=None,None

    if len(av)>3:
      data=av[3]
    else:
      data=None
    type = "s"
    text = None
    configfile = None

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
        if p0=="-d":     data,type = p1,"s"
        if p0=="-dn":    data,type = p1,"n"
        if p0=="-df":    data,type = float(p1), "f"
        if p0=="-dx":    data,type = float(p1), "f"
        if p0=="-t":     text = p1
        if p0=="-ttx":   globs.topicTx = p1
        if p0=="-trx":   globs.topicRx = p1
        if p0=="-cfg":   configfile=p1
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
            v = j.get("password")
            if v: pwd = v

    if ":" in server:
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

    rep-=1
    if text is None:
        if type == 's': data = '"'+ data + '"'
        text = '{"'+ key +'":'+str(data)+'}'
    send(client, text)
    time.sleep(.5)
    print("done.")
    if not r:
        print("testwait")
        time.sleep(20)
    return 0

if __name__ == "__main__":
    sys.exit( main() )
#eof
