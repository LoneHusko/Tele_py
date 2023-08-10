from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class NotifyWidget(QFrame):
    def __init__(self, parent=None):
        super(NotifyWidget, self).__init__(parent)
        self.setObjectName("menu")
        self.setVisible(False)
        self.setFixedSize(400,200)

        self.message_label = QLabel()

        spacer = QSpacerItem(5, 50)

        self.close_button = QPushButton("Close")
        self.close_button.setFixedHeight(30)
        self.close_button.clicked.connect(lambda: self.setVisible(False))

        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.v_layout.addWidget(self.message_label)
        self.v_layout.addItem(spacer)
        self.v_layout.addWidget(self.close_button)
        self.v_layout.setAlignment(Qt.AlignVCenter)

