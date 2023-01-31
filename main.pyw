import sys, os, shutil, threading, winsound, time

from PySide2 import QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from os.path import isfile, join
from os import listdir
import win32clipboard as clp
from configparser import ConfigParser
from utils import downloader
from io import BytesIO
from PIL import Image

"""
Uses PySide2, pywin32, winsound and modules.
"""




class Stickers(QMainWindow):

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
        self.setAttribute(Qt.WA_TranslucentBackground)
        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        settings = config_object["SETTINGS"]
        self.styleLocation = "stylesheet/"+settings["stylesheet"]
        self.visible = True
        self.stickersLoaded = False
        self.path = ""
        self.settings = []
        try:
            with open("utils/lastpack", "r") as pack:
                self.path = pack.read()
        except:
            pass
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
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
        self.centralWidget = QWidget()
        self.centralWidget.setObjectName("central_widget")
        self.setCentralWidget(self.centralWidget)
        self.widget = QWidget()
        #Layout of Container Widget
        self.layout = QGridLayout(self)


        self.widget.setLayout(self.layout)

        #Scroll Area Properties
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.scroll.setStyleSheet("border: none;")


        self.vLayout = QVBoxLayout(self)
        hLayout = QHBoxLayout(self)




        self.message = QLabel()
        self.message.setFixedHeight(30)
        self.message.setFixedWidth(370)
        if self.path == "utils/favourites/":
            self.animateMessage("Favourites", None, False)
        else:
            self.animateMessage(self.path, "Path: ", False)
        hLayout.addWidget(self.message)

        verticalSpacer = QSpacerItem(500, 0)
        hLayout.addItem(verticalSpacer)

        self.loadStickersBtn = QPushButton()
        size = QSize(30,30)
        self.loadStickersBtn.setFixedSize(30,30)
        self.loadStickersBtn.setIcon(QIcon(f"utils/{self.styleLocation}/loadStickers.png"))
        self.loadStickersBtn.setIconSize(size)
        self.loadStickersBtn.setToolTip("Menu")
        self.loadStickersBtn.clicked.connect(lambda :self.selectStickers())
        self.loadStickersBtn.setObjectName("no_bg_btn")
        hLayout.addWidget(self.loadStickersBtn)

        self.settings = QPushButton()
        size = QSize(25,25)
        self.settings.setFixedSize(30,30)
        self.settings.setIcon(QIcon(f"utils/{self.styleLocation}/settings.png"))
        self.settings.setToolTip("Settings")
        self.settings.setIconSize(size)
        self.settings.clicked.connect(lambda :self.settingOpen())
        self.settings.setObjectName("no_bg_btn")
        hLayout.addWidget(self.settings)

        self.backBtn = QPushButton()
        size = QSize(30, 30)
        self.backBtn.setFixedSize(30, 30)
        self.backBtn.setIcon(QIcon(f"utils/{self.styleLocation}/back.png"))
        self.backBtn.setIconSize(size)
        self.backBtn.setToolTip("Back")
        self.backBtn.setObjectName("no_bg_btn")
        self.backBtn.setVisible(False)
        hLayout.addWidget(self.backBtn)

        self.saveBtn = QPushButton()
        size = QSize(30, 30)
        self.saveBtn.setFixedSize(30, 30)
        self.saveBtn.setIcon(QIcon(f"utils/{self.styleLocation}/save.png"))
        self.saveBtn.setIconSize(size)
        self.saveBtn.setToolTip("Save")
        self.saveBtn.setObjectName("no_bg_btn")
        self.saveBtn.setVisible(False)
        hLayout.addWidget(self.saveBtn)

        self.vLayout.addLayout(hLayout)
        self.closeBtn = QPushButton()
        size = QSize(30,30)
        self.closeBtn.setFixedSize(30,30)
        self.closeBtn.setIcon(QIcon(f"utils/{self.styleLocation}/close.png"))
        self.closeBtn.setIconSize(size)
        self.closeBtn.setToolTip("Close")
        self.closeBtn.clicked.connect(lambda :self.closeWindow())
        self.closeBtn.setObjectName("no_bg_btn")
        hLayout.addWidget(self.closeBtn)
        self.vLayout.addWidget(self.scroll)
        self.centralWidget.setLayout(self.vLayout)

        version = QLabel("v1.4pre.0", parent=self)
        version.setObjectName("version")
        version.move(5, 460)
        version.setAttribute(Qt.WA_TransparentForMouseEvents)
        version.show()
    def notify(self, text = "Test message", isError = False, timeout = 1):
        notification = QLabel(text, parent=self)
        notification.setAttribute(Qt.WA_TransparentForMouseEvents)
        notification.setFixedHeight(30)
        notification.setFixedWidth(300)
        notification.setAlignment(Qt.AlignCenter)
        notification.setObjectName("notification")
        notification.move(100, 500)
        notification.show()
        def playsound():
            time.sleep(0.05)
            winsound.PlaySound("utils/notify.wav", winsound.SND_ASYNC)
        def thread():
            for i in range(40):
                notification.move(100, 500-i+1)
                time.sleep(0.01)
            time.sleep(timeout)
            for i in range(40):
                notification.move(100, 460+i+1)
                time.sleep(0.01)
            notification.hide()
        y = threading.Thread(target=playsound)
        y.start()
        x = threading.Thread(target=thread)
        x.start()

    def animateMessage(self, text, unanimated, isError):
        if isError:
            self.message.setObjectName("error")
        else:
            self.message.setObjectName("")
        with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
            self.message.setStyleSheet(str(style.read()))
            styleSheet = style
        def thread():
            if unanimated == None:
                prefix = ""
            else:
                prefix = unanimated
            templist = []
            self.message.setText(prefix)
            for i in list(text):
                templist.append(i)
                self.message.setText(prefix+"".join(templist))
                time.sleep(0.03)
        x = threading.Thread(target=thread)
        x.start()
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
        def close():
            self.loadStickersBtn.setVisible(True)
            self.settings.setVisible(True)
            self.closeBtn.clicked.connect(self.closeWindow)
            self.scroll.setVisible(True)
            self.widget.setVisible(True)
            self.Blur.setBlurRadius(0)
            self.scroll.setGraphicsEffect(self.Blur)
            widget.hide()
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)
        widget = QWidget(parent=self)
        blur_effect = QGraphicsBlurEffect(blurRadius=5)
        self.widget.setGraphicsEffect(blur_effect)
        widget.setObjectName("preview")
        # self.vLayout.addWidget(widget)
        widget.setLayout(dlayout)
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(close)
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                dlg.setStyleSheet(str(style.read()))
        except:
            pass
        QBtn = QDialogButtonBox.Ok

        button = QPushButton()
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(close)
        button.setObjectName("no_bg_btn")
        icon = QIcon(self.stickers[QPushButton.sender(self)])
        button.setIcon(icon)
        button.setMinimumSize(350,350)
        button.setMaximumSize(350,350)
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
                self.notify(text="Saved to favourites!")
                favButton.clicked.connect(removeFromFav)
            except:
                pass
        def removeFromFav():
            if os.path.exists("utils/favourites/"+file_name):
                os.remove("utils/favourites/"+file_name)
                favButton.setText("Save to favourites")
                self.notify(text="Removed from favourites!")
                favButton.clicked.connect(copyToFav)


        dlayout.addWidget(button)
        hLayout = QHBoxLayout()
        dlayout.addLayout(hLayout)
        if os.path.exists("utils/favourites/"+file_name):
            favButton = QPushButton("Remove from favourites")
            favButton.clicked.connect(removeFromFav)
        else:
            favButton = QPushButton("Save to favourites")
            favButton.clicked.connect(copyToFav)
        favButton.setFixedHeight(30)
        hLayout.addWidget(favButton)

        self.vLayout.addLayout(dlayout)
        if os.path.exists(sticker_location):
            print(f"Preview opened for: {sticker_location}")
            self.loadStickersBtn.setVisible(False)
            self.settings.setVisible(False)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(close)
            widget.setFixedSize(self.scroll.size())
            widget.move(self.scroll.pos())
            self.Blur = QGraphicsBlurEffect()
            self.Blur.setBlurRadius(10)
            self.scroll.setGraphicsEffect(self.Blur)
            # self.widget.setVisible(False)
            # self.scroll.setVisible(False)
            widget.show()
        else:
            self.dropError(f"File not found! ({sticker_location})")
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
                # clipboard = app.clipboard()
                #
                # image = QImage(file_path)
                # pixmap = QPixmap.fromImage(image)
                # clipboard.setPixmap(pixmap)


                # file = open(file_path, 'rb')
                # clp.SetClipboardData(clp.RegisterClipboardFormat('image/png'), file.read())
                # clp.CloseClipboard()

                image = Image.open(file_path)

                output = BytesIO()
                image.convert("RGBA").save(output, "BMP")
                data = output.getvalue()[14:]
                output.close()

                send_to_clipboard(clp.CF_DIB, data)


            print(f"Button: {QPushButton.sender(self)}")

            print(f"Copied file: {self.stickers[QPushButton.sender(self)]}")

            self.notify("Sticker copied!")
        else:
            self.dropError(f"File not found! ({file_path})")

    def closeWindow(self):
        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        hides = config_object["SETTINGS"]
        if not int(hides["hides"]) == 1:
            QApplication.quit()
        else:
            self.setVisible(False)
            self.visible = False
    def changeStyle(self):
        self.location = self.stylesheets[QPushButton.sender(self)]

        with open(f"utils/stylesheet/{self.location}/customname", "r") as f:
            self.settingsMessage.setText(f"Press 'Apply stylesheet' to apply theme '{f.read()}'")

    def settingOpen(self):
        def close():
            dlg.setVisible(False)
            self.saveBtn.setVisible(False)
            self.scroll.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.settings.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.closeWindow)
        dlg = QWidget()
        dlg.setContextMenuPolicy(Qt.CustomContextMenu)
        dlg.customContextMenuRequested.connect(close)
        dlayout = QVBoxLayout()
        dlg.setObjectName("menu")
        dlg.setLayout(dlayout)
        dlayout.setAlignment(Qt.AlignCenter)
        def applySyle():
            try:
                with open(f"utils/{self.styleLocation}/style_settings.css", "r") as style:
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
            close()
        def addStyle():
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            settings["stylesheet"] = self.location

            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)
            self.styleLocation = "stylesheet/"+self.location
            try:
                self.loadStickersBtn.setIcon(QIcon(f"utils/{self.styleLocation}/loadStickers.png"))
                self.closeBtn.setIcon(QIcon(f"utils/{self.styleLocation}/close.png"))
                self.settings.setIcon(QIcon(f"utils/{self.styleLocation}/settings.png"))
            except:
                pass

            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                self.setStyleSheet(str(style.read()))
                self.tray_menu.setStyleSheet(str(style.read()))
                self.message.setStyleSheet(str(style.read()))
                dlg.setStyleSheet(str(style.read()))
            close()

        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        settings = config_object["SETTINGS"]
        #Build dialog window
        applySyle()
        applyStyleBtn = QPushButton("Apply stylesheet")
        applyStyleBtn.setFixedWidth(300)
        applyStyleBtn.setFixedHeight(30)
        applyStyleBtn.clicked.connect(addStyle)
        styleListBtn = QPushButton("Select stylesheet")
        menu = QMenu()
        menu.setObjectName("style_menu")
        elements = []
        self.stylesheets = {}
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                menu.setStyleSheet(str(style.read()))
        except:
            pass
        if os.path.exists("utils/stylesheet/"):
            folders = [ name for name in os.listdir("utils/stylesheet/") if os.path.isdir(os.path.join("utils/stylesheet/", name)) ]
            if len(folders):
                for i in folders:
                    active = False
                    if settings["stylesheet"] == i:
                        active = True
                    try:
                        with open(f"utils/stylesheet/{i}/customname") as f:
                            if active:
                                name = f.read()+" (Active)"
                            else:
                                name = f.read()
                    except:
                        if active:
                            name = i+" (Active)"
                        else:
                            name = i
                    action = QAction(name)
                    self.stylesheets[action] = i
                    action.triggered.connect(self.changeStyle)
                    elements.append(action)
                for i in elements:
                    menu.addAction(i)
        else:
            menu.addAction("No stylesheets found").setEnabled(False)


        styleListBtn.setMenu(menu)
        styleListBtn.menu()
        styleListBtn.setFixedWidth(300)
        styleListBtn.setFixedHeight(30)
        self.settingsMessage = QLabel("Settings")
        self.settingsMessage.setFixedHeight(30)

        columnsGroup = QGroupBox("Columns")
        columnsGroup.setFixedWidth(300)
        columnsLayout = QHBoxLayout()
        columnsGroup.setLayout(columnsLayout)
        columnsIn = QLineEdit()
        columnsIn.setValidator(QIntValidator())
        columnsLayout.addWidget(columnsIn)
        columnsIn.returnPressed.connect(save)


        maxfileGroup = QGroupBox("Maximum readable stickers")
        maxfileGroup.setFixedWidth(300)
        maxLayout = QHBoxLayout()
        maxfileGroup.setLayout(maxLayout)
        maxFileIn = QLineEdit()
        maxLayout.addWidget(maxFileIn)
        maxFileIn.setPlaceholderText("Recommended is 120")
        maxFileIn.setValidator(QIntValidator())
        maxFileIn.returnPressed.connect(save)

        hidesGroup = QGroupBox("Close button action")
        hidesGroup.setFixedWidth(300)
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
        dcComp.setFixedHeight(30)
        gimpComp = QPushButton("Gimp")
        gimpComp.clicked.connect(gimpCopy)
        gimpComp.setFixedWidth(129)
        gimpComp.setFixedHeight(30)

        if settings["copy_method"] == "dc":
            dcComp.setObjectName("activeBtn")
        elif settings["copy_method"] == "gimp":
            gimpComp.setObjectName("activeBtn")
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        dlg.setWindowFlags(flags)


        dgrid = QGridLayout()

        groupComp = QGroupBox("Compatibility mode")
        groupComp.setFixedWidth(300)
        compLayout = QGridLayout()
        compLayout.addWidget(dcComp, 0, 0)
        compLayout.addWidget(gimpComp, 0, 1)
        groupComp.setLayout(compLayout)

        self.settingsMessage.setFixedWidth(300)
        dlayout.addWidget(self.settingsMessage)
        dlayout.addWidget(columnsGroup)
        dlayout.addWidget(maxfileGroup)
        dlayout.addWidget(groupComp)
        dlayout.addWidget(hidesGroup)
        dlayout.addWidget(styleListBtn)
        dlayout.addWidget(applyStyleBtn)

        self.vLayout.addWidget(dlg)

        dlg.setVisible(True)
        self.saveBtn.setVisible(True)
        try:
            self.saveBtn.clicked.disconnect()
        except:
            pass
        self.saveBtn.clicked.connect(save)
        self.scroll.setVisible(False)
        self.loadStickersBtn.setVisible(False)
        self.settings.setVisible(False)
        self.closeBtn.clicked.disconnect()
        self.closeBtn.clicked.connect(close)

    def checkStickers(self):
        if len(self.path) and not self.stickersLoaded:
            self.loadStickers()
        else:
            if self.stickersLoaded:
                self.unloadStickers()
                self.loadStickers()

    def loadFavourites(self):
        self.path = "utils/favourites/"
        self.unloadStickers()
        self.loadStickers()


    def downloadSticker(self):
        self.stickerDlg.setVisible(False)
        self.backBtn.setVisible(True)
        def close():
            dlg.setVisible(False)
            self.backBtn.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.scroll.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.closeWindow)
        def back():
            dlg.setVisible(False)
            self.backBtn.setVisible(False)
            self.selectStickers()

        def download():
            def thread():
                failed = False
                with open("utils/bottoken", "w") as token:
                    token.write(botToken.text())
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
                            if customName.text():
                                with open(f"downloads/{name}/customname", "wt") as f:
                                    f.write(customName.text())
                            message.setObjectName("success")
                            message.setStyleSheet(styleSheet)
                            message.setText("Download completed!")
                            winsound.PlaySound("utils/success.wav", winsound.SND_FILENAME)
                        else:
                            message.setObjectName("error")
                            message.setStyleSheet(styleSheet)
                            message.setText("Invalid URL!")
                            winsound.PlaySound("utils/error.wav", winsound.SND_FILENAME)
                    elif name == "":
                        message.setObjectName("error")
                        message.setStyleSheet(styleSheet)
                        message.setText("Invalid URL!")
                        winsound.PlaySound("utils/error.wav", winsound.SND_FILENAME)

                    elif os.path.exists(f"downloads/{name}"):
                        message.setObjectName("error")
                        message.setStyleSheet(styleSheet)
                        message.setText("Stickers already downloaded!")
                        winsound.PlaySound("utils/error.wav", winsound.SND_FILENAME)

                except:
                    message.setObjectName("error")
                    message.setStyleSheet(styleSheet)
                    message.setText("Download failed! Please check the token and the URL!")
                    winsound.PlaySound("utils/error.wav", winsound.SND_FILENAME)


            x = threading.Thread(target=thread)
            message.setObjectName("")
            message.setStyleSheet(styleSheet)
            message.setText("Downloading, please wait...")

            x.start()

        dlg = QWidget()
        dlg.setContextMenuPolicy(Qt.CustomContextMenu)
        dlg.customContextMenuRequested.connect(back)
        dlg.setObjectName("menu")
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)
        self.vLayout.addWidget(dlg)
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                dlg.setStyleSheet(str(style.read()))
                styleSheet = str(style.read())
        except:
            pass

        message = QLabel()
        message.setFixedHeight(30)
        message.setFixedWidth(300)
        message.setAlignment(Qt.AlignCenter)
        botToken = QLineEdit()
        botToken.setFixedWidth(300)
        botToken.setPlaceholderText("Token")
        try:
            with open("utils/bottoken", "r") as token:
                _ = token.read()
                botToken.setText(_)
        except:
            pass

        customName = QLineEdit()
        customName.setPlaceholderText("Custom name for the pack (leave blank for default)")
        customName.setFixedWidth(300)

        stickerURL = QLineEdit()
        stickerURL.setPlaceholderText("Sticker URL")
        stickerURL.setFixedWidth(300)

        downloadButton = QPushButton("Download")
        downloadButton.setFixedWidth(300)
        downloadButton.clicked.connect(download)
        downloadButton.setFixedHeight(30)



        dlayout.addWidget(message)
        dlayout.addWidget(stickerURL)
        dlayout.addWidget(customName)
        dlayout.addWidget(botToken)
        dlayout.addWidget(downloadButton)
        dlg.setLayout(dlayout)

        try:
            self.backBtn.clicked.disconnect()
        except:
            pass
        self.backBtn.clicked.connect(back)
        self.closeBtn.clicked.disconnect()
        self.closeBtn.clicked.connect(close)


    def quickLoadPrepare(self):
        self.path = self.loadPath[QPushButton.sender(self)]
        try:
            with open("utils/lastpack", "w") as pack:
                pack.write(self.path)
        except:
            pass
        self.unloadStickers()
        self.loadStickers()
    def quickLoad(self):
        added = 0
        def close():
            self.scroll.setVisible(True)
            self.stickerDlg.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.closeWindow)
        self.loadPath = {}
        menu = QMenu()
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
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
                    action.triggered.connect(close)
                    self.loadPath[action] = f"downloads/{i}/"
                    menu.addAction(action)
                    added += 1

        else:
            menu.addAction("No downloads found").setEnabled(False)
        return menu

    def editDropdown(self):
        menu = QMenu()
        self.packs = {}
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
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
                    action.triggered.connect(menu.close)
                    action.triggered.connect(self.editStickers)
                    self.packs[action] = f"downloads/{i}/"
                    menu.addAction(action)

        else:
            menu.addAction("No downloads found").setEnabled(False)
        return menu

    def selectStickers(self):
        def close():
            self.scroll.setVisible(True)
            self.stickerDlg.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.closeWindow)
        self.stickerDlg = QWidget()
        self.stickerDlg.setObjectName("menu")
        self.stickerDlg.setContextMenuPolicy(Qt.CustomContextMenu)
        self.stickerDlg.customContextMenuRequested.connect(close)
        self.vLayout.addWidget(self.stickerDlg)
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)

        qLoad = QPushButton("Quick Load")
        dropdown = self.quickLoad()
        qLoad.setMenu(dropdown)
        qLoad.menu() # For some reason it only sets the menu if this line is here.
        qLoad.setToolTip("Load downloaded stickers quickly")

        browseButton = QPushButton("Browse Stickers")
        browseButton.clicked.connect(self.setStickerPath)
        browseButton.setToolTip("Browse folders and load stickers from them")

        setButton = QPushButton("Load Stickers")
        setButton.clicked.connect(self.checkStickers)
        setButton.clicked.connect(close)
        setButton.setToolTip("Load the stickers to the interface")

        self.favButton = QPushButton("Load Favourites")
        self.favButton.clicked.connect(self.loadFavourites)
        self.favButton.clicked.connect(close)
        self.favButton.setToolTip("Load stickers that you previously saved to your favourites")

        clearButton = QPushButton("Unload Stickers")
        clearButton.clicked.connect(self.unloadStickers)
        clearButton.setToolTip("Unload the stickers from the interface")

        editButton = QPushButton("Manage stickerpacks")
        dropdown = self.editDropdown()
        editButton.setMenu(dropdown)
        editButton.menu()
        editButton.setToolTip("Manage downloaded stickerpacks")

        downloadButton = QPushButton("Download Stickers")
        downloadButton.setToolTip("Download stickers from Telegram")
        downloadButton.clicked.connect(self.downloadSticker)

        qLoad.setFixedWidth(300)
        qLoad.setFixedHeight(30)

        browseButton.setFixedWidth(300)
        browseButton.setFixedHeight(30)

        setButton.setFixedWidth(300)
        setButton.setFixedHeight(30)

        self.favButton.setFixedWidth(300)
        self.favButton.setFixedHeight(30)

        clearButton.setFixedWidth(300)
        clearButton.setFixedHeight(30)

        editButton.setFixedWidth(300)
        editButton.setFixedHeight(30)

        downloadButton.setFixedWidth(300)
        downloadButton.setFixedHeight(30)

        dlayout.addWidget(qLoad)
        dlayout.addWidget(editButton)
        dlayout.addWidget(browseButton)
        dlayout.addWidget(setButton)
        dlayout.addWidget(self.favButton)
        dlayout.addWidget(clearButton)
        dlayout.addWidget(downloadButton)

        self.stickerDlg.setLayout(dlayout)

        self.stickerDlg.setVisible(True)
        self.scroll.setVisible(False)
        self.loadStickersBtn.setVisible(False)
        self.settings.setVisible(False)
        self.widget.setVisible(False)
        self.closeBtn.clicked.disconnect()
        self.closeBtn.clicked.connect(close)
    def editStickers(self):
        self.stickerDlg.setVisible(False)
        def deleteRestore():
            deleteButton.clicked.disconnect()
            deleteButton.setText("Delete")
            deleteButton.clicked.connect(deleteQuestion)
        def delete():
            removable = path.split("/")[0]+"/"+path.split("/")[-2]
            shutil.rmtree(removable)
            time.sleep(0.01)
            back()
        def deleteQuestion():
            deleteButton.setText("Click again to confirm")
            deleteButton.clicked.connect(delete)
            deleteButton.setContextMenuPolicy(Qt.CustomContextMenu)
            deleteButton.customContextMenuRequested.connect(deleteRestore)
        def rename():
            with open(path+"customname", "w") as f:
                f.write(name.text())
            back()
        def close():
            widget.setVisible(False)
            self.backBtn.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.scroll.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.closeWindow)
        def back():
            widget.setVisible(False)
            self.backBtn.setVisible(False)
            self.selectStickers()
        path = self.packs[QPushButton.sender(self)]
        widget = QWidget()
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(back)
        widget.setObjectName("menu")
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)
        widget.setLayout(dlayout)
        self.vLayout.addWidget(widget)
        path = self.packs[QPushButton.sender(self)]
        label = QLabel()
        label.setFixedHeight(30)
        label.setFixedWidth(300)
        if os.path.exists(self.packs[QPushButton.sender(self)]+"customname"):
            with open(self.packs[QPushButton.sender(self)]+"customname") as name:
                label.setText("Edit pack: "+name.read())
        else:
            label.setText("Edit pack: "+self.packs[QPushButton.sender(self)].split("/")[-2])

        name = QLineEdit()
        name.setPlaceholderText("Name")
        name.setFixedWidth(300)
        renameButton = QPushButton("Rename")
        renameButton.setFixedHeight(30)
        renameButton.clicked.connect(rename)
        deleteButton = QPushButton("Delete")
        deleteButton.setFixedHeight(30)
        deleteButton.clicked.connect(lambda :deleteQuestion())
        deleteButton.setObjectName("highrisk")

        dlayout.addWidget(label)
        dlayout.addWidget(name)
        dlayout.addWidget(renameButton)
        dlayout.addWidget(deleteButton)

        try:
            self.backBtn.clicked.disconnect()
        except:
            pass
        self.backBtn.setVisible(True)
        self.backBtn.clicked.connect(back)
        self.closeBtn.clicked.disconnect()
        self.closeBtn.clicked.connect(close)

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

            else:
                self.dropError(f"Too many stickers! The limit is {max['max_stickers_loadable']}.")

    def loadStickers(self):
        error = False
        if os.path.exists(self.path):
            br = False
            onlyfiles = [f for f in listdir(self.path) if isfile(join(self.path, f)) if f.split(".")[-1].lower() == "jpg" or f.split(".")[-1].lower() == "png" or f.split(".")[-1].lower() == "webp"]
            if not self.stickersLoaded and len(self.path):
                config_object = ConfigParser()
                config_object.read("utils/config.ini")
                settings = config_object["SETTINGS"]
                columns = int(settings["columns"])
                width_height = 400/columns
                if self.path[-1] != "/":
                    self.path += "/"
                file = 0
                button_list = []
                self.stickers = {}
                for i in range(len(onlyfiles)):
                    conf = ConfigParser()
                    conf.read("utils/config.ini")
                    max = conf["SETTINGS"]
                    if len(onlyfiles) > int(max["max_stickers_loadable"]):
                        br = True
                        error = True
                        self.dropError(f"Too many stickers! The limit is {max['max_stickers_loadable']}.")
                        onlyfiles = []
                        break
                    if br:
                        break
                    for x in range(columns):

                        button = QPushButton()
                        try:
                            icon = self.path+onlyfiles[file]
                            button.setObjectName("no_bg_btn")
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

                try:
                    with open("utils/lastpack", "w") as pack:
                        pack.write(self.path)
                except:
                    pass
                self.stickersLoaded = True
                if not error:
                    if self.message.text() != "Favourites" and self.path == "utils/favourites/":
                        self.animateMessage("Favourites", None, False)
                    elif self.message.text() != "Favourites" and self.path != "utils/favourites/":
                        self.animateMessage(self.path, "Path: ", False)
                    elif self.message.text() == "Favourites" and self.path != "utils/favourites/":
                        self.animateMessage("Path: "+self.path, None, False)
                    elif self.message.text() == "Favourites" and self.path == "utils/favourites/":
                        pass
        else:
            self.dropError(f"The given path does not exist! ({self.path})")





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
        # C:\Windows\Media\Windows Notify Email.wav
        # "C:\Windows\Media\Windows Notify Calendar.wav
        def playsound():
            winsound.PlaySound("utils/error.wav", winsound.SND_FILENAME)
        def thread():
            self.animateMessage(message, None, True)
        x = threading.Thread(target=playsound)
        y = threading.Thread(target=thread)
        y.start()
        x.start()

        # msgBox = QMessageBox(self)
        # # Create a QPixmap object with the desired image file
        # icon_path = "utils/warning.png"
        # icon = QPixmap(icon_path)
        #
        # # Resize the QPixmap object
        #
        # # Set the icon for the QMessageBox
        # msgBox.setIconPixmap(icon)
        #
        # msgBox.setWindowTitle("Error")
        # msgBox.setText(message)
        #
        #
        # msgBox.show()



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
