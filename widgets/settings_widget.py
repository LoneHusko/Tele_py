from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from configparser import ConfigParser
import os, sys


class SettingsWidget(QFrame):
    def __init__(self):
        super(SettingsWidget, self).__init__()

        self.setObjectName("menu")

        # Layout of Container Widget
        self.v_layout = QGridLayout(self)
        self.v_layout.setAlignment(Qt.AlignCenter)
        self.widget = QWidget()
        self.widget.setObjectName("no_bg_widget")
        self.widget.setLayout(self.v_layout)

        # Scroll Area Properties
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff )
        self.scroll.setObjectName("scroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(self.scroll)


        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        self.settings = config_object["SETTINGS"]
        self.style_sheet = self.settings["stylesheet"]

        self.applyStyleBtn = QPushButton("Apply stylesheet")
        self.applyStyleBtn.setFixedHeight(30)

        self.styleListBtn = QPushButton("Select stylesheet")
        self.build_style_dropdown()
        self.menu.setObjectName("style_menu")
        self.styleListBtn.setFixedHeight(30)

        self.settingsMessage = QLabel("Settings")
        self.settingsMessage.setFixedHeight(30)

        columnsGroup = QGroupBox("Columns")
        columnsLayout = QHBoxLayout()
        columnsGroup.setLayout(columnsLayout)
        self.columnsIn = QLineEdit()
        self.columnsIn.setValidator(QIntValidator())
        columnsLayout.addWidget(self.columnsIn)

        maxfileGroup = QGroupBox("Maximum readable stickers")
        maxLayout = QHBoxLayout()
        maxfileGroup.setLayout(maxLayout)
        self.maxFileIn = QLineEdit()
        maxLayout.addWidget(self.maxFileIn)
        self.maxFileIn.setPlaceholderText("Recommended is 120")
        self.maxFileIn.setValidator(QIntValidator())

        hidesGroup = QGroupBox("Close button action")
        hidesLayout = QHBoxLayout()
        hidesGroup.setLayout(hidesLayout)
        self.hideWindowBtn = QPushButton("Hide window")
        self.hideWindowBtn.setFixedHeight(30)
        self.hideWindowBtn.clicked.connect(self.hides_window)
        self.closeWindowBtn = QPushButton("Close application")
        self.closeWindowBtn.setFixedHeight(30)
        self.closeWindowBtn.clicked.connect(self.closes_window)
        hidesLayout.addWidget(self.hideWindowBtn)
        hidesLayout.addWidget(self.closeWindowBtn)

        if self.settings["hides"] == "1":
            self.hideWindowBtn.setObjectName("activeBtn")
        elif self.settings["hides"] == "0":
            self.closeWindowBtn.setObjectName("activeBtn")

        self.dcComp = QPushButton("Discord")
        self.dcComp.clicked.connect(self.dc_copy)
        self.dcComp.setFixedHeight(30)

        self.gimpComp = QPushButton("Gimp")
        self.gimpComp.setEnabled(False)
        self.gimpComp.clicked.connect(self.gimp_copy)
        self.gimpComp.setFixedHeight(30)

        self.clipcopy = QPushButton("ClipCopy")
        self.clipcopy.clicked.connect(self.cc_copy)
        self.clipcopy.setFixedHeight(30)

        if self.settings["copy_method"] == "dc":
            self.dcComp.setObjectName("activeBtn")
        elif self.settings["copy_method"] == "gimp":
            self.gimpComp.setObjectName("activeBtn")
        elif self.settings["copy_method"] == "cc":
            self.clipcopy.setObjectName("activeBtn")

        groupComp = QGroupBox("Compatibility mode")
        compLayout = QGridLayout()
        compLayout.addWidget(self.dcComp, 0, 0)
        compLayout.addWidget(self.gimpComp, 0, 1)
        compLayout.addWidget(self.clipcopy, 0, 2)
        groupComp.setLayout(compLayout)

        ask_pack_group = QGroupBox("Ask to load last pack")
        ask_pack_group.setLayout(QVBoxLayout())

        ask_pack = "Disabled"
        self.ask_last_pack = QPushButton()
        if self.settings["ask_last_pack"] == "1":
            ask_pack = "Enabled"
            self.ask_last_pack.setObjectName("activeBtn")
        self.ask_last_pack.setText(ask_pack)
        self.ask_last_pack.clicked.connect(self.ask_pack)
        ask_pack_group.layout().addWidget(self.ask_last_pack)

        self.ask_last_pack.setFixedHeight(30)

        self.updateBtn = QPushButton("Update")
        self.updateBtn.setFixedHeight(30)


        self.v_layout.addWidget(self.settingsMessage, 0, 0, 1, 2)
        self.v_layout.addWidget(columnsGroup,1,0)
        self.v_layout.addWidget(maxfileGroup, 1, 1)
        self.v_layout.addWidget(groupComp, 2, 0)
        self.v_layout.addWidget(hidesGroup, 2, 1)
        self.v_layout.addWidget(ask_pack_group, 3, 0)
        self.v_layout.addWidget(self.styleListBtn, 4, 0)
        self.v_layout.addWidget(self.applyStyleBtn, 4, 1)
        self.v_layout.addWidget(self.updateBtn, 5,0 ,1 ,2)

    def ask_pack(self):
        if self.ask_last_pack.objectName() == "activeBtn":
            self.ask_last_pack.setObjectName("")
            self.ask_last_pack.setText("Disabled")
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            settings["ask_last_pack"] = "0"

            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)
        else:
            self.ask_last_pack.setObjectName("activeBtn")
            self.ask_last_pack.setText("Enabled")
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            settings["ask_last_pack"] = "1"

            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)

    def change_style(self):
        self.style_sheet = self.stylesheets[QAction.sender(self)]

        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        settings = config_object["SETTINGS"]
        settings["stylesheet"] = self.style_sheet

        with open('utils/config.ini', 'w') as conf:
            config_object.write(conf)
        with open(f"utils/stylesheet/{self.style_sheet}/customname") as f:
            self.settingsMessage.setText(f"Press \"Apply stylesheet\" to apply style \"{f.read()}\"")

    def applied_style(self):
        self.build_style_dropdown()
        self.settingsMessage.setText("Settings")

    def build_style_dropdown(self):
        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        settings = config_object["SETTINGS"]
        self.menu = QMenu()
        self.menu.setObjectName("style_menu")
        self.stylesheets = {}
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
                    self.menu.addAction(action)
            else:
                self.menu.addAction("No stylesheets found").setEnabled(False)
        else:
            self.menu.addAction("No stylesheets found").setEnabled(False)
        self.menu.setObjectName("style_menu")
        self.styleListBtn.setMenu(self.menu)
        self.styleListBtn.menu()
        with open(f"utils/stylesheet/{self.style_sheet}/style_main.css") as f:
            self.menu.setStyleSheet(f.read())

    def save_line_edits(self):
        if self.maxFileIn.text():
            # Read config.ini file
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]

            # Update the value
            settings["max_stickers_loadable"] = self.maxFileIn.text()

            # Write changes back to file
            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)
        if self.columnsIn.text() and int(self.columnsIn.text()) != 0:
            # Read config.ini file
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]

            # Update the value
            settings["columns"] = self.columnsIn.text()

            # Write changes back to file
            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)

    def hides_window(self):
        self.hideWindowBtn.setObjectName("activeBtn")
        self.closeWindowBtn.setObjectName("")
        # Read config.ini file
        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        settings = config_object["SETTINGS"]

        # Update the value
        settings["hides"] = "1"

        # Write changes back to file
        with open('utils/config.ini', 'w') as conf:
            config_object.write(conf)

    def closes_window(self):
        self.hideWindowBtn.setObjectName("")
        self.closeWindowBtn.setObjectName("activeBtn")
        # Read config.ini file
        config_object = ConfigParser()
        config_object.read("utils/config.ini")
        settings = config_object["SETTINGS"]

        # Update the value
        settings["hides"] = "0"

        # Write changes back to file
        with open('utils/config.ini', 'w') as conf:
            config_object.write(conf)

    def cc_copy(self):
        if not self.clipcopy.objectName() == "activeBtn":
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            settings["copy_method"] = "cc"

            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)
            self.gimpComp.setObjectName("")
            self.dcComp.setObjectName("")
            self.clipcopy.setObjectName("activeBtn")

    def gimp_copy(self):
        if not self.gimpComp.objectName() == "activeBtn":
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            settings["copy_method"] = "gimp"

            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)
            self.gimpComp.setObjectName("activeBtn")
            self.dcComp.setObjectName("")
            self.clipcopy.setObjectName("")

    def dc_copy(self):
        if not self.dcComp.objectName() == "activeBtn":
            config_object = ConfigParser()
            config_object.read("utils/config.ini")
            settings = config_object["SETTINGS"]
            settings["copy_method"] = "dc"

            with open('utils/config.ini', 'w') as conf:
                config_object.write(conf)
            self.dcComp.setObjectName("activeBtn")
            self.gimpComp.setObjectName("")
            self.clipcopy.setObjectName("")
