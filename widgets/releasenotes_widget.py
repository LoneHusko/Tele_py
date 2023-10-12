from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class ReleaseNotesWidget(QFrame):
    def __init__(self, parent=None):
        super(ReleaseNotesWidget, self).__init__(parent)
        self.setVisible(False)

        scroll_widget = QWidget()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(scroll_widget)
        self.scroll.setStyleSheet("border: none;")
        scroll_widget.setLayout(QVBoxLayout())

        self.release_notes_label = QLabel()
        self.release_notes_label.setWordWrap(True)
        scroll_widget.layout().addWidget(self.release_notes_label)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.scroll)
        self.layout().setAlignment(Qt.AlignCenter)
