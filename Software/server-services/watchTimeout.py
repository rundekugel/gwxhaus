#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
listen to mqtt topic(s)
if one device is offline, store it in a list from type Delayer
if device is offline for long time (msgdelaytime) then send alarm message via signal-service

params:
-cfg=<configfilename> default: watchTimeout.cfg
-u=<username>
-pw=password
-t=topic

'''

import sys, os
import paho.mqtt as mqtt
import paho.mqtt.client as mclient
import time, sys
from getpass import getpass
import ssl
import urllib
import json

__version__ = "1.0.1"
__author__ = "rundekugel @ github"


ALLOWED_KEYS = ("configname", "server", "verbosity","interval",
                "signalReceivers","signalSender", "signalAdmins",
                "topics_translator", "topics_sub", "control_topic",
                "msgdelaytime")

class Globs:
  cfg = {"verbosity":3}
  delayers=[]
  msgdelaytime = 20
  verbosity = 1
  configfile = "watchTimeout.cfg"
  server = ""
  topics_sub = [ ]
  topics_translator = { }
  control_topic = ""
  signalReceivers = []
  signalSender = ""
  signalAdmins = []
  client = mclient.Client
  configname = "?"
  interval=1
globs = Globs()

class Delayer:
    '''contains info about devices, sent LWT'''
    topic=""
    humanreadable_name = ""
    lwl=""
    startTime=None
    DESTROY_ME = -1
    info = ""
    msg = mclient.MQTTMessage
    def __init__(self, mqttmsg :mclient.MQTTMessage, topic=None, lwl=None, info=None):
        self.startTime = time.time()
        if mqttmsg:
            self.msg = mqttmsg
            self.topic = mqttmsg.topic
            self.lwl = str(mqttmsg.payload)
        if topic:
            self.topic = topic
        if lwl:
            self.lwl = lwl
        if info is not None:
            self.info = info
        else:
            self.info = self.topic + " " + str(self.lwl)
            devicename = globs.topics_translator.get("self.topic")
            if devicename:
                self.info = devicename + " " + str(self.lwl)

    def update(self, lwl):
        if globs.verbosity>1:
            print(self.__dict__)
            print(self.msg.timestamp)
        if self.lwl.lower() == "offline":
            if lwl.lower() =="online":
                if time.time() < self.startTime + globs.msgdelaytime:
                    self.startTime = self.DESTROY_ME
                    return
        startTime = time.time()
        self.lwl = lwl
        self.generateFullMsg()
    def generateFullMsg(self):
        devicename = globs.topics_translator.get(self.topic)
        if not devicename:
            devicename = self.topic
        since = time.time() -self.startTime
        since = "%d min. %d sec." % (since//60, since % 60)
        return devicename + " " + str(self.lwl) +" seit: "+str(since)


def on_connect(client, userdata, flags, rc):
    res=["ok","?","?","?","?","Auth error"]
    print("Connected with result code " + str(rc) +" "+str(res[rc]))
    client.subscribe(globs.topics_sub)

def on_message(client, userdata, msg):
    if sys.version_info[0]==3:
        msg.payload = msg.payload.decode()
    info = msg.topic + " " + str(msg.payload)
    print(info)
    if msg.topic.startswith(globs.control_topic):
        cmd = msg.topic.rsplit('/',1)[-1]
        if cmd=="msgdelaytime":
            globs.msgdelaytime = int(msg.payload)
            if globs.msgdelaytime > 60*60:
                signalTx(f"Alarmdelay ist auf groesser 1 Stunde eingestellt! "
                         f"({int(globs.msgdelaytime/60)}min.)",
                         globs.signalreceivers)
        if cmd=="disable":
            if globs.topics_translator.get(msg.payload):
                print("remove: "+msg.payload)
                try:
                    globs.topics_sub.remove((msg.payload,0))
                    globs.client.reconnect()
                except:
                    pass
        if cmd=="enable":
            if globs.topics_translator.get(msg.payload):
                print("add: "+msg.payload)
                globs.topics_sub.append((msg.payload,0))
                globs.client.reconnect()
        if cmd == "info":
            info=globs.configname +":"+str(globs.topics_sub)+";"+"delayTime:"+str(globs.msgdelaytime) + ";"+str(globs.delayers)
            info +=";"+"dict:"+str(globs.topics_translator)
            signalTx(info, globs.signalAdmins)
        if cmd == "verbosity":
            globs.verbosity = int(msg.payload)
        if cmd == "reloadconfig":
            loadconfig()
            globs.client.reconnect()
        return

    r=1  # globs.delayers.get(msg.topic)
    delayer = delayer_find(msg.topic)
    if delayer:
        delayer.update(str(msg.payload))
    else:
        d = Delayer(msg)
        globs.delayers.append(d)

def delayer_find(topic):
    delayer: Delayer
    for delayer in globs.delayers:
        if delayer.topic==topic:
            return delayer
    return None

def telegramTx(info, chatid="112350312"):    
  user="bot237720890"
  telegramkey = globs.cfg.get("tgkey")
  param=urllib.parse.urlencode({"text":info})
  url="https://api.telegram.org/%s:%s/sendMessage?chat_id=%s&%s"%(
        str(user), str(telegramkey), str(chatid), str(param) )
  if globs.cfg["verbosity"]>3:
    print("ttx-url:"+ str(url))
  r=urllib.request.urlopen(url,param.encode())
  r=r.msg
  if globs.cfg["verbosity"]:
    print("ttx-rx: "+str(r))
  return r

def signalTx(info, recipients, timeout=2):
    try:
      sender = globs.signalSender
      data = {"message": info, "number": sender, "recipients": recipients}
      data = json.dumps(data).encode("utf-8")
      if globs.verbosity >1:
          print(data)
      req = urllib.request.Request('http://localhost:8080/v2/send', method="POST")
      # req.timeout = 2
      req.add_header('Content-Type', 'application/json')
      r = urllib.request.urlopen(req, data=data, timeout=timeout)

      if globs.cfg["verbosity"]:
        content = r.read()
        print("ttx-rx: "+str(content))
    except Exception as e:
       print("Error in signal tx: "+str(e))

def loadconfig(filename=""):
    '''using globs.<attribute> is so handy, I don't wanna miss it, and I want to configure it.'''
    if not filename:
        filename=globs.configfile
    if globs.verbosity:
        print("load config from: "+filename)
    try:
        with open(filename,"r") as f:
            j = json.load(f)
            for k in j:
                if k in ALLOWED_KEYS:
                    globs.__setattr__(k, j[k])
    except Exception as e:
        print("Error in loadconfig:" +str(e))
        signalTx("Error in loadconfig:" +str(e), globs.signalAdmins)
    if globs.control_topic:
        globs.topics_sub.append((globs.control_topic+"/#",0))

