# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cutie.ui'
#
# Created: Sat Dec 07 01:34:44 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!
# 

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

from PyQt4 import QtWebKit


# work around to allow the taskbar to display the icon
import ctypes
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class WebPage(QtWebKit.QWebPage):
    def javaScriptConsoleMessage(self, msg, line, source):
        # print '%s line %d: %s' % (source, line, msg)
        # print 'js console, line %d: "%s"' % (line, msg)
        pass

class Ui_MainDialog(object):
    def setupUi(self, MainDialog):
        MainDialog.setObjectName(_fromUtf8("MainDialog"))
        MainDialog.resize(854, 680)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainDialog.sizePolicy().hasHeightForWidth())
        MainDialog.setSizePolicy(sizePolicy)
        MainDialog.setMinimumSize(QtCore.QSize(854, 510))
        MainDialog.setMaximumSize(QtCore.QSize(854, 680))
        MainDialog.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        MainDialog.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        #MainDialog.setSizeGripEnabled(False)
        #MainDialog.setModal(False)

        #self.ipInputBox = QtGui.QLineEdit(MainDialog)
        #self.ipInputBox.setGeometry(QtCore.QRect(490, 410, 111, 21))
        #self.ipInputBox.setObjectName(_fromUtf8("ipInputBox"))

        #self.joinButton = QtGui.QPushButton(MainDialog)
        #self.joinButton.setGeometry(QtCore.QRect(610, 410, 41, 21))
        #self.joinButton.setObjectName(_fromUtf8("joinButton"))

        self.ytWebView = QtWebKit.QWebView(MainDialog)
        self.ytWebView.setPage(WebPage())

        # small player w/ bar
        ##self.ytWebView.setGeometry(QtCore.QRect(10, 10, 640, 360))
        # reg player w/o bar
        ##self.ytWebView.setGeometry(QtCore.QRect(0, 0, 660, 370))
        # reg player w/ bar -- standard!
        #self.ytWebView.setGeometry(QtCore.QRect(0, 0, 660, 400))
        # bigger player w/ bar
        self.ytWebView.setGeometry(QtCore.QRect(0, 0, 854, 510))

        self.ytWebView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.ytWebView.setZoomFactor(1.0)
        self.ytWebView.setObjectName(_fromUtf8("ytWebView"))

        # http://srinikom.github.io/pyside-docs/PySide/QtGui/QListWidget.html
        self.ytQueue = QtGui.QListWidget(MainDialog)
        self.ytQueue.setGeometry(QtCore.QRect(10, 522, 370, 118))
        self.ytQueue.setFrameShadow(QtGui.QFrame.Plain)
        self.ytQueue.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ytQueue.setObjectName(_fromUtf8("ytQueue"))

        self.voteSkip = QtGui.QPushButton(MainDialog)
        self.voteSkip.setGeometry(QtCore.QRect(280, 650, 70, 20))
        self.voteSkip.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.voteSkip.setObjectName(_fromUtf8("voteSkip"))

        #self.addVideo = QtGui.QPushButton(MainDialog)
        #self.addVideo.setGeometry(QtCore.QRect(200, 540, 70, 20))
        #self.addVideo.setObjectName(_fromUtf8("addVideo"))

        self.voteSkipLabel = QtGui.QLabel(MainDialog)
        self.voteSkipLabel.setGeometry(QtCore.QRect(350, 650, 40, 20))
        self.voteSkipLabel.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.voteSkipLabel.setFrameShape(QtGui.QFrame.NoFrame)
        self.voteSkipLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.voteSkipLabel.setObjectName(_fromUtf8("voteSkipLabel"))

        self.videoLineURL = QtGui.QLineEdit(MainDialog)
        self.videoLineURL.setGeometry(QtCore.QRect(10, 650, 260, 20))
        self.videoLineURL.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.videoLineURL.setInputMask(_fromUtf8(""))
        self.videoLineURL.setText(_fromUtf8(""))
        self.videoLineURL.setObjectName(_fromUtf8("videoLineURL"))

        self.userList = QtGui.QListWidget(MainDialog)
        self.userList.setGeometry(QtCore.QRect(400, 522, 130, 148))
        self.userList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.userList.setObjectName(_fromUtf8("userList"))

        self.chatArea = QtGui.QTextBrowser(MainDialog)
        self.chatArea.setGeometry(QtCore.QRect(540, 522, 304, 128))
        self.chatArea.setFrameShape(QtGui.QFrame.StyledPanel)
        self.chatArea.setFrameShadow(QtGui.QFrame.Plain)
        self.chatArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.chatArea.setLineWidth(1)
        self.chatArea.setObjectName(_fromUtf8("chatArea"))

        self.chatBoxInput = QtGui.QLineEdit(MainDialog)
        self.chatBoxInput.setGeometry(QtCore.QRect(540, 650, 304, 20))
        self.chatBoxInput.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.chatBoxInput.setText(_fromUtf8(""))
        self.chatBoxInput.setObjectName(_fromUtf8("chatBoxInput"))

        #self.playlistLabel = QtGui.QLabel(MainDialog)
        #self.playlistLabel.setGeometry(QtCore.QRect(10, 405, 46, 16))
        #self.playlistLabel.setObjectName(_fromUtf8("playlistLabel"))

        self.line = QtGui.QFrame(MainDialog)
        self.line.setGeometry(QtCore.QRect(380, 522, 20, 148))
        self.line.setFrameShadow(QtGui.QFrame.Raised)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))

        self.retranslateUi(MainDialog)
        QtCore.QMetaObject.connectSlotsByName(MainDialog)
        MainDialog.setTabOrder(self.ytQueue, self.videoLineURL)
        MainDialog.setTabOrder(self.videoLineURL, self.voteSkip)
        #MainDialog.setTabOrder(self.addVideo, self.voteSkip)
        #MainDialog.setTabOrder(self.voteSkip, self.ipInputBox)
        MainDialog.setTabOrder(self.voteSkip, self.userList)
        #MainDialog.setTabOrder(self.ipInputBox, self.joinButton)
        #MainDialog.setTabOrder(self.joinButton, self.userList)
        MainDialog.setTabOrder(self.userList, self.chatArea)
        MainDialog.setTabOrder(self.chatArea, self.chatBoxInput)
        MainDialog.setTabOrder(self.chatBoxInput, self.ytWebView)

    def retranslateUi(self, MainDialog):
        MainDialog.setWindowTitle(_translate("MainDialog", "Cutie Sync", None))
        icon = QtGui.QIcon('res/img/heartnewbig.png')
        MainDialog.setWindowIcon(icon)
        #self.ipInputBox.setPlaceholderText(_translate("MainDialog", "Host IP", None))
        #self.joinButton.setText(_translate("MainDialog", "Join", None))
        self.voteSkip.setText(_translate("MainDialog", "Vote Skip", None))
        #self.addVideo.setText(_translate("MainDialog", "Add Video", None))
        self.voteSkipLabel.setText(_translate("MainDialog", "0/0", None))
        self.videoLineURL.setPlaceholderText(_translate("MainDialog", "Video URL", None))
        self.chatArea.setHtml(_translate("MainDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br />%s</p>\
            </body></html>" % "<span>...</span>", None))
        self.chatBoxInput.setPlaceholderText(_translate("MainDialog", "Enter message here", None))
        #self.playlistLabel.setText(_translate("MainDialog", "Playlist", None))

