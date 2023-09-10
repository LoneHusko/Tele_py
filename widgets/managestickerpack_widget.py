from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class ManageStickerpackWidget(QFrame):
    def __init__(self, parent = None):
        super(ManageStickerpackWidget, self).__init__(parent)
        self.resize(400,400)
        self.setObjectName("menu")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)

        self.label = QLabel()
        self.label.setFixedHeight(30)
        self.label.setFixedWidth(300)

        self.link_label = QLabel()
        self.link_label.setFixedHeight(30)

        self.name = QLineEdit()
        self.name.setPlaceholderText("Name")
        self.name.setFixedWidth(300)
        self.rename_button = QPushButton("Rename")
        self.rename_button.setFixedHeight(30)
        self.update_button = QPushButton("Update pack")
        self.update_button.setFixedHeight(30)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setFixedHeight(30)
        self.delete_button.setObjectName("highrisk")

        spacer = QSpacerItem(5, 30)

        dlayout.addWidget(self.label)
        dlayout.addWidget(self.link_label)
        dlayout.addWidget(self.name)
        dlayout.addWidget(self.rename_button)
        dlayout.addWidget(self.update_button)
        dlayout.addItem(spacer)
        dlayout.addWidget(self.delete_button)

        self.setLayout(dlayout)
