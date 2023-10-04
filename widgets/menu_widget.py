from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import threading

class MenuWidget(QFrame):
    def __init__(self, parent = None):
        super(MenuWidget, self).__init__(parent)
        self.setFixedSize(80,400)
        self.setObjectName("menu")
        self.style_sheet = ""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignLeft)

        self.qLoad = QPushButton()
        self.qLoad.setFixedSize(50,50)
        self.qLoad.setIconSize(QSize(40,40))
        self.qLoad.setContextMenuPolicy(Qt.CustomContextMenu)
        self.qLoad.customContextMenuRequested.connect(self.manage_packs)
        self.qLoad.setToolTip("Load Stickers")

        self.browseButton = QPushButton()
        self.browseButton.setToolTip("Browse")
        self.browseButton.setFixedSize(50,50)
        self.browseButton.setIconSize(QSize(40,40))

        self.downloadButton = QPushButton()
        self.downloadButton.setToolTip("Downlaod Stickers")
        self.downloadButton.setFixedSize(50,50)
        self.downloadButton.setIconSize(QSize(40,40))


        dlayout.addWidget(self.qLoad)
        dlayout.addWidget(self.browseButton)
        dlayout.addWidget(self.downloadButton)

        self.setLayout(dlayout)

    def manage_packs(self):
        print(self.qLoad.menu().pos())
        global_pos = self.qLoad.mapToGlobal(self.qLoad.pos())
        print(global_pos)
        self.edit_menu.move(global_pos.x()-10, global_pos.y()-70)
        self.edit_menu.show()
        def wait():
            while self.edit_menu.isVisible():
                pass
        wait_thread = threading.Thread(target=wait)
        wait_thread.start()


    def set_menu(self,quick_load_menu, edit_menu):
        self.qLoad.menu()
        self.qLoad.setMenu(quick_load_menu)
        self.qLoad.menu()
        self.edit_menu = edit_menu
