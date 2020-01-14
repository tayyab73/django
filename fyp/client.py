import socket,sys,time
import threading,pickle
from threading import Thread,Lock


class Client:
    def __init__(self,name,client):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = '127.0.0.1'
        self.port = 9000
        self.name=name
        self.client=client
        self.clientdata=''
        self.permsg=''
        self.received={}
        self.connect()
        self.run()



    def setname(self,name):
        self.name=name

    def setclient(self,client):
        self.client=client

    def getname(self):
        return self.name

    def connect(self):
        try:
            self.sock.connect((self.ip_address, self.port))
        except Exception,e:
            print str(e)

    def run(self):
        msg_rcv=threading.Thread(target=self.receiveMessage)
        msg_rcv.daemon=True
        msg_rcv.start()

   
    def sendMessage(self,msg):
        try:
            message=self.name+','+self.client+','+msg
            self.sock.sendall(pickle.dumps(message))
        except Exception, e:
            print str(e)

    def receiveMessage(self):
        print "thread receving is working.."
        while True:
            try:
                data=self.sock.recv(90456)
                if data:
                    fram= data[2:]
                    self.received.setdefault(self.client,fram)
                    self.clientdata=fram
                    return fram
            except:
                pass


    def disconnect(self):
        try:
            self.sock.close()
            print "Disconnect from Server"
        except Exception, e:
            print str(e)

    def sendClientAddress(self,ip):
        try:
            self.sock.sendall(ip)
        except Exception, e:
            print str(e)

