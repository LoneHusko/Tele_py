from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class AskPermWidget(QFrame):
    def __init__(self, parent=None):
        super(AskPermWidget, self).__init__(parent)
        self.setObjectName("menu")
        self.setFixedSize(400,200)

        self.setVisible(False)

        self.accepted = False
        self.denied = False

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)

        spacer = QSpacerItem(5, 30)

        button_layout = QHBoxLayout()
        self.deny_button = QPushButton("Deny")
        self.deny_button.setFixedHeight(30)
        self.accept_button = QPushButton("Allow")
        self.accept_button.setFixedHeight(30)
        button_layout.addWidget(self.deny_button)
        button_layout.addWidget(self.accept_button)

        self.deny_button.clicked.connect(self.deny)
        self.accept_button.clicked.connect(self.accept)

        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.v_layout.addWidget(self.message_label)
        self.v_layout.addItem(spacer)
        self.v_layout.addLayout(button_layout)
        self.v_layout.setAlignment(Qt.AlignVCenter)
    def accept(self):
        self.accepted = True
    def deny(self):
        self.denied = True