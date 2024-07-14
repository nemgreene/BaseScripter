from maya import OpenMayaUI
from PySide2 import QtWidgets
from shiboken2 import wrapInstance


def maya_main_window():
	main_window_ptr=OpenMayaUI.MQtUtil.mainWindow()
	return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class Window(QtWidgets.QDialog):
	def __init__(self, parent=maya_main_window()):
		super(Window, self).__init__(parent)

gui = Window()
gui.show()