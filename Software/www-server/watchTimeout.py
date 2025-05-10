#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
import paho.mqtt as mqtt
import paho.mqtt.client as mclient
import time, sys
from getpass import getpass
import ssl
import urllib
import json

topics_sub = [("slw/gwx/v1/tele/LWT",0),("slw/gwx/2/tele/LWT",0),("slw/gwx/nous/+/tele/LWT",0)]

class globs:
  cfg = {"verbosity":3}


def on_connect(client, userdata, flags, rc):
    res=["ok","?","?","?","?","Auth error"]
    print("Connected with result code " + str(rc) +" "+str(res[rc]))
    client.subscribe(topics_sub)

def on_message(client, userdata, msg):
    if sys.version_info[0]==3:
        msg.payload = msg.payload.decode()
    info = msg.topic + " " + str(msg.payload)
    print(info)
    rx = globs.cfg.get("signalReceivers")
    signalTx(info, rx)

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
      sender = globs.cfg.get("signalSender")
      data = {"message": info, "number": sender, "recipients": recipients}
      data = json.dumps(data).encode("utf-8")

      req = urllib.request.Request('http://localhost:8080/v2/send', method="POST")
      # req.timeout = 2
      req.add_header('Content-Type', 'application/json')
      r = urllib.request.urlopen(req, data=data, timeout=timeout)

      if globs.cfg["verbosity"]:
        content = r.read()
        print("ttx-rx: "+str(content))
    except Exception as e:
       print("Error in signal tx: "+str(e))


#main
av=sys.argv

av=["self","mq.qc9.de:18883", "-u=g1", "-pw=msowAsq1!"]

if len(av)<2:
  print("no args. use: "+av[0]+" server[:port] <topic>")
  sys.exit()
server=av[1]
port=1883
user=None
passwd=None
credentialspath=os.path.dirname(os.path.realpath(__file__)) +"/credentials.dat"

if  ":" in server:
  sp=server.split(":")
  server=sp[0]
  port=int(sp[1])
  
for p in av[1:]:  
    if p[:2]=="-u":
      user = p[3:]
    if p[:3]=="-pw":
      passwd = p[4:]
    if p[:2]=="-t":
      topic = p[3:]

with open(credentialspath) as f:
  d=json.load(f)
  globs.cfg.update(d)
print("Server: %s:%d  Topics: %s User: %s"%(server, port, topics_sub, user))
ca_certificate_file = None
client = mclient.Client()
if user:
    if not passwd:
        passwd = getpass("Password for "+user+": ")
    client.username_pw_set(user, passwd)  

client.on_connect = on_connect
client.on_message = on_message
# client.tls_set( ca_certs = ca_certificate_file, tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_set(tls_version=mclient.ssl.PROTOCOL_TLS)
client.tls_insecure_set(False)

client.connect(server, port, 60)
client.loop_forever()
print("fin.")
