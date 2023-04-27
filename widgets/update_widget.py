from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import urllib.request, os, sys, shutil, subprocess, winsound
from configparser import ConfigParser
from threading import Thread


class UpdateWidget(QFrame):
    def __init__(self, VERSION: str):
        super(UpdateWidget, self).__init__()

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
        self.v_layout.addWidget(self.check_for_updates_button)
        self.v_layout.addWidget(self.update_button)


        self.setLayout(self.v_layout)


    def check_for_updates(self):
        self.check_for_updates_button.setText("Please wait...")
        self.check_for_updates_button.clicked.disconnect()
        def thread():
            try:
                self.download_file("latest_version.txt", self.update_url)
            except:
                self.message_error.setText("Failed to reach the server! Please try again later!")
                winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                self.check_for_updates_button.setText("Check for updates")
                self.message.setVisible(False)
                self.message_error.setVisible(True)
                self.check_for_updates_button.clicked.connect(self.check_for_updates)
                return
            with open("_temp/latest_version.txt", "r") as f:
                self.latest_version = f.read()
                self.latest_version_label.setText(f"Latest version: {self.latest_version}")
                self.check_for_updates_button.setText("Check for updates")
                self.check_for_updates_button.clicked.connect(self.check_for_updates)
                if self.latest_version != self.current_version:
                    self.update_button.setEnabled(True)
                    self.update_available = True
                else:
                    self.update_button.setEnabled(False)
                    self.update_available = False
        x = Thread(target=thread)
        x.start()

    def check_version(self):
        self.download_file("latest_version.txt", self.update_url)
        with open("_temp/latest_version.txt", "r") as f:
            return f.read()

    def download_file(self, filename, url, download_dir="_temp"):
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        response = urllib.request.urlopen(url+filename)
        data = response.read()
        with open(download_dir+"/"+filename, "wb") as f:
            f.write(data)

    def update_program(self):
        self.is_update_in_progress = True
        self.bar.setMaximum(0)
        self.bar.setVisible(True)
        self.message.setVisible(False)
        self.message_error.setVisible(False)
        self.update_button.clicked.disconnect(self.update_program)
        self.update_button.setText("Getting update information...")
        # Download list of updateable files from server
        def thread():
            try:
                self.download_file("updateable_files.txt", self.update_url)
            except:
                self.update_button.clicked.connect(self.update_program)
                winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                self.update_button.setText("Update")
                self.message_error.setText("Failed to reach the server! Please try again later!")
                self.message.setVisible(False)
                self.message_error.setVisible(True)
                self.bar.setVisible(False)
                self.bar.setMaximum(100)
                self.is_update_in_progress = False
                return

            # Load list of updateable files from TXT file
            with open("_temp/updateable_files.txt", "r") as f:
                updateable_files = f.read().split("\n")
            print("Updateable:", updateable_files)

            self.update_button.setText("Downloading files...")

            for i in updateable_files:
                print("Attempting to download:", i.split("/")[-1], end="")
                try:
                    self.download_file(i.split("/")[-1], self.update_url)
                    print(" Done!")
                except:
                    self.update_button.clicked.connect(self.update_program)
                    winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                    self.update_button.setText("Update")
                    self.message_error.setText(f"Failed to download files! Please try again later!")
                    self.message.setVisible(False)
                    self.message_error.setVisible(True)
                    self.bar.setVisible(False)
                    self.bar.setMaximum(100)
                    print("Failed!")
                    self.is_update_in_progress = False
                    return
            for i in updateable_files:
                if not os.path.exists("_temp/"+i.split("/")[-1]):
                    self.update_button.clicked.connect(self.update_program)
                    return
                shutil.copyfile("_temp/"+i.split("/")[-1], i)
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
        x = Thread(target=thread)
        x.start()