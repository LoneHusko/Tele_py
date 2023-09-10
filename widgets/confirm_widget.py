from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class ConfirmWidget(QFrame):
    def __init__(self, parent=None):
        super(ConfirmWidget, self).__init__(parent)
        self.setObjectName("menu")
        # self.setFixedSize(400,200)
        self.setFixedWidth(400)

        self.setVisible(False)


        self.message_label = QLabel()
        self.message_label.setWordWrap(True)

        spacer = QSpacerItem(5, 500)

        button_layout = QHBoxLayout()
        self.deny_button = QPushButton("No")
        self.deny_button.setObjectName("left_btn")
        self.deny_button.setFixedHeight(30)
        self.accept_button = QPushButton("Yes")
        self.accept_button.setObjectName("right_btn")
        self.accept_button.setFixedHeight(30)
        button_layout.addWidget(self.deny_button)
        button_layout.addWidget(self.accept_button)

        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.v_layout.addWidget(self.message_label)
        self.v_layout.addItem(spacer)
        self.v_layout.addLayout(button_layout)
        self.v_layout.setAlignment(Qt.AlignVCenter)
