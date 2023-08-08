from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class ReleaseNotesWidget(QFrame):
    def __init__(self, parent=None):
        super(ReleaseNotesWidget, self).__init__(parent)
        self.setObjectName("menu")
        self.setVisible(False)
        self.setFixedSize(400,400)
        #480x444

        scroll_widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        scroll.setStyleSheet("border: none;")
        scroll_widget.setLayout(QVBoxLayout())

        self.release_notes_label = QLabel()
        self.release_notes_label.setWordWrap(True)
        scroll_widget.layout().addWidget(self.release_notes_label)
        close_button = QPushButton("Close")
        close_button.setFixedHeight(30)
        close_button.clicked.connect(lambda: self.setVisible(False))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)
        self.layout().addWidget(close_button)
        self.layout().setAlignment(Qt.AlignCenter)
