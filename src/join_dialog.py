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

class Ui_JoinDialog(QtGui.QWidget):#class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(160, 100)
        Dialog.setMinimumSize(QtCore.QSize(160, 100))
        Dialog.setMaximumSize(QtCore.QSize(160, 100))
        Dialog.setFocusPolicy(QtCore.Qt.StrongFocus)
        Dialog.setModal(False)

        self.okCancle = QtGui.QDialogButtonBox(Dialog)
        self.okCancle.setGeometry(QtCore.QRect(10, 70, 141, 21))
        self.okCancle.setOrientation(QtCore.Qt.Horizontal)
        self.okCancle.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.okCancle.setObjectName(_fromUtf8("okCancle"))

        self.nameInput = QtGui.QLineEdit(Dialog)
        self.nameInput.setGeometry(QtCore.QRect(10, 40, 141, 21))
        self.nameInput.setText(_fromUtf8(""))
        self.nameInput.setMaxLength(50)
        self.nameInput.setObjectName(_fromUtf8("nameInput"))

        self.addressInput = QtGui.QLineEdit(Dialog)
        self.addressInput.setGeometry(QtCore.QRect(10, 10, 81, 21))
        self.addressInput.setText(_fromUtf8(""))
        self.addressInput.setObjectName(_fromUtf8("addressInput"))

        self.portInput = QtGui.QLineEdit(Dialog)
        self.portInput.setGeometry(QtCore.QRect(100, 10, 51, 21))
        self.portInput.setText(_fromUtf8(""))
        self.portInput.setObjectName(_fromUtf8("portInput"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.okCancle, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.okCancle, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.addressInput, self.portInput)
        Dialog.setTabOrder(self.portInput, self.nameInput)
        Dialog.setTabOrder(self.nameInput, self.okCancle)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Connect", None))
        Dialog.setWindowIcon(QtGui.QIcon('../res/img/heartnewbig.png'))
        self.nameInput.setPlaceholderText(_translate("Dialog", "User Name", None))
        self.addressInput.setPlaceholderText(_translate("Dialog", "Address", None))
        self.portInput.setPlaceholderText(_translate("Dialog", "Port", None))