import threading
import time

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import urllib.request, os, sys, shutil, subprocess, winsound, requests, math
from configparser import ConfigParser
from threading import Thread
from markdown import markdown
from . import releasenotes_widget, updateconfirm_widget, notify_widget, askperm_widget
from zipfile import ZipFile


class UpdateWidget(QFrame):
    def __init__(self, VERSION: str):
        super(UpdateWidget, self).__init__()

        self.release_notes_widget = releasenotes_widget.ReleaseNotesWidget()
        self.release_notes_widget.move(40,22)
        self.release_notes_widget.scroll.verticalScrollBar().valueChanged.connect(self.check_scroll_value)

        self.confirm_update_widget = updateconfirm_widget.ConfirmUpdateWidget(self.release_notes_widget, parent=self)

        self.notify_widget = notify_widget.NotifyWidget(parent=self)
        self.notify_widget.move(40,125)

        self.ask_perm_widget = askperm_widget.AskPermWidget(parent=self)
        self.ask_perm_widget.move(40,125)

        self.bar = QProgressBar()
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)
        self.bar.setFixedHeight(30)
        self.bar.setFixedWidth(300)
        self.bar.setObjectName("update")

        self.setObjectName("menu")

        self.update_available = False
        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        settings = config_object["SETTINGS"]
        url = settings["update_url"]

        self.is_update_in_progress = False
        self.should_restart = False

        self.update_url = url

        self.current_version = VERSION
        self.latest_version = "Not checked yet"

        self.message = QLabel()
        self.message_succes = QLabel()
        self.message_succes.setFixedSize(QSize(300, 30))
        self.message_succes.setObjectName("success")
        self.message_error = QLabel()
        self.message_error.setObjectName("error")
        self.message_error.setFixedSize(QSize(300, 30))
        self.message.setFixedSize(QSize(300, 30))

        self.current_version_label = QLabel(f"Current version: {self.current_version}")
        self.current_version_label.setFixedSize(QSize(300, 30))
        self.latest_version_label = QLabel(f"Latest version: {self.latest_version}")
        self.latest_version_label.setFixedSize(QSize(300, 30))

        self.update_button = QPushButton("Update")
        self.update_button.setFixedSize(QSize(300, 30))
        self.update_button.clicked.connect(self.update_program)

        self.check_for_updates_button = QPushButton("Check for updates")
        self.check_for_updates_button.setFixedSize(QSize(300, 30))
        self.check_for_updates_button.clicked.connect(self.check_for_updates)


        self.update_button.setEnabled(False)

        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()
        self.v_layout.setAlignment(Qt.AlignCenter)
        self.v_layout.addWidget(self.message)
        self.v_layout.addWidget(self.message_succes)
        self.message_succes.setVisible(False)
        self.v_layout.addWidget(self.message_error)
        self.message_error.setVisible(False)
        self.v_layout.addWidget(self.bar)
        self.bar.setVisible(False)
        self.v_layout.addWidget(self.current_version_label)
        self.v_layout.addWidget(self.latest_version_label)
        self.v_layout.addLayout(self.h_layout)
        self.h_layout.addWidget(self.check_for_updates_button)
        self.v_layout.addWidget(self.update_button)


        self.setLayout(self.v_layout)

    def check_scroll_value(self):
        if self.release_notes_widget.scroll.verticalScrollBar().maximum() == self.release_notes_widget.scroll.verticalScrollBar().value():
            self.confirm_update_widget.accept_button.setEnabled(True)
            self.confirm_update_widget.accept_button.setToolTip("")
        else:
            self.confirm_update_widget.accept_button.setEnabled(False)
            self.confirm_update_widget.accept_button.setToolTip("Please read the release notes first")

    def read_notes(self):
        self.release_notes_widget.setVisible(True)
        self.release_notes_widget.release_notes_label.setText(
                                                              self.notes.replace('   -', '⠀   -')
        )#Contains blank unicode character


    def check_for_updates(self, no_thread = False):
        self.message.setText("Gathering release information...")
        self.check_for_updates_button.setText("Please wait...")
        self.check_for_updates_button.clicked.disconnect()
        def thread():
            try:
                self.api_response = requests.get(self.update_url)
                self.notes = markdown(self.api_response.json()["body"])
                self.notes = self.notes.replace("\n", "<br>")
            except:
                self.message.setText("")
                self.message_error.setText("Failed to reach the server! Please try again later!")
                winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                self.check_for_updates_button.setText("Check for updates")
                self.message.setVisible(False)
                self.message_error.setVisible(True)
                self.check_for_updates_button.clicked.connect(self.check_for_updates)
                return
            self.message.setText("")
            self.latest_version = self.api_response.json()["tag_name"]
            self.latest_version_label.setText(f"Latest version: {self.latest_version}")
            self.check_for_updates_button.setText("Check for updates")
            self.check_for_updates_button.clicked.connect(self.check_for_updates)
            if self.latest_version != self.current_version:
                self.update_button.setEnabled(True)
                self.update_available = True
            else:
                self.update_button.setEnabled(False)
                self.update_available = False

        if not no_thread:
            x = Thread(target=thread)
            x.start()
        else:
            thread()

    def download_file(self,url, download_dir="_temp"):
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        response = urllib.request.urlopen(url)
        data = response.read()
        with open(download_dir+"/"+url.split("/")[-1], "wb") as f:
            f.write(data)

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def update_program(self):
        def thread():
            self.is_update_in_progress = True
            self.bar.setMaximum(0)
            self.bar.setVisible(True)
            self.message.setVisible(False)
            self.message_error.setVisible(False)
            self.update_button.clicked.disconnect(self.update_program)
            self.update_button.setText("Downloading...")

            try:
                self.download_file(self.download)
            except:
                self.update_button.clicked.connect(self.update_program)
                winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                self.update_button.setText("Update")
                self.message_error.setText("Failed to download! Please try again later!")
                self.message.setVisible(False)
                self.message_error.setVisible(True)
                self.bar.setVisible(False)
                self.bar.setMaximum(100)
                self.is_update_in_progress = False
                return

            self.update_button.setText("Extracing package...")
            with ZipFile(f'_temp/{self.download.split("/")[-1]}') as zObject:
                zObject.extractall(path="_temp")

            root_dir = "_temp"
            file_list = []

            self.update_button.setText("Reading files...")

            root_dir = "_temp"
            files = []

            self.update_button.setText("Reading files...")

            for root, dirs, _files in os.walk(root_dir):
                for fileName in _files:
                    # Use '/' as the directory separator
                    file_path = os.path.join(root, fileName).replace("\\", "/")
                    # Remove the leading "_temp/" from the file_path
                    file_path = file_path.replace(root_dir + "/", "")
                    files.append(file_path)

            # Filter out files with ".zip" in their names
            file_list = []
            for i in files:
                print(i)
                if ".zip" not in i and i != "tele-py.exe":
                    file_list.append(i)

            print(list(file_list))

            self.update_button.setText("Moving files...")

            source_dir = "_temp"
            target_dir = ""

            for i in file_list:
                source_path = os.path.join(source_dir, i)  # Construct the source path
                target_path = os.path.join(target_dir, i)  # Construct the target path

                if os.path.exists(source_path):
                    try:
                        # Move the file to the target directory
                        shutil.move(source_path, target_path)
                        print(f"Moved {source_path} to {target_path}")
                    except Exception as error:
                        print(f"{error} {error.args}")
                        self.update_button.clicked.connect(self.update_program)
                        winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                        self.update_button.setText("Update")
                        self.message_error.setText("Failed to move file! Update cancelled!")
                        self.message.setVisible(False)
                        self.message_error.setVisible(True)
                        self.bar.setVisible(False)
                        self.bar.setMaximum(100)
                        self.is_update_in_progress = False
                        return
                else:
                    try:
                        print(f"{source_path} not found, creating directory and moving...")
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        shutil.move(os.path.join(source_dir, i), target_path)
                        print(f"Moved {source_path} to {target_path}")
                    except Exception as error:
                        print(f"{error} {error.args}")
                        self.update_button.clicked.connect(self.update_program)
                        winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                        self.update_button.setText("Update")
                        self.message_error.setText("Failed to move file! Update cancelled!")
                        self.message.setVisible(False)
                        self.message_error.setVisible(True)
                        self.bar.setVisible(False)
                        self.bar.setMaximum(100)
                        self.is_update_in_progress = False
                        return

            self.update_button.setText("Updating...")
            os.replace("_temp/tele-py.exe","tempfile.exe")
            os.replace("tele-py.exe", "tele-py-old.exe")
            os.replace("tempfile.exe", "tele-py.exe")


            shutil.rmtree("_temp")
            winsound.PlaySound("utils/success.wav", winsound.SND_ASYNC)
            self.update_button.setText("Done!")
            self.message_succes.setText("Please restart the application!")
            self.message.setVisible(False)
            self.message_succes.setVisible(True)
            self.bar.setMaximum(100)
            self.bar.setVisible(False)
            self.should_restart = True
            self.is_update_in_progress = False
        update_thread = Thread(target=thread)
        self.download = False
        self.download = self.api_response.json()["assets"][0]["browser_download_url"]
        size = self.convert_size(self.api_response.json()["assets"][0]["size"])
        if self.download:
            print(self.download)
        else:
            self.update_button.clicked.connect(self.update_program)
            winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
            self.update_button.setText("Update")
            self.message_error.setText("Update failed! Please try again later! (Missing file)")
            self.message.setVisible(False)
            self.message_error.setVisible(True)
            self.bar.setVisible(False)
            self.bar.setMaximum(100)
            self.is_update_in_progress = False
            return
        print(size)

        self.read_notes()
        self.release_notes_widget.release_notes_label.setText(self.release_notes_widget.release_notes_label.text() +
                                                      "<p><hr>"
                                                      f"A {size} sized package will be downloaded and extracted "
                                                      f"automatically. The download time depends on your "
                                                      f"internet connection speed but should be done under a few "
                                                      f"minutes.<br>"
                                                      f"Please don't close the application untill asked to!<br>"
                                                      "The application will still be usable during the update. "
                                                      "However the notifications will only be displayed if this page"
                                                      " is open. "
                                                      "You will hear a chime after the update is completed or if "
                                                      "user action is needed.<br>"
                                                      f"Do you wish to continue?</p>")
        self.confirm_update_widget.setVisible(True)
        self.confirm_update_widget.raise_()
        try:
            self.confirm_update_widget.accept_button.clicked.disconnect()
        except RuntimeError:
            pass
        self.check_scroll_value()
        self.confirm_update_widget.accept_button.clicked.connect(lambda: update_thread.start())
        self.confirm_update_widget.accept_button.clicked.connect(lambda: self.confirm_update_widget.setVisible(False))
