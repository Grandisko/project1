from PyQt5 import QtWidgets, QtCore
from typing import Callable, Iterator
from functools import partial
from docxtpl import DocxTemplate
import platform
import subprocess
import warnings

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
	PYQT_DATETIME_FORMAT = "dd.MM.yyyy HH:mm:ss"
	DATETIME_DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"
	# database
	DATABASE_PATH = "DB/database.db"
	# contracts
	CONTRACTS_TEMPLATE_PATH = "templates/contract_template.docx"
	CONTRACTS_PATH = "contracts/{}.docx"


# # example
# COLUMNS = {'col1': Constants.TEXT, 'col2': Constants.NUMERIC, 'col3': Constants.DATETIME}


def centerWidget(width: int, height: int) -> tuple[int]:
	"""
		Center widget on the desktop 
	"""
	
	bufferElem = QtWidgets.QApplication.desktop()
	return int((bufferElem.width() - width)/2), int((bufferElem.height() - height)/2), width, height

def fill_table(columns: dict, data: Callable|Iterator|list, table: QtWidgets.QTableWidget, counter: bool=False, counter_vals: dict|None=None, counter_handler: Callable|None=None):
	"""

	"""

	counter_limit_at = None
	if counter:
		columns = columns.copy()
		columns |= {'counter': -1}
		if columns.get('count', -1) != -1:
			counter_limit_at = list(columns.keys()).index('count') + 1

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
		if counter:
			item = QtWidgets.QSpinBox(table)
			if not counter_limit_at is None:
				item.setRange(0, int(rowData[counter_limit_at]))
			# TODO тут указать ограничение по умолчанию
			if not counter_vals is None:
				item.setValue(counter_vals.get(int(rowData[0]), 0))
			item.setAlignment(QtCore.Qt.AlignCenter)
			if not counter_handler is None:
				item.valueChanged.connect(partial(counter_handler, rowData[0]))
			table.setCellWidget(i, j + 1, item)

def generate_contract(operation_id: int, operation_name: str, datetime: str, text: dict, to_open: bool=True):
	"""

	"""
	
	# load a template
	doc = DocxTemplate(Constants.CONTRACTS_TEMPLATE_PATH)
	# rendering .docx by the template
	doc.render({'text': text, 'operation_name': operation_name, 'datetime': datetime})
	# save a new contract
	doc.save(file_path:=Constants.CONTRACTS_PATH.format(f"{operation_id}_{datetime.replace(' ', '_')}"))
	
	if to_open:
		match platform.system():
			case "Darwin":
				subprocess.run(["open", file_path])
			case "Windows":
				subprocess.run(["start", file_path], shell=True)
			case "Linux":
				subprocess.run(["xdg-open", file_path])
			case _:
				warnings.warn(OSError("Unrecognised operationg system to open contract!"))
