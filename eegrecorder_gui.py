import sys
import threading
import eegrecorder
from PySide2 import QtCore, QtWidgets
import kbcontroller
import datetime as dt

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

        self.chkWriteEEG = QtWidgets.QCheckBox()
        self.chkWriteEEG.setText("Raw EEG")
        self.chkWriteEEG.setChecked(True)
        self.chkWriteBands = QtWidgets.QCheckBox()
        self.chkWriteBands.setText("Standard bands")
        self.chkWriteQuality = QtWidgets.QCheckBox()
        self.chkWriteQuality.setText("Quality elements")
        writeLayout = QtWidgets.QVBoxLayout()
        writeLayout.addWidget(self.chkWriteEEG)
        writeLayout.addWidget(self.chkWriteBands)
        writeLayout.addWidget(self.chkWriteQuality)
        self.writeBox = QtWidgets.QGroupBox()
        self.writeBox.setTitle("Write to DB")
        self.writeBox.setLayout(writeLayout)

        self.lblStatus = QtWidgets.QLabel()
        statusLayout = QtWidgets.QHBoxLayout()
        statusLayout.addWidget(self.lblStatus)
        statusBox = QtWidgets.QGroupBox()
        statusBox.setTitle("Status")
        statusBox.setLayout(statusLayout)

        statusTimer = QtCore.QTimer(self)
        statusTimer.timeout.connect(self.updateStatus)
        statusTimer.start(1000)

        self.btnStartStop = QtWidgets.QPushButton()
        #self.btnStartStop.clicked.connect()
        self.connect(self.btnStartStop, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("onStartStop()"))
        self.btnNextTrack = QtWidgets.QPushButton("Next track")
        self.connect(self.btnNextTrack, QtCore.SIGNAL("clicked()"), self, QtCore.SLOT("onNextTrackPressed()"))
        btnLayout = QtWidgets.QVBoxLayout()
        btnLayout.addWidget(self.btnStartStop)
        btnLayout.addWidget(self.btnNextTrack)
        btnGroup = QtWidgets.QGroupBox()
        btnGroup.setTitle("Session control")
        btnGroup.setLayout(btnLayout)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(-2, 2)
        self.slider.setValue(0)

        self.lcd = QtWidgets.QLCDNumber(2)
        self.slider.connect(self.slider, QtCore.SIGNAL("valueChanged(int)"), self, QtCore.SLOT("onEnjoyValueChanged()"))

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.subjectBox, 0, 0)
        layout.addWidget(self.writeBox, 0, 1)
        layout.addWidget(statusBox, 0, 2)
        layout.addWidget(btnGroup, 0, 3)
        layout.addWidget(self.slider, 1, 0, 1, 3)
        layout.addWidget(self.lcd, 2, 0, 1, 3)
        self.setLayout(layout)

        self.session_running = False

        self.eeg_handler = eegrecorder.EEGDataRecorder(self)
        self.eeg_thread = threading.Thread(target=self.eeg_handler.run, daemon=True)

        self.updateControls()

    def updateControls(self):
        if self.session_running:
            self.subjectBox.setDisabled(True)
            self.writeBox.setDisabled(True)
            self.slider.setDisabled(False)
            self.btnNextTrack.setDisabled(False)
            self.btnStartStop.setText("End session")
        else:
           self.subjectBox.setDisabled(False)
           self.writeBox.setDisabled(False)
           self.slider.setDisabled(True)
           self.btnNextTrack.setDisabled(True)
           self.btnStartStop.setText("Start session")

    def updateStatus(self):
        eeg_online = False
        if hasattr(self.eeg_handler, "_last_eeg_ts"):
            diff = dt.datetime.now() - self.eeg_handler._last_eeg_ts
            eeg_online = diff.seconds < 1
        elements_online = False
        if hasattr(self.eeg_handler, "_last_elements_ts"):
            diff = dt.datetime.now() - self.eeg_handler._last_elements_ts
            elements_online = diff.seconds < 1
        self.lblStatus.setText("Session running: {}\nRaw EEG online: {}\nElements online: {}".format(self.session_running, eeg_online, elements_online))

    def onStartStop(self):
        if self.session_running:
            kbcontroller.stop()
            self.session_running = False
            self.eeg_handler.stop()
            self.eeg_thread.join()
            del self.eeg_thread
            del self.eeg_handler
            self.btnStartStop.setDisabled(True)
        else:
            subject_data = { "name" : self.inName.text() }
            self.eeg_handler.set_subject_data(subject_data)
            if self.chkWriteBands.isChecked():
                self.eeg_handler.record_bands()
            if self.chkWriteEEG.isChecked():
                self.eeg_handler.record_eeg()
            if self.chkWriteQuality.isChecked():
                self.eeg_handler.record_quality()
            self.eeg_thread.start()
            kbcontroller.playPause()
            self.session_running = True
        self.updateControls()

    def onNextTrackPressed(self):
        kbcontroller.nextTrack()
        self.eeg_handler.trigger_eeg_event("next_track_pressed")
        self.slider.setValue(0)

    def onEnjoyValueChanged(self):
        self.lcd.display(self.enjoyValue())
        self.eeg_handler.trigger_eeg_event("enjoy_changed", self.enjoyValue())

    def enjoyValue(self):
        return self.slider.value()

    def getVariables(self):
        return { "enjoy" : self.enjoyValue() }

app = QtWidgets.QApplication(sys.argv)
widget = MyWidget()
widget.show()
sys.exit(app.exec_())
