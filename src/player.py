from PyQt4 import QtCore
from utils import *

class PlayerState:
    OVER = 0
    PLAYING = 1
    PAUSED = 2
    BUFFERING = 3
    CUED = 5

# from: http://mspadaru.wordpress.com/2012/08/18/intro/
class YouTubeAPI(QtCore.QObject):
    def __init__(self, parent=None):
        super(YouTubeAPI, self).__init__(parent) 
        self.state     = -1
        self.time      = 0.00
        self.vid_id    = ''

    videoOver      = QtCore.pyqtSignal()
    videoPlaying   = QtCore.pyqtSignal()
    videoPaused    = QtCore.pyqtSignal()
    videoBuffering = QtCore.pyqtSignal()
    videoCued      = QtCore.pyqtSignal()

    @QtCore.pyqtSlot()
    def video_over(self):
        self.state = PlayerState.OVER
        self.videoOver.emit()
        print "video over"

    @QtCore.pyqtSlot()
    def video_playing(self):
        self.state = PlayerState.PLAYING
        self.videoPlaying.emit()
        print "video playing at", self.time

    @QtCore.pyqtSlot()
    def video_paused(self):
        self.state = PlayerState.PAUSED
        self.videoPaused.emit()
        print "video paused at", self.time

    @QtCore.pyqtSlot()
    def video_buffering(self):
        self.state = PlayerState.BUFFERING
        self.videoBuffering.emit()
        print "video buffering"

    @QtCore.pyqtSlot()
    def video_cued(self):
        self.state = PlayerState.CUED
        self.videoCued.emit()
        print "video cued"

    @QtCore.pyqtSlot(float)  
    def get_current_time(self, time):
        self.time = time

    @QtCore.pyqtSlot(str)
    def get_current_url(self, url):
        self.vid_id = get_video_id(url)

    @QtCore.pyqtSlot(float)  
    def get_loaded_fraction(self, fraction):
        self.loaded_fraction = fraction

class Player(object):
    def __init__(self, web_view):
        self.web_view = web_view

        self.state_change_listener = None

        self.youtube_api = YouTubeAPI()
        self.youtube_api.videoOver.connect(self.on_state_change)
        self.youtube_api.videoPlaying.connect(self.on_state_change)
        self.youtube_api.videoPaused.connect(self.on_state_change)
        self.youtube_api.videoBuffering.connect(self.on_state_change)
        self.youtube_api.videoCued.connect(self.on_state_change)

        self.web_view.loadFinished.connect(self.web_load_finished)

    def cue_video(self, vid_id):
        if self.youtube_api.vid_id != vid_id:
            self.web_view.page().mainFrame().evaluateJavaScript("player.stopVideo()")
            self.web_view.page().mainFrame().evaluateJavaScript("player.clearVideo()")
            self.web_view.page().mainFrame().evaluateJavaScript("player.cueVideoById('"+vid_id+"')")

    def play(self):
        self.web_view.page().mainFrame().evaluateJavaScript("player.playVideo()")

    def pause(self):
        self.web_view.page().mainFrame().evaluateJavaScript("player.pauseVideo()")

    def seek(self, time):
        self.web_view.page().mainFrame().evaluateJavaScript("player.seekTo("+str(time)+", true)")

    def set_on_state_change_listener(self, listener):
        self.state_change_listener = listener

    def on_state_change(self):
        if self.state_change_listener:
            vid_id = self.youtube_api.vid_id
            state = self.youtube_api.state
            time = self.youtube_api.time
            self.state_change_listener(vid_id, time, state)

    def web_load_finished(self):
        self.web_view.page().mainFrame().addToJavaScriptWindowObject('main', self.youtube_api)