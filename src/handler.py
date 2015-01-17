from PyQt4 import QtCore
import Pyro4

class CallbackHandler(QtCore.QObject):
    def __init__(self, parent=None):
    	super(CallbackHandler, self).__init__(parent)

    user_connected_signal 		= QtCore.pyqtSignal(dict)
    user_disconnected_signal 	= QtCore.pyqtSignal(dict)
    video_added_signal			= QtCore.pyqtSignal(dict)
    video_removed_signal 		= QtCore.pyqtSignal(int)

    #state_data_requested_signal = QtCore.pyqtSignal()
    message_received_signal 	= QtCore.pyqtSignal(str, str)
    queue_sorted_signal 		= QtCore.pyqtSignal(int, int)
    state_data_changed_signal 	= QtCore.pyqtSignal()

    @Pyro4.callback
    def user_connected(self, user):
        print("user_connected signal")
        self.user_connected_signal.emit(user)

    @Pyro4.callback
    def user_disconnected(self, user):
        print("user_disconnected signal")
        self.user_disconnected_signal.emit(user)

    @Pyro4.callback
    def video_added(self, qi):
        print("video_added callback")
        print("video_added signal")
        self.video_added_signal.emit(qi)

    @Pyro4.callback
    def video_removed(self, index):
        print("video_removed signal")
        self.video_removed_signal.emit(index)

    @Pyro4.callback
    def message_received(self, name, message):
        print("message_received signal")
        self.message_received_signal.emit(name, message)

    @Pyro4.callback
    def queue_sorted(self, initial, dropped):
        self.queue_sorted_signal.emit(initial, dropped)

    @Pyro4.callback
    def state_data_changed(self):
        self.state_data_changed_signal.emit()