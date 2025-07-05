#!/usr/bin/env python
"""
get tcp message and forward it to mqtt.
"""
import os,sys
import threading
import time
import json
import configparser
import socketserver

__version__ = "0.0.2"

class globs:
    doit = 1
    config = None
    verbosity = 3
    portrx = 18891

    @staticmethod
    def set(key, value):
        if key[0]=="_":
            return
        if isinstance(getattr(globs,key) ,int):
            value = int(value)
        if isinstance(getattr(globs,key) ,float):
            value = float(value)
        setattr(globs, key, value)
        
class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip().decode()
        if globs.verbosity>1:
            print("Received from {}:".format(self.client_address[0]))
        if globs.verbosity:
            print(self.data)
        value=""
        p= self.data.split(";")[0]  # don't send stuff after the semicolon
        p= p.split("=",1)
        p0= p[0]
        if len(p)>1:
            # todo: check value for validity
            value = "=" +p[1]
        topic = globs.config["global"]["topic"]
        # check whitelist
        if p0 in ("w1","w2","w3","w4","m1","m2","manually","globs?","globs","cfg","cfg?","rtc",
                  "wasser1","wasser2","motor1","motor2","d1","d2","n1","n2","n3","n4"):
            # remove this, if fw updated
            if p0 == "w1": p0 = "wasser1"
            if p0 == "w2": p0 = "wasser2"
            if p0 == "w3": p0 = "wasser3"
            if p0 == "w4": p0 = "wasser4"
            if p0 == "m1": p0 = "motor1"
            if p0 == "m2": p0 = "motor2"
            if p0 == "d1": p0 = "dose1"
            if p0 == "d2": p0 = "dose2"
            if p0 == "d3": p0 = "dose3"
            if p0 == "d4": p0 = "dose4"
            if p0 == "n1": topic = globs.config["nous"]["topic"]+"1/cmnd/power";p0="";value=p[1]
            if p0 == "n2": topic = globs.config["nous"]["topic"]+"2/cmnd/power";p0="";value=p[1]
            if p0 == "n3": topic = globs.config["nous"]["topic"]+"3/cmnd/power";p0="";value=p[1]
            if p0 == "n4": topic = globs.config["nous"]["topic"]+"4/cmnd/power";p0="";value=p[1]

            mqtttx(globs.config["global"]["user"], globs.config["global"]["pw"],
                   topic, p0 + value)
        else:
            mqtttx(globs.config["debug"]["user"], globs.config["debug"]["pw"],
                   globs.config["debug"]["topic"], p0 + value)

def mqtttx(user, pwd, topic, msg, sleep=0.1):
        try:
            cmd = "mosquitto_pub -h mq.qc9.de -p 18883 --tls-use-os-certs -u " + \
               user+" -P "+pwd+" -t "+topic+" -m '"+msg+"'"
            if globs.verbosity >1:
                print(cmd)
            os.system(cmd)
            time.sleep(sleep)    
        except Exception as e:
            print(f"Error in {name}: "+str(e))
        
# --- main ---
def main():
    print("PID:",os.getpid())
    pw = ""
    configfile = "tcp2mqtt.cfg"
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
        if p0=="-v": globs.verbosity= int(p1)
        
    if not config.read(configfile):
        raise Exception("No configfile given! Provide a config file. See example mqttbuf.cfg.template")
    
    if not path:
        path = config["DEFAULT"].get("destpath")
    if path:
        os.chdir(path)
    globs.config = config
    for key in ("verbosity","portrx"):
        try:
            globs.set(key, config["global"][key])
        except:
            pass
    for name in config.sections():
        try:
            c=config[name]
            # filename,user,pw,topic,sleep = c["file"],c["user"],c["pw"],c["topic"],c.getfloat("interval",1)
        except Exception as e:
            print("Error: "+str(e))
    try:     
        while globs.doit:
            time.sleep(1)
            HOST, PORT = "localhost", globs.portrx
            socketserver.TCPServer.allow_reuse_address = True
            server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
            server.serve_forever()
    except Exception as e: # catch a kill and stop the threads
        globs.doit=0
        print("e:"+str(e))
        time.sleep(1)
    print("end.")

if __name__ == "__main__":
    main()
