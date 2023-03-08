import sys, os, shutil, threading, winsound, time, subprocess

from PySide2 import QtCore
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from os.path import isfile, join
from os import listdir
import win32clipboard as clp
from configparser import ConfigParser
from modules import downloader
from io import BytesIO
from PIL import Image

VERSION = "v1.4"
FIRST = False
NAME = "Tele-py"

class Stickers(QMainWindow):

    def __init__(self):
        super(Stickers, self).__init__()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('utils/icon.png'))
        self.tray_icon.show()

        # Create a custom context menu for the tray icon
        self.tray_menu = QMenu(self)
        self.tray_menu.addAction("Show Window", self.window_to_visible)
        self.tray_menu.addAction("Load favourites", self.load_favourites)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction("Quit", QApplication.quit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_handle)

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
                path = pack.read()
                print(os.path.exists(path))
                if os.path.exists(path):
                    self.path = path
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
            self.animate_message("Favourites", None, False)
        elif os.path.exists(self.path+"/customname"):
            with open(self.path+"/customname") as f:
                self.animate_message(f.read(), None, False)
        elif self.path != "":
            self.animate_message(self.path, "Path: ", False)
        else:
            self.animate_message(f"Tele-py {VERSION}")
        hLayout.addWidget(self.message)

        verticalSpacer = QSpacerItem(500, 0)
        hLayout.addItem(verticalSpacer)

        self.loadStickersBtn = QPushButton()
        size = QSize(30,30)
        self.loadStickersBtn.setFixedSize(30,30)
        self.loadStickersBtn.setIcon(QIcon(f"utils/{self.styleLocation}/loadStickers.png"))
        self.loadStickersBtn.setIconSize(size)
        self.loadStickersBtn.setToolTip("Menu")
        self.loadStickersBtn.clicked.connect(lambda :self.menu())
        self.loadStickersBtn.setObjectName("no_bg_btn")
        hLayout.addWidget(self.loadStickersBtn)

        self.settings = QPushButton()
        size = QSize(25,25)
        self.settings.setFixedSize(30,30)
        self.settings.setIcon(QIcon(f"utils/{self.styleLocation}/settings.png"))
        self.settings.setToolTip("Settings")
        self.settings.setIconSize(size)
        self.settings.clicked.connect(lambda :self.settings_menu())
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
        self.closeBtn.clicked.connect(lambda :self.close_window())
        self.closeBtn.setObjectName("no_bg_btn")
        hLayout.addWidget(self.closeBtn)

        self.vLayout.addWidget(self.scroll)
        self.centralWidget.setLayout(self.vLayout)
    def progressbar(self):
        self.message.setObjectName("")
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                self.message.setStyleSheet(str(style.read()))
                styleSheet = style
        except FileNotFoundError:
            pass
        self.message.setText("Loading, please wait")
        self.bar = QProgressBar(parent=self)
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)
        self.bar.setFixedHeight(30)
        self.bar.setFixedWidth(300)
        self.bar.move(100, 461)
        self.bar.show()
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

    def animate_message(self, text, unanimated = None, isError = False):
        if isError:
            self.message.setObjectName("error")
        else:
            self.message.setObjectName("")
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                self.message.setStyleSheet(str(style.read()))
                styleSheet = style
        except:
            pass
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
    def window_to_visible(self):
        if not self.visible:
            flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
            self.setWindowFlags(flags)
            self.setVisible(True)
            self.visible = True

    def tray_icon_handle(self, reason):
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
            self.closeBtn.clicked.connect(self.close_window)
            self.scroll.setVisible(True)
            self.widget.setVisible(True)
            self.blur.setBlurRadius(0)
            widget.hide()
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)
        widget = QWidget(parent=self)
        blur_effect = QGraphicsBlurEffect(blurRadius=5)
        self.widget.setGraphicsEffect(blur_effect)
        widget.setObjectName("preview")
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
        button.clicked.connect(self.copy_sticker)
        sticker_location = self.stickers[QPushButton.sender(self)]
        original = rf'{sticker_location}'
        file_name = original.split("/")[-1]
        def favourite():
            try:
                target = r'utils/favourites/'+file_name
                shutil.copyfile(original, target)
                favButton.setText("Remove from favourites")
                self.notify(text="Saved to favourites!")
                favButton.clicked.connect(unfavourite)
            except:
                pass
        def unfavourite():
            if os.path.exists("utils/favourites/"+file_name):
                os.remove("utils/favourites/"+file_name)
                favButton.setText("Save to favourites")
                self.notify(text="Removed from favourites!")
                favButton.clicked.connect(favourite)


        dlayout.addWidget(button)
        hLayout = QHBoxLayout()
        dlayout.addLayout(hLayout)
        if os.path.exists("utils/favourites/"+file_name):
            favButton = QPushButton("Remove from favourites")
            favButton.clicked.connect(unfavourite)
        else:
            favButton = QPushButton("Save to favourites")
            favButton.clicked.connect(favourite)
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
            self.blur = QGraphicsBlurEffect()
            self.blur.setBlurRadius(10)
            self.scroll.setGraphicsEffect(self.blur)
            widget.show()
        else:
            self.unload_stickers()
            self.drop_error(f"File not found! ({sticker_location})")
    def copy_sticker(self):
        def send_to_clipboard(clip_type, data):
            clp.OpenClipboard()
            clp.EmptyClipboard()
            clp.SetClipboardData(clip_type, data)
            clp.CloseClipboard()
        file_path = self.stickers[QPushButton.sender(self)]
        if os.path.exists(file_path):
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            if settings["copy_method"] == "dc":
                clp.OpenClipboard()
                clp.EmptyClipboard()
                # This works for Discord, but not for Paint.NET:
                wide_path = os.path.abspath(file_path).encode('utf-16-le') + b'\0'
                clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), wide_path)
                clp.CloseClipboard()
            elif settings["copy_method"] == "gimp":
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
            self.unload_stickers()
            self.drop_error(f"File not found! ({file_path})")

    def close_window(self):
        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        hides = config_object["SETTINGS"]
        if not int(hides["hides"]) == 1:
            QApplication.quit()
        else:
            self.setVisible(False)
            self.visible = False
    def change_style(self):
        self.location = self.stylesheets[QPushButton.sender(self)]

        with open(f"utils/stylesheet/{self.location}/customname", "r") as f:
            self.settingsMessage.setText(f"Press 'Apply stylesheet' to apply theme '{f.read()}'")

    def settings_menu(self):
        def close():
            dlg.setVisible(False)
            self.saveBtn.setVisible(False)
            self.scroll.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.settings.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
        dlg = QWidget()
        dlg.setContextMenuPolicy(Qt.CustomContextMenu)
        dlg.customContextMenuRequested.connect(close)
        dlayout = QVBoxLayout()
        dlg.setObjectName("menu")
        dlg.setLayout(dlayout)
        dlayout.setAlignment(Qt.AlignCenter)
        def apply_syle():
            try:
                with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                    self.setStyleSheet(str(style.read()))
            except:
                pass

        def dc_copy():
            if not dcComp.objectName() == "activeBtn":
                config_object = ConfigParser()
                config_object.read("utils/config.ini")
                settings = config_object["SETTINGS"]
                settings["copy_method"] = "dc"

                with open('utils/config.ini', 'w') as conf:
                    config_object.write(conf)
                dcComp.setObjectName("activeBtn")
                gimpComp.setObjectName("")
                apply_syle()
        def gimp_copy():
            if not gimpComp.objectName() == "activeBtn":
                config_object = ConfigParser()
                config_object.read("utils/config.ini")
                settings = config_object["SETTINGS"]
                settings["copy_method"] = "gimp"

                with open('utils/config.ini', 'w') as conf:
                    config_object.write(conf)
                gimpComp.setObjectName("activeBtn")
                dcComp.setObjectName("")
                apply_syle()
        def closes_window():
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
            apply_syle()
        def hides_window():
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
            apply_syle()
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
        def add_style():
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

        applyStyleBtn = QPushButton("Apply stylesheet")
        applyStyleBtn.setFixedWidth(300)
        applyStyleBtn.setFixedHeight(30)
        applyStyleBtn.clicked.connect(add_style)
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
                                name = "["+f.read()+"]"
                            else:
                                name = f.read()
                    except:
                        if active:
                            name = "["+i+"]"
                        else:
                            name = i
                    action = QAction(name)
                    self.stylesheets[action] = i
                    action.triggered.connect(self.change_style)
                    elements.append(action)
                for i in elements:
                    menu.addAction(i)
            else:
                menu.addAction("No stylesheets found").setEnabled(False)
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
        hideWindowBtn.clicked.connect(hides_window)
        closeWindowBtn = QPushButton("Close application")
        closeWindowBtn.setFixedHeight(30)
        closeWindowBtn.clicked.connect(closes_window)
        hidesLayout.addWidget(hideWindowBtn)
        hidesLayout.addWidget(closeWindowBtn)

        if settings["hides"] == "1":
            hideWindowBtn.setObjectName("activeBtn")
        elif settings["hides"] == "0":
            closeWindowBtn.setObjectName("activeBtn")

        dcComp = QPushButton("Discord")
        dcComp.clicked.connect(dc_copy)
        dcComp.setFixedHeight(30)

        gimpComp = QPushButton("Gimp")
        gimpComp.clicked.connect(gimp_copy)
        gimpComp.setFixedHeight(30)

        if settings["copy_method"] == "dc":
            dcComp.setObjectName("activeBtn")
        elif settings["copy_method"] == "gimp":
            gimpComp.setObjectName("activeBtn")


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

    def check_stickers(self):
        if len(self.path) and not self.stickersLoaded:
            self.load_stickers()
        else:
            if self.stickersLoaded:
                self.unload_stickers()
                self.load_stickers()

    def load_favourites(self):
        self.path = "utils/favourites/"
        self.unload_stickers()
        self.load_stickers()


    def download_stickers(self):
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
            self.closeBtn.clicked.connect(self.close_window)
        def back():
            dlg.setVisible(False)
            self.backBtn.setVisible(False)
            self.menu()

        def download():
            def thread():
                failed = False
                with open("utils/bottoken", "w") as token:
                    token.write(botToken.text())
                try:
                    sticker_downloader = downloader.StickerDownloader(botToken.text())

                    name = stickerURL.text()
                    if not os.path.exists(f"downloads/{name}") and name != "":
                        if name != "":
                            message.setObjectName("")
                            message.setStyleSheet(styleSheet)
                            message.setText("Getting pack info...")
                            name = (name.split('/')[-1])


                            print('=' * 60)
                            pack = sticker_downloader.get_sticker_set(name)

                            print('-' * 60)
                            message.setText("Downloading files...")
                            sticker_downloader.download_sticker_set(pack)
                            if customName.text():
                                with open(f"downloads/{name}/customname", "wt") as f:
                                    f.write(customName.text())
                            else:
                                with open(f"downloads/{name}/customname", "wt") as f:
                                    f.write(pack["title"])
                            message.setObjectName("success")
                            message.setStyleSheet(styleSheet)
                            message.setText("Download completed!")
                            winsound.PlaySound("utils/success.wav", winsound.SND_ASYNC)
                        else:
                            message.setObjectName("error")
                            message.setStyleSheet(styleSheet)
                            message.setText("Invalid URL!")
                            winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                    elif name == "":
                        message.setObjectName("error")
                        message.setStyleSheet(styleSheet)
                        message.setText("Invalid URL!")
                        winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)

                    elif os.path.exists(f"downloads/{name}"):
                        message.setObjectName("error")
                        message.setStyleSheet(styleSheet)
                        message.setText("Stickers already downloaded!")
                        winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)

                except Exception as exception:
                    print(exception)
                    message.setObjectName("error")
                    message.setStyleSheet(styleSheet)
                    message.setText("Download failed! Please check the token and the URL!")
                    winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)

            x = threading.Thread(target=thread)

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
        botToken.setEchoMode(QLineEdit.Password)
        botToken.setPlaceholderText("Token")
        try:
            with open("utils/bottoken", "r") as token:
                _ = token.read()
                botToken.setText(_.strip())
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


    def quick_load_prepare(self):
        self.path = self.loadPath[QPushButton.sender(self)]
        try:
            with open("utils/lastpack", "w") as pack:
                pack.write(self.path)
        except:
            pass
        self.unload_stickers()
        self.load_stickers()
    def quick_load_dropdown(self):
        added = 0
        def close():
            self.scroll.setVisible(True)
            self.stickerDlg.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
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
                    action.triggered.connect(self.quick_load_prepare)
                    action.triggered.connect(menu.close)
                    action.triggered.connect(close)
                    self.loadPath[action] = f"downloads/{i}/"
                    menu.addAction(action)
                    added += 1
            else:
                menu.addAction("No downloads found").setEnabled(False)

        else:
            menu.addAction("No downloads found").setEnabled(False)
        return menu

    def manage_stickers_dropdown(self):
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
                    action.triggered.connect(self.manage_stickers)
                    self.packs[action] = f"downloads/{i}/"
                    menu.addAction(action)
            else:
                menu.addAction("No downloads found").setEnabled(False)
        else:
            menu.addAction("No downloads found").setEnabled(False)
        return menu

    def menu(self):
        def close():
            self.scroll.setVisible(True)
            self.stickerDlg.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
        self.stickerDlg = QWidget()
        self.stickerDlg.setObjectName("menu")
        self.stickerDlg.setContextMenuPolicy(Qt.CustomContextMenu)
        self.stickerDlg.customContextMenuRequested.connect(close)
        # self.vLayout.addWidget(self.stickerDlg)
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)

        qLoad = QPushButton("Quick Load")
        dropdown = self.quick_load_dropdown()
        qLoad.setMenu(dropdown)
        qLoad.menu() # For some reason it only sets the menu if this line is here.
        qLoad.setToolTip("Load downloaded stickers quickly")

        browseButton = QPushButton("Browse Stickers")
        browseButton.clicked.connect(self.set_sticker_path)
        browseButton.setToolTip("Browse folders and load stickers from them")

        setButton = QPushButton("Load Stickers")
        setButton.clicked.connect(self.check_stickers)
        setButton.clicked.connect(close)
        setButton.setToolTip("Load the stickers to the interface")

        self.favButton = QPushButton("Load Favourites")
        self.favButton.clicked.connect(self.load_favourites)
        self.favButton.clicked.connect(close)
        self.favButton.setToolTip("Load stickers that you previously saved to your favourites")

        clearButton = QPushButton("Unload Stickers")
        clearButton.clicked.connect(self.unload_stickers)
        clearButton.setToolTip("Unload the stickers from the interface")

        editButton = QPushButton("Manage stickerpacks")
        dropdown = self.manage_stickers_dropdown()
        editButton.setMenu(dropdown)
        editButton.menu()
        editButton.setToolTip("Manage downloaded stickerpacks")

        downloadButton = QPushButton("Download Stickers")
        downloadButton.setToolTip("Download stickers from Telegram")
        downloadButton.clicked.connect(self.download_stickers)

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
        self.vLayout.addWidget(self.stickerDlg)

        self.stickerDlg.resize(self.scroll.size())
        self.stickerDlg.move(self.scroll.pos())

        self.stickerDlg.setVisible(True)
        self.scroll.setVisible(False)
        self.loadStickersBtn.setVisible(False)
        self.settings.setVisible(False)
        self.widget.setVisible(False)
        self.closeBtn.clicked.disconnect()
        self.closeBtn.clicked.connect(close)

    def manage_stickers(self):
        self.stickerDlg.setVisible(False)
        def delete_restore():
            deleteButton.clicked.disconnect()
            deleteButton.setText("Delete")
            deleteButton.clicked.connect(delete_question)
        def delete():
            removable = path.split("/")[0]+"/"+path.split("/")[-2]
            shutil.rmtree(removable)
            self.notify(text="Pack deleted!")
            back()
        def delete_question():
            deleteButton.setText("Click again to confirm")
            deleteButton.clicked.connect(delete)
            deleteButton.setContextMenuPolicy(Qt.CustomContextMenu)
            deleteButton.customContextMenuRequested.connect(delete_restore)
        def rename():
            if name.text():
                with open(path+"customname", "w") as f:
                    f.write(name.text())
                self.notify(text="Pack renamed!")
                back()
            else:
                self.drop_error("Cannot set name!")
        def close():
            widget.setVisible(False)
            self.backBtn.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.scroll.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
        def back():
            widget.setVisible(False)
            self.backBtn.setVisible(False)
            self.menu()
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
        deleteButton.clicked.connect(lambda :delete_question())
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

    def set_sticker_path(self):
        self.path = QFileDialog.getExistingDirectory(self, "Select Sticker Folder")
        if len(self.path):
            self.message.setText(f"Path: {self.path}")

    def load_stickers(self):
        self.progressbar()
        if os.path.exists(self.path):
            br = False
            onlyfiles = [f for f in listdir(self.path)
                         if isfile(join(self.path, f))
                         if f.split(".")[-1].lower() == "jpg"
                         or f.split(".")[-1].lower() == "png"
                         or f.split(".")[-1].lower() == "webp"]
            bar_value = 0
            if not self.stickersLoaded and len(self.path):
                config_object = ConfigParser()
                config_object.read("utils/config.ini")
                settings = config_object["SETTINGS"]
                columns = int(settings["columns"])
                width_height = 400/columns
                if self.path[-1] != "/":
                    self.path += "/"
                file = 0
                col = 0
                row = 0
                button_list = []
                self.stickers = {}
                conf = ConfigParser()
                conf.read("utils/config.ini")
                max = conf["SETTINGS"]
                if not len(onlyfiles) > int(max["max_stickers_loadable"]):
                    segment = 100/len(onlyfiles)
                else:
                    segment = 100/int(max["max_stickers_loadable"])
                for i in onlyfiles:
                    if file+1 > int(max["max_stickers_loadable"]):
                        br = True
                        break
                    if br:
                        break
                    if file+1 > int(max["max_stickers_loadable"]):
                        br = True
                        break
                    bar_value += segment
                    self.bar.setValue(bar_value)
                    button = QPushButton()
                    icon = self.path + i
                    button.setObjectName("no_bg_btn")
                    button.setIcon(QIcon(icon))
                    button.setFixedSize(width_height,width_height)
                    size = QSize(width_height,width_height)
                    self.stickers[button] = self.path + i
                    button.setIconSize(size)
                    button_list.append(button)
                    self.layout.addWidget(button, row, col)
                    button.clicked.connect(self.copy_sticker)
                    button.setContextMenuPolicy(Qt.CustomContextMenu)
                    button.customContextMenuRequested.connect(self.preview)
                    file += 1
                    col += 1
                    if col % columns == 0:
                        row += 1
                        col = 0

                try:
                    with open("utils/lastpack", "w") as pack:
                        pack.write(self.path)
                except:
                    pass
                self.stickersLoaded = True
                self.bar.hide()
                if self.path == "utils/favourites/":
                    self.animate_message("Favourites", None, False)
                elif os.path.exists(self.path+"/customname"):
                    with open(self.path+"/customname") as f:
                        self.animate_message(f.read())
                else:
                    self.animate_message("Path: " + self.path)
        else:
            with open("utils/lastpack", "w") as file:
                file.write("")
            self.bar.hide()
            self.drop_error(f"The given path does not exist! ({self.path})")
            self.path = ""


    def unload_stickers(self):
        children = []
        for i in range(self.layout.count()):
            child = self.layout.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()
        self.stickersLoaded = False

    def drop_error(self, message):
        def playsound():
            winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
        def thread():
            self.animate_message(message, None, True)
        x = threading.Thread(target=playsound)
        y = threading.Thread(target=thread)
        y.start()
        x.start()

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
    title = NAME+" "+VERSION+" Debug Console"
    print(f"{title:_^60}")

    print("Checking directory \"favourites\"...", end="")
    if not os.path.exists("utils/favourites"):
        print("Not found!")
        print("Making directory \"favourites\"...", end="")
        os.mkdir("utils/favourites")
        FIRST = True
    print("Done!")

    print("Checking file \"lastpack\"...", end="")
    if not os.path.exists("utils/lastpack"):
        print("Not found!")
        print("Creating file \"lastpack\"...", end="")
        with open("utils/lastpack", "a") as _:
            FIRST = True
    print("Done!")

    print("Checking file \"bottoken\"...", end="")
    if not os.path.exists("utils/bottoken"):
        print("Not found!")
        print("Creating file \"bottoken\"...", end="")
        with open("utils/bottoken", "a") as _:
            FIRST = True
    print("Done!")

    print("Checking config file...", end="")
    if not os.path.exists("utils/config.ini"):
        print("Not found!")
        print("Creating config file...", end="")
        with open("utils/config.ini", "a") as _:
            FIRST = True
            _.write("""[SETTINGS]
max_stickers_loadable = 120
copy_method = dc
columns = 4
hides = 0
stylesheet = distant_horizon""")
    print("Done!")

    print("Launching application...")
    title = "Debug prints below:"
    print(f"{title:_^60}")
    del title
    app = QApplication(sys.argv)
    stickerWindow = Stickers()
    stickerWindow.show()
    app.exec_()