from PyQt4 import QtWebKit, QtGui, QtCore, QtGui
import sys
import time
import json
import threading
import gdata
import gdata.youtube 
import gdata.youtube.service
from qtui import Ui_MainDialog

from utils import *

class User(QtGui.QListWidgetItem):
    def __init__(self, user_name, parent=None):
        self.user_name = user_name
        super(User, self).__init__('', parent)

        self.setText(user_name)

class Video(QtGui.QListWidgetItem):
    def __init__(self, text, parent=None):
        self.ytID = text
        # https://developers.google.com/youtube/1.0/developers_guide_python?csw=1
        super(Video, self).__init__('', parent)

        self.setText('Retreiving title of "'+text+'."')
        self.t1 = threading.Thread(target=self.set_video_title)
        self.t1.start()

    def set_video_title(self):
        try:
            yt_service  = gdata.youtube.service.YouTubeService()
            entry       = yt_service.GetYouTubeVideoEntry(video_id=self.ytID)
            title       = entry.media.title.text
            duration    = entry.media.duration.seconds
    
            text = title + " - " + clock_from_seconds(duration)
            self.setText(text)
            self.setToolTip(text+"\nAdded by %s." % ("Lizzy"))
        except:
            self.setText("Retrying...")
            self.t1 = threading.Thread(target=self.set_video_title)
            self.t1.start()
        
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

import cutieclient
import cutieserv

