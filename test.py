import sys
from PySide2 import QtCore, QtGui, QtWidgets

class Example(QtWidgets.QWidget):

    def __init__(self,):
        super(Example, self).__init__()
        
        self.initUI()

    def initUI(self):

        # formatting
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle("Example")

        # widgets
        self.controlGroup = QtWidgets.QGroupBox()
        self.controlGroup.setTitle("Group")
        self.controlGroup.setCheckable(True)
        self.controlGroup.setChecked(True)

        # groupbox layout
        self.groupLayout = QtWidgets.QGridLayout(self.controlGroup)
        self.btn = QtWidgets.QPushButton("FOO")
        self.groupLayout.addWidget(self.btn)
        self.controlGroup.setFixedHeight(self.controlGroup.sizeHint().height())

        # signals
        self.controlGroup.toggled.connect(lambda: self.toggleGroup(self.controlGroup))
        
        # layout
        self.mainLayout = QtWidgets.QGridLayout(self)
        self.mainLayout.addWidget(self.controlGroup)
        self.show()    

    def toggleGroup(self, ctrl):
        state = ctrl.isChecked()
        if state:
            ctrl.setFixedHeight(ctrl.sizeHint().height())
        else:
            ctrl.setFixedHeight(30)
            
app = QtWidgets.QApplication(sys.argv)
widget = Example()
widget.show()
sys.exit(app.exec_())