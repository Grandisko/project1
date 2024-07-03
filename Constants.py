from PyQt5 import QtWidgets, QtCore
from typing import Callable, Iterator

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
	OPERATION_RELOCATE, OPERATION_WRITE_OFF, OPERATION_ACCEPT, OPERATION_SELL = 0, 1, 2, 3
	OPERATIONS_TYPES = {operation_name: operation_id for operation_name, operation_id in \
						zip(list(INNER_OPERATIONS.keys()) + list(OUTER_OPERATIONS.keys()), (OPERATION_RELOCATE, OPERATION_WRITE_OFF, OPERATION_ACCEPT, OPERATION_SELL))}
	# filter
	SORTING = 0
	CONDITIONS_SORTING = 1
	ASCENDING = 0
	DESCENDING = 1
	# data types
	TEXT, NUMERIC, DATETIME, FOREIGN_KEY, PRIMARY_KEY, BOOL = 0, 1, 2, 3, 4, 5
	DATA_TYPES = {0: 'TEXT', 1: 'NUMERIC', 2: 'DATETIME', 3: 'FOREIGN_KEY', 4: 'PRIMARY_KEY', 5: 'BOOL'}
	# datetime
	DATETIME_DEFAULT = QtCore.QDateTime(2000, 1, 1, 0, 0)
	DATETIME_FORMAT = "dd.MM.yyyy HH:mm:ss"
	# database
	DATABASE_PATH = "DB/database.db"


# example
COLUMNS = {'col1': Constants.TEXT, 'col2': Constants.NUMERIC, 'col3': Constants.DATETIME}


def centerWidget(width: int, height: int) -> tuple[int]:
	"""
		Center widget on the desktop 
	"""
	
	bufferElem = QtWidgets.QApplication.desktop()
	return int((bufferElem.width() - width)/2), int((bufferElem.height() - height)/2), width, height

def fill_table(columns: dict, data: Callable|Iterator|list, table: QtWidgets.QTableWidget):
	"""

	"""

	# set table's dimensions
	table.setColumnCount(len(columns))
	table.setHorizontalHeaderLabels(columns.keys())
	# decide how get data
	if isinstance(data, Callable):
		data = data()
	elif isinstance(data, Iterator):
		data = list(data)
	elif isinstance(data, list):
		data = data
	else:
		raise ValueError(f"Unrecognised type of the data variable: {type(data)}")
	# clear data in table
	table.clearContents()
	# set first row with 'id'
	table.setRowCount(len(data) + 1)
	table.setVerticalHeaderLabels(['id'])
	# inserting items into the table
	for i, rowData in enumerate(data, start=1):
		item = QtWidgets.QTableWidgetItem(str(rowData[0]))
		item.setTextAlignment(QtCore.Qt.AlignCenter)
		table.setVerticalHeaderItem(i, item)
		for j, item in enumerate(rowData[1:]):
			item = QtWidgets.QTableWidgetItem(str(item))
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			table.setItem(i, j, item)
