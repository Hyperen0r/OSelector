from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QPushButton, QLCDNumber, QLabel, QGroupBox)

def createButton(parent, text, function):
    button = QPushButton(text, parent)
    button.setFont(getNormalFont())
    button.setMinimumSize(button.minimumSizeHint())
    button.setStyleSheet(getButtonStyleSheet())
    button.clicked.connect(function)
    return button

def createGroupBox(text):
    groupBox = QGroupBox(text)
    groupBox.setFont(getTitleFont())
    groupBox.setAlignment(Qt.AlignHCenter)
    return groupBox

def createLCD(parent):
    lcd = QLCDNumber(parent)
    lcd.setSegmentStyle(2)
    return lcd

def createLabel(text):
    label = QLabel(text)
    label.setFont(getNormalFont())
    return label

def getTitleFont():
    return QFont("Bahnschrift", 13, QFont.Bold)

def getNormalFont():
    return QFont("Bahnschrift", 9, QFont.Normal)

def getButtonStyleSheet():
    return "padding: 10px"
