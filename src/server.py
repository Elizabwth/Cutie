#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import gdata
import gdata.youtube 
import gdata.youtube.service
from utils import *

import socket
import sys
import time
import threading
import uuid

import Pyro4.core
import Pyro4.naming
import Pyro4.socketutil


def _cull_chat(lines):
    num_of_lines = len(lines)
    max_lines = num_of_lines-100
    if len(lines) > max_lines:
        lines = lines[max_lines:len(lines)]


class Server:
    def __init__(self):
        self.users = []
        self.queue = []
        self.chat = []
        self.player_state = {}

    def run(self):
        def tick():
            while True:
                time.sleep(1)
                _cull_chat(self.chat)

        thread = threading.Thread(target=tick)
        thread.setDaemon(True)
        thread.start()

    def get_queue(self):
        return self.queue

    def get_users(self):
        return self.users

    def get_chat(self):
        return self.chat

    def get_player_state(self):
        return self.player_state

    @Pyro4.oneway
    def broadcast_message(self, message, callback):
        self.chat.append(message)

        for user in self.users:
            user['callback'].message_received(message)

        print("<"+message['name']+"> "+message['message'])

    @Pyro4.oneway
    def connect_user(self, name, callback):
        u = {}
        u['name']     = name
        u['callback'] = callback
        u['uid']      = str(uuid.uuid4())[:8]
        self.users.append(u)

        for user in self.users:
            user['callback'].user_connected(u)

        print("<Connnection> NAME: '"+u['name']+"' UID: "+u['uid'])

    @Pyro4.oneway
    def disconnect_user(self, uid):
        index = 0
        for i, user in enumerate(self.users):
            if user['uid'] == uid:
                self.users.remove(user)
                index = i
                break

            print("<Disconnect> NAME: '"+user['name']+"' UID: "+user['uid']+" INDEX: "+index)

    @Pyro4.oneway
    def add_video(self, url, user_name):
        # add something that will check if a video can be embedded or not
        # if it can't, send the user that added it a callback stating that 
        # the video could not be added to the queue
        vid_id     = get_video_id(url)
        yt_service = gdata.youtube.service.YouTubeService()
        entry      = yt_service.GetYouTubeVideoEntry(video_id=vid_id)

        qi             = {}
        qi['vid_id']   = vid_id
        qi['title']    = entry.media.title.text
        qi['views']    = entry.statistics.view_count
        qi['rating']   = entry.rating.average
        qi['duration'] = entry.media.duration.seconds
        qi['added_by'] = user_name
        self.queue.append(qi)

        print("Video added: "+qi['vid_id'])

    @Pyro4.oneway
    def remove_video(self, index):
        self.queue.pop(index)

        print("Video removed at index: "+str(index))

    @Pyro4.oneway
    def sort_queue(self, initial, dropped):
        self.queue[initial], self.queue[dropped] = self.queue[dropped], self.queue[initial]

        print("Queue item sorted from row {0} to {1}".format(initial, dropped))

    @Pyro4.oneway
    def set_player_state(self, vid_id, time, state, queue_index):
        self.player_state['vid_id']      = vid_id
        self.player_state['time']        = time
        self.player_state['state']       = state
        self.player_state['queue_index'] = queue_index


def main():
    server = Server()

    daemon = Pyro4.Daemon(host = socket.gethostbyname(socket.gethostname()), port = 8080)
    server_uri = daemon.register(server, "cutie")

    server.run()
    print("<Server Started> URI: "+str(server_uri))
    daemon.requestLoop()

if __name__ == '__main__':
    main()