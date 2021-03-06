#!/usr/bin/env python
# -*- coding: utf-8 -*-

import select
import socket
import Queue
import threading
import time
import NoBlockingSocket as NS
from PyQt4.QtCore import *

class ChannelProxy(QObject, NS.Monitor):
    def __init__(self, name, detector_ip, detector_port, service_port, listener=None):
        super(ChannelProxy,  self).__init__(None)
        self.input_queue = Queue.Queue()
        self.output_queue = Queue.Queue()
        self.detector_thread  = NS.SocketClientThread(name+"_detector", (detector_ip, detector_port), self.input_queue, self.output_queue)
        self.proxy_thread  = NS.ProxyThread(name+"_proxy", service_port, self.input_queue, self.output_queue, self)
        self.startTimer = QTimer(self)

 
        self.listener = listener
	
    def start_thread(self):
        self.detector_thread.start()
        self.proxy_thread.start()

		
    def start(self):
		self.startTimer.singleShot(5000, self.start_thread)

    def stop(self):
        print "ChannelProxy Stop"
        self.detector_thread.stop()
        self.proxy_thread.stop()



class ImgProxy (ChannelProxy):
    totalbytes = 0
    def __init__(self, name, detector_ip, detector_port, service_port, listener=None):
        ChannelProxy.__init__(self, name, detector_ip, detector_port, service_port, listener)

    def pre_process_data(self, cmd):
        pass

    def post_process_data(self, cmd):
        #caculate the image bandwidth here
        totalbytes += len(cmd)
        pass

    def set_clear_flag(self):
        self.detector_thread.set_clear_flag()
        self.proxy_thread.set_clear_flag()

class CmdProxy (ChannelProxy):
    def __init__(self, name, detector_ip, detector_port, service_port, listener=None):
        ChannelProxy.__init__(self, name, detector_ip, detector_port, service_port, listener)
        self.img_proxy =None

    def set_img_proxy (self, img_proxy):
        self.img_proxy = img_proxy

    def ping(self):
        self.detector_thread.ping()
    def pre_process_data(self, cmd):
        print "pre_process_data in"
        if "[SDR,1]" in cmd:#setup start grab status
            print "get detector sdr 1"
            self.listener.set_detector_running (True)
            return False
        elif "[SDR,0]" in cmd:
            print "get detector sdr 0"
            self.listener.set_detector_running (False)
            return False;    
        if "SDC" in cmd: #setup detector connection:
            if "1" in cmd:
                self.listener.set_detector_connected(True)
                return False;
            elif "0" in cmd:
                self.listener.set_detector_connected(False)
                return False;
        if "SDB" in cmd:  #setup battery info
            return False;

        if "SDS" in cmd:#setup detector speed
            nPos = cmd.index("SDS")
            speed = cmd[nPos+len("SDS")+1:]
            print "speed is" + speed
            speed = speed[:len(speed)-1]
            print speed
            self.listener.set_detector_speed(speed)

            return False;

        if "SSR" in cmd:#setup speaker status
            if "1" in cmd:
                return False;
            elif "0" in cmd:
                return False;

        if "SES" in cmd:#setup stop button status
            if "1" in cmd:
                return False;
            elif "0" in cmd:
                return False;

        if "STI" in cmd: #setup the display info: warning msg error etc
            return False;
        return True

    def post_process_data(self, cmd):
        if "[SF,0]" in cmd:
            print "CmdChannel get SF,0"
            time.sleep(0.5)
            #Not sure do I need to call clear buf on proxy side.
            #according to the xview code, the xview should clear all remain data in socket pipe in 250 ms
            self.img_channel_proxy.set_clear_flag()

        if "ST,W" in cmd:
            pass

class DetectorServer(QObject):
    def __init__(self, name, detector_ip, cmd_port, img_port, service_cmd_port, service_img_port, listener = None):
        super(DetectorServer,  self).__init__(None)    
        self.listener = listener
        self.cmd_proxy = CmdProxy("CmdProxy", detector_ip, cmd_port, service_cmd_port, listener)
        self.img_proxy = ImgProxy("ImgProxy", detector_ip, img_port, service_img_port, listener)
        self.cmd_proxy.set_img_proxy(self.img_proxy)
        self.checkTimer = QTimer(self)
        
    def start(self):
        self.cmd_proxy.start()
        self.img_proxy.start()
        self.connect(self.checkTimer,SIGNAL("timeout()"),self.checkConn)
        self.checkTimer.start(10000)
    def stop(self):
        self.checkTimer.stop()
        self.cmd_proxy.stop()
        self.img_proxy.stop()
    
    def checkConn(self):
        if self.cmd_proxy.detector_thread.connected:
            print "detector connected  "
            #send command to detector
            #self.cmd_proxy.ping()
        else:
            print "detetor not connected"
            self.cmd_proxy.detector_thread.open()
            self.img_proxy.detector_thread.open()
            #self.checkTimer.singleShot(5000, self.timeOut)
        if (self.listener):
            self.listener.set_detector_connected(self.cmd_proxy.detector_thread.connected)
if __name__ == "__main__":
    #server = start_server("imgServer", "192.168.2.2", 4001, 4001)
    try:
        server = DetectorServer("Detector", "192.168.217.135", 3000, 4001, 3001,4002)
        server.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "get key"
        stop_server(server)
