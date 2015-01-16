import Pyro4
import threading

class CallbackHandler:
    def __init__(self):
        self.user_connected_listener = None
        self.user_disconnected_listener = None
        self.video_added_listener = None
        self.video_removed_listener = None
        self.sync_data_requested_listener = None
        self.message_received_listener = None
        self.queue_sorted_listener = None

    def set_user_connected_listener(self, listener):
        self.user_connected_listener = listener

    def set_user_disconnected_listener(self, listener):
        self.user_disconnected_listener = listener

    def set_video_added_listener(self, listener):
        self.video_added_listener = listener

    def set_video_removed_listener(self, listener):
        self.video_removed_listener = listener

    def set_sync_data_requested_listener(self, listener):
        self.sync_data_requested_listener = listener

    def set_message_received_listener(self, listener):
        self.message_received_listener = listener

    def set_queue_sorted_listener(self, listener):
        self.queue_sorted_listener = listener

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
    def sync_data_requested(self):
        print("sync_data_requested callback")
        if self.sync_data_requested_listener:
            self.sync_data_requested_listener()

    @Pyro4.callback
    def message_received(self, name, message):
        print("message_received callback")
        if self.message_received_listener:
            self.message_received_listener(name, message)

    @Pyro4.callback
    def queue_sorted(self, initial, dropped):
        print("queue_sorted callback")
        if self.queue_sorted_listener:
            self.queue_sorted_listener(initial, dropped)

class PlaybackHandler:
	def __init__(self):
		self.play_listener = None
		self.pause_listener = None

	def play(self, vid_id, time):
		print("play callback")
		if self.play_listener:
			self.play_listener(vid_id, time)

	def pause(self, vid_id, time):
		print("pause callback")
		if self.pause_listener:
			self.pause_listener(vid_id, time)