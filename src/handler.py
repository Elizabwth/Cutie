import Pyro4
import threading

class CallbackHandler:
    def __init__(self):
        self.user_connected_listener = None
        self.user_disconnected_listener = None
        self.video_added_listener = None
        self.video_removed_listener = None
        self.sync_listener = None

    def set_user_connected_listener(self, listener):
        self.user_connected_listener = listener

    def set_user_disconnected_listener(self, listener):
        self.user_disconnected_listener = listener

    def set_video_added_listener(self, listener):
        self.video_added_listener = listener

    def set_video_removed_listener(self, listener):
        self.video_removed_listener = listener

    def set_sync_listener(self, listener):
        self.sync_listener = listener

    @Pyro4.callback
    def user_connected(self, user):
        print("user_connected callback")
        if self.user_connected_listener:
            self.user_connected_listener(user)

    @Pyro4.callback
    def user_disconnected(self, user):
        print("user_disconnected callback")
        if self.user_disconnected_listener:
            self.user_disconnected_listener(user)

    @Pyro4.callback
    def video_added(self, qi):
        print("video_added callback")
        if self.video_added_listener:
            self.video_added_listener(qi)

    @Pyro4.callback
    def video_removed(self, index):
        print("video_removed callback")
        if self.video_removed_listener:
            self.video_removed_listener(index)

    @Pyro4.callback
    def sync(self, data):
        print("sync callback")
        if self.sync_listener:
            self.sync_listener(data)