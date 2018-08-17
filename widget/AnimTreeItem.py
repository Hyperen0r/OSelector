import widget.AnimTreeWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem

class AnimTreeItem(QTreeWidgetItem):

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setFlags(self.flags())
        self.setCheckState(0, Qt.Checked)
        self.maxChildCount = 25
        self.splitter = 0
        self.isAnim = False

    def addChildWithSplitter(self, item):
        # If there are already splitter let's try to add the item to the first available
        for i in range(self.splitter):
            splitter = self.child(i)
            if splitter.childCount() < 25:
                return splitter.addChild(item)

        # If none is available, add an other splitter, if needed
        if self.splitter > 0 and self.splitter < 25:
            splitter = self.insertSplitter()
            return splitter.addChild(item)

        # If no splitter exists, check if one needed
        if self.childCount() == self.maxChildCount and self.splitter == 0:
            splitter = self.insertSplitter()
            for i in range(self.splitter, self.childCount()):
                child = self.takeChild(self.splitter)
                splitter.addChild(child)
            splitter = self.insertSplitter()
            splitter.addChild(item)
            return True

        return self.addChild(item)

    def flags(self):
        return super().flags() | Qt.ItemIsTristate | Qt.ItemIsEditable | Qt.ItemIsUserCheckable

    def insertSplitter(self):
        splitter = AnimTreeItem()
        splitter.setText(0, "Set " + str(self.splitter + 1))
        self.insertChild(self.splitter, splitter)
        self.splitter += 1
        return splitter

    def setAnimation(self, animation, i):
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.NAME.value, "PlaceHolder")
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.TYPE.value, animation.type.name)
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.OPTIONS.value, str([x.name for x in animation.options]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ID.value, str(animation.stages[i]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.FILE.value, str(animation.stages_file[i]))
        self.setText(widget.AnimTreeWidget.AnimTreeWidget.COLUMN.ANIM_OBJ.value, str(animation.stages_obj[i]))
        self.isAnim = True

    def isAnim(self):
        return self.isAnim
