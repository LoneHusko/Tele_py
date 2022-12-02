import sys, os, shutil
from PySide2 import QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from os.path import isfile, join
from os import listdir
import win32clipboard as clp
from win10toast import ToastNotifier

"""
Uses PySide2, win32clipboard and win10toast modules.
Later versions may use Pillow.
"""




class Stickers(QWidget):

    def __init__(self, parent= None):
        super(Stickers, self).__init__()
        #Basic settings
        self.stickersLoaded = False
        self.path = ""
        self.settings = []
        self.onlyfiles = []
        try:
            with open("utils/lastpack", "r") as pack:
                self.path = pack.read()
                self.onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f))]
        except:
            pass
        self.setStyleSheet("""
            QToolTip {
                background-color: #182644;
                border: 1px solid #56acee;
                color: #999999;
            }
            QWidget {
                background-color: #182644;
                border: 1px solid white;
            }

            QPushButton {
                border: none;
                background-color: none;
                border-radius: 3px;
            }

            QPushButton:hover {
                background-color: #666666;
            }

            QPushButton:pressed {
                background-color: #111111;
            }
            QScrollArea{
                border: none;
            }
            QGridLayout{
                border: none;
            }
        """)
        self.setWindowTitle("Tele-py")
        self.resize(500, 500)
        self.setMaximumSize(500, 500)
        self.setMinimumSize(500, 500)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.setWindowIcon(QIcon("utils/icon.png"))


        #Container Widget
        self.widget = QWidget()
        #Layout of Container Widget
        self.layout = QGridLayout(self)


        self.widget.setLayout(self.layout)

        #Scroll Area Properties
        scroll = QScrollArea()
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.verticalScrollBar().setStyleSheet("""
                                                QScrollBar{
                                                    background: nonce; 
                                                    border: none
                                                }
                                                QScrollBar:vertical {
                                                    min-height: 240px;
                                                    width: 5px;
                                                }
                                            
                                                QScrollBar::groove {
                                                    background: none;
                                                    border-radius: 5px;
                                                }
                                            
                                                QScrollBar::handle::vertical {
                                                    background: #56acee;
                                                    border-radius: 5px;
                                                    border: none;
                                                }
                                                
                                                QScrollBar::handle::vertical::pressed {
                                                    background: #315E80;
                                                }
                                            
                                                QScrollBar::handle:vertical {
                                                    height: 3px;
                                                    border-radius: 5px;
                                                }
                                                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                                     background: #111A2E;
                                                     border-radius: 5px;
                                                 }""")
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.widget)
        scroll.setStyleSheet("border: none;")


        vLayout = QVBoxLayout(self)
        hLayout = QHBoxLayout(self)




        horizontalSpacer = QSpacerItem(440,30)
        hLayout.addItem(horizontalSpacer)

        loadStickers = QPushButton()
        size = QSize(30,30)
        loadStickers.setMaximumSize(30,30)
        loadStickers.setIcon(QIcon("utils/loadStickers.png"))
        loadStickers.setIconSize(size)
        loadStickers.setToolTip("Stickers")
        loadStickers.clicked.connect(lambda :self.selectStickers())
        hLayout.addWidget(loadStickers)

        settings = QPushButton()
        size = QSize(30,30)
        settings.setMaximumSize(30,30)
        settings.setIcon(QIcon("utils/settings.png"))
        settings.setToolTip("Settings")
        settings.setIconSize(size)
        settings.clicked.connect(lambda :self.settingOpen())
        # hLayout.addWidget(settings)
        print("Settings are disabled in the code!!!")

        # qrip = QLabel(self)
        # hLayout.addWidget(qrip)

        vLayout.addLayout(hLayout)
        closeBtn = QPushButton()
        size = QSize(30,30)
        closeBtn.setMaximumSize(30,30)
        closeBtn.setIcon(QIcon("utils/close.png"))
        closeBtn.setIconSize(size)
        closeBtn.setToolTip("Close")
        closeBtn.clicked.connect(lambda :self.closeWindow())
        hLayout.addWidget(closeBtn)

        # vLayout.addWidget(settings)

        # vLayout.addWidget(btn_new)
        vLayout.addWidget(scroll)
        self.setLayout(vLayout)

    def send_to_clipboard(self, clip_type, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()



    def preview(self):
        dlg = QDialog()
        dlg.setStyleSheet("""
                QToolTip {
                        background-color: #182644;
                        border: 1px solid #56acee;
                        color: #999999;
                }
                QWidget {
                    background-color: #182644;
                    border: 1px solid #999999;
                    border-radius: 5px;
                }
                QLabel {
                    border: none;
                    background-color: rgba(102, 102, 102, 0.25);
                    border-radius: 3px;
                    width: 50px;
                    height: 30px;
                    color: #999999;
                    padding: 5px;
                }
                QPushButton {
                    border: none;
                    background-color: rgba(102, 102, 102, 0.25);
                    border-radius: 3px;
                    width: 50px;
                    height: 30px;
                    color: #999999;
                }
    
                QPushButton:hover {
                    background-color: #666666;
                }
    
                QPushButton:pressed {
                    background-color: #111111;
                }
                QScrollArea{
                    border: none;
                }
                QGridLayout{
                    border: none;
                }
                """)
        dlg.setWindowTitle("Preview")
        QBtn = QDialogButtonBox.Ok
        dlg.buttonBox = QDialogButtonBox(QBtn)
        dlg.buttonBox.accepted.connect(dlg.accept)
        # dlg.buttonBox.rejected.connect(dlg.reject)

        button = QPushButton()
        icon = QIcon(self.stickers[QPushButton.sender(self)])
        button.setIcon(icon)
        button.setMinimumSize(350,350)
        button.setMaximumSize(350,350)
        button.setStyleSheet("""QPushButton {
                                    border: none;
                                    background-color: none;
                                }
                    
                                QPushButton:hover {
                                    background-color: #666666;
                                }
                    
                                QPushButton:pressed {
                                    background-color: #111111;
                                }
                                QCheckBox {
                                    border: none;
                                    color: #999999; 
                                }
                                """)
        size = QSize(350,350)
        button.setIconSize(size)
        self.stickers[button] = self.stickers[QPushButton.sender(self)]
        button.clicked.connect(self.stickerCopy)
        sticker_location = self.stickers[QPushButton.sender(self)]
        print(f"Preview opened for: {sticker_location}")
        original = rf'{sticker_location}'
        file_name = original.split("/")[-1]
        def copyToFav():
            try:
                target = r'utils/favourites/'+file_name
                shutil.copyfile(original, target)
                favButton.setText("Remove from favourites")
                favButton.clicked.connect(removeFav)
            except:
                pass
        def removeFromFav():
            if os.path.exists("utils/favourites/"+file_name):
                os.remove("utils/favourites/"+file_name)
                favButton.setText("Save to favourites")
                favButton.clicked.connect(copyToFav)
                # self.reloadStickers()





        temp_files = [f for f in listdir("utils/favourites/") if isfile(join("utils/favourites/", f))]
        saveFav = QPushButton("Save to favourites")
        saveFav.clicked.connect(copyToFav)
        removeFav = QPushButton("Remove from favourites")
        removeFav.clicked.connect(removeFromFav)

        browseButton = QPushButton("Browse stickers")
        browseButton.clicked.connect(self.setStickerPath)
        browseButton.setToolTip("Browse folders and load stickers from them")
        setButton = QPushButton("Load stickers")
        setButton.clicked.connect(self.checkStickers)
        setButton.setToolTip("Load the stickers to the interface")
        clearButton = QPushButton("Unload stickers")
        clearButton.clicked.connect(self.unloadStickers)
        clearButton.setToolTip("Unload the stickers from the interface")

        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        dlg.setWindowFlags(flags)

        dlayout = QVBoxLayout()

        dlayout.addWidget(button)
        hLayout = QHBoxLayout()
        dlayout.addLayout(hLayout)
        if os.path.exists("utils/favourites/"+file_name):
            favButton = QPushButton("Remove from favourites")
            favButton.clicked.connect(removeFromFav)
        else:
            favButton = QPushButton("Save to favourites")
            favButton.clicked.connect(copyToFav)
        hLayout.addWidget(favButton)
        # dlayout.addWidget(setButton)
        # dlayout.addWidget(clearButton)
        dlayout.addWidget(dlg.buttonBox)

        dlg.setLayout(dlayout)
        result = dlg.exec_()
    def stickerCopy(self):
        print(f"Button: {QPushButton.sender(self)}")

        print(f"Copied file: {self.stickers[QPushButton.sender(self)]}")
        file_path = self.stickers[QPushButton.sender(self)]

        clp.OpenClipboard()
        clp.EmptyClipboard()

        # This works for Discord, but not for Paint.NET:
        wide_path = os.path.abspath(file_path).encode('utf-16-le') + b'\0'
        clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), wide_path)
        clp.CloseClipboard()

        toast = ToastNotifier()
        toast.show_toast(
            "Tele-py",
            "Sticker copied to the clipboard.",
            duration = 3,
            icon_path = "utils/icon.ico",
            threaded = True,
        )

    def closeWindow(self):
        quit(0)







    def settingOpen(self):

        #Build dialog window
        dlg = QDialog()
        dlg.setStyleSheet("""
            QWidget {
                background-color: #182644;
                border: 1px solid white;
            }

            QPushButton {
                border: none;
                background-color: rgba(102, 102, 102, 0.25);
                border-radius: 3px;
                width: 50px;
                height: 20px;
            }

            QPushButton:hover {
                background-color: #666666;
            }

            QPushButton:pressed {
                background-color: #111111;
            }
            QScrollArea{
                border: none;
            }
            QGridLayout{
                border: none;
            }
            """)
        dlg.setWindowTitle("Settings")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        dlg.buttonBox = QDialogButtonBox(QBtn)
        dlg.buttonBox.accepted.connect(dlg.accept)
        dlg.buttonBox.rejected.connect(dlg.reject)
        browseButton = QPushButton("Browse stickers")
        browseButton.clicked.connect(self.setStickerPath)

        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        dlg.setWindowFlags(flags)

        dlayout = QVBoxLayout()

        dlayout.addWidget(browseButton)
        dlayout.addWidget(dlg.buttonBox)

        dlg.setLayout(dlayout)
        dlg.exec_()

    def checkStickers(self):
        if len(self.path) and not self.stickersLoaded:
            self.loadStickers()
        else:
            if self.stickersLoaded:
                self.unloadStickers()
                self.loadStickers()
            # self.dropError("No stickers are loaded!")

    def loadFavourites(self):
        self.path = "utils/favourites/"
        self.onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f))]
        self.unloadStickers()
        self.loadStickers()

    def reloadStickers(self):
        self.unloadStickers()
        self.loadStickers()

    def selectStickers(self):

        dlg = QDialog()
        dlg.setStyleSheet("""
                QToolTip {
                        background-color: #182644;
                        border: 1px solid #56acee;
                        color: #999999;
                }
                QWidget {
                    background-color: #182644;
                    border: 1px solid #999999;
                    border-radius: 5px;
                }
                QLabel {
                    border: none;
                    background-color: rgba(102, 102, 102, 0.25);
                    border-radius: 3px;
                    width: 50px;
                    height: 30px;
                    color: #999999;
                    padding: 5px;
                }
                QPushButton {
                    border: none;
                    background-color: rgba(102, 102, 102, 0.25);
                    border-radius: 3px;
                    width: 50px;
                    height: 30px;
                    color: #999999;
                }
    
                QPushButton:hover {
                    background-color: #666666;
                }
    
                QPushButton:pressed {
                    background-color: #111111;
                }
                QScrollArea{
                    border: none;
                }
                QGridLayout{
                    border: none;
                }
                """)
        dlg.setWindowTitle("Select Stickerpack")
        QBtn = QDialogButtonBox.Ok
        dlg.buttonBox = QDialogButtonBox(QBtn)
        dlg.buttonBox.accepted.connect(dlg.accept)
        dlg.buttonBox.rejected.connect(dlg.reject)
        dlg.setMinimumSize(275,139)
        browseButton = QPushButton("Browse stickers")
        browseButton.clicked.connect(self.setStickerPath)
        browseButton.setToolTip("Browse folders and load stickers from them")
        setButton = QPushButton("Load stickers")
        setButton.clicked.connect(self.checkStickers)
        setButton.setToolTip("Load the stickers to the interface")
        self.favButton = QPushButton("Load Favourites")
        self.favButton.clicked.connect(self.loadFavourites)
        self.favButton.setToolTip("Load stickers that you previously saved to your favourites")
        reloadButton = QPushButton("Reload stickers")
        reloadButton.setToolTip("Reloads the stickers on the intarface")
        reloadButton.clicked.connect(self.reloadStickers)
        clearButton = QPushButton("Unload stickers")
        clearButton.clicked.connect(self.unloadStickers)
        clearButton.setToolTip("Unload the stickers from the interface")

        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        dlg.setWindowFlags(flags)

        dlg.setMinimumSize(400, 232)

        dlayout = QVBoxLayout()
        if len(self.path):
            self.message = QLabel(f"Path: {self.path}")
            dlayout.addWidget(self.message)

        dlayout.addWidget(browseButton)
        dlayout.addWidget(setButton)
        dlayout.addWidget(self.favButton)
        # dlayout.addWidget(reloadButton)
        dlayout.addWidget(clearButton)
        dlayout.addWidget(dlg.buttonBox)

        dlg.setLayout(dlayout)
        result = dlg.exec_()

    def addStickerPath(self, path):
        self.path = path



    def setStickerPath(self):
        self.path = QFileDialog.getExistingDirectory(self, "Select Sticker Folder")
        if len(self.path):
            if len([f for f in listdir(self.path) if isfile(join(self.path, f))]) <= 300:
                try:
                    self.message.setText(f"Path: {self.path}")
                except:
                    pass
                self.onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f))]

            else:
                self.dropError("Too many stickers! The limit is 300.")

    def loadStickers(self):
        if not self.stickersLoaded and len(self.path):
            if self.path[-1] != "/":
                self.path += "/"
            br = False
            onlyfiles = []
            for i in self.onlyfiles:
                if i.split(".")[-1].lower() == "jpg" or i.split(".")[-1].lower() == "png" or i.split(".")[-1].lower() == "webp":
                    onlyfiles.append(i)
            file = 0
            button_list = []
            self.stickers = {}
            for i in range(len(onlyfiles)):
                if len(onlyfiles) > 300:
                    self.dropError("Too many stickers! The limit is 300.")
                    onlyfiles = []
                    break
                if br:
                    break
                for x in range(4):

                    button = QPushButton()
                    try:
                        icon = self.path+onlyfiles[file]
                        button.setIcon(QIcon(icon))
                        button.setMinimumSize(100,100)
                        button.setMaximumSize(100,100)
                        size = QSize(100,100)
                        self.stickers[button] = self.path+onlyfiles[file]
                        button.setIconSize(size)
                        button_list.append(button)
                        self.layout.addWidget(button, i, x)
                        button.clicked.connect(self.stickerCopy)
                        button.setContextMenuPolicy(Qt.CustomContextMenu)
                        button.customContextMenuRequested.connect(self.preview)
                        file += 1

                    except:
                        self.stickersLoaded = True
                        br = True
                        break

            print(f"Loaded {file} files out of {len(self.onlyfiles)}")
            try:
                with open("utils/lastpack", "w") as pack:
                    pack.write(self.path)
            except:
                pass
            self.stickersLoaded = True





    def unloadStickers(self):
        children = []
        for i in range(self.layout.count()):
            child = self.layout.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()
        self.stickersLoaded = False

    def dropError(self, message):
        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setWindowTitle("Error")
        msgBox.setText(message)
        msgBox.setStyleSheet("""
            QMessageBox::Watning::Icon {
                border: none;
            }
            QWidget {
                background-color: #182644;
                border: none;
            }
            QLabel{
                color: white
            }

            QPushButton {
                border: none;
                background-color: rgba(102, 102, 102, 0.25);
                border-radius: 3px;
                width: 50px;
                height: 20px;
                color: #999999;
            }

            QPushButton:hover {
                background-color: #666666;
            }

            QPushButton:pressed {
                background-color: #111111;
            }
            QGridLayout{
                border: none;
            }
        """)

        msgBox.show()

    def dropInfo(self, message):
        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Error")
        msgBox.setText(message)
        msgBox.setStyleSheet("""
            QMessageBox::Watning::Icon {
                border: none;
            }
            QWidget {
                background-color: #182644;
                border: none;
            }
            QLabel{
                color: white
            }

            QPushButton {
                border: none;
                background-color: rgba(102, 102, 102, 0.25);
                border-radius: 3px;
                width: 50px;
                height: 20px;
                color: #999999;
            }

            QPushButton:hover {
                background-color: #666666;
            }

            QPushButton:pressed {
                background-color: #111111;
            }
            QGridLayout{
                border: none;
            }
        """)

        msgBox.show()

    # action #1
    def mousePressEvent(self, event):
        self.oldPosition = event.globalPos()

    # action #2
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPosition)
        if event.localPos().y() <= 32:
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()

if __name__ == '__main__':
    if not os.path.exists("utils/favourites"):
        os.mkdir("utils/favourites")
    if not os.path.exists("utils/lastpack"):
        with open("utils/lastpack", "a") as _:
            pass
    app = QApplication(sys.argv)
    stickerWindow = Stickers()
    stickerWindow.show()
    app.exec_()
