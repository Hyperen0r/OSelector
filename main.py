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

    def __init__(self, mod, line):

        self.mod        = mod
        self.base_id    = self.getBaseIdFromLine(line)
        self.author     = self.getAuthorFromId(self.base_id)
        self.name       = self.getNameFromId(self.base_id)

        if self.author == self.base_id:
            self.author = self.mod

        self.actorCount = 1
        self.stageCount = 1

    def getBaseIdFromLine(self, line):
        baseId  = ""
        regexp  = re.compile(r"(\S*)_((?:a|A)\d_(?:s|S)\d)\b[^.]")
        found   = regexp.search(line)
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

    def isSameAnim(self, line):
        if self.base_id == self.getBaseIdFromLine(line):
            return True
        return False

    def incrementActorCount(self):
        self.actorCount += 1

    def incrementStageCount(self):
        if self.actorCount == 1:    # No need to increment stage count for other actor
            self.stageCount += 1

    def getAnimStageId(self, actorIndex, stageIndex):
        return self.base_id + "_" + "A" + str(actorIndex) + "_" + "S" + str(stageIndex)

    def getAnimActorId(self, actorIndex):
        return [self.getAnimStageId(actorIndex, i) for i in self.stageCount]

    def getAllAnimId(self):
        return [self.getAnimActorId(i) for i in self.actorCount ]

    def __str__(self):
        return "[ANIM] Mod: " + self.mod + " Author:" + self.author + " BaseId: " + self.base_id + " Atotal: " + str(self.actorCount) + " Stotal: " + str(self.stageCount)

    @staticmethod
    def isValidLine(line):
        if ".hkx" in line:
            return True
        return False



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
        animations  = []
        scanDir = QFileDialog.getExistingDirectory(self, 'Mod folder location', self.config.get("PATHS", "ModFolder"), QFileDialog.ShowDirsOnly)

        if scanDir:
            for root, dirs, files in os.walk(scanDir):
                for file in files:
                    if file.startswith("FNIS") and file.endswith("List.txt"):
                        animFile    = os.path.join(root, file)
                        mod         = animFile.replace(scanDir + '\\', '').rsplit('\\',1)[1][5:-9].split("_")[0]

                        with open(animFile, 'r') as f:
                            anim        = None
                            for line in f:
                                if Animation.isValidLine(line):
                                    if anim == None or not anim.isSameAnim(line):
                                        if line.startswith("s"):
                                            anim = Animation(mod, line)
                                            animations.append(anim)

                                    else:
                                        if line.startswith("s"):
                                            anim.incrementActorCount()
                                        elif line.startswith("+") :
                                            anim.incrementStageCount()

        self.lcdAnimsFound.display(len(animations))
        self.createTreeByMod(animations)

    def createTreeByMod(self, animations):

        previousMod = ""
        section     = None

        for animation in animations:
            mod = animation.mod

            if mod != previousMod:
                previousMod = mod

                section = QTreeWidgetItem(self.treeAnimFiles)
                section.setText(0, mod)
                section.setFlags(section.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            animSection = QTreeWidgetItem(section)
            animSection.setFlags(animSection.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            animSection.setText(0, animation.base_id)
            animSection.setCheckState(0, Qt.Checked)

            for i in range(animation.actorCount):
                actorSection = QTreeWidgetItem(animSection)
                actorSection.setFlags(actorSection.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                actorSection.setText(0, "A" + str(i+1))
                actorSection.setCheckState(0, Qt.Checked)

                for j in range(animation.stageCount):
                    stageSection = QTreeWidgetItem(actorSection)
                    stageSection.setFlags(stageSection.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                    stageSection.setText(0, "S" + str(j+1))
                    stageSection.setText(1, animation.getAnimStageId(i,j))
                    stageSection.setCheckState(0, Qt.Checked)


    def generatePlugin(self):
        print("generating plugin ...")

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

        print("saving plugin to file")
        pluginPath = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "Plugin")
        self.create_dir(pluginPath)

        # File allowing the plugin to be recognized by OSA
        pluginInstallPath = self.config.get("PATHS", "ModFolder") + "/" + self.config.get("PLUGIN", "Name") + "/" + self.config.get("PATHS", "installPlugin") + "/"
        self.create_dir(pluginInstallPath)
        file = open( pluginInstallPath + "/" + self.config.get("PLUGIN", "Name") + ".osplug", "w")

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

            for j in range(modItem.childCount()):
                animItem = modItem.child(j)

                for k in range(animItem.childCount()):
                    actorItem   = animItem.child(k)

                    for l in range(actorItem.childCount()):
                        stageItem = actorItem.child(l)

                        animId      = stageItem.text(1)
                        stageId     = stageItem.text(0)
                        actorId     = actorItem.text(0)

                        animInfo    = (animId, modItem.text(0), animItem.text(0), actorId, stageId)
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
