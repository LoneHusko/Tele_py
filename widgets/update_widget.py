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

        self.release_notes_widget = releasenotes_widget.ReleaseNotesWidget(parent=self)
        self.release_notes_widget.move(40,22)

        self.confirm_update_widget = updateconfirm_widget.ConfirmUpdateWidget(parent=self)
        self.confirm_update_widget.move(40,125)

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

        self.read_release_notes_button = QPushButton("Read release notes")
        self.read_release_notes_button.setFixedSize(QSize(145, 30))
        self.read_release_notes_button.clicked.connect(self.read_notes)

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
        self.h_layout.addWidget(self.read_release_notes_button)
        self.read_release_notes_button.setVisible(False)
        self.v_layout.addWidget(self.update_button)


        self.setLayout(self.v_layout)

    def read_notes(self):
        self.release_notes_widget.setVisible(True)
        self.release_notes_widget.raise_()
        self.release_notes_widget.release_notes_label.setText(self.notes.replace("   -","⠀   -"))#Contains blank unicode
                                                                                                 #character


    def check_for_updates(self):
        self.message.setText("Gathering release information...")
        self.check_for_updates_button.setText("Please wait...")
        self.check_for_updates_button.clicked.disconnect()
        def thread():
            try:
                self.api_response = requests.get("https://api.github.com/repos/LoneHusko/Tele_py/releases/latest")
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
                self.check_for_updates_button.setFixedWidth(145)
                self.read_release_notes_button.setVisible(True)
            else:
                self.update_button.setEnabled(False)
                self.update_available = False


        x = Thread(target=thread)
        x.start()

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


            if not os.path.exists("_temp/commandfile.txt"):
                if os.path.exists("_temp"):
                    shutil.rmtree("_temp")
                self.update_button.clicked.connect(self.update_program)
                winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                self.update_button.setText("Update")
                self.message_error.setText("Update failed! (Missing command file)")
                self.message.setVisible(False)
                self.message_error.setVisible(True)
                self.bar.setVisible(False)
                self.bar.setMaximum(100)
                self.is_update_in_progress = False
                return
            self.update_button.setText("Checking the commandfile...")
            with open("_temp/commandfile.txt") as file:
                for i in file.readlines():
                    if "://" in i or r":\\" in i or "../" in i and "NOTIFIY" not in i:
                        self.update_button.clicked.connect(self.update_program)
                        winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                        self.update_button.setText("Update")
                        self.message_error.setText("Update refused!")
                        self.message.setVisible(False)
                        self.message_error.setVisible(True)
                        self.bar.setVisible(False)
                        self.bar.setMaximum(100)
                        self.is_update_in_progress = False
                        return
            self.update_button.setText("Updating...")
            permission_needed = False
            with open("_temp/commandfile.txt") as file:
                for i in file.readlines():
                    try:
                        command = i.split(" ")[0].strip()
                        if permission_needed:
                            winsound.PlaySound("utils/user_action_needed.wav", winsound.SND_ASYNC)

                            permission_needed = False
                            args = i.split(" ")
                            args.remove(command)
                            task = ""
                            if command == "NOTIFY":
                                task = "Display a notification"
                            elif command == "MKFILE":
                                task = f"Create a new file at \"{args[0].strip()}\""
                            elif command == "WFILE":
                                task = f"Modify a file's content at \"{args[0].strip()}\""
                            elif command == "MKDIR":
                                task = f"Create a new directory at \"{args[0].strip()}\""
                            elif command == "RFILE":
                                task = f"Replace \"{args[0].strip()}\" with \"{args[1].strip()}\""
                            elif command == "RMFILE":
                                task = f"Delete a file at \"{args[0].strip()}\""
                            elif command == "RMDIR":
                                task = f"Delete a directory at \"{args[0].strip()}\""

                            self.ask_perm_widget.setVisible(True)
                            self.ask_perm_widget.raise_()
                            self.ask_perm_widget.message_label.setText("User permission is required to perform the "
                                                                       f"following action as it is not "
                                                                       f"crutial for the update:\n\n{task}")
                            while True:
                                if self.ask_perm_widget.accepted or self.ask_perm_widget.denied:
                                    break
                                time.sleep(0.1)
                            self.ask_perm_widget.setVisible(False)
                            print("Accepted" if self.ask_perm_widget.accepted else "Denied")
                            if self.ask_perm_widget.accepted:
                                self.ask_perm_widget.accepted = False
                                pass
                            elif self.ask_perm_widget.denied:
                                self.ask_perm_widget.denied = False
                                continue

                        if command != "ASKPERM":
                            args = i.split(" ")
                            args.remove(command)
                        if command == "NOTIFY": #Notify the user and continue after closed
                            text = " ".join(args)
                            if self.isVisible():
                                winsound.PlaySound("utils/notify.wav", winsound.SND_ASYNC)
                                self.notify_widget.message_label.setText(text.strip()+"\n\nThe update will continue after you"
                                                                                      " closed this notification.")
                                self.notify_widget.setVisible(True)
                                self.notify_widget.raise_()
                                while self.notify_widget.isVisible():
                                    time.sleep(0.1)
                            continue
                        elif command == "ASKPERM": # Only execute the next line if permission is given
                            permission_needed = True
                            continue
                        elif command == "MKFILE": # Make a file
                            with open(args[0].strip(), f"w{args[1].strip() if args[1].strip() in 'tb' else ''}") as f:
                                f.write(args[2].strip() .replace("*", " ").replace("^", "\n")
                                        if args[1].strip() in 'tb'
                                        else args[1].strip().replace("*", " ").replace("^", "\n"))
                            continue
                        elif command == "WFILE": # (over)write a file
                            with open(args[0].strip(), f"{args[1].strip() if args[1].strip() in 'wa' else 'w'}") as f:
                                f.write(args[2].strip().replace("*", " ").replace("^", "\n")
                                        if args[1].strip() in 'wa'
                                        else args[1].strip().replace("*", " ").replace("^", "\n"))
                        elif command == "MKDIR": # Make a directory
                            os.mkdir(args[0].strip())
                            continue
                        elif command == "RFILE": # Replace a file (src, dst)
                            os.replace(args[0].strip(), args[1].strip())
                            continue
                        elif command == "RMFILE": # Delete a file
                            if os.path.exists(args[0].strip()):
                                os.remove(args[0].strip())
                            continue
                        elif command == "RMDIR": #Remove a directory
                            if os.path.exists(args[0].strip()):
                                shutil.rmtree(args[0].strip())
                            continue
                        elif command == "PRNTARGS": # Print arguments (debug only)
                            print(args)
                            continue
                    except Exception as error:
                        print(f"{error} {error.args}")
                        self.update_button.clicked.connect(self.update_program)
                        winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)
                        self.update_button.setText("Update")
                        self.message_error.setText("Failed to execute command! Update cancelled!")
                        self.message.setVisible(False)
                        self.message_error.setVisible(True)
                        self.bar.setVisible(False)
                        self.bar.setMaximum(100)
                        self.is_update_in_progress = False
                        return

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
        for i in self.api_response.json()["assets"]:
            if i["name"] == "update.zip":
                self.download = i["browser_download_url"]
                size = self.convert_size(i["size"])
                break
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

        self.confirm_update_widget.message_label.setText(f"A {size} sized package will be downloaded and extracted "
                                                         f"automatically. The download time depends on your "
                                                         f"internet connection speed but should be done under a few "
                                                         f"minutes.\n"
                                                         f"Please don't close the application untill asked to!\n"
                                                         "The application will still be usable during the update. "
                                                         "However the notifications will only be displayed if this page"
                                                         " is open. "
                                                         "You will hear a chime after the update is completed or if "
                                                         "user action is needed.\n"
                                                         f"Do you wish to continue?")
        self.confirm_update_widget.setVisible(True)
        self.confirm_update_widget.raise_()
        try:
            self.confirm_update_widget.accept_button.clicked.disconnect()
        except RuntimeError:
            pass
        try:
            self.confirm_update_widget.deny_button.clicked.disconnect()
        except RuntimeError:
            pass
        self.confirm_update_widget.accept_button.clicked.connect(lambda: update_thread.start())
        self.confirm_update_widget.accept_button.clicked.connect(lambda: self.confirm_update_widget.setVisible(False))
        self.confirm_update_widget.deny_button.clicked.connect(lambda: self.confirm_update_widget.setVisible(False))
