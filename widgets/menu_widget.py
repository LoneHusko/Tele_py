from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import threading

class MenuWidget(QFrame):
    def __init__(self, parent = None):
        super(MenuWidget, self).__init__(parent)
        self.resize(400,175)
        self.setObjectName("menu")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignLeft)

        self.qLoad = QPushButton("Load Stickers")
        self.qLoad.setContextMenuPolicy(Qt.CustomContextMenu)
        self.qLoad.customContextMenuRequested.connect(self.manage_packs)

        self.qLoad.menu()  # For some reason it only sets the menu if this line is here.
        self.qLoad.setToolTip("Load downloaded stickers quickly")

        self.browseButton = QPushButton("Browse Stickers")
        # self.browseButton.clicked.connect(self.set_sticker_path)
        self.browseButton.setToolTip("Browse folders and load stickers from them")

        self.setButton = QPushButton("Load Stickers")
        # self.setButton.clicked.connect(self.check_stickers)
        # self.setButton.clicked.connect(close)
        self.setButton.setToolTip("Load the stickers to the interface")

        self.favButton = QPushButton("Load Favourites")
        # self.favButton.clicked.connect(self.load_favourites)
        # self.favButton.clicked.connect(close)
        self.favButton.setToolTip("Load stickers that you previously saved to your favourites")

        self.clearButton = QPushButton("Unload Stickers")
        # self.clearButton.clicked.connect(self.unload_stickers)
        self.clearButton.setToolTip("Unload the stickers from the interface")

        self.editButton = QPushButton("Manage stickerpacks")

        self.editButton.menu()
        self.editButton.setToolTip("Manage downloaded stickerpacks")

        self.downloadButton = QPushButton("Download Stickers")
        self.downloadButton.setToolTip("Download stickers from Telegram")
        # self.downloadButton.clicked.connect(self.download_stickers)

        self.qLoad.setFixedWidth(150)
        self.qLoad.setFixedHeight(30)

        self.browseButton.setFixedWidth(150)
        self.browseButton.setFixedHeight(30)

        # self.setButton.setFixedWidth(300)
        # self.setButton.setFixedHeight(30)

        # self.favButton.setFixedWidth(300)
        # self.favButton.setFixedHeight(30)

        # self.clearButton.setFixedWidth(300)
        # self.clearButton.setFixedHeight(30)

        # self.editButton.setFixedWidth(300)
        # self.editButton.setFixedHeight(30)
        # self.editButton.menu()

        self.downloadButton.setFixedWidth(150)
        self.downloadButton.setFixedHeight(30)

        dlayout.addWidget(self.qLoad)
        # dlayout.addWidget(self.editButton)
        dlayout.addWidget(self.browseButton)
        # dlayout.addWidget(self.setButton)
        # dlayout.addWidget(self.favButton)
        # dlayout.addWidget(self.clearButton)
        dlayout.addWidget(self.downloadButton)

        self.setLayout(dlayout)

    def manage_packs(self):
        print(self.qLoad.menu().pos())
        self.edit_menu.move(1050, 499)
        self.edit_menu.show()
        self.qLoad.setText("Manage stickerpacks")
        def wait():
            while self.edit_menu.isVisible():
                pass
            self.qLoad.setText("Load Stickers")
        wait_thread = threading.Thread(target=wait)
        wait_thread.start()


    def set_menu(self,quick_load_menu, edit_menu):
        self.qLoad.menu()
        self.qLoad.setMenu(quick_load_menu)
        self.qLoad.menu()
        self.edit_menu = edit_menu
