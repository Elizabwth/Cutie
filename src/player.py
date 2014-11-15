from PyQt4 import QtCore
from utils import *
# from: http://mspadaru.wordpress.com/2012/08/18/intro/
class Player(QtCore.QObject):
    def __init__(self, parent=None):
        super(Player, self).__init__(parent) 
        self.state  = -1
        self.time   = 0.00
        self.ID     = ''

    videoOver       = QtCore.pyqtSignal()
    videoPlaying    = QtCore.pyqtSignal()
    videoPaused     = QtCore.pyqtSignal()
    videoBuffering  = QtCore.pyqtSignal()
    videoCued       = QtCore.pyqtSignal()

    @QtCore.pyqtSlot()
    def video_over(self):
        self.state = 0
        self.videoOver.emit()
        print "Video is over."
    @QtCore.pyqtSlot()
    def video_playing(self):
        self.state = 1
        self.videoPlaying.emit()
        print "Video is playing.", self.time
    @QtCore.pyqtSlot()
    def video_paused(self):
        self.state = 2
        self.videoPaused.emit()
        print "Video is paused.", self.time
    @QtCore.pyqtSlot()
    def video_buffering(self):
        self.state = 3
        self.videoBuffering.emit()
        print "Video is buffering."
    @QtCore.pyqtSlot()
    def video_cued(self):
        self.state = 5
        self.videoCued.emit()
        print "Video is cued."
    @QtCore.pyqtSlot(float)  
    def curTime(self, time):
        self.time = time
        #print "Time on video", time
    @QtCore.pyqtSlot(str)  
    def curURL(self, URL):
        self.URL = URL
        self.ID = get_vid_code(URL)
        #print "Time on video", time