# http://www.youtube.com/watch?v=oy18DJwy5lI
class MainForm(QtGui.QWidget):
    def __init__(self):
        super(MainForm, self).__init__()
        self.ui = Ui_MainDialog()
        self.ui.setupUi(self)
        self.ui.ytWebView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True) 
        self.ui.ytWebView.setUrl(QtCore.QUrl('../res/docs/index.html'))

        self.player = Player()
        self.ui.ytWebView.loadFinished.connect(self.web_loadFinished)

        self.player.videoOver.connect(self.play_next) # play the next video function
        self.player.videoCued.connect(self.transmit_state)
        self.player.videoPlaying.connect(self.transmit_state)
        self.player.videoPaused.connect(self.transmit_state)

        self.ui.addVideo.clicked.connect(self.add_to_queue)
        self.ui.videoLineURL.returnPressed.connect(self.add_to_queue)
        self.ui.voteSkip.clicked.connect(self.get_current_time_and_state)

        self.ui.ytQueue.doubleClicked.connect(self.playlist_play_index)
        self.ui.ytQueue.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.ui.ytQueue.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.ytQueue.customContextMenuRequested.connect(self.openQueueContextMenu)

        self.ui.chatBoxInput.returnPressed.connect(self.send_chat_message)

        self.ui.ipInputBox.returnPressed.connect(self.connect_to_server)

        self.current_idx = 0

        try:
            self.server = cutieserv.CutieServer()
            self.server.start()
        except: self.server = None

        self.client = cutieclient.CutieClient('localhost', 'Lizzy')
        self.client.start()
        self.client.vid_update_signal.sig.connect(self.client_state)
        self.client.chat_signal.sig.connect(self.update_chat)
        self.client.queue_signal.sig.connect(self.update_queue)

        self.chat_text = ''

    def web_loadFinished(self):
        self.ui.ytWebView.page().mainFrame().addToJavaScriptWindowObject('main', self.player)

    # ----- START CONTEXT MENU FUNCTIONS -----
    def openQueueContextMenu(self, position):
        # don't display context menu if list is empty
        if len(self.ui.ytQueue)==0: 
            return

        menu         = QtGui.QMenu(self.ui.ytQueue)
        removeAction = menu.addAction("Remove from queue")
        copyAction   = menu.addAction("Copy URL to clipboard")
        action       = menu.exec_(self.ui.ytQueue.mapToGlobal(position))

        if action == removeAction:
            item = self.ui.ytQueue.currentItem()
            self.ui.ytQueue.takeItem(self.ui.ytQueue.row(item))
            del item
        elif action == copyAction:
            item_id = self.ui.ytQueue.currentItem().ytID
            clipboard = QtGui.QApplication.clipboard()
            clipboard.clear(mode=clipboard.Clipboard)
            clipboard.setText("https://www.youtube.com/watch?v="+item_id, mode=clipboard.Clipboard)

    # ----- END CONTEXT MENU FUNCTIONS -----

    # ----- START CLIENT/SERVER FUNCTIONS -----
    def connect_to_server(self):
        self.client = cutieclient.CutieClient(self.ui.ipInputBox.text(), self.user_name)
        self.client.start()
        self.client.vid_update_signal.sig.connect(self.client_state)

    def add_user(self, user_name, user_group):
        self.ui.userList.addItem(User(user_name, user_group))

    # ----- CHAT FUNCTIONS -----
    def send_chat_message(self):
        self.client.send_chat(str(self.ui.chatBoxInput.text()))
        self.ui.chatBoxInput.setText("")

    def update_chat(self, message):
        if self.chat_text != '':
            self.chat_text += '<br />'
        self.chat_text += message
        self.ui.chatArea.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "body { font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal; margin:0px; padding:0px }"
            "p, li { white-space: pre-wrap; padding:0px; }\n"
            "</style></head><body><p style=\"margin-top:0px; text-indent:0px; font-size:8pt;\">%s</p></body></html>" % self.chat_text)
        self.ui.chatArea.verticalScrollBar().setValue(self.ui.chatArea.verticalScrollBar().maximum())

    # ----- STATE FUNCTIONS -----
    def transmit_state(self):
        if self.server != None:
            for client in self.server.client_threads[1:]:
                data = '{"sync":{"id":"'+self.player.ID+'","state":'+str(self.player.state)+',"time":'+str(self.player.time)+'}}'
                client.socket.send(data)

    def client_state(self, video_id, time, state):
        self.get_current_time_and_state()
        print video_id, time, state

        # Need to implement a play from (id, time) function as well as 
        # pause and whatever.
        if self.player.time < time-1 or self.player.time > time+1:
            print self.player.time, time
            self.ui.ytWebView.page().mainFrame().evaluateJavaScript("player.seekTo("+str(time)+",true)")
        if video_id != self.player.ID:
            self.play_video(video_id)
        if state == 1:
            self.ui.ytWebView.page().mainFrame().evaluateJavaScript("player.playVideo()")
        if state == 2:
            self.ui.ytWebView.page().mainFrame().evaluateJavaScript("player.pauseVideo()")
    
    # ----- VIDEO PLAYBACK FUNCTIONS -----
    def play_video(self, vid):
        self.ui.ytWebView.page().mainFrame().evaluateJavaScript("showVideo('"+vid+"',true)")

    def play_next(self):
        if self.current_idx+1 != self.ui.ytQueue.count():
            self.play_video(self.ui.ytQueue.item(self.current_idx+1).ytID)
            self.current_idx += 1
            self.ui.ytQueue.item(self.current_idx).setSelected(True)

    def playlist_play_index(self, idx):
        self.current_idx = idx.row()
        self.play_video(self.ui.ytQueue.item(idx.row()).ytID)
        self.ui.ytQueue.item(self.current_idx).setSelected(True)

    # ----- QUEUE FUNCTIONS -----
    def send_queue_to_server(self):
        pass

    def add_to_queue(self):
        """Adds url to the playlist"""
        url = self.ui.videoLineURL.text()
        vid_code = get_vid_code(url)
        
        if vid_code == 'xxx':
            QtGui.QMessageBox.warning(self, "Oopsie!", "Bad video URL.\nI only support YouTube video playback.")
            return
        if self.ui.ytQueue.count() == 0 or self.player.state == 0:
            self.play_video(vid_code)

        listItem = Video(vid_code)
        self.ui.ytQueue.addItem(listItem)
        self.ui.ytQueue.scrollToBottom()

        threading.Thread(target=self.scroll_up_delay).start()

        self.ui.ytQueue.reset()
        self.ui.videoLineURL.clear()

    def get_current_time_and_state(self):
        self.ui.ytWebView.page().mainFrame().evaluateJavaScript("getCurrentTime()")
        print ("Current state: "+str(self.player.state))
        print ("Current vids in queue: "+str(self.ui.ytQueue.count()))
        print ("Current time on video: "+str(self.player.time))

    def scroll_up_delay(self):
        time.sleep(2)
        self.ui.ytQueue.scrollToTop()

    def closeEvent(self, event):
        print("Closing and attempting to clear window.")
        self.ui.ytWebView.page().mainFrame().evaluateJavaScript("clearVideo()")
        sys.exit()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = MainForm()
    myapp.show()
    sys.exit(app.exec_())