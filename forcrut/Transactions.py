from PyQt5 import QtWidgets, QtCore
from Constants import centerWidget, Constants
from Filter import FilterButton, ConditionsWidget
from typing import Generator
from functools import cmp_to_key
import re


# example of data to be filled the table
def gen_data():
	return [[1, ":params clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 1, "10.01.2024 01:02:03"], [11, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 17, "10.07.2024 01:02:03"],
			[2, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 2, "10.02.2024 01:02:03"], [22, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 18, "10.08.2024 01:02:03"],
			[3, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 3, "10.03.2024 01:02:03"], [33, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 91, "10.09.2024 01:02:03"],
			[4, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 44, "10.04.2024 01:02:03"], [44, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 81, "10.10.2024 01:02:03"],
			[5, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 5, "10.05.2024 01:02:03"], [55, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 17, "10.11.2024 01:02:03"],
			[6, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 66, "10.06.2024 01:02:03"], [66, ":param clients_edit: does worker have permission to saw/edit clients? #TODO расписать все параметры", 13, "10.12.2024 01:02:03"]]

class Window(QtWidgets.QMainWindow):
	"""
		Main window with transactions and other functionality
	"""

	def __init__(self, params: dict, columns: dict) -> None:
		"""
			:param params: dict of keys and boolean values
				inner: permission for INNER_OPERATIONS,
				outer: permission for OUTER_OPERATIONS,
				clients: permission to saw/edit clients,
				redact: permission to edit information,
				super: super-user;

			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT}.
		"""

		# QMainWindow init
		super().__init__()
		# set title and window dimensions
		self.setWindowTitle("Транзакции")
		self.setGeometry(*centerWidget(800, 600))
		# required fields
		self.__columns = columns
		self.super = params.get('super')
		self.redact = params.get('redact')
		# central widget settings
		self.centralWidget = QtWidgets.QWidget(self)
		self.centralWidget.setObjectName("MainContainer")
		self.setCentralWidget(self.centralWidget)
		# main layout
		self.mainLayout = QtWidgets.QGridLayout(self.centralWidget)
		self.mainLayout.setObjectName("Main-layout")
		# widget for label and operations' buttons
		bufferWidget = QtWidgets.QWidget(self.centralWidget)
		bufferWidget.setGeometry(10, 0, 391, 71)
		self.mainLayout.addWidget(bufferWidget, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		bufferLayout = QtWidgets.QVBoxLayout(bufferWidget)
		label = QtWidgets.QLabel('Операции:', bufferWidget)
		label.setObjectName("labelOperations")
		bufferLayout.addWidget(label)
		# widget for operations' buttons
		self.operationsWidget = QtWidgets.QWidget(bufferWidget)
		bufferLayout.addWidget(self.operationsWidget)
		# form operations' buttons
		bufferLayout = QtWidgets.QHBoxLayout(self.operationsWidget)
		if params.get('inner'):
			for operation_name, text in Constants.INNER_OPERATIONS.items():
				bufferElem = QtWidgets.QPushButton(text)
				bufferElem.setObjectName(operation_name)
				bufferElem.setText(text)
				bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
				bufferElem.clicked.connect(self.__getattribute__(operation_name))
				bufferLayout.addWidget(bufferElem)
		if params.get('sell'):
			bufferElem = QtWidgets.QPushButton("Продать{}товар".format(' ' if not params.get('inner') else '\n'))
			bufferElem.setObjectName('sellGoods')
			bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
			bufferElem.clicked.connect(self.sellGoods)
			bufferLayout.addWidget(bufferElem)
		# widget for label and views' buttons
		bufferWidget = QtWidgets.QWidget(self.centralWidget)
		bufferWidget.setGeometry(570, 0, 311, 101)
		self.mainLayout.addWidget(bufferWidget, 0, 2, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
		bufferLayout = QtWidgets.QVBoxLayout(bufferWidget)
		label = QtWidgets.QLabel('Просмотреть:', bufferWidget)
		label.setObjectName("labelViewButtons")
		bufferLayout.addWidget(label)
		# widget for views' buttons
		self.viewButtonsWidget = QtWidgets.QWidget(bufferWidget)
		bufferLayout.addWidget(self.viewButtonsWidget)
		# form stuff-view button
		viewButtonsLayout = QtWidgets.QGridLayout(self.viewButtonsWidget)
		bufferElem = QtWidgets.QPushButton("Склады и\nтовары")
		bufferElem.setObjectName("stuffView")
		bufferElem.clicked.connect(self.stuffView)
		viewButtonsLayout.addWidget(bufferElem, 0, 0)
		# form template-view button
		bufferElem = QtWidgets.QPushButton("Шаблон\nдоговора")
		bufferElem.setObjectName("templateView")
		bufferElem.clicked.connect(self.templateView)
		viewButtonsLayout.addWidget(bufferElem, 0, 1)
		# form clients-view button if necessary
		if params.get('clients'):
			bufferElem = QtWidgets.QPushButton("Клиенты")
			bufferElem.setObjectName("clientsView")
			bufferElem.clicked.connect(self.clientsView)
			viewButtonsLayout.addWidget(bufferElem, 1, 0, 1, 2)
		# form the filter button
		self.filterButton = FilterButton("Фильтр", self.__columns, parent=self.centralWidget, dataHandler=self.reload)
		self.filterButton.setObjectName("dataFilter")
		self.filterButton.setMinimumSize(100, 30)
		self.mainLayout.setRowMinimumHeight(1, 30)
		self.mainLayout.addWidget(self.filterButton, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
		# form the table
		self.transactionsView = QtWidgets.QTableWidget(self.centralWidget)
		self.transactionsView.setGeometry(10, 130, 771, 391)
		self.transactionsView.setObjectName("transactionsView")
		self.transactionsView.setSortingEnabled(False)
		self.transactionsView.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.transactionsView.setWordWrap(True)
		self.mainLayout.addWidget(self.transactionsView, 2, 0, 3, 3)
		# adaptability of the table
		self.transactionsView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		self.transactionsView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
		# form the reload button
		self.reloadButton = QtWidgets.QPushButton("Обновить", self.centralWidget)
		self.reloadButton.setObjectName("reloadTable")
		self.reloadButton.setMinimumSize(100, 30)
		self.mainLayout.setRowMinimumHeight(5, 30)
		self.reloadButton.clicked.connect(lambda: self.reload())
		self.mainLayout.addWidget(self.reloadButton, 5, 2, QtCore.Qt.AlignRight)
		# filling out the table
		self.reload()
		# possible retranslate for other languages
		self.retranslate()

	def getData(self) -> Generator:
		"""
			Get table's data
		"""

		for i in range(1, self.transactionsView.rowCount()):
			yield [self.transactionsView.verticalHeaderItem(i).text()] + [buffer.text() if (buffer:=self.transactionsView.item(i, j)) else None for j in range(len(self.__columns))]

	def relocateGoods(self):
		pass

	def writeOffGoods(self):
		pass

	def acceptGoods(self):
		pass

	def sellGoods(self):
		pass

	def stuffView(self):
		pass

	def templateView(self):
		pass

	def clientsView(self):
		pass

	def retranslate(self):
		"""
			Possible for introducing another language
		"""
		
		pass

	def filterData(self, instructions) -> Generator:
		"""
			Filter table's data
		"""
		
		# check type of recieved instructions
		if instructions.get('type') == Constants.CONDITIONS_SORTING:
			# filter according to the conditions
			del instructions['type']
			def __check(row: list) -> bool:
				for instruction in instructions.values():
					# check for errors in instruction
					if instruction['options'][0] is None and instruction['options'][1] is None:
						raise Exception(f"Problems with instruction {instruction} to the column {column}")
					# check instructions according to the type
					match instruction['type']:
						case Constants.NUMERIC:
							if not (instruction['options'][0] is None) and float(row[instruction['id'] + 1]) < instruction['options'][0]:
								return False
							if not (instruction['options'][1] is None) and float(row[instruction['id'] + 1]) > instruction['options'][1]:
								return False
						case Constants.TEXT:
							if not (instruction['options'][0] is None) and not re.match(rf".*{instruction['options'][0]}.*", row[instruction['id'] + 1]):
								return False
							if not (instruction['options'][1] is None) and not re.search(rf"{instruction['options'][1]}", row[instruction['id'] + 1]):
								return False
						case Constants.DATETIME:
							# check for invalid date format
							if (buffer:=QtCore.QDateTime.fromString(row[instruction['id'] + 1], Constants.DATETIME_FORMAT)).isNull():
								raise Exception(f"Unreadable date {row[instruction['id'] + 1]} (required format: {Constants.DATETIME_FORMAT})")

							if not (instruction['options'][0] is None) and instruction['options'][0].isValid() and buffer < instruction['options'][0]:
								return False
							if not (instruction['options'][1] is None) and instruction['options'][1].isValid() and buffer > instruction['options'][1]:
								return False
				return True
			# data filter
			data = filter(__check, list(self.getData()))
		elif instructions.get('type') == Constants.SORTING:
			# sorting
			del instructions['type']
			def __check(row1: list, row2: list) -> bool:
				for instruction in sorted(instructions.values(), key=lambda instruction_: instruction_['order']):
					index = instruction['id'] + 1
					match instruction['type']:
						case Constants.NUMERIC:
							bufferDate1, bufferDate2 = float(row1[index]), float(row2[index])
						case Constants.TEXT:
							bufferDate1, bufferDate2 = row1[index], row2[index]
						case Constants.DATETIME:
							bufferDate1 = QtCore.QDateTime.fromString(row1[index], Constants.DATETIME_FORMAT)
							if bufferDate1.isNull():
								raise Exception(f"Unreadable date {row1[index]} (required format: {Constants.DATETIME_FORMAT})")
							bufferDate2 = QtCore.QDateTime.fromString(row2[index], Constants.DATETIME_FORMAT)
							if bufferDate2.isNull():
								raise Exception(f"Unreadable date {row2[index]} (required format: {Constants.DATETIME_FORMAT})")
					if bufferDate1 == bufferDate2:
						continue
					match instruction['option']:
						case Constants.ASCENDING:
							return -1 if bufferDate1 < bufferDate2 else 1
						case Constants.DESCENDING:
							return -1 if bufferDate1 > bufferDate2 else 1
				return 0
			# get data from table
			data = list(self.getData())
			data.sort(key=cmp_to_key(__check))
		else:
			raise Exception(f"Unrecognised instructions type {instructions.get('type')} in {instructions}")
		# yield each row of data
		for row in data:
			yield row

	def reload(self, instructions: dict|None=None, *args):
		"""
			Reload data in table by database or filter
		"""

		# set table's dimensions
		self.transactionsView.setColumnCount(len(self.__columns))
		self.transactionsView.setHorizontalHeaderLabels(self.__columns.keys())
		# decide get data by database or filter
		if instructions is None:
			data = gen_data()
		else:
			data = list(self.filterData(instructions))
		# clear data in table
		self.transactionsView.clearContents()
		# set first row with 'id'
		self.transactionsView.setRowCount(len(data) + 1)
		self.transactionsView.setVerticalHeaderLabels(['id'])
		# inserting items into the table
		for i, rowData in enumerate(data, start=1):
			item = QtWidgets.QTableWidgetItem(str(rowData[0]))
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.transactionsView.setVerticalHeaderItem(i, item)
			for j, item in enumerate(rowData[1:]):
				item = QtWidgets.QTableWidgetItem(str(item))
				item.setTextAlignment(QtCore.Qt.AlignCenter)
				self.transactionsView.setItem(i, j, item)


if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = Window({'inner': False, 'sell': True, 'clients': True})
	window.show()
	sys.exit(app.exec_())
