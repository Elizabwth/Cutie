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
from joindialog import *
from player import Player
import cutieclient
import cutieserv

class User(QtGui.QListWidgetItem):
    def __init__(self, user_name, parent=None):
        self.user_name = user_name
        super(User, self).__init__('', parent)

        self.setText(user_name)
        self.setToolTip(user_name)

class Video(QtGui.QListWidgetItem):
    def __init__(self, ytid, title, added_by, parent=None):
        super(Video, self).__init__('', parent)
        self.ytID = ytid
        self.title = title
        self.added_by = added_by
        
        self.setText(title)

        if ytid == title:
            self.setText('Retreiving title of "'+ytid+'."')
            self.t1 = threading.Thread(target=self.set_video_title)
            self.t1.start()

    def set_video_title(self):
        try:
            # https://developers.google.com/youtube/1.0/developers_guide_python?csw=1
            yt_service  = gdata.youtube.service.YouTubeService()
            entry       = yt_service.GetYouTubeVideoEntry(video_id=self.ytID)
            title       = entry.media.title.text
            duration    = entry.media.duration.seconds
    
            self.title = title + " - " + clock_from_seconds(duration)
            self.setText(self.title)
            self.setToolTip(self.title+"\nAdded by %s." % (self.added_by))
        except:
            self.setText("Retrying to retreive title...")
            self.t1 = threading.Thread(target=self.set_video_title)
            self.t1.start()

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
        self.ui.ytQueue.installEventFilter(self)

        self.ui.chatBoxInput.returnPressed.connect(self.send_chat_message)

        self.current_idx = 0
        self.playing_id = ''

        self.chat_text = ''

        # open dialogue
        self.dialog = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.dialog.ui = Ui_JoinDialog()
        self.dialog.ui.setupUi(self.dialog)

        self.dialog.ui.addressInput.setText("localhost") # debug
        self.dialog.ui.nameInput.setText("Lizzy") # debug
        self.dialog.ui.portInput.setText("55567") # debug

        self.dialog.ui.okCancle.accepted.connect(self.connect_to_server)
        self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.dialog.exec_()

        self.user_name = self.dialog.ui.nameInput.text

    def web_loadFinished(self):
        self.ui.ytWebView.page().mainFrame().addToJavaScriptWindowObject('main', self.player)

    # ----- START CLIENT/SERVER FUNCTIONS -----
    def connect_to_server(self):
        address = self.dialog.ui.addressInput.text()
        port    = int(self.dialog.ui.portInput.text())
        name    = self.dialog.ui.nameInput.text()

        self.client = cutieclient.CutieClient(address, port, name)
        self.client.start()
        self.client.vid_update_signal.sig.connect(self.client_state)
        self.client.chat_signal.sig.connect(self.update_chat)
        self.client.users_signal.sig.connect(self.populate_users)
        self.client.queue_signal.sig.connect(self.populate_queue)

        self.client.queue_request_signal.sig.connect(self.send_queue)

    def populate_users(self, users):
        self.ui.userList.clear()
        for user in users:
            self.ui.userList.addItem(User(user["name"]))

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

    # ----- CHAT FUNCTIONS -----
    def send_chat_message(self):
        text = str(self.ui.chatBoxInput.text())
        text = text.replace('"', "&quot;") 
        self.client.send_chat(text)
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
        data = '{"sync":{"id":"'+self.player.ID+'","state":'+str(self.player.state)+',"time":'+str(self.player.time)+'}}'
        self.client.clientsocket.send(data)

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
        self.playing_id = vid
        self.ui.ytWebView.page().mainFrame().evaluateJavaScript("showVideo('"+vid+"',true)")

    def play_next(self):
        if self.current_idx+1 != self.ui.ytQueue.count():

            item = self.ui.ytQueue.currentItem()
            self.current_idx = self.ui.ytQueue.row(item)+1
            self.play_video(self.ui.ytQueue.item(self.current_idx).ytID)
            self.ui.ytQueue.item(self.current_idx).setSelected(True)

    def playlist_play_index(self, idx):
        self.current_idx = idx.row()
        self.play_video(self.ui.ytQueue.item(idx.row()).ytID)
        self.ui.ytQueue.item(self.current_idx).setSelected(True)

    # ----- QUEUE FUNCTIONS -----
    # --- SERVER REQUESTED ---
    def construct_queue(self):
        queue = {"queue":{"index":self.current_idx,"videos":[]}}

        for index in xrange(self.ui.ytQueue.count()):
            ytid = self.ui.ytQueue.item(index).ytID
            title = self.ui.ytQueue.item(index).title

            queue["queue"]["videos"] += [{"id":ytid,"title":title}]

        return queue

    def send_queue(self):
        data = json.dumps(self.construct_queue())
        self.client.clientsocket.send(data)

    # --- FROM SERVER ---
    def populate_queue(self, index, videos):
        self.current_idx = index

        self.ui.ytQueue.clear()
        for video in videos:
            listItem = Video(video["id"], video["title"], "?")
            self.ui.ytQueue.addItem(listItem)
            self.ui.ytQueue.reset()

        if self.ui.ytQueue.count() > 0:
            self.ui.ytQueue.item(self.current_idx).setSelected(True)

    # --- ORCHESTRATOR ---
    def add_to_queue(self):
        """Adds url to the playlist"""
        url = self.ui.videoLineURL.text()
        vid_code = get_vid_code(url)
        
        if vid_code == 'xxx':
            QtGui.QMessageBox.warning(self, "Oopsie!", "Bad video URL.\nI only support YouTube video playback.")
            return
        if self.ui.ytQueue.count() == 0 or self.player.state == 0:
            self.play_video(vid_code)

        listItem = Video(vid_code, vid_code, self.user_name)
        self.ui.ytQueue.addItem(listItem)
        self.ui.ytQueue.scrollToBottom()

        self.ui.ytQueue.reset()
        self.ui.videoLineURL.clear()

    def get_current_time_and_state(self):
        self.ui.ytWebView.page().mainFrame().evaluateJavaScript("getCurrentTime()")
        print ("Current state: "+str(self.player.state))
        print ("Current vids in queue: "+str(self.ui.ytQueue.count()))
        print ("Current time on video: "+str(self.player.time))

        self.construct_queue()

    def closeEvent(self, event):
        print("Closing and attempting to clear window.")
        self.ui.ytWebView.page().mainFrame().evaluateJavaScript("clearVideo()")
        sys.exit()

    # http://stackoverflow.com/questions/13788452/pyqt-how-to-handle-event-without-inheritance
    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.ChildRemoved: # and source is self.ui.ytQueue)
            dropped = source.currentItem()
            if self.playing_id == dropped.ytID:
                self.current_idx = source.row(dropped)

        return QtGui.QWidget.eventFilter(self, source, event)

if __name__ == '__main__':
    try:
        server = cutieserv.CutieServer()
        server.start()
    except: pass

    app = QtGui.QApplication(sys.argv)
    myapp = MainForm()
    myapp.show()
    sys.exit(app.exec_())