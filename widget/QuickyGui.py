from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QPushButton, QLCDNumber, QLabel, QGroupBox, QMessageBox)


def create_button(parent, text, fun):
    button = QPushButton(text, parent)
    button.setFont(get_normal_font())
    button.setMinimumSize(button.minimumSizeHint())
    button.setStyleSheet("padding : 10px")
    button.clicked.connect(fun)
    return button


def create_group_box(self, text):
    group_box = QGroupBox(text, self)
    group_box.setFont(get_title_font())
    group_box.setAlignment(Qt.AlignHCenter)
    group_box.setMinimumWidth(400)
    return group_box


def create_lcd(parent):
    lcd = QLCDNumber(parent)
    lcd.setSegmentStyle(2)
    return lcd


def create_label(self, text):
    label = QLabel(text, self)
    label.setFont(get_normal_font())
    return label


def question(widget, title, text):
    return QMessageBox.question(widget, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


def get_title_font():
    return QFont("Bahnschrift", 13, QFont.Bold)


def get_normal_font():
    return QFont("Bahnschrift", 9, QFont.Normal)