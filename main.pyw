import sys, os, shutil, threading, winsound, time

from PySide2 import QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from os.path import isfile, join
from os import listdir
import win32clipboard as clp
from win10toast import ToastNotifier
from configparser import ConfigParser
from utils import downloader
from io import BytesIO
from PIL import Image

"""
Uses PySide2, pywin32, winsound and win10toast modules.
"""




class Stickers(QWidget):

    def __init__(self, parent= None):
        super(Stickers, self).__init__()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('utils/icon.png'))
        self.tray_icon.show()

        # Create a custom context menu for the tray icon
        self.tray_menu = QMenu(self)
        self.tray_menu.addAction("Show Window", self.windowAppear)
        self.tray_menu.addAction("Open settings", self.settingOpen)
        self.tray_menu.addAction("Load favourites", self.loadFavourites)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction("Quit", QApplication.quit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.trayIconHandle)

        #Basic settings
        self.visible = True
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
        try:
            with open("utils/style_main.css", "r") as style:
                self.setStyleSheet(str(style.read()))
                self.tray_menu.setStyleSheet(str(style.read()))
        except:
            pass
        self.setWindowTitle("Tele-py")
        self.resize(500, 500)
        self.setMaximumSize(500, 500)
        self.setMinimumSize(500, 500)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.setWindowIcon(QIcon("utils/icon.png"))
        self.setWindowModality(Qt.WindowModal)

        #Container Widget
        self.widget = QWidget()
        #Layout of Container Widget
        self.layout = QGridLayout(self)


        self.widget.setLayout(self.layout)

        #Scroll Area Properties
        scroll = QScrollArea()
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
        size = QSize(25,25)
        settings.setMaximumSize(30,30)
        settings.setIcon(QIcon("utils/settings.png"))
        settings.setToolTip("Settings")
        settings.setIconSize(size)
        settings.clicked.connect(lambda :self.settingOpen())
        hLayout.addWidget(settings)

        vLayout.addLayout(hLayout)
        closeBtn = QPushButton()
        size = QSize(30,30)
        closeBtn.setMaximumSize(30,30)
        closeBtn.setIcon(QIcon("utils/close.png"))
        closeBtn.setIconSize(size)
        closeBtn.setToolTip("Close")
        closeBtn.clicked.connect(lambda :self.closeWindow())
        hLayout.addWidget(closeBtn)
        vLayout.addWidget(scroll)
        self.setLayout(vLayout)

    def windowAppear(self):
        if not self.visible:
            flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
            self.setWindowFlags(flags)
            self.setVisible(True)
            self.visible = True

    def trayIconHandle(self, reason):
        if reason == QSystemTrayIcon.Trigger and not self.visible:
            flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
            self.setWindowFlags(flags)
            self.setVisible(True)
            self.visible = True
        elif reason == QSystemTrayIcon.Context:
            self.tray_menu.popup(QCursor.pos())

    def preview(self):
        dlg = QDialog()
        try:
            with open("utils/style_preview.css", "r") as style:
                dlg.setStyleSheet(str(style.read()))
        except:
            pass
        dlg.setWindowTitle("Preview")
        QBtn = QDialogButtonBox.Ok
        dlg.buttonBox = QDialogButtonBox(QBtn)
        dlg.buttonBox.accepted.connect(dlg.accept)

        button = QPushButton()
        icon = QIcon(self.stickers[QPushButton.sender(self)])
        button.setIcon(icon)
        button.setMinimumSize(350,350)
        button.setMaximumSize(350,350)
        try:
            with open("utils/style_main.css", "r") as style:
                button.setStyleSheet(str(style.read()))
        except:
            pass
        size = QSize(350,350)
        button.setIconSize(size)
        self.stickers[button] = self.stickers[QPushButton.sender(self)]
        button.clicked.connect(self.stickerCopy)
        sticker_location = self.stickers[QPushButton.sender(self)]
        original = rf'{sticker_location}'
        file_name = original.split("/")[-1]
        def copyToFav():
            try:
                target = r'utils/favourites/'+file_name
                shutil.copyfile(original, target)
                favButton.setText("Remove from favourites")
                favButton.clicked.connect(removeFromFav)
            except:
                pass
        def removeFromFav():
            if os.path.exists("utils/favourites/"+file_name):
                os.remove("utils/favourites/"+file_name)
                favButton.setText("Save to favourites")
                favButton.clicked.connect(copyToFav)

        saveFav = QPushButton("Save to favourites")
        saveFav.clicked.connect(copyToFav)
        removeFav = QPushButton("Remove from favourites")
        removeFav.clicked.connect(removeFromFav)


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
        dlayout.addWidget(dlg.buttonBox)

        dlg.setLayout(dlayout)
        if os.path.exists(sticker_location):
            print(f"Preview opened for: {sticker_location}")
            dlg.exec_()
        else:
            self.dropError("File not found!")
    def stickerCopy(self):
        def send_to_clipboard(clip_type, data):
            clp.OpenClipboard()
            clp.EmptyClipboard()
            clp.SetClipboardData(clip_type, data)
            clp.CloseClipboard()
        file_path = self.stickers[QPushButton.sender(self)]
        if os.path.exists(file_path):

            clp.OpenClipboard()
            clp.EmptyClipboard()
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            if settings["copy_method"] == "dc":
                # This works for Discord, but not for Paint.NET:
                wide_path = os.path.abspath(file_path).encode('utf-16-le') + b'\0'
                clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), wide_path)
                clp.CloseClipboard()
            elif settings["copy_method"] == "gimp":
                filepath = file_path
                image = Image.open(filepath)

                output = BytesIO()
                image.convert("RGBA").save(output, "BMP")
                data = output.getvalue()[14:]
                output.close()

                send_to_clipboard(clp.CF_DIB, data)


            print(f"Button: {QPushButton.sender(self)}")

            print(f"Copied file: {self.stickers[QPushButton.sender(self)]}")

            toast = ToastNotifier()
            toast.show_toast(
                "Tele-py",
                "Sticker copied to the clipboard.",
                duration = 3,
                icon_path = "utils/icon.ico",
                threaded = True,
            )
        else:
            self.dropError("File not found!")

    def closeWindow(self):
        config_object = ConfigParser()
        config_object.read("utils/config.ini")

        #Get the password
        hides = config_object["SETTINGS"]
        if not int(hides["hides"]) == 1:
            QApplication.quit()
        else:
            self.setVisible(False)
            self.visible = False

    def settingOpen(self):
        dlg = QDialog()
        # dlg.setAttribute(Qt.WA_TranslucentBackground)
        dlg.setWindowModality(Qt.NonModal)
        def applySyle():
            try:
                with open("utils/style_settings.css", "r") as style:
                    dlg.setStyleSheet(str(style.read()))
            except:
                pass
        def dcCopy():
            if not dcComp.objectName() == "activeBtn":
                config_object = ConfigParser()
                config_object.read("utils/config.ini")
                settings = config_object["SETTINGS"]
                settings["copy_method"] = "dc"

                with open('utils/config.ini', 'w') as conf:
                    config_object.write(conf)
                dcComp.setObjectName("activeBtn")
                gimpComp.setObjectName("")
                applySyle()
        def gimpCopy():
            if not gimpComp.objectName() == "activeBtn":
                config_object = ConfigParser()
                config_object.read("utils/config.ini")
                settings = config_object["SETTINGS"]
                settings["copy_method"] = "gimp"

                with open('utils/config.ini', 'w') as conf:
                    config_object.write(conf)
                gimpComp.setObjectName("activeBtn")
                dcComp.setObjectName("")
                applySyle()
        def closesWindow():
            hideWindowBtn.setObjectName("")
            closeWindowBtn.setObjectName("activeBtn")
            #Read config.ini file
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]

            #Update the value
            settings["hides"] = "0"

            #Write changes back to file
            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)
            applySyle()
        def hidesWindow():
            hideWindowBtn.setObjectName("activeBtn")
            closeWindowBtn.setObjectName("")
            #Read config.ini file
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]

            #Update the value
            settings["hides"] = "1"

            #Write changes back to file
            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)
            applySyle()
        def save():
            if maxFileIn.text():
                #Read config.ini file
                config_object = ConfigParser()
                config_object.read("utils/config.ini")
                settings = config_object["SETTINGS"]

                #Update the value
                settings["max_stickers_loadable"] = maxFileIn.text()

                #Write changes back to file
                with open('utils/config.ini', 'w') as conf:
                    config_object.write(conf)
            if columnsIn.text() and int(columnsIn.text()) != 0:
                #Read config.ini file
                config_object = ConfigParser()
                config_object.read("utils/config.ini")
                settings = config_object["SETTINGS"]

                #Update the value
                settings["columns"] = columnsIn.text()

                #Write changes back to file
                with open('utils/config.ini', 'w') as conf:
                    config_object.write(conf)
            dlg.setVisible(False)
        def addStyle():
            styles = ["utils/style_download.css", "utils/style_main.css", "utils/style_menu.css", "utils/style_preview.css", "utils/style_quickLoad.css", "utils/style_settings.css"]
            missing = []
            for i in styles:
                if not os.path.exists(i):
                    missing.append(i)
                elif i == "utils/style_main.css" and i not in missing:
                    with open("utils/style_main.css", "r") as style:
                        self.setStyleSheet(str(style.read()))
                elif i == "utils/style_settings.css" and i not in missing:
                    with open("utils/style_settings.css", "r") as style:
                        dlg.setStyleSheet(str(style.read()))
            if len(missing):
                self.dropError(", ".join(missing)+" was not found!")


        #Build dialog window
        applySyle()
        dlg.setWindowTitle("Settings")
        QBtn = QDialogButtonBox.Ok
        dlg.buttonBox = QDialogButtonBox(QBtn)
        dlg.buttonBox.accepted.connect(save)
        applyStyleBtn = QPushButton("Read stylesheet")
        applyStyleBtn.clicked.connect(addStyle)

        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        settings = config_object["SETTINGS"]

        columnsGroup = QGroupBox("Columns")
        columnsLayout = QHBoxLayout()
        columnsGroup.setLayout(columnsLayout)
        columnsIn = QLineEdit()
        columnsIn.setValidator(QIntValidator())
        columnsLayout.addWidget(columnsIn)
        columnsIn.returnPressed.connect(save)


        maxfileGroup = QGroupBox("Maximum readable stickers")
        maxLayout = QHBoxLayout()
        maxfileGroup.setLayout(maxLayout)
        maxFileIn = QLineEdit()
        maxFileIn.setFixedHeight(30)
        maxLayout.addWidget(maxFileIn)
        maxFileIn.setPlaceholderText("Recommended is 120")
        maxFileIn.setValidator(QIntValidator())
        maxFileIn.returnPressed.connect(save)

        hidesGroup = QGroupBox("Close button action")
        hidesLayout = QHBoxLayout()
        hidesGroup.setLayout(hidesLayout)
        hideWindowBtn = QPushButton("Hide window")
        hideWindowBtn.setFixedHeight(30)
        hideWindowBtn.clicked.connect(hidesWindow)
        closeWindowBtn = QPushButton("Close application")
        closeWindowBtn.setFixedHeight(30)
        closeWindowBtn.clicked.connect(closesWindow)
        hidesLayout.addWidget(hideWindowBtn)
        hidesLayout.addWidget(closeWindowBtn)

        if settings["hides"] == "1":
            hideWindowBtn.setObjectName("activeBtn")
        elif settings["hides"] == "0":
            closeWindowBtn.setObjectName("activeBtn")

        dcComp = QPushButton("Discord")
        dcComp.clicked.connect(dcCopy)
        dcComp.setFixedWidth(129)
        gimpComp = QPushButton("Gimp")
        gimpComp.clicked.connect(gimpCopy)
        gimpComp.setFixedWidth(129)

        if settings["copy_method"] == "dc":
            dcComp.setObjectName("activeBtn")
        elif settings["copy_method"] == "gimp":
            gimpComp.setObjectName("activeBtn")
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        dlg.setWindowFlags(flags)

        dlayout = QVBoxLayout()
        dgrid = QGridLayout()

        groupComp = QGroupBox("Compatibility mode")
        compLayout = QGridLayout()
        compLayout.addWidget(dcComp, 0, 0)
        compLayout.addWidget(gimpComp, 0, 1)
        groupComp.setLayout(compLayout)


        dlayout.addWidget(columnsGroup)
        dlayout.addWidget(maxfileGroup)
        dlayout.addWidget(groupComp)
        dlayout.addWidget(hidesGroup)
        dlayout.addWidget(applyStyleBtn)
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

    def loadFavourites(self):
        self.path = "utils/favourites/"
        try:
            self.message.setText(f"Path: {self.path}")
        except:
            pass
        self.onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f))]
        self.unloadStickers()
        self.loadStickers()


    def downloadSticker(self):
        self.stickerDlg.accept()


        def download():
            def thread():
                failed = False
                with open("utils/bottoken", "w") as token:
                    token.write(botToken.text())
                dlg.buttonBox.accepted.disconnect(dlg.accept)
                try:
                    asd = downloader.StickerDownloader(botToken.text())

                    name = stickerURL.text()
                    if not os.path.exists(f"downloads/{name}") and name != "":
                        if name != "":
                            name = (name.split('/')[-1])


                            print('=' * 60)
                            _ = asd.get_sticker_set(name)

                            print('-' * 60)
                            _ = asd.download_sticker_set(_)
                            dlg.buttonBox.accepted.connect(dlg.accept)
                            if customName.text():
                                with open(f"downloads/{name}/customname", "wt") as f:
                                    f.write(customName.text())
                            message.setStyleSheet("color: #009f3b; background-color: #00260E;")
                            message.setText("Download completed!")
                            winsound.PlaySound("C:\Windows\Media\Windows Notify Messaging.wav", winsound.SND_FILENAME)
                        else:
                            dlg.buttonBox.accepted.connect(dlg.accept)
                            message.setStyleSheet("color:red; background-color: #540612;")
                            message.setText("Invalid URL!")
                            winsound.PlaySound("C:\Windows\Media\Windows Notify Email.wav", winsound.SND_FILENAME)
                    elif name == "":
                        dlg.buttonBox.accepted.connect(dlg.accept)
                        message.setStyleSheet("color:red; background-color: #540612;")
                        message.setText("Invalid URL!")
                        winsound.PlaySound("C:\Windows\Media\Windows Notify Email.wav", winsound.SND_FILENAME)

                    elif os.path.exists(f"downloads/{name}"):
                        dlg.buttonBox.accepted.connect(dlg.accept)
                        message.setStyleSheet("color:red; background-color: #540612;")
                        message.setText("Stickers already downloaded!")
                        winsound.PlaySound("C:\Windows\Media\Windows Notify Email.wav", winsound.SND_FILENAME)

                except:
                    dlg.buttonBox.accepted.connect(dlg.accept)
                    message.setStyleSheet("color:red; background-color: #540612;")
                    message.setText("Download failed! Please check the token and the URL!")
                    winsound.PlaySound("C:\Windows\Media\Windows Notify Email.wav", winsound.SND_FILENAME)


            x = threading.Thread(target=thread)
            try:
                with open("utils/style_download.css", "r") as style:
                    message.setStyleSheet(str(style))
            except:
                pass
            message.setText("Downloading, please wait...")
            x.start()

        dlg = QDialog()
        try:
            with open("utils/style_download.css", "r") as style:
                dlg.setStyleSheet(str(style.read()))
        except:
            pass
        dlg.setWindowTitle("Download Stickers")
        QBtn = QDialogButtonBox.Ok
        dlg.buttonBox = QDialogButtonBox(QBtn)
        dlg.buttonBox.accepted.connect(dlg.accept)
        message = QLabel()
        message.setFixedHeight(30)
        message.setAlignment(Qt.AlignCenter)
        botToken = QLineEdit()
        botToken.setPlaceholderText("Token")
        try:
            with open("utils/bottoken", "r") as token:
                _ = token.read()
                botToken.setText(_)
        except:
            pass

        customName = QLineEdit()
        customName.setPlaceholderText("Custom name for the pack (leave blank for default)")

        stickerURL = QLineEdit()
        stickerURL.setPlaceholderText("Sticker URL")

        downloadButton = QPushButton("Download")
        downloadButton.clicked.connect(download)

        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        dlg.setWindowFlags(flags)

        dlg.setMinimumSize(400, 232)

        dlayout = QVBoxLayout()
        dlayout.addWidget(message)
        dlayout.addWidget(stickerURL)
        dlayout.addWidget(customName)
        dlayout.addWidget(botToken)
        dlayout.addWidget(downloadButton)
        dlayout.addWidget(dlg.buttonBox)
        dlg.setLayout(dlayout)
        dlg.exec_()

    def quickLoadPrepare(self):
        self.path = self.loadPath[QPushButton.sender(self)]
        self.message.setText(f"Path: {self.path}")
        try:
            with open("utils/lastpack", "w") as pack:
                pack.write(self.path)
        except:
            pass
        self.unloadStickers()
        self.loadStickers()
    def quickLoad(self):
        self.loadPath = {}
        menu = QMenu()
        try:
            with open("utils/style_quickLoad.css", "r") as style:
                menu.setStyleSheet(str(style.read()))
        except:
            pass
        if os.path.exists("downloads"):
            folders = [ name for name in os.listdir("downloads/") if os.path.isdir(os.path.join("downloads/", name)) ]
            if len(folders):

                for i in folders:
                    action = QAction(i)
                    size = QSize(10,10)
                    icon = [f for f in listdir(f"downloads/{i}/") if isfile(join(f"downloads/{i}/", f)) and f != "customname"][0]
                    if os.path.exists(f"downloads/{i}/customname"):
                        with open(f"downloads/{i}/customname") as f:
                            name = f.read()
                    else:
                        name = i
                    action = QAction(name)
                    action.setIcon(QIcon(fr"downloads/{i}/{icon}"))
                    action.triggered.connect(self.quickLoadPrepare)
                    action.triggered.connect(menu.close)
                    action.triggered.connect(self.stickerDlg.accept)
                    self.loadPath[action] = f"downloads/{i}/"
                    menu.addAction(action)
        else:
            menu.addAction("No downloads found").setEnabled(False)
        return menu


    def selectStickers(self):

        self.stickerDlg = QDialog()
        vertical = QVBoxLayout()
        try:
            with open("utils/style_menu.css", "r") as style:
                self.stickerDlg.setStyleSheet(str(style.read()))
        except:
            pass
        self.stickerDlg.setWindowTitle("Select Stickerpack")
        QBtn = QDialogButtonBox.Ok
        self.stickerDlg.buttonBox = QDialogButtonBox(QBtn)
        self.stickerDlg.buttonBox.accepted.connect(self.stickerDlg.accept)
        self.stickerDlg.setMinimumSize(275,139)
        qLoad = QPushButton("Quick Load")
        dropdown = self.quickLoad()
        qLoad.setMenu(dropdown)
        qLoad.setToolTip("Load downloaded stickers quickly")
        browseButton = QPushButton("Browse Stickers")
        browseButton.clicked.connect(self.setStickerPath)
        browseButton.setToolTip("Browse folders and load stickers from them")
        setButton = QPushButton("Load Stickers")
        setButton.clicked.connect(self.checkStickers)
        setButton.clicked.connect(self.stickerDlg.accept)
        setButton.setToolTip("Load the stickers to the interface")
        self.favButton = QPushButton("Load Favourites")
        self.favButton.clicked.connect(self.loadFavourites)
        self.favButton.clicked.connect(self.stickerDlg.accept)
        self.favButton.setToolTip("Load stickers that you previously saved to your favourites")
        clearButton = QPushButton("Unload Stickers")
        clearButton.clicked.connect(self.unloadStickers)
        clearButton.setToolTip("Unload the stickers from the interface")
        downloadButton = QPushButton("Download Stickers")
        downloadButton.setToolTip("Download stickers from Telegram")
        downloadButton.clicked.connect(self.downloadSticker)

        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.stickerDlg.setWindowFlags(flags)

        self.stickerDlg.setMinimumSize(400, 232)

        dlayout = QVBoxLayout()
        self.message = QLabel()
        if len(self.path):
            self.message.setText(f"Path: {self.path}")
        else:
            self.message.setText("Path:")
        dlayout.addWidget(self.message)
        self.message.setFixedHeight(30)

        dlayout.addWidget(qLoad)
        dlayout.addWidget(browseButton)
        dlayout.addWidget(setButton)
        dlayout.addWidget(self.favButton)
        dlayout.addWidget(clearButton)
        dlayout.addWidget(downloadButton)
        dlayout.addWidget(self.stickerDlg.buttonBox)

        self.stickerDlg.setLayout(dlayout)
        self.stickerDlg.exec_()

    def addStickerPath(self, path):
        self.path = path



    def setStickerPath(self):
        self.path = QFileDialog.getExistingDirectory(self, "Select Sticker Folder")
        if len(self.path):
            conf = ConfigParser()
            conf.read("utils/conf.ini")
            max = conf["SETTINGS"]
            if len([f for f in listdir(self.path) if isfile(join(self.path, f))]) <= int(max["max_stickers_loadable"]):
                try:
                    self.message.setText(f"Path: {self.path}")
                except:
                    pass
                self.onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f))]

            else:
                self.dropError(f"Too many stickers! The limit is {max['max_stickers_loadable']}.")

    def loadStickers(self):
        if os.path.exists(self.path):
            self.onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f))]
            if not self.stickersLoaded and len(self.path):
                #Read config.ini file
                config_object = ConfigParser()
                config_object.read("utils/config.ini")

                #Get the password
                settings = config_object["SETTINGS"]
                columns = int(settings["columns"])
                width_height = 400/columns
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
                    conf = ConfigParser()
                    conf.read("utils/config.ini")
                    max = conf["SETTINGS"]
                    if len(onlyfiles) > int(max["max_stickers_loadable"]):
                        self.dropError(f"Too many stickers! The limit is {max['max_stickers_loadable']}.")
                        onlyfiles = []
                        break
                    if br:
                        break
                    for x in range(columns):

                        button = QPushButton()
                        try:
                            icon = self.path+onlyfiles[file]
                            button.setIcon(QIcon(icon))
                            button.setMinimumSize(width_height,width_height)
                            button.setMaximumSize(width_height,width_height)
                            size = QSize(width_height,width_height)
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
        else:
            self.dropError("The given path does not exist!")





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
        def playsound():
            winsound.PlaySound("C:\Windows\Media\Windows Notify Calendar.wav", winsound.SND_FILENAME)
        x = threading.Thread(target=playsound)
        x.start()
        msgBox = QMessageBox(self)
        # Create a QPixmap object with the desired image file
        icon_path = "utils/warning.png"
        icon = QPixmap(icon_path)

        # Resize the QPixmap object
        icon = icon.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set the icon for the QMessageBox
        msgBox.setIconPixmap(icon)

        msgBox.setWindowTitle("Error")
        msgBox.setText(message)

        msgBox.setStyleSheet("""
            QLabel{
                border: none;
                background-color: rgba(102, 102, 102, 0.25);
                border-radius: 3px;
                height: 30px !important;
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
        """)
        msgBox.show()



    def dropInfo(self, message):
        def playsound():
            winsound.PlaySound("C:\Windows\Media\Windows Message Nudge.wav", winsound.SND_FILENAME)
        x = threading.Thread(target=playsound)
        x.start()
        msgBox = QMessageBox(self)
        # Create a QPixmap object with the desired image file
        icon_path = "utils/info.png"
        icon = QPixmap(icon_path)

        # Resize the QPixmap object
        icon = icon.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Set the icon for the QMessageBox
        msgBox.setIconPixmap(icon)
        msgBox.setWindowTitle("Information")
        msgBox.setText(message)
        msgBox.setStyleSheet("""
            QLabel{
                border: none;
                background-color: rgba(102, 102, 102, 0.25);
                border-radius: 3px;
                height: 30px !important;
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
    if not os.path.exists("utils/bottoken"):
        with open("utils/bottoken", "a") as _:
            pass
    app = QApplication(sys.argv)
    stickerWindow = Stickers()
    stickerWindow.show()
    app.exec_()
