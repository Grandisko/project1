from PyQt5 import QtWidgets, QtCore

"""
	static functions and Constants
"""


class Constants:
	"""
		Constants
	"""

	# operations
	INNER_OPERATIONS = {'relocateGoods': "Переместить\nтовар", 'writeOffGoods': "Списать\nтовар",
						'acceptGoods': "Принять\nтовар"}
	OUTER_OPERATIONS = {'sellGoods': "Продать товар"}
	OPERATIONS_TYPES = {key: value for value, key in enumerate(sorted(INNER_OPERATIONS.keys()|OUTER_OPERATIONS.keys()))}
	# filter
	SORTING = 0
	CONDITIONS_SORTING = 1
	ASCENDING = 0
	DESCENDING = 1
	# data types
	TEXT, NUMERIC, DATETIME, FOREIGN_KEY, PRIMARY_KEY, BOOL = 0, 1, 2, 3, 4, 5
	DATA_TYPES = {0: 'TEXT', 1: 'NUMERIC', 2: 'DATETIME', 3: 'FOREIGN_KEY', 4: 'PRIMARY_KEY', 5: 'BOOL'}
	# datetime
	DATETIME_DEFAULT= QtCore.QDateTime(2000, 1, 1, 0, 0)
	DATETIME_FORMAT = "dd.MM.yyyy HH:mm:ss"


# example
COLUMNS = {'col1': Constants.TEXT, 'col2': Constants.NUMERIC, 'col3': Constants.DATETIME}


def centerWidget(width: int, height: int) -> tuple[int]:
	"""
		Center widget on the desktop 
	"""
	
	bufferElem = QtWidgets.QApplication.desktop()
	return int((bufferElem.width() - width)/2), int((bufferElem.height() - height)/2), width, height
