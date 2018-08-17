import widget.AnimTreeWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem

class AnimTreeItem(QTreeWidgetItem):

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFlags(self.flags())
        self.setCheckState(0, Qt.Checked)
        self.maxChildCount = 25
        self.bIsSplitter = False

    def addChildWithSplitter(self, item):
        # If there are already splitter let's try to add the item to the first available
        for i in range(self.childCount()):
            splitter = self.child(i)
            if splitter.isSplitter():
                if splitter.childCount() < self.maxChildCount:
                    return splitter.addChild(item)

        # If none is available, add an other splitter, if needed
        if self.splitterCount() > 0:
            if self.splitterCount() < self.maxChildCount:
                splitter = self.insertSplitter()
                return splitter.addChild(item)

        if self.childCount() == self.maxChildCount:
            if self.splitterCount() == self.maxChildCount:
                splitter = self.insertSplitter("1", 0)
            else:
                splitter = self.insertSplitter()

            for i in range(self.childCount()):
                child = self.takeChild(1)
                splitter.addChild(child)

            splitter = self.insertSplitter()
            splitter.addChild(item)
            return True

        return self.addChild(item)

    def flags(self):
        return super().flags() | Qt.ItemIsTristate | Qt.ItemIsEditable | Qt.ItemIsUserCheckable

    def splitterCount(self):
        counter = 0
        for i in range(self.childCount()):
            child = self.child(i)
            if child.isSplitter():
                counter += 1
        return counter

    def insertSplitter(self, text="", index=-1):
        splitter = AnimTreeItem()

        if not text:
            text = str(self.splitterCount() + 1)
        if index == -1:
            index = self.splitterCount()

        splitter.setText(0, "Set " + text)
        splitter.setIsSplitter(True)
        self.insertChild(index, splitter)
        return splitter

    def setIsSplitter(self, bool):
        self.bIsSplitter = bool

    def setAnimation(self, animation, i):
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.NAME.value, "PlaceHolder")
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.TYPE.value, animation.type.name)
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.OPTIONS.value, str([x.name for x in animation.options]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value, str(animation.stages[i]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.FILE.value, str(animation.stages_file[i]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ANIM_OBJ.value, str(animation.stages_obj[i]))

    def isSplitter(self):
        return self.bIsSplitter

