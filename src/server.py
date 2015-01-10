from __future__ import print_function

import gdata
import gdata.youtube 
import gdata.youtube.service
from utils import *

import socket
import select
import sys

import Pyro4.core
import Pyro4.naming
import Pyro4.socketutil

# start nameserver:
# python -m Pyro4.naming &

class User(object):
    def __init__(self, name, group):
        self.name = name
        self.group = group
        # possible groups: 
        ## regular (can't add videos)
        ## promoted (can add videos)
        ## curator (can add videos, promote and kick users, is user everyone will sync to)
        #### there must be only one curator
        #### set as curator if first user to connect or next successive

    def get_name(self):
        return self.name

    def get_group(self):
        return self.group

    def set_group(self, group):
        self.group = group

class QueueItem(object):
    def __init__(self, vid_id):
        self.vid_id   = vid_id

        yt_service = gdata.youtube.service.YouTubeService()
        entry = yt_service.GetYouTubeVideoEntry(video_id=self.vid_id)

        self.title            = entry.media.title.text
        self.duration         = entry.media.duration.seconds
        self.view_count       = entry.statistics.view_count
        self.rating_average   = entry.rating.average
        self.duration_display = clock_from_seconds(self.duration)

    def get_title(self):
        return self.title

    def get_duration(self):
        return self.duration

    def get_view_count(self):
        return self.view_count

    def get_rating_average(self):
        return self.rating_average

    def get_duration_display(self):
        return self.duration_display
        
class Server:
    def __init__(self):
        self.users = []
        self.queue = []

        self.daemon = None
        self.nameserver = None
        self.uri = ""

    def start(self):
        self.daemon = Pyro4.core.Daemon()
        self.nameserver = Pyro4.naming.locateNS()
        self.uri = self.daemon.register(self)

        self.nameserver.register("cutie.server", self.uri)

        print ("Server started (uri = "+str(self.uri)+")")

        self.daemon.requestLoop()

    def get_uri(self):
        return self.uri

    def get_queue(self):
        return self.queue

    def get_users(self):
        return self.users

    def broadcast_chat_message(self, message):
        pass

    def add_user(self, user_name, group):
        u = User(user_name, group)
        self.daemon.register(u)
        self.users.append(u)

        print("User joined: "+u.name+", "+u.group)

    def add_video(self, vid_id):
        qi = QueueItem(vid_id)
        self.daemon.register(qi)
        self.queue.append(qi)

        print("Video added: "+vid_id)

    def user_disconnect(self, user):
        self.users.remove(user)

    def remove_video(self, index):
        self.queue.pop(index)

if __name__ == '__main__':
    server = Server()
    server.start()