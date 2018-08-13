#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys, configparser, os, re
import xml.etree.ElementTree as ET

from PyQt5.QtWidgets    import (QApplication, QWidget, QToolTip,
                                QPushButton, QMessageBox, QDesktopWidget,
                                QMainWindow, QFileDialog, QHBoxLayout,
                                QVBoxLayout, QLCDNumber, QLabel, QListWidget,
                                QTreeWidget, QTreeWidgetItem)
from PyQt5.QtGui        import QIcon, QFont, QBrush, QColor
from PyQt5.QtCore       import QSize, Qt

class Animation():

    def __init__(self, line):

        split   = line.split(" ")

        self.base_id    = self.getBaseIdFromId(split[1])
        self.type       = self.getTypeFromSymbol(split[0])
        self.author     = self.getAuthorFromId(self.id)
        self.name       = self.getNameFromId(self.id)
        self.category   = self.getTypeFromSymbol(split[0])

        self.actorCount = 0
        self.stageCount = 0

    def getBaseIdFromId(self, id):
        baseId  = ""
        regexp  = re.compile(r"(\S*)_((?:a|A)\d_(?:s|S)\d)\b")
        found   = regexp.search(id)
        if found:
            baseId = found.group(1)
        return baseId

    def getTypeFromSymbol(self, symbol):
        type = None
        return type

    def getAuthorFromId(self, id):
        author = id.split("_")[0]
        return author

    def getNameFromId(self, id):
        name = id.split("_")[0]
        return name

    def isSameAnim(self, id):
        if self.id.rsplit("_",2) == id.rsplit("_", 2):
            return True
        return False

    def incrementActorCount(self):
        self.actorCount += 1

    def incrementStageCount(self):
        self.stageCount += 1

    def getAnimStageId(self, actorIndex, stageIndex):
        return self.base_id + "_" + "A" + actorIndex + "_" + "S" + stageIndex

    def getAnimActorId(self, actorIndex):
        return [self.getAnimStageId(actorIndex, i) for i in self.stageCount]

    def getAllAnimId(self):
        return [self.getAnimActorId(i) for i in self.actorCount ]




class Example(QMainWindow):

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
        animFiles = []
        scanDir = QFileDialog.getExistingDirectory(self, 'Mod folder location', self.config.get("PATHS", "ModFolder"), QFileDialog.ShowDirsOnly)

        previousParent  = ""
        section         = None
        brushS          = QBrush(Qt.blue)

        if scanDir:
            for root, dirs, files in os.walk(scanDir):
                for file in files:
                    if file.startswith("FNIS") and file.endswith("List.txt"):
                        animFile = os.path.join(root, file)
                        parentName  = animFile.replace(scanDir + '\\', '').split('\\',1)[0]
                        fileName    = animFile.replace(scanDir + '\\', '').rsplit('\\',1)[1]

                        if parentName != previousParent:
                            section = QTreeWidgetItem(self.treeAnimFiles)
                            section.setText(0, parentName)
                            section.setFlags(section.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                            previousParent = parentName

                        with open(animFile, 'r') as f:
                            animSection = None
                            for line in f:
                                if line.startswith('s'):
                                    regexp = re.compile(r"(\S*_(a|A)\d)_(s|S)\d")
                                    found = regexp.search(line)
                                    if found:
                                        animName = found.group(1)

                                        animSection = QTreeWidgetItem(section)
                                        animSection.setFlags(animSection.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                                        animSection.setText(0, animName)
                                        animSection.setCheckState(0, Qt.Checked)

                                        section.setForeground(0, brushS)
                                        animSection.setForeground(0, brushS)

                                        animStageSection = QTreeWidgetItem(animSection)
                                        animStageSection.setFlags(animSection.flags() | Qt.ItemIsUserCheckable)
                                        animStageSection.setText(0, found.group(3) + '1')
                                        animStageSection.setCheckState(0, Qt.Checked)

                                elif line.startswith('+'):
                                    regexp = re.compile(r"\S*_(a|A)\d_((s|S)\d)")
                                    found = regexp.search(line)
                                    if found:
                                        stageIndex = found.group(2)

                                        animStageSection = QTreeWidgetItem(animSection)
                                        animStageSection.setFlags(animSection.flags() | Qt.ItemIsUserCheckable)
                                        animStageSection.setText(0, stageIndex)
                                        animStageSection.setCheckState(0, Qt.Checked)

                        animFiles.append(animFile)
                        self.lcdAnimsFound.display(len(animFiles))

        self.buttonScan.setDefault(False)
        self.buttonGenerate.setDefault(True)

    def generatePlugin(self):
        print("generating plugin ...")

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

        print("saving plugin to file")
        pluginPath = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "Plugin")
        self.create_dir(pluginPath)

        with open(pluginPath + self.config.get("PLUGIN", "Name") + ".xml", "w") as file:
            data = ET.tostring(header, "unicode")
            file.write(data)
            data = ET.tostring(folderStyle, "unicode")
            file.write(data)
            data = ET.tostring(entryStyle, "unicode")
            file.write(data)
            data = ET.tostring(folder0, "unicode")
            file.write(data)
        print("Done !")

    """
        :return
            checkedAnimsInfo    - Animations' info of all checked item
                sectionName     - (generally author's name) Used to gather animations in the same folder
                animName        - Used to display animation's name
                id              - Animation ID used to retrieve corresponding animation
    """
    def getCheckedAnimsInfo(self):

        checkedAnimsInfo  = []

        root = self.treeAnimFiles.invisibleRootItem()
        for i in range(root.childCount()):
            modItem = root.child(i)

            if modItem.childCount() == 0:
                modItem.setDisabled(True)

            else:
                for j in range(modItem.childCount()):
                    animItem = modItem.child(j)

                    for k in range(animItem.childCount()):
                        stageItem   = animItem.child(k)
                        animId      = animItem.text(0) + "_" + stageItem.text(0)
                        splitAnimId = animId.split("_")
                        stageId     = splitAnimId[-1]
                        actorId     = splitAnimId[-2]

                        # Handle Anim Id like NAME_ACTOR_STAGE
                        if len(splitAnimId) == 3:
                            animName    = splitAnimId[0]
                            sectionName = modItem.text(0)
                        else:
                            animName    = '_'.join(splitAnimId[1:-2])
                            sectionName = splitAnimId[0]

                        animInfo    = (animId, sectionName, animName, actorId, stageId)
                        checkedAnimsInfo.append(animInfo)

        return checkedAnimsInfo

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def create_dir(self, path):
        # Prevent execution if the library already exists
        if (os.path.exists(path)):
            print("WARNING: " + path + " already exists")
        else:
            print("Creating new directory: " + path)
            os.makedirs(path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example(sys.argv)
    sys.exit(app.exec_())
