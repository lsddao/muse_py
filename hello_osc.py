import sys
import threading
import eegrecorder

from PySide2 import QtCore, QtWidgets

class MyWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        lblName = QtWidgets.QLabel()
        lblName.setText("Full name")
        self.inName = QtWidgets.QLineEdit()
        subjectLayout = QtWidgets.QGridLayout()
        subjectLayout.addWidget(lblName, 0, 0)
        subjectLayout.addWidget(self.inName, 0, 1)
        self.subjectBox = QtWidgets.QGroupBox()
        self.subjectBox.setTitle("Subject data")
        self.subjectBox.setLayout(subjectLayout)

        lblStatus = QtWidgets.QLabel()
        statusLayout = QtWidgets.QHBoxLayout()
        statusLayout.addWidget(lblStatus)
        statusBox = QtWidgets.QGroupBox()
        statusBox.setTitle("Status")
        statusBox.setLayout(statusLayout)

        self.btnStartStop = QtWidgets.QPushButton()
        self.connect(self.btnStartStop, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("onStartStop()"))

        self.btnNextTrack = QtWidgets.QPushButton("Next track")
        btnLayout = QtWidgets.QVBoxLayout()
        btnLayout.addWidget(self.btnStartStop)
        btnLayout.addWidget(self.btnNextTrack)
        btnGroup = QtWidgets.QGroupBox()
        btnGroup.setTitle("Session control")
        btnGroup.setLayout(btnLayout)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(-5, 5)
        self.slider.setValue(0)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.subjectBox, 0, 0)
        layout.addWidget(statusBox, 0, 1)
        layout.addWidget(btnGroup, 0, 2)
        layout.addWidget(self.slider, 1, 0, 1, 3)
        self.setLayout(layout)

        self.session_running = False

        self.eeg_handler = eegrecorder.EEGDataRecorder(subject_name=self.inName.text())
        self.eeg_thread = threading.Thread(target=self.eeg_handler.run)

        self.updateControls()

    def updateControls(self):
        if self.session_running:
            self.subjectBox.setDisabled(True)
            self.slider.setDisabled(False)
            self.btnNextTrack.setDisabled(False)
            self.btnStartStop.setText("End session")
        else:
           self.subjectBox.setDisabled(False)
           self.slider.setDisabled(True)
           self.btnNextTrack.setDisabled(True)
           self.btnStartStop.setText("Start session")

    def onStartStop(self):
        if self.session_running:
            self.session_running = False
            self.eeg_handler.stop()
            self.eeg_thread.join()
        else:
            self.eeg_thread.start()
            self.session_running = True
        self.updateControls()

app = QtWidgets.QApplication(sys.argv)
widget = MyWidget()
widget.show()
sys.exit(app.exec_())
