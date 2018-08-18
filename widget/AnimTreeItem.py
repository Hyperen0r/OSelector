import xml.etree.ElementTree as ET
import widget.AnimTreeWidget
import math
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem

class AnimTreeItem(QTreeWidgetItem):

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFlags(self.flags())
        self.setCheckState(0, Qt.Checked)
        self.splitterCounter = 0
        self.splitterIndex = 0
        self.levelTwoCounter = 0
        self.maxChildCount = 25
        self.bIsSplitter = False

    def addChildWithSplitter(self, item):
        # If there are already splitter let's try to add the item to the first available
        for i in range(self.childCount()):
            splitter = self.child(i)
            if splitter.bIsSplitter:
                if splitter.childCount() < splitter.maxChildCount:
                    return splitter.addChild(item)

        # If none is available, add an other splitter, if needed
        if self.nextSplitterIndex() > 0 and self.nextSplitterIndex() < self.maxChildCount:
            index = self.nextSplitterIndex()
            splitter = self.insertSplitter(index)

            return splitter.addChild(item)

        if self.childCount() == self.maxChildCount:
            index = self.nextSplitterIndex()
            if self.splitterLevel() > 1:
                self.levelTwoCounter += 1
                index = (self.levelTwoCounter)
            splitter = self.insertSplitter(index)
            for i in range(self.childCount()):
                child = self.takeChild(index+1)
                if not child:
                    child = AnimTreeItem()
                if child.bIsSplitter:
                    child.setText(0, "Set " + str(i+1))
                splitter.addChild(child)

            splitter = self.insertSplitter()
            splitter.addChild(item)
            return True

        return self.addChild(item)

    def animationCount(self, state=Qt.Unchecked):
        if self.bIsSplitter or not self.isAnim():
            counter = 0
            for i in range(self.childCount()):
                child = self.child(i)
                if child.checkState(0) != state:
                    counter += child.animationCount(state)
            return counter
        else:
            return 1

    def toXML(self, parent, level, config):
        if self.bIsSplitter or not self.isAnim():
            elt = ET.SubElement(parent, "folder" + str(level))
            elt.set("n", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.NAME.value))
            elt.set("i", config.get("PLUGIN", "setFolderImage"))

            for i in range(self.childCount()):
                child = self.child(i)
                if child.checkState(0) != Qt.Unchecked:
                    child.toXML(elt, level + 1, config)
        else:
            entry = ET.SubElement(parent, "entry")
            entry.set("n", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.NAME.value))
            entry.set("i", config.get("PLUGIN", "stageFolderImage"))
            entry.set("id", self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value))

    def flags(self):
        return super().flags() | Qt.ItemIsTristate | Qt.ItemIsEditable | Qt.ItemIsUserCheckable

    def nextSplitterIndex(self):
        return self.splitterIndex

    def setNextSplitterIndex(self, num=-1):
        if num == -1:
            self.splitterIndex = (self.splitterIndex+1 % self.maxChildCount)
        else:
            self.splitterIndex = (num % self.maxChildCount)
        return

    def splitterLevel(self):
        return math.floor(self.splitterCounter / self.maxChildCount)

    def insertSplitter(self, index=-1):
        if index == -1:
            index = self.nextSplitterIndex()
        splitter = AnimTreeItem()
        splitter.setText(0, "Set " + str(index+1))
        splitter.bIsSplitter = True
        self.insertChild(index, splitter)
        self.splitterCounter += 1
        self.setNextSplitterIndex(index+1)
        return splitter

    def isAnim(self):
        if self.text(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value):
            return True
        return False

    def setAnimation(self, animation, i):
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.NAME.value, "PlaceHolder")
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.TYPE.value, animation.type.name)
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.OPTIONS.value, str([x.name for x in animation.options]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value, str(animation.stages[i]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.FILE.value, str(animation.stages_file[i]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ANIM_OBJ.value, str(animation.stages_obj[i]))

