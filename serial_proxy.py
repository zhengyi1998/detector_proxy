#python
import serial

#from SocketServer import ThreadingTCPServer, StreamRequestHandler
import socket
import threading
import time
import sys
import tcp_serial_redirect as TcpRedirector

SerialServicePort=1234
COM = "COM2"
"""
class MyCmdBaseRequestHandlerr(StreamRequestHandler):
    def handle(self):
        while True:
            try:
                #The command need to remove the \r\n
                data = self.request.recv(128).strip() 
                if len(data) == 0:
                    break;
                print "receive from (%r):%r" % (self.client_address, data)
                if len(data) > 0 :
                    if cmp(data, '[close]') == 0 :
                        self.server.shutdown()
                        break;
                    elif cmp(data, '[on]') == 0 :
                        self.server.listener.set_detector_running(True)
                    elif cmp(data, '[off]') == 0 :
                        print "call off"
                        self.server.listener.set__detector_running(False)
                        print "call end"
                    elif cmp(data, '[sp_on]') == 0:
                        self.server.listener.set_speaker_status (True);
                    elif cmp(data, '[sp_off]') == 0:
                        self.server.listener.set_speaker_status (False);

                    elif cmp(data, '[e_on]') == 0:
                        self.server.listener.set_stop_status (True);
                    elif cmp(data, '[e_off]') == 0:
                        self.server.listener.set_stop_status (False);
                    else:
                        print "goin to write\n"
                        self.server.serial.write(data)
                        #time.sleep(1)
                        self.server.serial.timeout=2
                        print "going to read"
                        #The max length of the return msg is 13 bytes
                        #import pdb
                        #pdb.set_trace()
                        response = self.server.serial.read(1)
                        n = self.server.serial.inWaiting()
                        print "ther is %d bytes\n"%n
                        response = response + self.server.serial.read(n)
                        #import pdb
                        #pdb.set_trace()
                        if len(response) > 0:

                            self.wfile.write(response)
                            if response[0] == '\xaa':
                                self.server.listener.set_trace_info ("ok")
                            else:
                                self.server.listener.set_trace_info ("error")

                if self.server.stopped:
                    break;
            except:
                self.server.shutdown()
                traceback.print_exc()
                break

class CmdTCPServer(ThreadingTCPServer):
    def __init__(self, service_addr, handler, serial, listener):
        ThreadingTCPServer.__init__(self, service_addr, handler)
        self.serial = serial
        self.stopped = False
        self.listener = listener
        
    def serve_forever(self):
        while not self.stopped:
            self.handle_request()
    
    def force_stop (self):
        self.server_close()
        self.stopped = True

class SerialProxy(threading.Thread):
    def __init__(self, service_port, listener):
        threading.Thread.__init__(self, name='CmdProxy')
        self.service_port = service_port
        self.listener = listener
        self.serial = None

    def openSerial(self):
        try:
            self.serial  = serial.Serial(COM)
            self.serial.timeout = 2
            #self.detector_serial  = serial.Serial('/dev/tty.usbserial-FT20E5D5')
            print self.serial.portstr
            print "serial connect successful"
        except Exception, e:
            print "error open serial port: " + str(e)
    def stop(self):
        self.server.force_stop()

    def run(self):
        service_addr = ('', self.service_port)
        #start service
        try:
            self.server = CmdTCPServer(service_addr, MyCmdBaseRequestHandlerr, self.serial, self.listener)
            print "run tcp server"
            self.server.serve_forever()
        except Exception,  e:
            print "error start CmdTCP server  " + str(e)
            self.server.shutdown()
        finally: 
            if hasattr(self, 'serial') is not None:
                self.serial.close()

"""

class NoBlockingSerialProxy(threading.Thread):
    def __init__(self, service_port, listener):
        threading.Thread.__init__(self)
        self.port = service_port
        self.listener = listener
        self.Alive = True
        self.setupSerial()
        self.daemon = True

    def setupSerial(self):
        self.ser = serial.Serial()
        self.ser.port     = "COM2"
        self.ser.timeout  = 1     # required so that the reader thread can exit


    def run(self):
        try:
            self.ser.open()
        except serial.SerialException, e:
            sys.stderr.write("Could not open serial port %s: %s\n" % (ser.portstr, e))
            return

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind( ('', self.port) )
        srv.listen(1)
        while self.Alive:
            try:
                print "SerialProxy waiting for connection on %s ...\n"%self.port
                connection, addr = srv.accept()
                print "Connected by %s\n"%(addr,)
                self.redirector = TcpRedirector.Redirector(
                    self.ser,
                    connection,
                    spy = True
                )
                print "Redirector shortcut"
                self.redirector.shortcut()
                print "SerialProxy Disconnected\n"
                connection.close()
            except socket.error, msg:
                sys.stderr.write('ERROR: %s\n' % msg)

    def stop(self):
        self.Alive = False
        self.redirector.stop()

        print "Redirector stopped"



def start_proxy (listener = None):

    proxy = NoBlockingSerialProxy(SerialServicePort, listener);
    proxy.start()
    return proxy





if __name__ == '__main__':

    start_proxy()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(1)
