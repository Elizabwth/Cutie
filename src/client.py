from __future__ import with_statement
import sys
import time

import Pyro4
from Pyro4 import threadutil

class Client:
    def __init__(self, user_name, group):
        self.user_name = user_name
        self.group = group

        self.abort = 0
        self.server = Pyro4.core.Proxy('PYRONAME:cutie.server')

    def start(self):
        self.join()
        print "client joined "+str(self.server.get_uri())

        self.add_video("foXTsDKvRgc")
        print "queue length = "+str(len(self.get_queue()))

    def join(self):
        self.server.add_user(self.user_name, self.group)

    def add_video(self, vid_id):
        self.server.add_video(vid_id)

    def send_message(self, message):
        pass

    def get_users(self):
        return self.server.get_users()

    def get_queue(self):
        return self.server.get_queue()

    def get_sync_info(self):
        pass

class DaemonThread(threadutil.Thread):
    def __init__(self, server):
        threadutil.Thread.__init__(self)
        self.server = server
        self.setDaemon(True)

    def run(self):
        with Pyro4.core.Daemon() as daemon:
            daemon.register(self.server)
            daemon.requestLoop(lambda: not self.server.abort)

if __name__ == '__main__':
    client = Client("Lizzy", "curator")
    daemonthread = DaemonThread(client)
    daemonthread.start()
    client.start()