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
                                QTreeWidget, QTreeWidgetItem, QProgressBar,
                                QGroupBox, QFontDialog, QHeaderView)
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


class TREE_VIEW_COLUMN(Enum):
    NAME        = 0
    TYPE        = 1
    OPTIONS     = 2
    ID          = 3
    FILE        = 4
    ANIM_OBJ    = 5


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
    lcd  = QLCDNumber(parent)
    lcd.setSegmentStyle(2)
    return lcd


def createLabel(text):
    label = QLabel("Animations found : ")
    label.setFont(getNormalFont())
    return label


def getTitleFont():
    return QFont("Bahnschrift", 13, QFont.Bold)


def getNormalFont():
    return QFont("Bahnschrift", 9, QFont.Normal)


def getButtonStyleSheet():
    return "padding: 10px"


class OSelectorWindow(QMainWindow):

    def __init__(self, argv):
        super().__init__()

        self.initUI()
        self.initSettings(argv)


    def initUI(self):
        self.setMinimumSize(QSize(1200, 1000))
        self.center()
        self.setWindowTitle('OSelector - Generation Tool')

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout()
        self.centralWidget.setLayout(self.mainLayout)

        # ----- FIRST ROW : Scanning for animations files -----
        self.groupBoxScanning   = createGroupBox("STEP I - Scan")
        self.buttonScan         = createButton(self, "Scan for animations", self.scanFolder)
        labelAnimsFound         = createLabel("Animations found : ")
        self.lcdAnimsFound      = createLCD(self)

        hbox = QHBoxLayout()
        hbox.addWidget(self.buttonScan)
        hbox.addStretch(1)
        hbox.addWidget(labelAnimsFound)
        hbox.addWidget(self.lcdAnimsFound)

        self.groupBoxScanning.setLayout(hbox)
        self.mainLayout.addWidget(self.groupBoxScanning)

        # ----- SECOND ROW : List animations files -----
        self.groupBoxAnim = createGroupBox("STEP II - Select")

        self.treeAnimFiles = QTreeWidget()
        self.treeAnimFiles.header().setDefaultAlignment(Qt.AlignHCenter)
        self.treeAnimFiles.header().setMinimumSectionSize(85)
        self.treeAnimFiles.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.treeAnimFiles.header().setFont(getNormalFont())
        self.treeAnimFiles.setHeaderLabels([TREE_VIEW_COLUMN.NAME.name, TREE_VIEW_COLUMN.TYPE.name, TREE_VIEW_COLUMN.OPTIONS.name, TREE_VIEW_COLUMN.ID.name, TREE_VIEW_COLUMN.FILE.name, TREE_VIEW_COLUMN.ANIM_OBJ.name])
        self.treeAnimFiles.setColumnWidth(TREE_VIEW_COLUMN.NAME.value, 400)
        self.treeAnimFiles.setColumnWidth(TREE_VIEW_COLUMN.TYPE.value, 100)
        self.treeAnimFiles.setColumnWidth(TREE_VIEW_COLUMN.ID.value, 200)
        self.treeAnimFiles.setSortingEnabled(True)
        self.treeAnimFiles.setAlternatingRowColors(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.treeAnimFiles)

        hbox = QHBoxLayout()
        hbox.addWidget(createButton(self, "Test", self.none))
        hbox.addWidget(createButton(self, "Test", self.none))
        hbox.addWidget(createButton(self, "Test", self.none))
        hbox.addWidget(createButton(self, "Test", self.none))
        hbox.addWidget(createButton(self, "Test", self.none))
        hbox.addWidget(createButton(self, "Test", self.none))

        vbox.addItem(hbox)

        self.groupBoxAnim.setLayout(vbox)
        self.mainLayout.addWidget(self.groupBoxAnim)

        # ----- THIRD ROW : Generate plugin -----
        self.groupBoxGenerate   = createGroupBox("STEP III - Generate")
        self.buttonGenerate     = createButton(self, "Generate Plugin", self.generatePlugin)
        labelAnimsChecked       = createLabel("Animations checked : ")
        self.lcdAnimsChecked    = createLCD(self)

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

        self.show()

    def none(self):
        print("debug")
        return

    def initSettings(self, argv):
        self.path           = argv[0].rsplit('/', 1)[0]

        self.config_path    = self.path + "/config.cfg"
        self.config         = configparser.ConfigParser()
        self.config.read(self.config_path)

        logging.basicConfig(filename=self.config.get("LOG", "name"), level=logging.DEBUG, format='[%(levelname)s] : %(message)s')
        logger = logging.getLogger()
        logger.disabled = self.config.getboolean("LOG", "disabled")

        if self.config.getboolean("CONFIG", "bFirstTime"):

            bUseMo  = QMessageBox.question(self, 'Initialization', "Do you use MO ?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if bUseMo == QMessageBox.Yes:
                self.config.set("CONFIG", "bUseMo", "True")
                QMessageBox.information(self, "Instuctions for MO users", "Next dialog window will ask you where your Mod Organiser mods/ folder is, thus allowing to install the plugin directly. You will still need to activate it in Mod Organizer left pane. If you don't see the mod, refresh the left pane.")
            else:
                QMessageBox.information(self, "Instuctions for Non-MO users", "Next dialog window will ask you to specify a folder location to store the plugin. In order to install it with a mod manager, compress the generated folder (Unless you specified skyrim/data folder")
                self.config.set("CONFIG", "bUseMo", "False")

            fname   = QFileDialog.getExistingDirectory(self, 'Mod folder location', '', QFileDialog.ShowDirsOnly)

            if fname:
                self.config.set("PATHS", "ModFolder", str(fname))

            self.config.set("CONFIG", "bFirstTime", "False")

            # Save changes to ini file
            with open(self.config_path, 'w') as configFile:
                self.config.write(configFile)


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def displayLCDAnimChecked(self):
        self.lcdAnimsChecked.display(len(self.getCheckedAnimsInfo()))


    def scanFolder(self):

        self.progressBar.setRange(0, 0)

        self.groupBoxGenerate.setDisabled(True)
        self.groupBoxScanning.setDisabled(True)
        packages = []

        scanDir = QFileDialog.getExistingDirectory(self, 'Mod folder location', self.config.get("PATHS", "ModFolder"), QFileDialog.ShowDirsOnly)

        previousPackage = ""

        animPackage = None
        animModule = None

        counter = 0

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
                            if animPackage != None:
                                animPackage.modules.sort(key=lambda x: x.name, reverse=False)
                            animPackage = AnimationPackage(package)
                        animModule = AnimationModule(module)

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
                                    counter +=1
                                    logging.info("        Adding basic animation")

                                elif animType == ANIM_TYPE.SEQUENCE:
                                    anim = Animation(animType, animOptions, animId, animFile, animObj)
                                    animModule.addAnimation(anim)
                                    counter +=1
                                    logging.info("        Adding sequence animation")

                                elif animType == ANIM_TYPE.ADDITIVE:
                                    anim.addStage(animId, animFile, animObj)
                                    counter +=1
                                    logging.info("            Adding stage")

                        animModule.animations.sort(key=lambda x: x.name, reverse=False)

                        if animModule.animations:
                            animPackage.addModule(animModule)
                            if package != previousPackage:
                                previousPackage = package
                                packages.append(animPackage)

        self.createTreeByMod(packages)
        self.treeAnimFiles.itemClicked.connect(self.displayLCDAnimChecked)
        self.lcdAnimsFound.display(counter)
        self.displayLCDAnimChecked()
        self.groupBoxGenerate.setDisabled(False)
        self.groupBoxScanning.setDisabled(False)


    def createTreeByMod(self, packages):

        self.treeAnimFiles.clear()

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
                        stageSection.setText(1, animation.stages[0][i])
                        stageSection.setCheckState(0, Qt.Checked)
                        counter += 1




        """
        root = self.treeAnimFiles.invisibleRootItem()
        for i in range(root.childCount()):
            package = root.child(i)
            print(root.childCount())
            print(i)
            print(package)
            for j in range(package.childCount()):
                module = package.child(j)
                for k in range(module.childCount()):
                    anim = module.child(k)
                    if anim.childCount() == 0:
                        module.removeChild(anim)
                if module.childCount() == 0:
                   package.removeChild(module)
            if package.childCount() == 0:
                root.removeChild(package)
        """

        self.progressBar.setRange(0, 1)


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

        root = ET.Element("folder0")
        root.set("n", self.config.get("PLUGIN", "name" ) )
        root.set("i", self.config.get("PLUGIN", "image") )

        previousPackage = ""
        previousModule  = ""
        previousAnim    = ""

        maxItemPerSection   = self.config.getint("PLUGIN", "maxItemPerSection")
        animations          = self.getCheckedAnimsInfo()

        packageFolder       = None
        packageSetFolder    = None
        moduleFolder        = None
        moduleSetFolder     = None
        animFolder          = None
        animSetFolder       = None
        entry               = None
        stageSetFolder      = None

        packageCounter      = 0
        packageSetCounter   = 0
        packageFolderOffset = 0
        moduleCounter       = 0
        moduleSetCounter    = 0
        moduleFolderOffset  = 0
        animCounter         = 0
        animSetCounter      = 0
        animFolderOffset    = 0
        stageCounter        = 0
        stageSetCounter     = 0
        minusOffset         = 0

        for animId, package, module, anim, stage in animations:

            # ===== PACKAGE =====
            nbPackages      = self.getNumberOfCheckedPackage()
            nbOfPackageSets =  nbPackages / maxItemPerSection

            if nbOfPackageSets > 1:
                packageFolderOffset =1

                if packageCounter >= maxItemPerSection or packageSetCounter == 0:
                    packageSetCounter += 1
                    packageCounter     = 0

                    packageSetFolder = ET.SubElement(root, "folder1")
                    packageSetFolder.set("n", "Package Set " + str(packageSetCounter))
                    packageSetFolder.set("i", self.config.get("PLUGIN", "setFolderImage") )

            if package != previousPackage:
                moduleCounter       = 0
                moduleSetCounter    = 0
                moduleFolderOffset  = 0
                animCounter         = 0
                animSetCounter      = 0
                animFolderOffset    = 0
                stageCounter        = 0
                stageSetCounter     = 0

                if nbOfPackageSets > 1:
                    packageFolder = ET.SubElement(packageSetFolder, "folder" + str(1+packageFolderOffset))
                else:
                    packageFolder = ET.SubElement(root, "folder" + str(1+packageFolderOffset))

                packageFolder.set("n", package)
                packageFolder.set("i", self.config.get("PLUGIN", "packageFolderImage") )
                packageCounter +=1
                previousPackage = package

            # ===== MODULE =====
            nbModules      = self.getNumberOfCheckedModuleFromPackage(package)
            nbOfModuleSets =  nbModules / maxItemPerSection

            if nbOfModuleSets > 1:
                moduleFolderOffset = 1

                if moduleCounter >= maxItemPerSection or moduleSetCounter == 0:
                    moduleSetCounter += 1
                    moduleCounter     = 0

                    moduleSetFolder = ET.SubElement(packageFolder, "folder" + str(2 + packageFolderOffset))
                    moduleSetFolder.set("n", "Module Set " + str(moduleSetCounter))
                    moduleSetFolder.set("i", self.config.get("PLUGIN", "setFolderImage") )

            if module != previousModule:
                animCounter         = 0
                animSetCounter      = 0
                animFolderOffset    = 0
                stageCounter        = 0
                stageSetCounter     = 0

                if nbOfModuleSets > 1:
                    moduleFolder = ET.SubElement(moduleSetFolder, "folder" + str(2 + packageFolderOffset + moduleFolderOffset))
                else:
                    moduleFolder = ET.SubElement(packageFolder, "folder" + str(2 + packageFolderOffset + moduleFolderOffset))

                moduleFolder.set("n", module)
                moduleFolder.set("i", self.config.get("PLUGIN", "moduleFolderImage") )
                moduleCounter +=1
                previousModule = module

            # ===== ANIM =====
            nbAnims      = self.getNumberOfCheckedAnimFromModule(package, module)
            nbOfAnimSets =  nbAnims / maxItemPerSection

            if nbOfAnimSets > 1:
                animFolderOffset = 1

                if animCounter >= maxItemPerSection or animSetCounter == 0:
                    animSetCounter += 1
                    animCounter     = 0

                    animSetFolder = ET.SubElement(moduleFolder, "folder" + str(3 + packageFolderOffset + moduleFolderOffset))
                    animSetFolder.set("n", "Anim Set " + str(animSetCounter))
                    animSetFolder.set("i", self.config.get("PLUGIN", "setFolderImage") )

            if anim != previousAnim:
                stageCounter        = 0
                stageSetCounter     = 0

                nbStages = self.getNumberOfCheckedStageFromAnim(package, module, anim)

                if nbStages > 1:
                    if nbOfAnimSets > 1:
                        animFolder = ET.SubElement(animSetFolder, "folder" + str(3 + packageFolderOffset + moduleFolderOffset + animFolderOffset))
                    else:
                        animFolder = ET.SubElement(moduleFolder, "folder" + str(3 + packageFolderOffset + moduleFolderOffset + animFolderOffset))

                    animFolder.set("n", anim)
                    animFolder.set("i", self.config.get("PLUGIN", "animFolderImage") )
                else:
                    minusOffset = 1

                animCounter +=1
                previousAnim = anim

            # ===== STAGE =====
            nbStages      = self.getNumberOfCheckedStageFromAnim(package, module, anim)
            nbOfStageSets =  nbStages / maxItemPerSection

            if nbOfStageSets > 1:
                if stageCounter >= maxItemPerSection or stageSetCounter == 0:
                    stageSetCounter += 1
                    stageCounter    = 0

                    stageSetFolder = ET.SubElement(animFolder, "folder" + str(4 + packageFolderOffset + moduleFolderOffset + animFolderOffset))
                    stageSetFolder.set("n", "Stage Set " + str(stageSetCounter))
                    stageSetFolder.set("i", self.config.get("PLUGIN", "setFolderImage") )

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

            entry.set("i", self.config.get("PLUGIN", "stageFolderImage") )
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
        root    = self.treeAnimFiles.invisibleRootItem()
        count   = 0

        for i in range(root.childCount()):
            if root.child(i).checkState(0) != Qt.Unchecked:
                count += 1

        return count


    def getNumberOfCheckedModuleFromPackage(self, packageName):
        root = self.treeAnimFiles.invisibleRootItem()
        count   = 0

        for i in range(root.childCount()):
            package = root.child(i)
            if package.text(0) == packageName:

                for j in range(package.childCount()):
                    if package.child(j).checkState(0) != Qt.Unchecked:
                        count += 1
        return count


    def getNumberOfCheckedAnimFromModule(self, packageName, moduleName):
        root = self.treeAnimFiles.invisibleRootItem()
        count   = 0

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
        count   = 0

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

        checkedAnimsInfo  = []

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
