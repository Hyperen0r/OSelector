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

    def displayLCDAnimChecked(self):
        self.lcdAnimsChecked.display(len(self.getCheckedAnimsInfo()))

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
            self.treeAnimFiles.repaint()

        invisibleRoot = self.treeAnimFiles.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.takeChild(0)
            invisibleRoot.addChild(child)
        invisibleRoot.removeChild(root)

        self.treeAnimFiles.cleanup()
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

        root = ET.Element("folder0")
        root.set("n", self.config.get("PLUGIN", "name"))
        root.set("i", self.config.get("PLUGIN", "image"))

        previousPackage = ""
        previousModule = ""
        previousAnim = ""

        maxItemPerSection = self.config.getint("PLUGIN", "maxItemPerSection")
        animations = self.getCheckedAnimsInfo()

        packageFolder = None
        packageSetFolder = None
        moduleFolder = None
        moduleSetFolder = None
        animFolder = None
        animSetFolder = None
        stageSetFolder = None

        packageCounter = 0
        packageSetCounter = 0
        packageFolderOffset = 0
        moduleCounter = 0
        moduleSetCounter = 0
        moduleFolderOffset = 0
        animCounter = 0
        animSetCounter = 0
        animFolderOffset = 0
        stageCounter = 0
        stageSetCounter = 0
        minusOffset = 0

        for animId, package, module, anim, stage in animations:

            # ===== PACKAGE =====
            nbPackages = self.getNumberOfCheckedPackage()
            nbOfPackageSets = nbPackages / maxItemPerSection

            if nbOfPackageSets > 1:
                packageFolderOffset = 1

                if packageCounter >= maxItemPerSection or packageSetCounter == 0:
                    packageSetCounter += 1
                    packageCounter = 0

                    packageSetFolder = ET.SubElement(root, "folder1")
                    packageSetFolder.set("n", "Package Set " + str(packageSetCounter))
                    packageSetFolder.set("i", self.config.get("PLUGIN", "setFolderImage"))

            if package != previousPackage:
                moduleCounter = 0
                moduleSetCounter = 0
                moduleFolderOffset = 0
                animCounter = 0
                animSetCounter = 0
                animFolderOffset = 0
                stageCounter = 0
                stageSetCounter = 0

                if nbOfPackageSets > 1:
                    packageFolder = ET.SubElement(packageSetFolder, "folder" + str(1 + packageFolderOffset))
                else:
                    packageFolder = ET.SubElement(root, "folder" + str(1 + packageFolderOffset))

                packageFolder.set("n", package)
                packageFolder.set("i", self.config.get("PLUGIN", "packageFolderImage"))
                packageCounter += 1
                previousPackage = package

            # ===== MODULE =====
            nbModules = self.getNumberOfCheckedModuleFromPackage(package)
            nbOfModuleSets = nbModules / maxItemPerSection

            if nbOfModuleSets > 1:
                moduleFolderOffset = 1

                if moduleCounter >= maxItemPerSection or moduleSetCounter == 0:
                    moduleSetCounter += 1
                    moduleCounter = 0

                    moduleSetFolder = ET.SubElement(packageFolder, "folder" + str(2 + packageFolderOffset))
                    moduleSetFolder.set("n", "Module Set " + str(moduleSetCounter))
                    moduleSetFolder.set("i", self.config.get("PLUGIN", "setFolderImage"))

            if module != previousModule:
                animCounter = 0
                animSetCounter = 0
                animFolderOffset = 0
                stageCounter = 0
                stageSetCounter = 0

                if nbOfModuleSets > 1:
                    moduleFolder = ET.SubElement(moduleSetFolder,
                                                 "folder" + str(2 + packageFolderOffset + moduleFolderOffset))
                else:
                    moduleFolder = ET.SubElement(packageFolder,
                                                 "folder" + str(2 + packageFolderOffset + moduleFolderOffset))

                moduleFolder.set("n", module)
                moduleFolder.set("i", self.config.get("PLUGIN", "moduleFolderImage"))
                moduleCounter += 1
                previousModule = module

            # ===== ANIM =====
            nbAnims = self.getNumberOfCheckedAnimFromModule(package, module)
            nbOfAnimSets = nbAnims / maxItemPerSection

            if nbOfAnimSets > 1:
                animFolderOffset = 1

                if animCounter >= maxItemPerSection or animSetCounter == 0:
                    animSetCounter += 1
                    animCounter = 0

                    animSetFolder = ET.SubElement(moduleFolder,
                                                  "folder" + str(3 + packageFolderOffset + moduleFolderOffset))
                    animSetFolder.set("n", "Anim Set " + str(animSetCounter))
                    animSetFolder.set("i", self.config.get("PLUGIN", "setFolderImage"))

            if anim != previousAnim:
                stageCounter = 0
                stageSetCounter = 0

                nbStages = self.getNumberOfCheckedStageFromAnim(package, module, anim)

                if nbStages > 1:
                    if nbOfAnimSets > 1:
                        animFolder = ET.SubElement(animSetFolder, "folder" + str(
                            3 + packageFolderOffset + moduleFolderOffset + animFolderOffset))
                    else:
                        animFolder = ET.SubElement(moduleFolder, "folder" + str(
                            3 + packageFolderOffset + moduleFolderOffset + animFolderOffset))

                    animFolder.set("n", anim)
                    animFolder.set("i", self.config.get("PLUGIN", "animFolderImage"))
                else:
                    minusOffset = 1

                animCounter += 1
                previousAnim = anim

            # ===== STAGE =====
            nbStages = self.getNumberOfCheckedStageFromAnim(package, module, anim)
            nbOfStageSets = nbStages / maxItemPerSection

            if nbOfStageSets > 1:
                if stageCounter >= maxItemPerSection or stageSetCounter == 0:
                    stageSetCounter += 1
                    stageCounter = 0

                    stageSetFolder = ET.SubElement(animFolder, "folder" + str(
                        4 + packageFolderOffset + moduleFolderOffset + animFolderOffset))
                    stageSetFolder.set("n", "Stage Set " + str(stageSetCounter))
                    stageSetFolder.set("i", self.config.get("PLUGIN", "setFolderImage"))

                entry = ET.SubElement(stageSetFolder, "entry")
                entry.set("n", stage)
            else:
                if minusOffset:
                    if animFolderOffset:
                        entry = ET.SubElement(animSetFolder, "entry")
                    else:
                        entry = ET.SubElement(moduleFolder, "entry")
                    minusOffset = 0
                    entry.set("n", animId)
                else:
                    entry = ET.SubElement(animFolder, "entry")
                    entry.set("n", stage)

            entry.set("i", self.config.get("PLUGIN", "stageFolderImage"))
            entry.set("id", animId)
            stageCounter += 1

        with open(pluginPath + self.config.get("PLUGIN", "osplug") + ".myo", "w") as file:
            """
            data = ET.tostring(header, "unicode")
            file.write(data)
            data = ET.tostring(folderStyle, "unicode")
            file.write(data)
            data = ET.tostring(entryStyle, "unicode")
            file.write(data)
            """
            data = ET.tostring(root, "unicode")
            file.write(data)
            print("Done !")

    def getNumberOfCheckedPackage(self):
        root = self.treeAnimFiles.invisibleRootItem()
        count = 0

        for i in range(root.childCount()):
            if root.child(i).checkState(0) != Qt.Unchecked:
                count += 1

        return count

    def getNumberOfCheckedModuleFromPackage(self, packageName):
        root = self.treeAnimFiles.invisibleRootItem()
        count = 0

        for i in range(root.childCount()):
            package = root.child(i)
            if package.text(0) == packageName:

                for j in range(package.childCount()):
                    if package.child(j).checkState(0) != Qt.Unchecked:
                        count += 1
        return count

    def getNumberOfCheckedAnimFromModule(self, packageName, moduleName):
        root = self.treeAnimFiles.invisibleRootItem()
        count = 0

        for i in range(root.childCount()):
            package = root.child(i)
            if package.text(0) == packageName:

                for j in range(package.childCount()):
                    module = package.child(j)
                    if module.text(0) == moduleName:

                        for k in range(module.childCount()):
                            if module.child(k).checkState(0) != Qt.Unchecked:
                                count += 1
        return count

    def getNumberOfCheckedStageFromAnim(self, packageName, moduleName, animName):
        root = self.treeAnimFiles.invisibleRootItem()
        count = 0

        for i in range(root.childCount()):
            package = root.child(i)
            if package.text(0) == packageName:

                for j in range(package.childCount()):
                    module = package.child(j)
                    if module.text(0) == moduleName:

                        for k in range(module.childCount()):
                            anim = module.child(k)
                            if anim.text(0) == animName:

                                for l in range(anim.childCount()):
                                    if anim.child(l).checkState(0) == Qt.Checked:
                                        count += 1
        return count

    def getCheckedAnimsInfo(self):

        checkedAnimsInfo = []

        root = self.treeAnimFiles.invisibleRootItem()
        for i in range(root.childCount()):
            package = root.child(i)
            if package.checkState(0) != Qt.Unchecked:

                for j in range(package.childCount()):
                    module = package.child(j)
                    if module.checkState(0) != Qt.Unchecked:

                        for k in range(module.childCount()):
                            anim = module.child(k)
                            if anim.checkState(0) != Qt.Unchecked:

                                for l in range(anim.childCount()):
                                    stage = anim.child(l)

                                    if stage.checkState(0) != Qt.Unchecked:
                                        packageName = package.text(AnimTreeWidget.COLUMN.NAME.value)
                                        moduleName = module.text(AnimTreeWidget.COLUMN.NAME.value)
                                        animName = anim.text(AnimTreeWidget.COLUMN.NAME.value)
                                        stageName = stage.text(AnimTreeWidget.COLUMN.NAME.value)
                                        animId = stage.text(AnimTreeWidget.COLUMN.ID.value)

                                        animInfo = (animId, packageName, moduleName, animName, stageName)
                                        checkedAnimsInfo.append(animInfo)
        return checkedAnimsInfo

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
