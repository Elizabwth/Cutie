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

from player import Player
from client import Client
from utils import *

class WebPage(QtWebKit.QWebPage):
    def javaScriptConsoleMessage(self, msg, line, source):
        # print '%s line %d: %s' % (source, line, msg)
        # print 'js console, line %d: "%s"' % (line, msg)
        pass

class Main(QtGui.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.ui = uic.loadUi('ui/cutierework.ui', self)
        
        self.player = Player()

        ### webView setup ###
        self.ui.webView.setPage(WebPage())
        adManager = adblocker.AdblockerNetworkManager()
        self.ui.webView.page().setNetworkAccessManager(adManager)
        self.ui.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True) 
        self.ui.webView.setUrl(QtCore.QUrl('res/docs/index.html'))
        self.ui.webView.loadFinished.connect(self.webLoadFinished)

        ### queueList setup ###
        #self.ui.queueList.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.ui.queueList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.queueList.customContextMenuRequested.connect(self.queueContextMenu)
        self.ui.queueList.dropEvent = self.queueDropEvent

        ### videoInput setup ###
        self.ui.videoInput.returnPressed.connect(self.add_video)

        ### skipButton setup ###

        ### userList setup ###

        ### chatText setup ###

        ### chatInput setup ###

        ### RO Proxy ###   
        uri = "PYRO:cutie@10.0.1.12:8080"

        self.proxy = Pyro4.Proxy(uri)

        self.handler = handler.CallbackHandler()
        self.handler.set_user_connected_listener(self.user_connected)
        self.handler.set_user_disconnected_listener(self.user_disconnected)
        self.handler.set_video_added_listener(self.video_added)
        self.handler.set_video_removed_listener(self.video_removed)
        self.handler.set_sync_listener(self.sync)

        daemon = Pyro4.core.Daemon()
        daemon.register(self.handler)

        thread = threading.Thread(target=daemon.requestLoop)
        thread.setDaemon(True)
        thread.start()

        self.user_name = "Lizzy"
        self.user_group = "curator"

        self.showConnectDialog()

    def webLoadFinished(self):
        self.ui.webView.page().mainFrame().addToJavaScriptWindowObject('main', self.player)

    def showConnectDialog(self):
        dialog = QtGui.QDialog(self, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        dialog.ui = uic.loadUi('ui/connectdialog.ui', dialog)

        dialog.ui.nameInput.setText("Lizzy") # debug

        dialog.ui.okCancle.accepted.connect(self.connect)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        dialog.show()

        # move proxy creation into here or into the connect function?

    def queueDropEvent(self, event):
        QtGui.QListWidget.dropEvent(self.ui.queueList, event)
        if event.isAccepted():
            source  = event.source()
            dropped = source.currentItem()
            index   = source.row(dropped)
            print "Index = " + str(index)

    def queueContextMenu(self, position):
        if len(self.ui.queueList) == 0: 
            return

        cbicon = QtGui.QIcon(r"res/img/clipboard.png")
        ericon = QtGui.QIcon(r"res/img/eraser.png")

        menu         = QtGui.QMenu(self.ui.queueList)
        removeAction = menu.addAction(ericon, "Remove from queue")
        copyAction   = menu.addAction(cbicon, "Copy URL to clipboard")
        action       = menu.exec_(self.ui.queueList.mapToGlobal(position))

        item = self.ui.queueList.currentItem()
        item_index = self.ui.queueList.row(item)
        if action == removeAction:
            self.proxy.remove_video(item_index)
            del item
        elif action == copyAction:
            qi = self.proxy.get_queue()[item_index]
            clipboard = QtGui.QApplication.clipboard()
            clipboard.clear(mode=clipboard.Clipboard)
            clipboard.setText("http://youtu.be/"+qi['vid_id'], mode=clipboard.Clipboard)

    ### SERVER CALLS ###
    def connect(self):
        self.proxy.connect_user(self.user_name, self.user_group, self.handler)

    def disconnect(self):
        self.proxy.disconnect_user(self.user_name)

    def add_video(self):
        url = str(self.ui.videoInput.text())
        self.proxy.add_video(url, self.user_name)
        self.ui.videoInput.clear()

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

    def sync(self, data):
        pass

    def closeEvent(self,event):
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