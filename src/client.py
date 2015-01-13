from __future__ import with_statement
import logging
import sys
import time

import Pyro4
from Pyro4 import threadutil

class DaemonThread(threadutil.Thread):
    def __init__(self, client):
        threadutil.Thread.__init__(self)
        self.client = client
        self.setDaemon(True)

    def run(self):
        with Pyro4.core.Daemon() as daemon:
            daemon.register(self.client)
            daemon.requestLoop(lambda: not self.client.abort)

class Client:
    def __init__(self):
        self.user_disconnect_event  = None
        self.user_connect_event     = None
        self.video_added_event = None

        self.abort = False
        self.server = Pyro4.core.Proxy('PYRONAME:cutie.server')

        self.user = None

        daemonthread = DaemonThread(self)
        daemonthread.start()

    def start(self):
        while not self.abort:
            time.sleep(1)

    def connect(self, user_name, group):
        self.server.connect_user(user_name, group, self)

    def disconnect(self):
        index = self.server.get_users().index(self.user)
        self.server.disconnect_user(index, self)
        self.abort = True

    def add_video(self, vid_id):
        self.server.add_video(vid_id, self)
        print "video id = "+vid_id

    def send_message(self, message):
        pass

    def get_users(self):
        return self.server.get_users()

    def get_queue(self):
        return self.server.get_queue()

    def get_sync_info(self):
        pass

    def test(self, arbitrary):
        ## testing function ##
        print arbitrary

    @Pyro4.callback
    def user_disconnect_listener(self, index):
        print "disconnected"
        if self.user_disconnect_event != None:
            self.user_disconnect_event(index)

    @Pyro4.callback
    def user_connect_listener(self, user):
        self.user = user
        print user.get_name()+" connected"
        if self.user_connect_event != None:
            self.user_connect_event(user)

    @Pyro4.callback
    def video_added_listener(self, queue_item):
        print "video added"
        if self.video_added_event != None:
            self.video_added_event(queue_item)

if __name__ == '__main__':
    client = Client()
    client.connect("Lizzy", "curator")
    client.start()