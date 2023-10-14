from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class ConfirmUpdateWidget(QFrame):
    def __init__(self,release_notes_widget: QWidget , parent=None):
        super(ConfirmUpdateWidget, self).__init__(parent)
        self.setObjectName("menu")
        self.setFixedSize(482, 446)

        self.setVisible(False)


        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.close)

        self.release_notes_widget = release_notes_widget

        self.message_label = QLabel()
        self.message_label.setWordWrap(True)

        spacer = QSpacerItem(5, 30)

        button_layout = QHBoxLayout()
        self.deny_button = QPushButton("Cancel")
        self.deny_button.setObjectName("left_btn")
        self.deny_button.setFixedHeight(30)
        self.deny_button.clicked.connect(self.close)
        self.accept_button = QPushButton("Update")
        self.accept_button.setToolTip("Please read the release notes first")
        self.accept_button.setEnabled(False)
        self.accept_button.setObjectName("right_btn")
        self.accept_button.setFixedHeight(30)
        button_layout.addWidget(self.deny_button)
        button_layout.addWidget(self.accept_button)

        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.v_layout.addWidget(self.release_notes_widget)
        # self.v_layout.addWidget(self.message_label)
        self.v_layout.addItem(spacer)
        self.v_layout.addLayout(button_layout)
        self.v_layout.setAlignment(Qt.AlignVCenter)

    def close(self):
        self.setVisible(False)
