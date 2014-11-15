# http://seanmcgary.com/posts/threaded-tcp-server-in-python

from socket import *
import thread
import time
import threading
import json

from PyQt4 import QtCore

from utils import *

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

        self.queue = []
        self.users = []

    def run(self):
        while 1:
            print "Listening for connections...\n"
            clientsocket, clientaddr = self.serversocket.accept()
            print "Accepted connection from:", clientaddr

            ct = ClientThread(clientsocket, clientaddr)
            ct.serv = self
            ct.start()
            self.client_threads.append(ct)

            time.sleep(0.05)

            print "Current users connected: "+str(len(self.client_threads))

    def disconnect_client(self, thread):
        print "Disconnecting user ("+thread.name+") with address "+str(thread.address[0])+" and popping thread"
        self.client_threads.remove(thread)

    def broadcast_chat(self, message):
        for thread in self.client_threads:
            thread.send_message_to_client(message)

    def broadcast_connected_users(self, users):
        for thread in self.client_threads:
            thread.send_users_to_client(users)

    def broadcast_queue(self, queue):
        pass


class ClientThread(QtCore.QThread):
    def __init__(self, socket, address, parent=None):
        QtCore.QThread.__init__(self, parent)

        self.socket = socket
        self.address = address

        self.name = ""

        self.serv = None

    def run(self):
        while 1:
            try:
                data = self.socket.recv(1024)
                data = data.replace("\x00", "") # remove null bytes
            except:
                data = 'None'
                self.serv.disconnect_client(self)

            # handle setting of user name
            if data.startswith('{"join_request"'):
                result = json.loads(data)
                self.name = result["join_request"]["name"]

            # handle incoming chats
            if data.startswith('{"chat"'):
                self.serv.broadcast_chat(data)
            
            if not data or data == 'None':
                break
            else:
                print "(ClientThread) recv: %s" % data
    
        self.socket.close()

    def send_message_to_client(self, message):
        self.socket.send(message)

    def send_queue_to_client(self, queue):
        self.socket.send(message)

    def send_users_to_client(self, users):
        self.socket.send(message)

    def request_queue(self):
        self.socket.send('{"queue_request"}')

if __name__ == "__main__":
    cs = CutieServer()
    cs.start()
    while True:
        pass