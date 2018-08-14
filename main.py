#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ----------------------------
# ---------- IMPORT ----------
# ----------------------------
import os
import re
import sys
import logging
import configparser


import xml.etree.ElementTree as ET

from enum               import Enum
from PyQt5.QtWidgets    import (QApplication, QWidget, QToolTip,
                                QPushButton, QMessageBox, QDesktopWidget,
                                QMainWindow, QFileDialog, QHBoxLayout,
                                QVBoxLayout, QLCDNumber, QLabel, QListWidget,
                                QTreeWidget, QTreeWidgetItem)
from PyQt5.QtGui        import QIcon, QFont, QBrush, QColor
from PyQt5.QtCore       import QSize, Qt

# -----------------------------
# ----------  CLASSES----------
# -----------------------------
class ANIM_TYPE(Enum):
    BASIC       = "^(b)"
    ANIM_OBJ    = "^(fu|fuo)"
    SEQUENCE    = "^(s|so)"
    ADDITIVE    = "^(\+)"
    OFFSET      = "^(ofa)"
    PAIRED      = "^(pa)"
    KILLMOVE    = "^(km)"
    UNKNOWN     = ""


class ANIM_OPTION(Enum):
    ACYCLIC         = "(?:,|-)a"
    ANIM_OBJ        = "(?:,|-)o"
    TRANSITION      = "(?:,|-)Tn"
    HEAD_TRACKING   = "(?:,|-)h"
    BLEND_TIME      = "(?:,|-)(B\d*\.\d*)"
    KNOWN           = "(?:,|-)k"
    BSA             = "(?:,|-)bsa"
    STICKY_AO       = "(?:,|-)st"
    DURATION        = '(?:,|-)(D\d*\.\d*)'
    TRIGGER         = "(?:,|-)(T[^\/]*\/\d*\.\d*)"
    UNKNOWN         = ""


class Animation():

    def __init__(self, type, options, animId, animFile, animObj):
        self.stages         = []
        self.stages_file    = []
        self.stages_obj     = []

        self.type = type
        self.options = options
        self.stages.append([animId])
        self.stages_file.append([animFile])
        self.stages_obj.append([animObj])

        self.name = self.stages[0][0].rsplit("_", 2)[0]


    def addStage(self, animId, animFile, animObj):
        self.stages[0].append(animId)
        self.stages_file[0].append(animFile)
        self.stages_obj[0].append(animObj)


    @staticmethod
    def parseLine(line):
        # See FNIS_FNISBase_List.txt for more information (in FNIS  Behavior <Version>/Meshes/Character/animations/FNISBase
        regexp  = re.compile(r"^(\S*)(?: -(\S*))? (\S*) (\S*)((?:\s(?:\S*))*)")
        found   = regexp.search(line)
        if found:
            type        = found.group(1)    # Single word (s + b ...)
            options     = found.group(2)    # o,a,Tn,B.2, ...
            animId      = found.group(3)    # ANIM_ID_ ...
            animFile    = found.group(4)    # <path/to/file>.hkx
            animObj     = found.group(5)    # Chair Ball ...
            return Animation.getAnimTypeFromString(type), Animation.getOptionsFromString(options), animId, animFile, animObj
        return ANIM_TYPE.UNKNOWN, [], "", "", ""


    @staticmethod
    def getAnimTypeFromString(string):
        for animType in ANIM_TYPE:
            regexp  = re.compile(animType.value)
            found   = regexp.search(string)
            if found:
                return animType
        return ANIM_TYPE.UNKNOWN


    @staticmethod
    def getOptionsFromString(string):
        if string:
            options = []
            for animOptions in ANIM_OPTION:
                regexp  = re.compile(animOptions.value)
                found   = regexp.search(string)
                if found:
                    options.append( animOptions )
        return ANIM_OPTION.UNKNOWN


    def getBaseIdFromLine(self, line):
        baseId  = ""
        regexp  = re.compile(r"(\S*)_((?:a|A)\d_(?:s|S)\d)\b[^.]")
        found   = regexp.search(line)
        if found:
            baseId = found.group(1)
        return baseId

class AnimationModule():

    def __init__(self, name):
        self.name       = name
        self.animations = []

    def addAnimation(self, animation):
        self.animations.append(animation)


class AnimationPackage():

    def __init__(self, name):
        self.name       = name
        self.modules = []

    def addModule(self, module):
        self.modules.append(module)


