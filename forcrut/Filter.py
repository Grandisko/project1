from PyQt5 import QtWidgets, QtCore, QtGui
from Constants import center_widget, Constants
from functools import partial
from functools import cmp_to_key
import re
from typing import Callable, Any, Iterator
import warnings


class FilterButton(QtWidgets.QToolButton):
	"""
		QToolButton as FilterButton.
		Example:
			filterButton =  FilterButton("Фильтр", dict of columns, table=table with data to filter, parent=any widget, handler=function that inserts data into the table)
			filterButton.setObjectName("dataFilter")
			...
	"""

	filtered = QtCore.pyqtSignal(object)

	def __init__(self, text: str, columns: dict, table: QtWidgets.QTableWidget|None, parent: QtCore.QObject|None=None, handler: Callable[[QtCore.QObject, dict], Any]|None=None) -> None:
		"""
			:param text: label text for button
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param parent: parent QObject for filter button,
			:param handler: function, which takes filtered data
		"""

		super().__init__()
		# two types filtering data and others necessary variables 
		self.__table = table
		self.__columns = columns
		self.__handler = handler
		self.sortingWidget = None
		self.conditionsWidget = None
		# QToolButton settings
		self.setText(text)
		self.setParent(parent)
		# form popup menu for the filter button
		menu = QtWidgets.QMenu()
		menu.addAction('Сортировать').triggered.connect(self.sortDataMenu)
		menu.addAction('Фильтровать по условию').triggered.connect(self.filterDataMenu)
		# menu setting
		self.setMenu(menu)
		self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

	def setColumns(self, columns: dict):
		"""
			Sets columns
		"""

		self.__columns = columns

	def sortDataMenu(self) -> None:
		"""
			Shows a sorting menu
		"""

		if self.sortingWidget is None:
			self.sortingWidget = SortingWidget(self.__columns, table=self.__table, parent=self, handler=self.__handler)
			self.sortingWidget.filtered.connect(self.filteredData)
			self.sortingWidget.closed.connect(lambda: setattr(self, 'sortingWidget', None))
			self.sortingWidget.show()

	def filterDataMenu(self) -> None:
		"""
			Shows a filtering menu
		"""
		
		if self.conditionsWidget is None:
			self.conditionsWidget = ConditionsWidget(self.__columns, table=self.__table, parent=self, handler=self.__handler)
			self.conditionsWidget.filtered.connect(self.filteredData)
			self.conditionsWidget.closed.connect(lambda: setattr(self, 'conditionsWidget', None))
			self.conditionsWidget.show()

	def filteredData(self, data: Iterator) -> None:
		"""
			Processes the filtered signal of the menu
		"""

		self.filtered.emit(data)

	def closeEvent(self, event) -> None:
		"""
			Processes closing event
		"""

		# close sorting widget if it exists
		if not self.sortingWidget is None:
			self.sortingWidget.close()
		# close conditions widget if it exists
		if not self.conditionsWidget is None:
			self.conditionsWidget.close()


class AbstractFilterWidget(QtWidgets.QDialog):
	"""
		Parent of filter widgets that have signal
			closed: when widget is closing,
			filtered: when data is filtered
	"""

	closed = QtCore.pyqtSignal()
	filtered = QtCore.pyqtSignal(object)

	def __init__(self, columns: dict, table: QtWidgets.QTableWidget|None, title: str="Параметры фильтра", parent: QtCore.QObject|None=None, handler: Callable[[QtCore.QObject, dict], None]|None=None) -> None:
		"""
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param table: QTableWidget with data to filter,
			:param title: title of QDialog,
			:param parent: parent QObject for widget,
			:param handler: function, which takes filtered data
		"""

		super().__init__(parent)
		# necessary variables
		self.instructions = dict()
		self.options = []
		self.get_columns = lambda: columns
		# QDialog setting
		self.setWindowTitle(title)
		# main layout
		self.mainLayout = QtWidgets.QVBoxLayout(self)
		# grid layout
		self.gridWidget = QtWidgets.QWidget(self)
		self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
		self.mainLayout.addWidget(self.gridWidget)
		# buttons (Ok, Cancel)
		self.confirmButtons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok , parent=self)
		self.confirmButtons.setObjectName("Options")
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Ok).setText("Ок")
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Cancel).setText("Отмена")
		self.mainLayout.addWidget(self.confirmButtons)
		self.confirmButtons.accepted.connect(lambda: self.acceptFilter(table, handler))
		self.confirmButtons.rejected.connect(self.close)
		self.confirmButtons.setCenterButtons(True)

	def acceptFilter(self, table: QtWidgets.QTableWidget, handler: Callable[[QtCore.QObject, dict], None]|None=None) -> None:
		"""
			Processes Ok button, which filter data.
			:param table: QtWidgets.QTableWidget with data to filter,
			:param handler: function, which takes filtered data
		"""

		self.close()

	def closeEvent(self, event) -> None:
		"""
			Processes closing event
		"""

		self.closed.emit()
		self.instructions = {}
		super().closeEvent(event)


