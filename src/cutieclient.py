# http://seanmcgary.com/posts/threaded-tcp-server-in-python

from socket import *
import threading
import time
import cutieserv
import json

from PyQt4 import QtCore

from utils import *

class VidUpdateSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(str,float,int)

class ChatSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(str)

class QueueSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(list)

class UsersSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(list)

class CutieClient(QtCore.QThread):
    def __init__(self, host, port, name, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.name = name

        addr = (host, port)
    
        self.clientsocket = socket(AF_INET, SOCK_STREAM)
        self.clientsocket.connect(addr)

        info = '{"join_request":{"name":"'+name+'"}}'
        self.clientsocket.send(info)

        self.vid_update_signal  = VidUpdateSignal()
        self.chat_signal        = ChatSignal()
        self.queue_signal       = QueueSignal()
        self.users_signal       = UsersSignal()

    def run(self):
        while True:
            data = self.clientsocket.recv(1024)
            data = str(data)

            self.incoming_chat_handle(data)
            self.video_update_handle(data)
            self.queue_handle(data)
            self.users_handle(data)

            if not data:
                break
            else:
                print data

        self.clientsocket.close()

    def incoming_chat_handle(self, data):
        if data.startswith('{"chat":'):
            result = json.loads(data)
            name = result["chat"]["name"]
            msg = result["chat"]["message"]
            chat = "<b>"+name+"</b>: "+msg
            self.chat_signal.sig.emit(chat)

    def video_update_handle(self, data):
        if data.startswith('{"sync":'):
            result = json.loads(data)
            vid_id = result["sync"]["id"]
            time = result["sync"]["time"]
            state = result["sync"]["state"]
            self.vid_update_signal.sig.emit(vid_id, time, state)

    def queue_handle(self, data):
        if data.startswith('{"queue":'):
            result = json.loads(data)
            queue = result["queue"]
            self.queue_signal.sig.emit(queue)

    def users_handle(self, data):
        if data.startswith('{"users":'):
            result = json.loads(data)
            users = result["users"]
            self.users_signal.sig.emit(users)

    def send_chat(self, message):
        data = '{"chat":{"name":"'+self.name+'","message":"'+message+'"}}'
        self.clientsocket.send(data)

if __name__ == '__main__':
    cc = CutieClient('localhost', 55567, 'Lizzy')
    cc.start()
    while True:
        pass