#main
av=sys.argv
server="localhost"
port=1883
user=None
passwd=None
credentialspath=os.path.dirname(os.path.realpath(__file__)) +"/credentials.dat"
globs.configfile = os.path.dirname(os.path.realpath(__file__)) +"/watchTimeout.cfg"

if len(av)<2:
  print("no args. use: "+av[0]+" server[:port] <topic>")
  # sys.exit()
else:
    server=av[1]
port=1883
user=None
passwd=None
credentialspath=os.path.dirname(os.path.realpath(__file__)) +"/credentials.dat"
globs.configfile = os.path.dirname(os.path.realpath(__file__)) +"/watchTimeout.cfg"

for p in av[1:]:
    if "=" in p:
        p0, p1 = p.split("=", 1)
    else:
        p0, p1 = p, None
    if p0=="-u":    user = p1
    if p0=="-pw":   passwd = p1
    if p0=="-t":    globs.topics = p1
    if p0=="-ct":   globs.controltopic = p1
    if p0=="-cfg":  globs.configfile = p1
    if p0 in ("-h", "--help", "-?"):
        print(__doc__)
        sys.exit(0)

loadconfig(globs.configfile)
with open(credentialspath) as f:
  d=json.load(f)
  globs.cfg.update(d)

if globs.cfg.get("server"):
    server = globs.cfg.get("server")
if  ":" in server:
  sp=server.split(":")
  server=sp[0]
  port=int(sp[1])
print("Server: %s:%d  Topics: %s User: %s"%(server, port, globs.topics_sub, user))

ca_certificate_file = None
client = mclient.Client()
globs.client = client
if user:
    if not passwd:
        passwd = getpass("Password for "+user+": ")
    client.username_pw_set(user, passwd)  

client.on_connect = on_connect
client.on_message = on_message
# client.tls_set( ca_certs = ca_certificate_file, tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_set(tls_version=mclient.ssl.PROTOCOL_TLS)
client.tls_insecure_set(False)

client.connect(server, port, 90)
    # client.loop_forever()
client.loop_start()
dorun = 1
while dorun:
    if client.is_connected():
        dorun =2
    else:
        if dorun==2:
            dorun=1
            print("disconnected!")
    if globs.verbosity>3:
        print("."+str(dorun), end="")
    delayer: Delayer

    for delayer in globs.delayers:
        if globs.verbosity>4:
            print(delayer.__dict__)
        if delayer.startTime == Delayer.DESTROY_ME:
            globs.delayers.remove(delayer)
            continue
        if time.time() >= delayer.startTime +globs.msgdelaytime:
            try:
                info = delayer.generateFullMsg()
                globs.delayers.remove(delayer)
                rx = globs.signalReceivers
                if globs.verbosity:
                    print("Alarm!",info, rx)
                signalTx(info, rx)
            except Exception as e:
                print(e)
    time.sleep(globs.interval)
client.loop_stop()
print("fin.")