class SortingWidget(AbstractFilterWidget):
	"""
		Widget with sorting settings
	"""

	def __init__(self, columns: dict, parent: QtCore.QObject|None=None, **kwargs) -> None:
		"""
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param table: QTableWidget with data to filter,
			:param title: title of QDialog,
			:param parent: parent QObject for widget,
			:param handler: function, which takes filtered data
			Ps. doesn't process column_type = -1
		"""

		super().__init__(columns, parent=parent, **kwargs)
		# type of the instruction
		self.instructions['__type__'] = Constants.SORTING
		# variable containing the last instruction sequence number
		self.__q = 0
		# QDialog setting
		self.setGeometry(*center_widget(400, 75*(len(columns)+2)))
		# filling header fields
		for j, field in enumerate(['<b>Поле</b>', '<b>Порядок</b>', '<b>По возрастанию</b>', '<b>По убыванию</b>']):
			bufferElem = QtWidgets.QLabel(field, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
			self.gridLayout.addWidget(bufferElem, 0, j, QtCore.Qt.AlignCenter)
		# filling the settings
		i = 1
		for column, columnType in columns.items():
			# possible here to add checking missed Columns
			# column label
			bufferElem = QtWidgets.QLabel(column, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			self.gridLayout.addWidget(bufferElem, i, 0, QtCore.Qt.AlignCenter)
			# button group and spinbox
			bufferElem = QtWidgets.QButtonGroup(self.gridWidget)
			self.gridLayout.addWidget(spinBox:=QtWidgets.QSpinBox(self.gridWidget), i, 1, QtCore.Qt.AlignCenter)
			spinBox.setRange(0, 0)
			spinBox.setAlignment(QtCore.Qt.AlignCenter)
			spinBox.setEnabled(False)
			spinBox.valueChanged.connect(partial(self.updateSortOrder, i-1))
			self.options.append([spinBox, bufferElem])
			# first radio button
			self.gridLayout.addWidget(btn1:=QtWidgets.QRadioButton("", self.gridWidget), i, 2, QtCore.Qt.AlignCenter)
			bufferElem.addButton(btn1, 0)
			# second radio button
			self.gridLayout.addWidget(btn2:=QtWidgets.QRadioButton("", self.gridWidget), i, 3, QtCore.Qt.AlignCenter)
			bufferElem.addButton(btn2, 1)
			# handler button group
			bufferElem.buttonClicked.connect(partial(self.addSortOrder, i-1))
			i += 1

	def updateSortOrder(self, rowId: int, value: int) -> None:
		"""
			Processes sorting order 
		"""

		absentValue = set(range(1, self.__q + 1)) - {spinBox.value() for spinBox, _ in self.options}
		for i, [spinBox, _] in enumerate(self.options):
			if i != rowId and spinBox.value() == value:
				spinBox.setValue(absentValue.pop())
				break

	def addSortOrder(self, rowId: int):
		"""
			Processes new setting
		"""

		if (spinBox:=self.options[rowId][0]).value() == 0:
			spinBox.setEnabled(True)
			self.__q += 1
			for bufferSpinBox, _ in self.options:
				if bufferSpinBox.value() != 0 or bufferSpinBox == spinBox:
					bufferSpinBox.setRange(1, self.__q)
			spinBox.setValue(self.__q)

	def acceptFilter(self, table: QtWidgets.QTableWidget, handler: Callable[[QtCore.QObject, dict], None]|None=None) -> None:
		"""
			Processes Ok button, which filter data.
			:param table: QtWidgets.QTableWidget with data to filter,
			:param handler: function, which takes filtered data
		"""

		# from instructions
		for (column, columnType), [sortOrder, inputs] in zip(self.get_columns().items(), self.options):
			instruction = inputs.checkedId()
			if instruction != -1:
				self.instructions[column] = {'order': sortOrder.value(), 'id': list(self.get_columns().keys()).index(column), 
											 'option': Constants.ASCENDING if instruction == 0 else Constants.DESCENDING, 
											 'type': columnType}
		# check type of instructions
		if self.instructions.get('__type__') == Constants.SORTING:
			# sorting
			del self.instructions['__type__']
			def __check(row1: list, row2: list) -> bool:
				for instruction in sorted(self.instructions.values(), key=lambda instruction_: instruction_['order']):
					index = instruction['id'] + 1
					match instruction['type']:
						case Constants.NUMERIC:
							bufferDate1, bufferDate2 = float(row1[index]), float(row2[index])
						case Constants.FOREIGN_KEY:
							try:
								bufferDate1, bufferDate2 = int(row1[index].split('/')[0]), int(row2[index].split('/')[0])
							except KeyError:
								bufferDate1, bufferDate2 = row1[index], row2[index]
						case Constants.TEXT:
							bufferDate1, bufferDate2 = row1[index], row2[index]
						case Constants.DATETIME:
							bufferDate1 = QtCore.QDateTime.fromString(row1[index], Constants.PYQT_DATETIME_FORMAT)
							if bufferDate1.isNull():
								raise Exception(f"Unreadable date {row1[index]} (required format: {Constants.PYQT_DATETIME_FORMAT})")
							bufferDate2 = QtCore.QDateTime.fromString(row2[index], Constants.PYQT_DATETIME_FORMAT)
							if bufferDate2.isNull():
								raise Exception(f"Unreadable date {row2[index]} (required format: {Constants.PYQT_DATETIME_FORMAT})")
					if bufferDate1 == bufferDate2:
						continue
					match instruction['option']:
						case Constants.ASCENDING:
							return -1 if bufferDate1 < bufferDate2 else 1
						case Constants.DESCENDING:
							return -1 if bufferDate1 > bufferDate2 else 1
				return 0
			# get data from table
			data = list(table.getData())
			data.sort(key=cmp_to_key(__check))
			data = iter(data)
		else:
			raise Exception(f"Unrecognised instructions type {self.instructions.get('type')} in {self.instructions}")
		# data is filtered
		self.filtered.emit(data)
		# process the filtered data
		if handler:
			handler(data)
		# accept filter
		super().acceptFilter(table, handler)

	def closeEvent(self, event):
		"""
			Processes closing event
		"""

		self.__q = 0
		super().closeEvent(event)


class ConditionsWidget(AbstractFilterWidget):
	"""
		Widget with conditions settings
	"""

	def __init__(self, columns: dict, parent: QtCore.QObject|None=None, **kwargs) -> None:
		"""
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param table: QTableWidget with data to filter,
			:param title: title of QDialog,
			:param parent: parent QObject for widget,
			:param handler: function, which takes filtered data
		"""

		super().__init__(columns, parent=parent, **kwargs)
		# type of the instruction
		self.instructions['__type__'] = Constants.CONDITIONS_SORTING
		# QDialog setting
		self.setGeometry(*center_widget(400, 75*(len(columns)+2)))
		# filling header fields
		for j, field in enumerate(['<b>Поле</b>', '<b>Тип</b>', '<b>Первая опция</b>', '<b>Вторая опция</b>']):
			bufferElem = QtWidgets.QLabel(field, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
			self.gridLayout.addWidget(bufferElem, 0, j, QtCore.Qt.AlignCenter)
		# filling the settings
		for i, (column, columnType) in enumerate(columns.items(), start=1):
			self.options.append([])
			bufferElem = QtWidgets.QLabel(column, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			self.gridLayout.addWidget(bufferElem, i, 0, QtCore.Qt.AlignCenter)
			bufferElem = QtWidgets.QLabel(Constants.DATA_TYPES[columnType], parent=self.gridWidget)
			self.gridLayout.addWidget(bufferElem, i, 1, QtCore.Qt.AlignCenter)
			# special filling according to the type of data
			match columnType:
				case Constants.NUMERIC | Constants.TEXT | Constants.FOREIGN_KEY:
					for j, labelName in zip([2, 3], ['Нижняя граница', 'Верхняя граница'] if columnType == Constants.NUMERIC else ['Поиск по значению', 'Поиск по регулярке']):
						optionWidget = QtWidgets.QWidget(self.gridWidget)
						layout = QtWidgets.QVBoxLayout(optionWidget)
						layout.addWidget(label:=QtWidgets.QLabel(labelName, parent=optionWidget))
						label.setWordWrap(True)
						label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

						layout.addWidget(inputLine:=QtWidgets.QLineEdit(optionWidget))
						self.options[i-1].append(inputLine)
						inputLine.setAlignment(QtCore.Qt.AlignCenter)

						if columnType == Constants.NUMERIC:
							inputLine.setValidator(validator:=QtGui.QRegularExpressionValidator(optionWidget))
							validator.setRegularExpression(QtCore.QRegularExpression(r'^[+-]?(\d*\.?\d+)|(\d+)$'))

						self.gridLayout.addWidget(optionWidget, i, j, QtCore.Qt.AlignCenter)
				case Constants.DATETIME:
					for j, labelName in zip([2, 3], ['От', 'До']):
						optionWidget = QtWidgets.QWidget(self.gridWidget)
						layout = QtWidgets.QVBoxLayout(optionWidget)
						layout.addWidget(label:=QtWidgets.QLabel(labelName, parent=optionWidget))
						label.setWordWrap(True)
						label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

						layout.addWidget(inputDate:=QtWidgets.QDateTimeEdit(optionWidget))
						self.options[i-1].append(inputDate)
						inputDate.setCalendarPopup(True)
						inputDate.setDateTime(Constants.DATETIME_DEFAULT)
						self.gridLayout.addWidget(optionWidget, i, j, QtCore.Qt.AlignCenter)
				case -1:
					pass
				case _:
					warnings.warn(f"ConditionsWidget: 'Unrecognised column {columnType}'")

	def acceptFilter(self, table: QtWidgets.QTableWidget, handler: Callable[[QtCore.QObject, dict], None]|None=None) -> None:
		"""
			Processes Ok button, which filter data.
			:param table: QtWidgets.QTableWidget with data to filter,
			:param handler: function, which takes filtered data
		"""

		for (column, columnType), inputs in zip(self.get_columns().items(), self.options):
			instructions = []
			match columnType:
				case Constants.NUMERIC:
					instructions = [float(buffer) if (buffer:=input_.text().strip()) and input_.hasAcceptableInput() else None for input_ in inputs]
				case Constants.TEXT | Constants.FOREIGN_KEY:
					instructions = [buffer if (buffer:=input_.text().strip()) else None for input_ in inputs]
				case Constants.DATETIME:
					instructions = [buffer if (buffer:=input_.dateTime()) != Constants.DATETIME_DEFAULT and not buffer.isNull() else None for input_ in inputs]
				case -1:
					pass

			if [instruction for instruction in instructions if instruction or instruction == 0]:
				self.instructions[column] = {'id': list(self.get_columns().keys()).index(column), 'options': instructions, 'type': columnType}

		# check type of instructions
		if self.instructions.get('__type__') == Constants.CONDITIONS_SORTING:
			# filter according to the conditions
			del self.instructions['__type__']
			def __check(row: list) -> bool:
				for instruction in self.instructions.values():
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
						case Constants.TEXT | Constants.FOREIGN_KEY:
							if not (instruction['options'][0] is None) and not row[instruction['id'] + 1].startswith(instruction['options'][0]):
								return False
							if not (instruction['options'][1] is None) and not re.search(rf"{instruction['options'][1]}", row[instruction['id'] + 1]):
								return False
						case Constants.DATETIME:
							# check for invalid date format
							if (buffer:=QtCore.QDateTime.fromString(row[instruction['id'] + 1], Constants.PYQT_DATETIME_FORMAT)).isNull():
								raise Exception(f"Unreadable date {row[instruction['id'] + 1]} (required format: {Constants.PYQT_DATETIME_FORMAT})")

							if not (instruction['options'][0] is None) and instruction['options'][0].isValid() and buffer < instruction['options'][0]:
								return False
							if not (instruction['options'][1] is None) and instruction['options'][1].isValid() and buffer > instruction['options'][1]:
								return False
				return True
			# data filter
			data = filter(__check, list(table.getData()))
		else:
			raise Exception(f"Unrecognised instructions type {self.instructions.get('type')} in {self.instructions}")
		# data is filtered
		self.filtered.emit(data)
		# process the filtered data
		if handler:
			handler(data)
		# accept filter
		super().acceptFilter(table, handler)
