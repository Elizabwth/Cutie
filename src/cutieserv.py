# http://seanmcgary.com/posts/threaded-tcp-server-in-python

from socket import *
import thread
import time
import threading
import json

from PyQt4 import QtCore

class Tick(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.server = None

    def set_server(self, server):
        self.server = server

    def run(self):
        while 1:
            time.sleep(5)
            self.server.tick()
        self.terminate()

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

        self.queue_json = None

        self.ticker = Tick()
        self.ticker.set_server(self)

    def run(self):
        self.ticker.start()

        while 1:
            print "Listening for connections...\n"
            clientsocket, clientaddr = self.serversocket.accept()
            print "Accepted connection from:", clientaddr

            ct = ClientThread(clientsocket, clientaddr)
            ct.serv = self
            ct.start()
            self.client_threads.append(ct)

            print "Current users connected: "+str(len(self.client_threads))

    def disconnect_client(self, thread):
        print "Disconnecting user ("+thread.name+") with address "+str(thread.address[0])+" and popping thread"
        self.client_threads.remove(thread)

    def broadcast_sync(self, data):
        for thread in self.client_threads[1:]:
            thread.send_packet(data)

    def broadcast_chat(self, message):
        for thread in self.client_threads:
            thread.send_packet(message)

    def broadcast_users(self):
        # construct packet
        data = {"users":[]}

        for thread in self.client_threads:
            address = thread.address[0]
            name    = thread.name
            power   = "user"

            if thread == self.client_threads[0]:
                name += "*"
                power = "admin"

            data["users"] += [{"ip":address, "name":name, "power":power}]

        # dump json to string
        self.users_json = json.dumps(data)
        for thread in self.client_threads:
            thread.send_packet(self.users_json)

    def broadcast_queue(self, queue):
        for thread in self.client_threads[1:]:
            thread.send_packet(queue)

    def tick(self):
        if len(self.client_threads) > 0:
            self.client_threads[0].request_sync()
            time.sleep(1)

            self.client_threads[0].request_queue()
            time.sleep(1)
            
            self.broadcast_users()

class ClientThread(QtCore.QThread):
    def __init__(self, socket, address, parent=None):
        QtCore.QThread.__init__(self, parent)

        self.socket  = socket
        self.address = address
        self.name    = ""

        self.serv = None

    def run(self):
        while 1:
            try:
                data = self.socket.recv(1024)
                data = data.replace("\x00", "") # remove null bytes
            except:
                data = 'None'
                self.serv.disconnect_client(self)

            # handle setting of thread's user name
            if data.startswith('{"join_request"'):
                result = json.loads(data)
                self.name = result["join_request"]["name"]

            # handle incoming chats
            if data.startswith('{"chat"'):
                self.serv.broadcast_chat(data)

            # handle sending data to all clients other than the orchestrator (first user)
            if (len(self.serv.client_threads) > 0):
                if ((self == self.serv.client_threads[0]) and data.startswith('{"sync"')):
                    self.serv.broadcast_sync(data)
                if ((self == self.serv.client_threads[0]) and data.startswith('{"queue"')):
                    self.serv.broadcast_queue(data)
            
            if not data or data == 'None':
                break
            else:
                print "(ClientThread) recv: "+ data
    
        self.socket.close()

    def send_packet(self, data):
        self.socket.send(data)

    def request_queue(self):
        self.socket.send('{"queue_request"}')

    def request_sync(self):
        self.socket.send('{"sync_request"}')

if __name__ == "__main__":
    cs = CutieServer()
    cs.start()
    while True:
        time.sleep(1)