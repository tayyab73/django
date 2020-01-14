import socket,sys
import urllib2,Queue
import threading,time
from threading import Lock,RLock
import thread,pickle
class Server:
    ##########################################################################
    def __init__(self):
        self.clients=[]
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip_address = '127.0.0.1'

        self.port = 9000

        self.socketBind()
        self.socketListen()
        self.socket.setblocking(False)
        self.count=0
        
        while 1:
            sockAccept=threading.Thread(target=self.socketAccept)
            process=threading.Thread(target=self.socketProcess)
            sockAccept.daemon = True
            process.daemon = True
            sockAccept.start()
            process.start()



    #######################################################################
    def socketBind(self):
        try:
            self.socket.bind((self.ip_address, self.port))
        except Exception,e:
            print str(e)

    def socketListen(self):
        try:
            self.socket.listen(5)
        except Exception, e:
            print str(e)

    def socketAccept(self):
        try:
            self.connection, self.clientAddress = self.socket.accept()
            self.connection.setblocking(False)
            di={}
            di.setdefault(self.count,[self.connection,self.count])
            self.count+=1
            self.clients.append(di)
            return True
        except Exception, e:
            return str(e)

    ########################################################################

    def socketProcess(self):
        try:
            counter=0
            if len(self.clients)>0:
                for c in self.clients:

                    try:
                        if counter in c:
                            data=c[counter][0].recv(90456)
                            if data:
                                data=data.split(',')
                                c[counter][1]=data[0][1:]

                                clientname=data[1]
                                self.msg_to_client(data[2],clientname)

                            else:
                                print "not mention about client info.."
                        else:
                            print "data is not received by "+str(c)
                    except:
                        pass
                    counter+=1
        except Exception,e:
            print "Error due to "+str(e)


    def msg_to_client(self,msg,cli):
        try:
            counter=0
            for cl in self.clients:
                if counter<len(self.clients):

                    if cl[counter][1]==cli:
                        try:

                            s=cl[counter][0]
                            s.sendall(pickle.dumps(msg))
                            return True
                        except Exception,e:
                            return False
                else:
                    return False

                counter+=1
        except Exception,e:
            return False



