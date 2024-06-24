from PyQt5 import QtWidgets, QtCore

"""
	Static functions and Constants
"""


class Constants:
	"""
		Constants
	"""
	DEFAULT_DATETIME = QtCore.QDateTime(2000, 1, 1, 0, 0)
	INNER_OPERATIONS = {'relocateGoods': "Переместить\nтовар", 'writeOffGoods': "Списать\nтовар",
						'acceptGoods': "Принять\nтовар"}
	OUTER_OPERATIONS = {'sellGoods': "Продать товар"}
	TEXT, NUMERIC, DATETIME, FOREIGN_KEY, BOOL, URL = 0, 1, 2, 3, 4, 5
	TYPES = {0: 'TEXT', 1: 'NUMERIC', 2: 'DATETIME', 3: 'FOREIGN_KEY', 4:'BOOL', 5:'URL'}


# example
# COLUMNS = {'col1': Constants.TEXT, 'col2': Constants.NUMERIC, 'col3': Constants.DATETIME}


def centerWidget(width: int, height: int) -> tuple[int]:
	"""
		Сalculate screen center coordinates
	"""
	
	bufferElem = QtWidgets.QApplication.desktop()
	return int((bufferElem.width() - width)/2), int((bufferElem.height() - height)/2), width, height
