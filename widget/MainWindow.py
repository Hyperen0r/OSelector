#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QMainWindow, QDesktopWidget, QWidget, QVBoxLayout, QStyle)


class MainWindow(QMainWindow):

    def __init__(self, title):
        super().__init__()

        self.setWindowTitle(title)
        self.setMinimumSize(QSize(1200, 1000))
        self.center()

        self.mainLayout = QVBoxLayout()
        self.centralWidget = QWidget(self)
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        self.init_ui()

        self.show()

    def center(self):
        self.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.size(), QDesktopWidget().availableGeometry()))

    def init_ui(self):
        """ To implement in child """
        return