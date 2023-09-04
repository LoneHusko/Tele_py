from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import os, winsound, threading, shutil

class DownloadWidget(QFrame):
    def __init__(self):
        super(DownloadWidget, self).__init__()
        self.setObjectName("menu")
        self.downloader = None
        self.menu_dropdown_update_func = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        dlayout = QVBoxLayout()
        dlayout.setAlignment(Qt.AlignCenter)

        self.message_label = QLabel()
        self.message_label.setFixedSize(QSize(300, 30))
        self.message_label.setAlignment(Qt.AlignCenter)

        self.message_succes = QLabel()
        self.message_succes.setFixedSize(QSize(300, 30))
        self.message_succes.setObjectName("success")
        self.message_succes.setAlignment(Qt.AlignCenter)

        self.message_error = QLabel()
        self.message_error.setObjectName("error")
        self.message_error.setFixedSize(QSize(300, 30))
        self.message_error.setAlignment(Qt.AlignCenter)

        self.message_error.setVisible(False)
        self.message_succes.setVisible(False)

        self.botToken = QLineEdit()
        self.botToken.returnPressed.connect(self.download)
        self.botToken.setFixedWidth(300)
        self.botToken.setEchoMode(QLineEdit.Password)
        self.botToken.setPlaceholderText("Token")

        try:
            with open("utils/bottoken", "r") as token:
                _ = token.read()
                self.botToken.setText(_.strip())
        except:
            pass

        self.customName = QLineEdit()
        self.customName.returnPressed.connect(self.download)
        self.customName.setPlaceholderText("Custom name for the pack (leave blank for default)")
        self.customName.setFixedWidth(300)

        self.stickerURL = QLineEdit()
        self.stickerURL.setFocus()
        self.stickerURL.textChanged.connect(self.check_packs)
        self.stickerURL.returnPressed.connect(self.download)
        self.stickerURL.setPlaceholderText("Sticker URL")
        self.stickerURL.setFixedWidth(300)

        self.downloadButton = QPushButton("Download")
        self.downloadButton.setFixedWidth(300)
        self.downloadButton.clicked.connect(self.download)
        self.downloadButton.setFixedHeight(30)

        dlayout.addWidget(self.message_label)
        dlayout.addWidget(self.message_succes)
        dlayout.addWidget(self.message_error)
        dlayout.addWidget(self.stickerURL)
        dlayout.addWidget(self.customName)
        dlayout.addWidget(self.botToken)
        dlayout.addWidget(self.downloadButton)
        self.setLayout(dlayout)

        self.stickerURL.setFocus()


    def message(self, text):
        self.message_error.setVisible(False)
        self.message_succes.setVisible(False)
        self.message_label.setVisible(True)
        self.message_label.setText(text)

    def succes(self, text):
        self.message_error.setVisible(False)
        self.message_label.setVisible(False)
        self.message_succes.setVisible(True)
        self.message_succes.setText(text)

    def error(self,text):
        self.message_label.setVisible(False)
        self.message_succes.setVisible(False)
        self.message_error.setVisible(True)
        self.message_error.setText(text)

    def progressbar(self):
        self.bar = QProgressBar(parent=self)
        self.bar.setMinimum(0)
        self.bar.setMaximum(100)
        self.bar.setFixedHeight(30)
        self.bar.setFixedWidth(300)
        bar_x = (self.width() - self.bar.width()) / 2
        bar_y = self.height() - self.bar.height()

        # Set the position of the progress bar
        self.bar.move(bar_x, bar_y)
        self.bar.show()

    def check_packs(self):
        if os.path.exists(f"downloads/{self.stickerURL.text()}") and self.stickerURL.text() != "":
            self.message_label.setObjectName("")
            self.downloadButton.setText("Update")
            self.message_label.setText("Stickerpack is already downloaded, but can be updated")
        else:
            self.message_label.setObjectName("")
            self.downloadButton.setText("Download")
            self.message_label.setText("")

    def download(self):

        def thread():
            failed = False
            with open("utils/bottoken", "w") as token:
                token.write(self.botToken.text())
            try:
                self.message_label.setObjectName("")
                self.message_label.setText("Preparing for download...")

                sticker_downloader = self.downloader.StickerDownloader(self.botToken.text())

                name = self.stickerURL.text()
                if name != "":

                    if os.path.exists(f"downloads/{name}"):
                        shutil.rmtree(f"downloads/{name}")

                    self.message("Getting pack info...")
                    name = (name.split('/')[-1])

                    print('=' * 60)
                    pack = sticker_downloader.get_sticker_set(name)

                    print('-' * 60)
                    self.message("Downloading files...")
                    sticker_downloader.download_sticker_set(pack)
                    self.message("Writing customname file...")
                    if self.customName.text():
                        with open(f"downloads/{name}/customname", "wt") as f:
                            f.write(customName.text())
                    else:
                        with open(f"downloads/{name}/customname", "wt") as f:
                            f.write(pack["title"])
                    self.bar.hide()
                    self.succes("Download completed!")
                    winsound.PlaySound("utils/success.wav", winsound.SND_ASYNC)
                    self.menu_dropdown_update_func()
                else:
                    self.bar.hide()
                    self.error("Invalid URL!")
                    winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)

            except Exception as exception:
                print(exception)
                self.message_label.setObjectName("error")
                self.bar.hide()
                self.error("Download failed! Please check the token and the URL!")
                winsound.PlaySound("utils/error.wav", winsound.SND_ASYNC)

        x = threading.Thread(target=thread)

        self.progressbar()
        self.bar.setMaximum(0)

        x.start()
