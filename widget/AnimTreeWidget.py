import xml.etree.ElementTree as ET
import widget.AnimTreeItem

from enum import Enum
from widget.QuickyGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView, QMenu, QTreeWidget
from PyQt5.QtGui import QCursor

class AnimTreeWidget(QTreeWidget):

    class ROLE(Enum):
        FOLDER = 1001
        SPLITTER = 1002
        ANIMATION = 1003

    class COLUMN(Enum):
        NAME = 0
        TYPE = 1
        OPTIONS = 2
        ID = 3
        FILE = 4
        ANIM_OBJ = 5

    def __init__(self, parent=None):
        super().__init__(parent)

        self.header().setDefaultAlignment(Qt.AlignHCenter)
        self.header().setMinimumSectionSize(85)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.header().setFont(getNormalFont())
        self.setHeaderLabels([AnimTreeWidget.COLUMN.NAME.name, AnimTreeWidget.COLUMN.TYPE.name, AnimTreeWidget.COLUMN.OPTIONS.name, AnimTreeWidget.COLUMN.ID.name, AnimTreeWidget.COLUMN.FILE.name, AnimTreeWidget.COLUMN.ANIM_OBJ.name])
        self.setColumnWidth(AnimTreeWidget.COLUMN.NAME.value, 400)
        self.setColumnWidth(AnimTreeWidget.COLUMN.TYPE.value, 100)
        self.setColumnWidth(AnimTreeWidget.COLUMN.ID.value, 200)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTreeWidget.DoubleClicked | QTreeWidget.EditKeyPressed)
        self.setSelectionMode(QTreeWidget.ContiguousSelection)

    def animationCount(self, state=Qt.Unchecked):
        root = self.invisibleRootItem()

        counter = 0
        for i in range(root.childCount()):
            child = root.child(i)
            if child.checkState(0) != state:
                counter += child.animationCount(state)
        return counter

    def checkAll(self):
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            self.checkSubTree(root.child(i), Qt.Checked)

    def checkSubTree(self, item, state):
        item.setCheckState(0, state)
        for i in range(item.childCount()):
            self.checkSubTree(item.child(i), state)

    def cleanup(self, item=None):
        hasBeenRemoved = False
        if not item:
            item = self.invisibleRootItem()

        if not item.text(AnimTreeWidget.COLUMN.ID.value):
            if item.childCount() == 0:
                self.removeFromParent(item)
                hasBeenRemoved = True
            else:
                counter = 0
                for i in range(item.childCount()):
                    if not self.cleanup(item.child(counter)):
                        counter += 1

            if item.childCount() == 1:
                child = item.child(0)
                if self.moveUp(child):
                    self.removeFromParent(item)
                    hasBeenRemoved = True
                self.cleanup(child)
        return hasBeenRemoved

    def createFromPackages(self, packages):

        self.clear()
        animations = []
        duplicateCounter = 0

        root = widget.AnimTreeItem.AnimTreeItem(self)
        for package in packages:
            section = widget.AnimTreeItem.AnimTreeItem()
            section.setText(0, package.name)
            root.addChildWithSplitter(section)

            for module in package.items:
                moduleSection = widget.AnimTreeItem.AnimTreeItem()
                moduleSection.setText(0, module.name)
                section.addChildWithSplitter(moduleSection)

                previousAnimation = ""
                animSection = None
                counter = 1
                for animation in module.items:
                    if animation.name != previousAnimation or not animSection:
                        previousAnimation = animation.name
                        counter = 1
                        animSection = widget.AnimTreeItem.AnimTreeItem()
                        animSection.setText(0, animation.name)
                        moduleSection.addChildWithSplitter(animSection)

                    for i, stage in enumerate(animation.stages):
                        if animation.stages[i] in animations:
                            duplicateCounter += 1
                        else:
                            stageSection = widget.AnimTreeItem.AnimTreeItem()
                            stageSection.setAnimation(animation, i)
                            animSection.addChildWithSplitter(stageSection)
                            counter += 1
                            animations.append(animation.stages[i])

        invisibleRoot = self.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.takeChild(0)
            invisibleRoot.addChild(child)
        invisibleRoot.removeChild(root)

        return duplicateCounter

    def openMenu(self, position):
        selection = self.selectedItems()
        if selection:
            menu = QMenu()
            menu.addAction("Check All", self.checkAll)
            menu.addAction("Uncheck All", self.uncheckAll)
            menu.addAction("Cleanup", self.cleanup)
            menu.addSeparator()
            if selection[0].parent():
                menu.addAction("Move Up", self.moveUp)
                menu.addSeparator()
            menu.addAction("Insert parent", self.insertParent)
            menu.addAction("Remove", self.removeFromParent)
            menu.exec_(QCursor.pos())
        return

    def insertParent(self, item=None, parent=None):
        if parent == None:
            parent = widget.AnimTreeItem.AnimTreeItem()
            parent.setText(0, "New Parent")

        if not item:
            items = self.selectedItems()
            for item in items:
                self.insertParent(item, parent)
            return True

        actualParent = item.parent()
        if not actualParent:
            actualParent = self.invisibleRootItem()

        index = actualParent.indexOfChild(item)
        item = actualParent.takeChild(index)
        parent.addChild(item)
        actualParent.insertChild(index, parent)
        return

    def moveUp(self, item=None):
        if not item:
            items = self.selectedItems()
            for item in items:
                self.moveUp(item)
            return True

        n1 = item.parent()
        if not n1:
            n1 = self.invisibleRootItem()
            for i in range(item.childCount()):
                self.moveUp(item.child(0))
            self.removeFromParent(item)
            return True

        n2 = n1.parent()
        if not n2:
            n2 = self.invisibleRootItem()

        itemIndex = n1.indexOfChild(item)
        n1Index = n2.indexOfChild(n1)
        item = n1.takeChild(itemIndex)
        n2.addChild(item)
        return True

    def toXML(self, config):
        root = self.invisibleRootItem()
        folder0 = ET.Element("folder0")
        folder0.set("n", config.get("PLUGIN", "name"))
        folder0.set("i", config.get("PLUGIN", "defaultPackageIcon"))

        for i in range(root.childCount()):
            child = root.child(i)
            if child.checkState(0) != Qt.Unchecked:
                child.toXML(folder0, 1, config)
        return folder0

    def removeFromParent(self, item=None):
        if not item:
            items = self.selectedItems()
            for item in items:
                self.removeFromParent(item)
            return True

        parent = item.parent()
        if not parent:
            parent = self.invisibleRootItem()
        parent.removeChild(item)

    def uncheckAll(self):
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            self.checkSubTree(root.child(i), Qt.Unchecked)

