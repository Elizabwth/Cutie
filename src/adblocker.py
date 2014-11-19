# referenced from http://stackoverflow.com/questions/1083170/how-would-you-adblock-using-python
# and https://code.google.com/p/simple-media-player/source/browse/trunk/MyPlayer/src/adblock.py?spec=svn15&r=15

from PyQt4.QtNetwork import QNetworkAccessManager
from PyQt4 import QtCore, QtGui, QtNetwork

class AdblockerNetworkManager(QNetworkAccessManager):
    def __init__(self):
        super(AdblockerNetworkManager, self).__init__()
    
    def createRequest(self, op, request, device = None ):
        path = str(request.url().path())
        lower_case = path.lower()
        lst = ["banner", "ads", r"||youtube-nocookie.com/gen_204?", r"youtube.com###watch-branded-actions", "imagemapurl"]
        block = False
        for l in lst:
            if lower_case.find(l) != -1:
                block = True
                break
        if block:
            print "Skipping "+request.url().path()
            return QNetworkAccessManager.createRequest(self, QNetworkAccessManager.GetOperation, QtNetwork.QNetworkRequest(QtCore.QUrl()))
        else:
            return QNetworkAccessManager.createRequest(self, op, request, device)