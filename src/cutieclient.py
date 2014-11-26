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
    sig = QtCore.pyqtSignal(int, list)

class UsersSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal(list)

class QueueRequestSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

class SyncRequestSignal(QtCore.QObject):
    sig = QtCore.pyqtSignal()

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

        self.queue_request_signal = QueueRequestSignal()
        self.sync_request_signal = SyncRequestSignal()

    def run(self):
        while True:
            data = self.clientsocket.recv(1024)
            data = str(data)

            self.incoming_chat_handle(data)
            self.video_update_handle(data)
            self.queue_handle(data)
            self.users_handle(data)

            self.queue_request_handle(data)
            self.sync_request_handle(data)

            if not data:
                break
            else:
                print "client recv " + data

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

    def users_handle(self, data):
        if data.startswith('{"users":'):
            result = json.loads(data)
            users = result["users"]
            self.users_signal.sig.emit(users)

    def queue_handle(self, data):
        if data.startswith('{"queue":'):
            result = json.loads(data)
            index = result["queue"]["index"]
            videos = result["queue"]["videos"]
            self.queue_signal.sig.emit(index, videos)

    def queue_request_handle(self, data):
        if data.startswith('{"queue_request"}'):
            self.queue_request_signal.sig.emit()

    def sync_request_handle(self, data):
        if data.startswith('{"sync_request"}'):
            self.sync_request_signal.sig.emit()

    def send_chat(self, message):
        data = '{"chat":{"name":"'+self.name+'","message":"'+message+'"}}'
        self.clientsocket.send(data)

    def vote_skip(self):
        data = '{"vote_skip"}'
        self.clientsocket.send(data)

if __name__ == '__main__':
    cc = CutieClient('localhost', 55567, 'Lizzy')
    cc.start()
    while True:
        time.sleep(1)