class OSelectorWindow(QMainWindow):

    def __init__(self, argv):
        super().__init__()

        self.initUI()
        self.initSettings(argv)


    def initUI(self):
        self.setMinimumSize(QSize(900, 900))
        self.center()
        self.setWindowTitle('OSelector - Generation Tool')

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)

        # ----- FIRST ROW : Scanning for animations files -----
        self.buttonScan          = QPushButton("Scan for animations", self)
        self.buttonScan.setDefault(True)
        self.lcdAnimsFound  = QLCDNumber(self)

        self.buttonScan.resize(self.buttonScan.sizeHint())
        self.buttonScan.clicked.connect(self.scanFolder)

        labelAnimsFound = QLabel("Animations files found : ")

        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonScan)
        hbox.addStretch(1)
        hbox.addWidget(labelAnimsFound)
        hbox.addWidget(self.lcdAnimsFound)

        self.mainLayout.addItem(hbox)

        # ----- SECOND ROW : List animations files -----
        self.treeAnimFiles = QTreeWidget();
        self.treeAnimFiles.header().hide()

        self.mainLayout.addWidget(self.treeAnimFiles)

        # ----- THIRD ROW : Generate plugin -----
        self.buttonGenerate = QPushButton("Generate Plugin", self)
        self.buttonGenerate.clicked.connect(self.generatePlugin)

        self.mainLayout.addWidget(self.buttonGenerate)

        self.show()


    def initSettings(self, argv):
        self.path           = argv[0].rsplit('/', 1)[0]

        self.config_path    = self.path + "/config.cfg"
        self.config         = configparser.ConfigParser()
        self.config.read(self.config_path)

        logging.basicConfig(filename=self.config.get("LOG", "name"), level=logging.DEBUG, format='[%(levelname)s] : %(message)s')

        if self.config.getboolean("CONFIG", "bFirstTime"):

            bUseMo  = QMessageBox.question(self, 'Initialization', "Do you use MO ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            fname   = QFileDialog.getExistingDirectory(self, 'Mod folder location', '', QFileDialog.ShowDirsOnly)

            if fname:
                self.config.set("PATHS", "ModFolder", str(fname))

            if bUseMo == QMessageBox.Yes:
                self.config.set("CONFIG", "bUseMo", "True")
            else:
                self.config.set("CONFIG", "bUseMo", "False")

            self.config.set("CONFIG", "bFirstTime", "False")

            # Save changes to ini file
            with open(self.config_path, 'w') as configFile:
                self.config.write(configFile)


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def scanFolder(self):
        packages = []

        scanDir = QFileDialog.getExistingDirectory(self, 'Mod folder location', self.config.get("PATHS", "ModFolder"), QFileDialog.ShowDirsOnly)

        previousPackage = ""

        animPackage = None
        animModule = None

        if scanDir:

            logging.info("=============== SCANNING ===============")
            logging.info("Scanning directory : " + scanDir)

            for root, dirs, files in os.walk(scanDir):
                for file in files:
                    if file.startswith("FNIS") and file.endswith("List.txt"):
                        animFile    = os.path.join(root, file)
                        package     = animFile.replace(scanDir + '\\', '').split('\\',1)[0]
                        module      = animFile.replace(scanDir + '\\', '').rsplit('\\',1)[1][5:-9]

                        if package != previousPackage:
                            previousPackage = package
                            if animPackage != None:
                                animPackage.modules.sort(key=lambda x: x.name, reverse=False)
                            animPackage = AnimationPackage(package)
                            packages.append(animPackage)
                        animModule = AnimationModule(module)
                        animPackage.addModule(animModule)

                        logging.info("       Package : " + package)
                        logging.info("        Module : " + module)
                        logging.info("       Reading : " + animFile)

                        with open(animFile, 'r') as f:
                            anim = None
                            for line in f:
                                animType, animOptions, animId, animFile, animObj = Animation.parseLine(line)

                                logging.debug("        animType : " + animType.name + " || Line : " + line.strip())

                                if animType == ANIM_TYPE.BASIC:
                                    anim = Animation(animType, animOptions, animId, animFile, animObj)
                                    animModule.addAnimation(anim)
                                    logging.info("        Adding basic animation")

                                elif animType == ANIM_TYPE.SEQUENCE:
                                    anim = Animation(animType, animOptions, animId, animFile, animObj)
                                    animModule.addAnimation(anim)
                                    logging.info("        Adding sequence animation")

                                elif animType == ANIM_TYPE.ADDITIVE:
                                    anim.addStage(animId, animFile, animObj)
                                    logging.info("            Adding stage")

                        animModule.animations.sort(key=lambda x: x.name, reverse=False)

        self.createTreeByMod(packages)
        self.lcdAnimsFound.display(len(module))


    def createTreeByMod(self, packages):

        for package in packages:
            section = QTreeWidgetItem(self.treeAnimFiles)
            section.setText(0, package.name)
            section.setFlags(section.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            for module in package.modules:
                moduleSection = QTreeWidgetItem(section)
                moduleSection.setFlags(moduleSection.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                moduleSection.setText(0, module.name)
                moduleSection.setCheckState(0, Qt.Checked)

                previousAnimation = ""
                counter = 1
                for animation in module.animations:
                    if animation.name != previousAnimation:
                        counter = 1
                        previousAnimation = animation.name
                        animSection = QTreeWidgetItem(moduleSection)
                        animSection.setFlags(animSection.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                        animSection.setText(0, animation.name)
                        animSection.setCheckState(0, Qt.Checked)

                    for i, stage in enumerate(animation.stages[0]):
                        stageSection = QTreeWidgetItem(animSection)
                        stageSection.setFlags(stageSection.flags() | Qt.ItemIsUserCheckable)
                        stageSection.setText(0, "Stage " + str(counter))
                        stageSection.setText(1, animation.stages_file[0][i])
                        stageSection.setCheckState(0, Qt.Checked)
                        counter += 1

        root = self.treeAnimFiles.invisibleRootItem()

        # TODO Cleanup TreeView
        """
        for i in range(root.childCount()):
            package = root.child(i)

            for j in range(package.childCount()):
                module = package.child(j)
                if module.childCount() == 0:
                    module.disable()
        """


    def generatePlugin(self):
        logging.info("=============== GENERATING PLUGIN ===============")

        pluginPath          = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "Plugin") + "/"
        pluginInstallPath   = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "installPlugin") + "/"

        self.create_dir(pluginPath)
        self.create_dir(pluginInstallPath)

        logging.info("Plugin destination : " + pluginPath)

        # File allowing the plugin to be recognized by OSA
        file = open( pluginInstallPath + "/" + self.config.get("PLUGIN", "osplug") + ".osplug", "w")

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

        folder0 = ET.Element("folder0")
        folder0.set("n", self.config.get("PLUGIN", "name" ) )
        folder0.set("i", self.config.get("PLUGIN", "image") )

        previousSection     = ""
        previousAnim        = ""
        previousActor       = ""

        folder1 = None
        folder2 = None
        folder3 = None

        anims = self.getCheckedAnimsInfo()
        for animId, section, anim, actor, stage in anims:

            if previousSection != section:
                folder1 = ET.SubElement(folder0, "folder1")
                folder1.set("n", section)
                folder1.set("i", self.config.get("PLUGIN", "sectionLevelImage") )
                previousSection = section

            if previousAnim != anim:
                folder2 = ET.SubElement(folder1, "folder2")
                folder2.set("n", anim)
                folder2.set("i", self.config.get("PLUGIN", "animLevelImage") )
                previousAnim = anim

            if previousActor != actor:
                folder3 = ET.SubElement(folder2, "folder3")
                folder3.set("n", actor)
                folder3.set("i", self.config.get("PLUGIN", "actorLevelImage") )
                previousActor = actor

            entry = ET.SubElement(folder3, "entry")
            entry.set("n", stage)
            entry.set("id", animId)
            entry.set("i", self.config.get("PLUGIN", "stageLevelImage") )

        with open(pluginPath + self.config.get("PLUGIN", "osplug") + ".myo", "w") as file:
            """
            data = ET.tostring(header, "unicode")
            file.write(data)
            data = ET.tostring(folderStyle, "unicode")
            file.write(data)
            data = ET.tostring(entryStyle, "unicode")
            file.write(data)
            """
            data = ET.tostring(folder0, "unicode")
            file.write(data)
            print("Done !")


    def getCheckedAnimsInfo(self):

        checkedAnimsInfo  = []

        root = self.treeAnimFiles.invisibleRootItem()
        for i in range(root.childCount()):
            package = root.child(i)

            for j in range(package.childCount()):
                module = package.child(j)

                for k in range(module.childCount()):
                    anim = module.child(k)

                    for l in range(anim.childCount()):
                        stage = anim.child(l)

                        packageName = package.text(0)
                        moduleName  = module.text(0)
                        animName    = anim.text(0)
                        stageName   = stage.text(0)
                        animId      = stage.text(1)

                        animInfo    = (animId, packageName, moduleName, animName, stageName)
                        checkedAnimsInfo.append(animInfo)

        return checkedAnimsInfo

    def create_dir(self, path):
        # Prevent execution if the library already exists
        if (os.path.exists(path)):
            logging.info("Path already exists : " + path)
        else:
            logging.info("Creating new directory: " + path)
            os.makedirs(path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OSelectorWindow(sys.argv)
    sys.exit(app.exec_())
