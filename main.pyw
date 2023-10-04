# import logging
import sys, os, shutil, threading, winsound, time, subprocess, re

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from os.path import isfile, join
from os import listdir
import win32clipboard as clp
from configparser import ConfigParser
from modules import downloader
from widgets import (update_widget, settings_widget, download_widget, menu_widget, managestickerpack_widget,
                     confirm_widget)
from io import BytesIO

VERSION = "indev"
FIRST = False #currently unused
NAME = "Tele-py"

class Stickers(QMainWindow):

    def __init__(self):
        super(Stickers, self).__init__()


        self.settings_widget = settings_widget.SettingsWidget()

        self.download_widget = download_widget.DownloadWidget(parent=self)
        self.download_widget.move(50,50)
        self.download_widget.downloader = downloader
        self.download_widget.progressbar = self.progressbar
        self.download_widget.hide_progressbar = self.hide_progress_bar
        self.download_widget.menu_dropdown_update_func = self.update_menu_dropdown_remote

        self.confirm_widget = confirm_widget.ConfirmWidget(parent=self)
        self.confirm_widget.move(50,100)

        self.menu_widget = menu_widget.MenuWidget(parent=self)
        self.menu_widget.move(330, 50)

        self.manage_stickerpack_widget = managestickerpack_widget.ManageStickerpackWidget(parent=self)
        self.manage_stickerpack_widget.move(50,50)


        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('utils/icon.png'))
        self.tray_icon.setToolTip("Tele-py")
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
        if os.path.exists("utils/lastpack"):
            with open("utils/lastpack", "r") as pack:
                path = pack.read()
                print(os.path.exists(path))
                if os.path.exists(path):
                    self.path = path

        if os.path.exists(f"utils/{self.styleLocation}/style_main.css"):
            flags = Qt.WindowFlags(Qt.FramelessWindowHint)
            self.menu_widget.style_sheet = self.styleLocation
            self.menu_widget.qLoad.setIcon(QIcon(f"utils/{self.styleLocation}/load_stickers.png"))
            self.menu_widget.browseButton.setIcon(QIcon(QIcon(f"utils/{self.styleLocation}/browse.png")))
            self.menu_widget.downloadButton.setIcon(QIcon(f"utils/{self.styleLocation}/plus.png"))
            self.setWindowFlags(flags)
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                self.setStyleSheet(str(style.read()))

        self.setWindowTitle("Tele-py")
        self.resize(500, 500)
        self.setMaximumSize(500, 500)
        self.setMinimumSize(500, 500)


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
        pack = ""
        if self.path == "utils/favourites/" or self.path == "utils/favourites":
            pack = "Favourites"
        elif os.path.exists(self.path+"/customname"):
            with open(self.path+"/customname") as f:
                pack = f.read()
        elif self.path != "":
            pack = self.path
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

        self.vLayout.addWidget(self.settings_widget)

        if settings["disable_updater"] == "0":
            self.update_widget = update_widget.UpdateWidget(VERSION)
            self.settings_widget.update_widget = self.update_widget
            self.settings_widget.saveBtn = self.saveBtn
            self.updater_disabled = False
            self.vLayout.addWidget(self.update_widget)
            self.update_widget.setVisible(False)
            self.settings_widget.updateBtn.clicked.connect(self.update_program)
        else:
            self.updater_disabled = True
            self.settings_widget.updateBtn.setVisible(False)

        self.settings_widget.setVisible(False)
        self.download_widget.setVisible(False)
        self.menu_widget.setVisible(False)
        self.manage_stickerpack_widget.setVisible(False)
        self.settings_widget.dcComp.clicked.connect(self.apply_style)
        self.settings_widget.gimpComp.clicked.connect(self.apply_style)
        self.settings_widget.clipcopy.clicked.connect(self.apply_style)
        self.settings_widget.hideWindowBtn.clicked.connect(self.apply_style)
        self.settings_widget.closeWindowBtn.clicked.connect(self.apply_style)
        self.settings_widget.ask_last_pack.clicked.connect(self.apply_style)

        self.blur = QGraphicsBlurEffect()
        self.scroll.setGraphicsEffect(self.blur)

        self.overlay_widget = QWidget(parent=self)
        self.overlay_widget.setStyleSheet("")
        self.overlay_widget.setVisible(False)

        #Todo: implement auto-check for updates

        self.centralWidget.setLayout(self.vLayout)

        self.update_menu_dropdown()

        self.should_update_menu_dropdown = False

        self.is_menu_open = False

        if pack and settings["ask_last_pack"] == "1": self.load_last_pack(pack)

    def load_last_pack(self, pack):
        self.menu_open()
        self.confirm_widget.setVisible(True)
        self.confirm_widget.setFixedHeight(200)
        self.confirm_widget.raise_()
        self.confirm_widget.message_label.setText(f"<p>Your last used pack was<br>"
                                                  f"<code>{pack}</code><br>"
                                                  f"Do you want to load it?</p>")
        def load():
            self.load_stickers()
            self.confirm_widget.setVisible(False)
            self.menu_close()
        def close():
            self.confirm_widget.setVisible(False)
            self.menu_close()
        self.confirm_widget.accept_button.clicked.connect(load)
        self.confirm_widget.deny_button.clicked.connect(close)


    def update_menu_dropdown_remote(self):
        self.should_update_menu_dropdown = True

    def update_menu_dropdown(self):
        print("Updated")
        self.menu_widget.set_menu(self.quick_load_dropdown(),self.manage_stickers_dropdown())


    def hide_progress_bar(self):
        self.bar.setVisible(False)

    def progressbar(self):
        self.bar = QProgressBar(parent=self)
        self.bar.setMinimum(0)
        self.bar.setMaximum(0)
        self.bar.setFixedHeight(30)
        self.bar.setFixedWidth(300)
        self.bar.move(100, 461)
        self.bar.show()


    def notify(self, text, isError = False, timeout = 1):
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
            winsound.PlaySound("utils/notify.wav" if not isError else "utils/error.wav", winsound.SND_ASYNC)
        def thread():
            for i in range(40):
                notification.move(100, 500-i+1)
                time.sleep(0.01)
            time.sleep(timeout)
            for i in range(40):
                notification.move(100, 460+i+1)
                time.sleep(0.01)
            notification.hide()
            notification.deleteLater()
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
            flags = Qt.WindowFlags(Qt.FramelessWindowHint)
            self.setWindowFlags(flags)
            self.setVisible(True)
            self.visible = True

    def tray_icon_handle(self, reason):
        if reason == QSystemTrayIcon.Trigger and not self.visible:
            self.window_to_visible()
        elif reason == QSystemTrayIcon.Context:
            self.tray_menu.popup(QCursor.pos())

    def preview(self):
        def close():
            self.menu_close()
            self.loadStickersBtn.setVisible(True)
            self.settings.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
            self.scroll.setVisible(True)
            self.widget.setVisible(True)
            widget.hide()
            widget.deleteLater()
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)
        widget = QWidget(parent=self)


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
            self.menu_open()
            widget.show()
        else:
            self.unload_stickers()
            self.drop_error(f"File not found! ({sticker_location})")
    def copy_sticker(self):
        file_path = self.stickers[QPushButton.sender(self)]
        if os.path.exists(file_path):
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            if settings["copy_method"] == "dc":
                clp.OpenClipboard()
                clp.EmptyClipboard()
                wide_path = os.path.abspath(file_path).encode('utf-16-le') + b'\0'
                clp.SetClipboardData(clp.RegisterClipboardFormat('FileNameW'), wide_path)
                clp.CloseClipboard()
            elif settings["copy_method"] == "gimp":
                self.notify("Unsupported copy method!", isError=True)
                return
            elif settings["copy_method"] == "cc":
                subprocess.run(["modules\clipcopy.exe", file_path], shell=True)



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
    def apply_style(self):
        with open(f"utils/stylesheet/{self.settings_widget.style_sheet}/style_main.css") as f:
            self.setStyleSheet(f.read())

    def settings_menu(self):
        def close():
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.scroll.setVisible(True)
            self.saveBtn.setVisible(False)
            self.settings_widget.setVisible(False)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)

        # Not the prettiest but it does the job
        try:
            self.settings_widget.applyStyleBtn.clicked.disconnect()
        except RuntimeError:
            pass
        try:
            self.backBtn.clicked.disconnect()
        except RuntimeError:
            pass
        try:
            self.settings_widget.maxFileIn.returnPressed.disconnect()
        except RuntimeError:
            pass
        try:
            self.settings_widget.columnsIn.returnPressed.disconnect()
        except RuntimeError:
            pass

        self.settings_widget.scroll.verticalScrollBar().setValue(0)
        self.settings_widget.maxFileIn.setText(None)
        self.settings_widget.columnsIn.setText(None)
        self.settings_widget.applyStyleBtn.clicked.connect(self.apply_style)
        self.settings_widget.applyStyleBtn.clicked.connect(self.settings_widget.applied_style)
        self.saveBtn.clicked.connect(self.settings_widget.save_line_edits)
        self.saveBtn.clicked.connect(close)
        self.closeBtn.clicked.disconnect()
        self.closeBtn.clicked.connect(close)
        self.settings_widget.columnsIn.returnPressed.connect(self.settings_widget.save_line_edits)
        self.settings_widget.columnsIn.returnPressed.connect(close)
        self.settings_widget.maxFileIn.returnPressed.connect(self.settings_widget.save_line_edits)
        self.settings_widget.maxFileIn.returnPressed.connect(close)
        self.settings.setVisible(False)
        self.loadStickersBtn.setVisible(False)
        self.scroll.setVisible(False)
        self.saveBtn.setVisible(True)
        self.settings_widget.setVisible(True)
        self.settings_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.settings_widget.customContextMenuRequested.connect(close)



    def update_program(self):
        self.update_widget.update_button.setText("Update")
        self.update_widget.message.setText("")
        # if not self.update_widget.message_succes.text() == "Please restart the application!":
        #     self.update_widget.message_error.setVisible(False)
        #     self.update_widget.message.setVisible(True)
        #     self.update_widget.bar.setVisible(False)

        self.settings_widget.setVisible(False)
        self.update_widget.setVisible(True)
        self.saveBtn.setVisible(False)
        def close():
            if self.update_widget.is_update_in_progress:
                self.notify(text="The update is still running in the background!")
            elif self.update_widget.should_restart:
                self.notify(text="Please restart the application")
            self.update_widget.setVisible(False)
            self.backBtn.setVisible(False)
            self.scroll.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.settings.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
            self.closeBtn.setVisible(True)
        def back():
            if self.update_widget.is_update_in_progress:
                self.notify(text="The update is still running in the background!")
            elif self.update_widget.should_restart:
                self.notify(text="Please restart the application")
            self.backBtn.setVisible(False)
            self.update_widget.setVisible(False)
            self.settings_menu()


        self.update_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.update_widget.customContextMenuRequested.connect(back)



        self.scroll.setVisible(False)
        self.loadStickersBtn.setVisible(False)
        self.settings.setVisible(False)
        try:
            self.backBtn.clicked.disconnect()
        except:
            pass
        self.closeBtn.clicked.disconnect()
        self.closeBtn.clicked.connect(close)
        self.backBtn.clicked.connect(back)
        self.backBtn.setVisible(True)

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


    def download_stickers(self, ignore_menu = False):
        self.download_widget.raise_()
        self.download_widget.message("")
        if not ignore_menu:
            def anim():
                self.menu_widget.move(430, 50)
                for i in range(76):
                    if i % 10 == 0:
                        self.menu_widget.move(430 + i, 50)
                        time.sleep(0.001)
            anim_thread = threading.Thread(target=anim)
            anim_thread.start()
        self.backBtn.setVisible(True)
        def close():
            self.menu_close()
            self.download_widget.stickerURL.setText("")
            self.download_widget.setVisible(False)
            self.backBtn.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.scroll.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
        def back():
            self.download_widget.stickerURL.setText("")
            self.download_widget.setVisible(False)
            self.backBtn.setVisible(False)
            self.menu()
        self.download_widget.customContextMenuRequested.connect(back)
        self.download_widget.setVisible(True)
        self.download_widget.stickerURL.setFocus()
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
        def close():
            self.menu_close(delay=.1)
            self.scroll.setVisible(True)

            def anim():
                self.menu_widget.move(430, 50)
                for i in range(76):
                    if i % 10 == 0:
                        self.menu_widget.move(430 + i, 50)
                        time.sleep(0.001)

                self.menu_widget.setVisible(False)
            anim_thread = threading.Thread(target=anim)
            anim_thread.start()
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

        menu.addAction("Load Stickers").setEnabled(False)
        menu.addSeparator()
        name = "Favourites"
        action = QAction(name)
        action.triggered.connect(self.quick_load_prepare)
        action.setIcon(QIcon(f"utils/{self.styleLocation}/favourites_icon.png"))
        action.triggered.connect(menu.close)
        action.triggered.connect(close)
        self.loadPath[action] = f"utils/favourites"
        menu.addAction(action)
        menu.addSeparator()
        if os.path.exists("downloads"):
            folders = [ name for name in os.listdir("downloads/") if os.path.isdir(os.path.join("downloads/", name)) ]
            if len(folders):

                for i in folders:
                    for f in listdir(f"downloads/{i}/"):
                        if isfile(join(f"downloads/{i}/", f)) and f != "customname" and os.path.exists(f"downloads/{i}/{f}"):
                            icon = f
                            break

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

        menu.addAction("Manage Stickers").setEnabled(False)
        menu.addSeparator()
        if os.path.exists("downloads"):
            folders = [ name for name in os.listdir("downloads/") if os.path.isdir(os.path.join("downloads/", name)) ]
            if len(folders):

                for i in folders:
                    action = QAction(i)
                    size = QSize(10,10)
                    # icon = [f for f in listdir(f"downloads/{i}/") if isfile(join(f"downloads/{i}/", f)) and f != "customname"][0]
                    for f in listdir(f"downloads/{i}/"):
                        if isfile(join(f"downloads/{i}/", f)) and f != "customname" and os.path.exists(f"downloads/{i}/{f}"):
                            icon = f
                            break
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

    def hide_scroll(self):
        self.scroll.setVisible(False)
        self.widget.setVisible(False)
    def show_scroll(self):
        self.scroll.setVisible(True)
        self.widget.setVisible(True)

    def menu_open(self):
        if not self.is_menu_open:
            self.is_menu_open = True
            self.overlay_widget.setFixedSize(self.scroll.size())
            self.overlay_widget.move(self.scroll.pos())
            self.overlay_widget.setVisible(True)
            def anim():
                for i in range(11):
                    self.blur.setBlurRadius(i)
                    time.sleep(0.01)
            anim_thread = threading.Thread(target=anim)
            anim_thread.start()

    def menu_close(self, delay = 0):
        self.is_menu_open = False
        def anim():
            time.sleep(delay)
            for i in range(11):
                self.blur.setBlurRadius(11 - i)
                time.sleep(0.01)
        self.overlay_widget.setVisible(False)
        anim_thread = threading.Thread(target=anim)
        anim_thread.start()

    def menu(self):
        self.menu_widget.setVisible(True)
        def anim():
            self.menu_widget.move(500,50)
            for i in range(76):
                if i%10==0:
                    self.menu_widget.move(500-i, 50)
                    time.sleep(0.001)
        anim_thread = threading.Thread(target=anim)
        anim_thread.start()
        self.menu_open()
        def close():
            def anim():
                self.menu_widget.move(430, 50)
                for i in range(76):
                    if i % 10 == 0:
                        self.menu_widget.move(430 + i, 50)
                        time.sleep(0.001)

                self.menu_widget.setVisible(False)
            anim_thread = threading.Thread(target=anim)
            anim_thread.start()
            self.menu_close()
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
        try: self.menu_widget.customContextMenuRequested.disconnect()
        except: pass
        self.menu_widget.customContextMenuRequested.connect(close)

        try: self.menu_widget.browseButton.clicked.disconnect()
        except: pass
        self.menu_widget.browseButton.clicked.connect(self.set_sticker_path)
        try: self.menu_widget.downloadButton.clicked.disconnect()
        except: pass
        self.menu_widget.downloadButton.clicked.connect(self.download_stickers)

        if self.should_update_menu_dropdown:
            self.should_update_menu_dropdown = False
            self.update_menu_dropdown()

        self.menu_widget.show()
        self.menu_widget.raise_()
        self.menu_widget.resize(QSize(400,400))
        self.loadStickersBtn.setVisible(False)
        self.settings.setVisible(False)
        self.closeBtn.clicked.disconnect()
        self.closeBtn.clicked.connect(close)


    def manage_stickers(self):
        def anim():
            self.menu_widget.move(430, 50)
            for i in range(76):
                if i % 10 == 0:
                    self.menu_widget.move(430 + i, 50)
                    time.sleep(0.001)

        anim_thread = threading.Thread(target=anim)
        anim_thread.start()
        self.manage_stickerpack_widget.setVisible(True)
        self.manage_stickerpack_widget.raise_()
        self.manage_stickerpack_widget.name.setText("")
        def delete_restore():
            self.manage_stickerpack_widget.delete_button.clicked.disconnect()
            self.manage_stickerpack_widget.delete_button.setText("Delete")
            self.manage_stickerpack_widget.delete_button.clicked.connect(delete_question)
        def delete():
            delete_restore()
            removable = path.split("/")[0]+"/"+path.split("/")[-2]
            shutil.rmtree(removable)
            self.notify(text="Pack deleted!")
            self.update_menu_dropdown()
            back()
        def delete_question():
            self.manage_stickerpack_widget.delete_button.setText("Click again to confirm")
            self.manage_stickerpack_widget.delete_button.clicked.connect(delete)
            self.manage_stickerpack_widget.delete_button.setContextMenuPolicy(Qt.CustomContextMenu)
            self.manage_stickerpack_widget.delete_button.customContextMenuRequested.connect(delete_restore)
        def rename():
            if self.manage_stickerpack_widget.name.text():
                with open(path+"customname", "w") as f:
                    f.write(self.manage_stickerpack_widget.name.text())
                self.notify(text="Pack renamed!")
                self.update_menu_dropdown()
                back()
            else:
                self.drop_error("Cannot set name!")
        def close():
            self.menu_close()
            self.manage_stickerpack_widget.setVisible(False)
            self.backBtn.setVisible(False)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.scroll.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)
        def back():
            self.backBtn.setVisible(False)
            self.manage_stickerpack_widget.setVisible(False)
            self.menu()
        def update_pack():
            self.backBtn.setVisible(False)
            self.manage_stickerpack_widget.setVisible(False)
            self.download_stickers(ignore_menu=True)
            self.download_widget.stickerURL.setText(pack_link)
            self.download_widget.download()
        path = self.packs[QPushButton.sender(self)]
        self.manage_stickerpack_widget.customContextMenuRequested.connect(back)
        path = self.packs[QPushButton.sender(self)]
        pack_name = ""
        pack_link = self.packs[QPushButton.sender(self)].split("/")[-2]
        if os.path.exists(self.packs[QPushButton.sender(self)]+"customname"):
            with open(self.packs[QPushButton.sender(self)]+"customname") as name:
                pack_name = name.read()
        else:
            pack_name = pack_link
        self.manage_stickerpack_widget.label.setText(f"Edit pack: {pack_name}")

        self.manage_stickerpack_widget.link_label.setText("Pack's link: https://t.me/addstickers/"
                                                           +self.packs[QPushButton.sender(self)].split("/")[-2])

        try: self.manage_stickerpack_widget.rename_button.clicked.disconnect()
        except: pass
        self.manage_stickerpack_widget.rename_button.clicked.connect(rename)

        try: self.manage_stickerpack_widget.update_button.clicked.disconnect()
        except: pass
        self.manage_stickerpack_widget.update_button.clicked.connect(update_pack)

        try: self.manage_stickerpack_widget.delete_button.clicked.disconnect()
        except: pass
        self.manage_stickerpack_widget.delete_button.clicked.connect(delete_question)

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
            self.load_stickers()

            def anim():
                self.menu_widget.move(430, 50)
                for i in range(76):
                    if i % 10 == 0:
                        self.menu_widget.move(430 + i, 50)
                        time.sleep(0.001)
                self.menu_widget.setVisible(False)

            anim_thread = threading.Thread(target=anim)
            anim_thread.start()
            self.menu_close(delay=.1)
            self.scroll.setVisible(True)
            self.widget.setVisible(True)
            self.settings.setVisible(True)
            self.loadStickersBtn.setVisible(True)
            self.closeBtn.clicked.disconnect()
            self.closeBtn.clicked.connect(self.close_window)

    def get_files(self, path):
        files = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                if f.split(".")[-1].lower() in ["jpg", "png", "webp"]:
                    files.append(f)
        sorted_files = sorted(files, key=lambda x: int(re.findall(r'\d+', x)[0]))
        return sorted_files

    def load_stickers(self):
        self.message.setObjectName("")
        try:
            with open(f"utils/{self.styleLocation}/style_main.css", "r") as style:
                self.message.setStyleSheet(str(style.read()))
                styleSheet = style
        except FileNotFoundError:
            pass
        if os.path.exists(self.path):
            br = False
            onlyfiles = self.get_files(self.path)
            if not onlyfiles:
                self.drop_error(f"No files found at {self.path}")
                return
            bar_value = 0
            if not self.stickersLoaded and len(self.path):
                self.message.setText("Loading, please wait...")
                self.progressbar()
                self.bar.setMaximum(100)
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
                self.bar.setMaximum(0)
                if self.path == "utils/favourites/":
                    self.animate_message("Favourites", None, False)
                elif os.path.exists(self.path+"/customname"):
                    with open(self.path+"/customname") as f:
                        self.animate_message(f.read())
                else:
                    self.animate_message("Path: " + self.path)
                self.scroll.verticalScrollBar().setValue(0)
            elif self.stickersLoaded:
                self.bar.hide()
                self.bar.setMaximum(0)
                self.unload_stickers()
                self.load_stickers()
                return
            elif not self.path:
                self.bar.hide()
                self.bar.setMaximum(0)
                self.drop_error("Invalid path!")

        else:
            with open("utils/lastpack", "w") as file:
                file.write("")
            self.bar.hide()
            self.bar.setMaximum(0)
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
stylesheet = distant_horizon
disable_updater = 0
update_url = https://api.github.com/repos/LoneHusko/Tele_py/releases/latest
ask_last_pack = 1""")
    else:
        print("Done!")
        print("Checking keys...", end="")
        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        config = config_object["SETTINGS"]
        keys = {"max_stickers_loadable" : "120",
                "copy_method": "dc" ,
                "columns": "4",
                "hides": "0",
                "stylesheet": "distant_horizon",
                "disable_updater": "0",
                "update_url": "https://api.github.com/repos/LoneHusko/Tele_py/releases/latest",
                "ask_last_pack": "1"}
        for i in keys.keys():
            if not config_object.has_option("SETTINGS", i):
                config[i] = keys[i]

                with open('utils/config.ini', 'w') as conf:
                    config_object.write(conf)

    print("Done!")
    print(f"Command-line args: {sys.argv}")
    print("Launching application...")
    title = "Debug prints below:"
    print(f"{title:_^60}")
    del title, keys, config_object, config
    app = QApplication(sys.argv)
    stickerWindow = Stickers()
    stickerWindow.show()
    app.exec_()