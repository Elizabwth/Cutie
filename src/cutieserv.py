# http://seanmcgary.com/posts/threaded-tcp-server-in-python

from socket import *
import thread
import time
import threading
import json

from PyQt4 import QtCore

from utils import *


class OnJoinSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(str)

class BroadcastChatSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(str)

class CutieServer(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        host = ''
        port = 55567

        addr = (host, port)

        self.serversocket = socket(AF_INET, SOCK_STREAM)

        self.serversocket.bind(addr)
        self.serversocket.listen(10)

        self.client_threads = []

        self.broadcast_chat_signal = BroadcastChatSignal()

    def run(self):
        while 1:
            print "Listening for connections...\n"
            clientsocket, clientaddr = self.serversocket.accept()
            print "Accepted connection from:", clientaddr

            ct = ClientThread(clientsocket, clientaddr)
            ct.serv = self
            ct.start()
            self.client_threads.append(ct)

            time.sleep(.05)

            print "Current users connected: "+str(len(self.client_threads))

    def disconnect_client(self, thread):
        print "Popping thread ("+thread.name+")"
        self.client_threads.remove(thread)

    def broadcast_chat(self, message):
        for thread in self.client_threads:
            thread.send_chat(message)

    def broadcast_connected_users(self, user_packet):
        pass


class ClientThread(QtCore.QThread):
    def __init__(self, socket, address, parent=None):
        QtCore.QThread.__init__(self, parent)

        self.socket     = socket
        self.address    = address
        self.power = ''
        self.name  = ''

        self.serv = None

    def run(self):
        while 1:
            try:
                data = self.socket.recv(1024)
            except:
                data = 'None'
                self.serv.disconnect_client(self)
                print("Disconnected "+self.address[0]+" ("+self.name+") from server.")

            # handle incoming chats
            if data.startswith('{"chat"'):
                self.serv.broadcast_chat(data)
            
            if not data or data == 'None':
                break
            else:
                #print data
                msg = "You sent me: %s" % data
                self.socket.send(msg)
    
        self.socket.close()

    def send_chat(self, message):
        self.socket.send(message)

if __name__ == "__main__":
    cs = CutieServer()
    cs.start()
    while True:
        pass