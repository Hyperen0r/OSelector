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

from data.Animation import Animation
from data.NamedContainer import NamedContainer
from widget.AnimTreeWidget import AnimTreeWidget
from widget.AnimTreeItem import AnimTreeItem
from widget.QuickyGui import *
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QMessageBox, QDesktopWidget,
                             QMainWindow, QFileDialog, QHBoxLayout,
                             QVBoxLayout, QProgressBar)


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

        # ----- FOURTH ROW : Progress Bar -----
        self.progressBar = QProgressBar(self)
        self.mainLayout.addWidget(self.progressBar)

    def initSettings(self, argv):
        self.path = argv[0].rsplit('/', 1)[0]

        self.config_path = self.path + "/ressources/config.cfg"
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        if not self.config.get("LOG", "enabled"):
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

    def displayLCDAnimChecked(self):
        self.lcdAnimsChecked.display(self.treeAnimFiles.animationCount())

    def scanFolder(self):

        self.progressBar.setRange(0, 0)
        self.groupBoxGenerate.setDisabled(True)
        self.groupBoxAnim.setDisabled(True)
        self.groupBoxScanning.setDisabled(True)

        scanDir = QFileDialog.getExistingDirectory(self, 'Mod folder location', self.config.get("PATHS", "ModFolder"), QFileDialog.ShowDirsOnly)

        packages = []
        previousPackage = ""
        animPackage = None
        counter = 0

        if scanDir:

            logging.info("=============== SCANNING ===============")
            logging.info("Scanning directory : " + scanDir)

            for root, dirs, files in os.walk(scanDir):
                for file in files:
                    if file.startswith("FNIS") and file.endswith("List.txt"):
                        animFile = os.path.join(root, file)
                        package = animFile.replace(scanDir + '\\', '').split('\\', 1)[0]
                        module = animFile.replace(scanDir + '\\', '').rsplit('\\', 1)[1][5:-9]

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

        self.createTreeByMod(packages)
        self.treeAnimFiles.cleanup()
        self.treeAnimFiles.itemClicked.connect(self.displayLCDAnimChecked)
        self.lcdAnimsFound.display(counter)
        self.displayLCDAnimChecked()
        self.groupBoxGenerate.setDisabled(False)
        self.groupBoxAnim.setDisabled(False)
        self.groupBoxScanning.setDisabled(False)

    def createTreeByMod(self, packages):

        self.treeAnimFiles.clear()

        root = AnimTreeItem(self.treeAnimFiles)
        for package in packages:
            section = AnimTreeItem()
            section.setText(0, package.name)
            root.addChildWithSplitter(section)

            for module in package.items:
                moduleSection = AnimTreeItem()
                moduleSection.setText(0, module.name)
                section.addChildWithSplitter(moduleSection)

                previousAnimation = ""
                animSection = None
                counter = 1
                for animation in module.items:
                    if animation.name != previousAnimation or not animSection:
                        previousAnimation = animation.name
                        counter = 1
                        animSection = AnimTreeItem()
                        animSection.setText(0, animation.name)
                        moduleSection.addChildWithSplitter(animSection)

                    for i, stage in enumerate(animation.stages):
                        stageSection = AnimTreeItem()
                        stageSection.setAnimation(animation, i)
                        animSection.addChildWithSplitter(stageSection)
                        counter += 1

        invisibleRoot = self.treeAnimFiles.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.takeChild(0)
            invisibleRoot.addChild(child)
        invisibleRoot.removeChild(root)

        self.progressBar.setRange(0, 1)

    def generatePlugin(self):
        logging.info("=============== GENERATING PLUGIN ===============")

        pluginPath = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "Plugin") + "/"
        pluginInstallPath = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "installPlugin") + "/"

        self.create_dir(pluginPath)
        self.create_dir(pluginInstallPath)

        logging.info("Plugin destination : " + pluginPath)

        # File allowing the plugin to be recognized by OSA
        open(pluginInstallPath + "/" + self.config.get("PLUGIN", "osplug") + ".osplug", "w")

        """
        header = ET.Element("global")
        header.set("id", self.config.get("PLUGIN", "Name"))
        
        folderStyle = ET.Element("folderStyle")
        folderStyle.set("fc", "FFFFFF")
        folderStyle.set("h", "h_bigdot_op")
        folderStyle.set("th", "1.5")
        folderStyle.set("b", "")
        folderStyle.set("lc", "FFFFFF")
        folderStyle.set("h", "!")
        folderStyle.set("sh", "sq")
        folderStyle.set("sth", "3")
        folderStyle.set("sb", "000000")
        folderStyle.set("slc", "!")

        entryStyle = ET.Element("entryStyle")
        entryStyle.set("fc", "FFFFFF")
        entryStyle.set("h", "h_bigdot_op")
        entryStyle.set("th", "1.5")
        entryStyle.set("b", "")
        entryStyle.set("lc", "FFFFFF")
        entryStyle.set("h", "!")
        entryStyle.set("sh", "ci")
        entryStyle.set("sth", "3")
        entryStyle.set("sb", "e85670")
        entryStyle.set("slc", "FFFFFF")
        """

        XMLRoot = self.treeAnimFiles.toXML(self.config)

        with open(pluginPath + self.config.get("PLUGIN", "osplug") + ".myo", "w") as file:
            """
            data = ET.tostring(header, "unicode")
            file.write(data)
            data = ET.tostring(folderStyle, "unicode")
            file.write(data)
            data = ET.tostring(entryStyle, "unicode")
            file.write(data)
            """
            data = ET.tostring(XMLRoot, "unicode")
            file.write(data)
            print("Done !")

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
