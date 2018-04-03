from PyQt4 import QtCore, QtGui


class ComboBoxDelegate(QtGui.QItemDelegate):
    values = ""
    editable = ""

    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def def_values(self, values):
        self.values = values

    def def_editable(self, editable):
        self.editable = editable

    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        editor.addItems(self.values)
        editor.setEditable(eval(self.editable))
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, QtCore.Qt.DisplayRole)  # .String()
        i = editor.findText(text)
        if i == -1:
            i = 0
        editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        # model.setData(index, QtCore.QVariant(editor.currentText() ))
        model.setData(index, editor.currentText())
