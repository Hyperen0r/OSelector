#!/usr/bin/python3
# -*- coding: utf-8 -*-

import configparser
import logging
# ----------------------------
# ---------- IMPORT ----------
# ----------------------------
import os
import sys
import xml.etree.ElementTree as ET

from enum import Enum
from data.Animation import Animation
from data.NamedContainer import NamedContainer
from widget.AnimTreeWidget import AnimTreeWidget
from widget.QuickyGui import *
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QMessageBox, QDesktopWidget,
                             QMainWindow, QFileDialog, QHBoxLayout, QVBoxLayout)

#TODO Remove comment from line containing an animation
#TODO Handle maxStringLength (hard coded)

class COLOR(Enum):
    NORMAL = Qt.black
    DUPLICATE = Qt.red

class OSelectorWindow(QMainWindow):

    def __init__(self, argv):
        super().__init__()

        self.setWindowTitle('OSelector - Generation Tool')
        self.setMinimumSize(QSize(1200, 1000))
        self.center()

        self.mainLayout = QVBoxLayout()
        self.centralWidget = QWidget(self)
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)

        self.initUI()
        self.initSettings(argv)

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def displayLCDAnimChecked(self):
        self.lcdAnimsChecked.display(self.treeAnimFiles.animationCount())

    def initUI(self):
        # ----- FIRST ROW : Scanning for animations files -----
        self.groupBoxScanning = createGroupBox("STEP I - Scan")
        self.buttonScan = createButton(self, "Scan for animations", self.scanFolder)
        labelAnimsFound = createLabel("Animations found : ")
        self.lcdAnimsFound = createLCD(self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonScan)
        hbox.addStretch(1)
        hbox.addWidget(labelAnimsFound)
        hbox.addWidget(self.lcdAnimsFound)

        self.groupBoxScanning.setLayout(hbox)
        self.mainLayout.addWidget(self.groupBoxScanning)

        # ----- SECOND ROW : List animations files -----
        self.groupBoxAnim = createGroupBox("STEP II - Select")
        self.treeAnimFiles = AnimTreeWidget()

        vbox = QVBoxLayout()
        vbox.addWidget(self.treeAnimFiles)

        hbox = QHBoxLayout()
        hbox.addWidget(createButton(self, "Check All", self.treeAnimFiles.checkAll))
        hbox.addWidget(createButton(self, "Uncheck All", self.treeAnimFiles.uncheckAll))
        hbox.addWidget(createButton(self, "Clean Up", self.treeAnimFiles.cleanup))

        vbox.addItem(hbox)

        self.groupBoxAnim.setLayout(vbox)
        self.mainLayout.addWidget(self.groupBoxAnim)

        # ----- THIRD ROW : Generate plugin -----
        self.groupBoxGenerate = createGroupBox("STEP III - Generate")
        self.buttonGenerate = createButton(self, "Generate Plugin", self.generatePlugin)
        labelAnimsChecked = createLabel("Animations checked : ")
        self.lcdAnimsChecked = createLCD(self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonGenerate)
        hbox.addStretch(1)
        hbox.addWidget(labelAnimsChecked)
        hbox.addWidget(self.lcdAnimsChecked)

        self.groupBoxGenerate.setLayout(hbox)
        self.mainLayout.addWidget(self.groupBoxGenerate)

    def initSettings(self, argv):
        self.path = argv[0].rsplit('/', 1)[0]

        self.config_path = self.path + "/ressources/config.cfg"
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        if self.config.get("LOG", "enabled"):
            logging.basicConfig(filename=self.config.get("LOG", "name"), level=logging.DEBUG, format='[%(levelname)s] : %(message)s')
        else:
            logger = logging.getLogger()
            logger.disabled = True

        if self.config.getboolean("CONFIG", "bFirstTime"):

            bUseMo = QMessageBox.question(self, 'Initialization', "Do you use MO ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if bUseMo == QMessageBox.Yes:
                QMessageBox.information(self, "Instuctions for MO users", "Next dialog window will ask you where your Mod Organiser mods/ folder is, thus allowing to install the plugin directly. You will still need to activate it in Mod Organizer left pane. If you don't see the mod, refresh the left pane.")
                self.config.set("CONFIG", "bUseMo", "True")
            else:
                QMessageBox.information(self, "Instuctions for Non-MO users", "Next dialog window will ask you to specify a folder location to store the plugin. In order to install it with a mod manager, compress the generated folder (Unless you specified skyrim/data folder")
                self.config.set("CONFIG", "bUseMo", "False")

            dir = QFileDialog.getExistingDirectory(self, 'Mod folder location', '', QFileDialog.ShowDirsOnly)

            if dir:
                self.config.set("PATHS", "ModFolder", str(dir))

            self.config.set("CONFIG", "bFirstTime", "False")

            # Save changes to ini file
            with open(self.config_path, 'w') as configFile:
                self.config.write(configFile)

    def scanFolder(self):

        self.groupBoxGenerate.setDisabled(True)
        self.groupBoxAnim.setDisabled(True)
        self.groupBoxScanning.setDisabled(True)

        scanDir = QFileDialog.getExistingDirectory(self, 'Mod folder location', self.config.get("PATHS", "ModFolder"), QFileDialog.ShowDirsOnly)

        packages = []
        previousPackage = ""
        animPackage = None
        counter = 0
        maxStringLength = self.config.get("PLUGIN", "maxstringlength")

        if scanDir:

            logging.info("=============== SCANNING ===============")
            logging.info("Scanning directory : " + scanDir)

            for root, dirs, files in os.walk(scanDir):
                for file in files:
                    if file.startswith("FNIS") and file.endswith("List.txt"):
                        animFile = os.path.join(root, file)
                        package = animFile.replace(scanDir + '\\', '').split('\\', 1)[0][:26]
                        module = animFile.replace(scanDir + '\\', '').rsplit('\\', 1)[1][5:-9][-25:]

                        if package != previousPackage:
                            if animPackage:
                                animPackage.items.sort(key=lambda x: x.name, reverse=False)
                            animPackage = NamedContainer(package)
                        animModule = NamedContainer(module)

                        logging.info("       Package : " + str(package))
                        logging.info("        Module : " + str(module))
                        logging.info("       Reading : " + animFile)

                        with open(animFile, 'r') as f:
                            anim = None
                            for line in f:
                                animType, animOptions, animId, animFile, animObj = Animation.parseLine(line)

                                logging.debug("        animType : " + animType.name + " || Line : " + line.strip())

                                name = animId.replace(package, "").replace(module, "").replace("_","")
                                if animType == Animation.TYPE.BASIC:
                                    anim = Animation(animType, animOptions, animId, animFile, animObj)
                                    animModule.addItem(anim)
                                    counter += 1
                                    logging.info("        Adding basic animation")

                                elif animType == Animation.TYPE.ANIM_OBJ:
                                    anim = Animation(animType, animOptions, animId, animFile, animObj)
                                    animModule.addItem(anim)
                                    counter += 1
                                    logging.info("        Adding anim obj animation")

                                elif animType == Animation.TYPE.SEQUENCE:
                                    anim = Animation(animType, animOptions, animId, animFile, animObj)
                                    animModule.addItem(anim)
                                    counter += 1
                                    logging.info("        Adding sequence animation")

                                elif animType == Animation.TYPE.ADDITIVE:
                                    anim.addStage(animId, animFile, animObj)
                                    counter += 1
                                    logging.info("            Adding stage")

                        animModule.items.sort(key=lambda x: x.name, reverse=False)

                        if animModule.items:
                            animPackage.addItem(animModule)
                            if package != previousPackage:
                                previousPackage = package
                                packages.append(animPackage)

        duplicate = self.treeAnimFiles.createFromPackages(packages)
        QMessageBox.information(self, "Results", str(duplicate) + " duplicates found (Not added)")
        self.treeAnimFiles.cleanup()
        self.treeAnimFiles.itemClicked.connect(self.displayLCDAnimChecked)
        self.lcdAnimsFound.display(counter)
        self.displayLCDAnimChecked()
        self.groupBoxGenerate.setDisabled(False)
        self.groupBoxAnim.setDisabled(False)
        self.groupBoxScanning.setDisabled(False)

    def generatePlugin(self):
        logging.info("=============== GENERATING PLUGIN ===============")

        pluginPath = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "Plugin")
        pluginInstallPath = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "installPlugin")

        self.create_dir(pluginPath)
        self.create_dir(pluginInstallPath)

        logging.info("Plugin destination : " + pluginPath)

        # File allowing the plugin to be recognized by OSA
        open(pluginInstallPath + "/" + self.config.get("PLUGIN", "osplug") + ".osplug", "w")

        XMLRoot = self.treeAnimFiles.toXML(self.config)

        with open(pluginPath + self.config.get("PLUGIN", "osplug") + ".myo", "w") as file:
            data = ET.tostring(XMLRoot, "unicode")
            file.write(data)

        QMessageBox.information(self, "Results", "Plugin Generation Done !\n ----- Plugin path -----\n" + pluginPath)

    @staticmethod
    def create_dir(path):
        # Prevent execution if the library already exists
        if os.path.exists(path):
            logging.info("Path already exists : " + path)
        else:
            logging.info("Creating new directory: " + path)
            os.makedirs(path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OSelectorWindow(sys.argv)
    sys.exit(app.exec_())
