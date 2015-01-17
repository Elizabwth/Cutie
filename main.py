#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtWebKit, QtGui, QtCore, QtGui, uic
import ctypes
import sys
import time
import threading
import os
lib_path = os.path.abspath('src/')
sys.path.append(lib_path)

import Pyro4
import threading
import handler
import adblocker

from player import Player, PlayerState
from client import Client
from utils import *

class WebPage(QtWebKit.QWebPage):
    def javaScriptConsoleMessage(self, msg, line, source):
        # print '%s line %d: %s' % (source, line, msg)
        print 'js console, line %d: "%s"' % (line, msg)
        pass

class Main(QtGui.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.ui = uic.loadUi('ui/main.ui', self)
        
        ### webView setup ###
        self.ui.webView.setPage(WebPage())
        adManager = adblocker.AdblockerNetworkManager()
        self.ui.webView.page().setNetworkAccessManager(adManager)
        self.ui.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True) 
        self.ui.webView.setUrl(QtCore.QUrl('res/docs/index.html'))

        ### queueList setup ###
        self.ui.queueList.doubleClicked.connect(self.play_video_at_index)
        self.ui.queueList.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.ui.queueList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.queueList.customContextMenuRequested.connect(self.queue_context_menu)
        self.ui.queueList.dropEvent = self.queue_drop_event

        ### videoInput setup ###
        self.ui.videoInput.returnPressed.connect(self.add_video)

        ### voteButton setup ###
        self.ui.voteButton.clicked.connect(self.state_data_changed)

        ### userList setup ###

        ### chatText setup ###

        ### chatInput setup ###
        self.ui.chatInput.returnPressed.connect(self.send_message)

        ### Callback Handler ###
        self.handler = handler.CallbackHandler()
        self.handler.user_connected_signal.connect(self.user_connected)
        self.handler.user_disconnected_signal.connect(self.user_disconnected)
        self.handler.video_added_signal.connect(self.video_added)
        self.handler.video_removed_signal.connect(self.video_removed)
        #self.handler.state_data_requested_signal.connect(self.state_data_requested)
        self.handler.message_received_signal.connect(self.message_received)
        self.handler.queue_sorted_signal.connect(self.queue_sorted)
        self.handler.state_data_changed_signal.connect(self.state_data_changed)

        ### Playback Handlers ###
        self.player = Player(self.ui.webView)
        self.player.set_on_state_change_listener(self.player_state_changed)

        ### Daemon Thread ###
        daemon = Pyro4.core.Daemon()
        daemon.register(self.handler)

        thread = threading.Thread(target=daemon.requestLoop)
        thread.setDaemon(True)
        thread.start()

        ### initial setup ###
        # this will eventually pull from an ini with previous settings
        self.user_name  = "Lizzy"
        self.user_group = "curator"

        self.dialog = None
        self.show_connect_dialog()

        self.previous_state = -2

    ### PLAYER ###
    def play_video_at_index(self, item):
        queue = self.proxy.get_queue()[:]
        index = item.row()
        qi = queue[index]
        self.player.cue_video(qi['vid_id'])
        self.player.play()

    def player_state_changed(self, vid_id, time, state):
        if self.user_group == "curator":
            self.proxy.set_state_data(vid_id, time, state, 4)

        print("id = {0}, time = {1}, state = {2}".format(vid_id, time, state))

    def state_data_changed(self):
        data = self.proxy.get_state_data()
        state = data['state']
        print data
        
        if state == PlayerState.PLAYING:
            self.player.cue_video(data['vid_id'])
            self.player.seek(data['time'])
            self.player.play()
        elif state == PlayerState.PAUSED:
            self.player.seek(data['time'])
            self.player.pause()
        elif state == PlayerState.CUED:
            self.player.cue_video(data['vid_id'])
            self.player.seek(data['time'])

    ### SERVER CALLS ###
    def connect(self):
        ## RO Proxy ##
        name = str(self.dialog.ui.nameInput.text())
        ip   = str(self.dialog.ui.addressInput.text())
        port = str(self.dialog.ui.portInput.text())

        uri  = "PYRO:cutie@{0}:{1}".format(ip, port) # PYRO:cutie@10.0.1.12:8080
        self.proxy = Pyro4.Proxy(uri)

        users = self.proxy.get_users()[:]

        for user in users:
            self.ui.userList.addItem(user['name'])

        queue = self.proxy.get_queue()[:]
        for qi in queue:
            self.video_added(qi)

        unique = 0
        for user in users:
            if self.user_name == user['name']:
                unique += 1
                self.user_name = name+" ({0})".format(unique)
        if unique == 0:
            self.user_name = name

        for user in users:
            if user['group'] == "curator" and len(users) >= 1:
                self.user_group = "regular"

        self.proxy.connect_user(self.user_name, self.user_group, self.handler)

    def disconnect(self):
        self.proxy.disconnect_user(self.user_name)

    def add_video(self):
        url = str(self.ui.videoInput.text())
        self.proxy.add_video(url, self.user_name)
        self.ui.videoInput.clear()

    def send_message(self):
        text = str(self.ui.chatInput.text())
        text = text.replace('"', "&quot;") 
        self.proxy.broadcast_message(self.user_name, text)
        self.ui.chatInput.setText("")

    ### CALLBACKS ###
    def user_connected(self, user):
        self.ui.userList.addItem(user['name'])

    def user_disconnected(self, index):
        self.ui.userList.takeItem(index)

    def video_added(self, qi):
        # future point release: create a custom listwidgetitem that contains
        # more info about the video (and possibly a thumbnail?)
        title    = qi['title']
        added_by = qi['added_by']
        rating   = str(qi['rating'])[0:4]
        views    = intWithCommas(int(qi['views']))
        duration = clock_from_seconds(qi['duration'])

        item = QtGui.QListWidgetItem()
        item.setText(title + " - " + duration)
        item.setToolTip("Added by:\t{0}\nRating:\t\t{1}\nTotal views:\t{2}".format(added_by, rating, views))
        self.ui.queueList.addItem(item)

    def video_removed(self, index):
        self.ui.queueList.takeItem(index)

    def queue_sorted(self, initial_row, dropped_row):
        if initial_row != dropped_row:
            item = self.ui.queueList.takeItem(initial_row)
            self.ui.queueList.insertItem(dropped_row, item)

    def message_received(self, name, message):
        self.ui.chatText.append("<b>"+name+":</b> "+message)
        self.ui.chatText.verticalScrollBar().setValue(self.ui.chatText.verticalScrollBar().maximum())

    ### UI ###
    def queue_drop_event(self, event):
        # get inital row of dragged item before continuing
        source        = event.source()
        item          = source.currentItem()
        initial_index = source.row(item)

        # do the drop action
        QtGui.QListWidget.dropEvent(self.ui.queueList, event)

        if event.isAccepted():
            dropped_index = source.row(item)
            self.proxy.sort_queue(initial_index, dropped_index)

            print "initial index = {0}, dropped index = {1}".format(str(initial_index), str(dropped_index))

    def queue_context_menu(self, position):
        if len(self.ui.queueList) == 0: 
            return

        cbicon = QtGui.QIcon(r"res/img/clipboard.png")
        ericon = QtGui.QIcon(r"res/img/eraser.png")

        menu         = QtGui.QMenu(self.ui.queueList)
        removeAction = menu.addAction(ericon, "Remove from queue")
        copyAction   = menu.addAction(cbicon, "Copy URL to clipboard")
        action       = menu.exec_(self.ui.queueList.mapToGlobal(position))

        queue = self.proxy.get_queue()[:]
        item = self.ui.queueList.currentItem()
        item_index = self.ui.queueList.row(item)
        if action == removeAction:
            self.proxy.remove_video(item_index)
            del item
        elif action == copyAction:
            qi = queue[item_index]
            clipboard = QtGui.QApplication.clipboard()
            clipboard.clear(mode = clipboard.Clipboard)
            clipboard.setText("http://youtu.be/"+qi['vid_id'], mode = clipboard.Clipboard)

    def show_connect_dialog(self):
        self.dialog = QtGui.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.dialog.ui = uic.loadUi('ui/connectdialog.ui', self.dialog)

        self.dialog.ui.nameInput.setText("Lizzy") # debug
        self.dialog.ui.addressInput.setText("10.0.1.12") # debug
        self.dialog.ui.portInput.setText("8080")

        self.dialog.ui.okCancle.accepted.connect(self.connect)
        self.dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.dialog.show()

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 
                                           "Cutie", 
                                           "Quit Cutie?", 
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.disconnect()
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    # allow taskbar to display icon
    myappid = 'elizabwth.cutie' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QtGui.QApplication(sys.argv)
    #myapp = MainForm()
    #myapp.show()
    myapp = Main()
    myapp.show()

    sys.exit(app.exec_())