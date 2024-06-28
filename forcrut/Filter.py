from PyQt5 import QtWidgets, QtCore, QtGui
from .Constants import centerWidget, Constants
from functools import partial
from typing import Callable, Any


class FilterButton(QtWidgets.QToolButton):
	"""
		QToolButton as FilterButton.
		Example:
			filterButton = FilterButton("Фильтр", columns, dataHandler=self.reload, parent=self.centralWidget)
			filterButton.setObjectName("dataFilter")
			...
	"""

	def __init__(self, text: str, columns: dict, parent: QtCore.QObject | None=None, dataHandler: Callable[[QtCore.QObject, dict], tuple[Any, ...]] | None=None) -> None:
		"""
			:param text: label text for button
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param parent: parent QObject for filter button,
			:param dataHandler: function, which takes instructions (dict) and return filtered data
		"""
		
		super().__init__()
		# two types filtering data and others necessary variables 
		self.__columns = columns
		self.sortingWidget = None
		self.conditionsWidget = None
		self.handler = (lambda: None) if dataHandler is None else dataHandler
		# QToolButton settings
		self.setText(text)
		if not parent is None:
			self.setParent(parent)
		# form popup menu for the filter button
		menu = QtWidgets.QMenu()
		menu.addAction('Сортировать').triggered.connect(self.sortData)
		menu.addAction('Фильтровать по условию').triggered.connect(self.sortDataBy)
		# menu setting
		self.setMenu(menu)
		self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

	def sortData(self):
		"""
			Creats and shows 1 sorting widget
		"""

		if self.sortingWidget is None:
			self.sortingWidget = SortingWidget(self.__columns, parent=self)
			self.sortingWidget.closed.connect(lambda: setattr(self, 'sortingWidget', None))
			self.sortingWidget.toFilter.connect(self.handler)
			self.sortingWidget.show()

	def sortDataBy(self):
		"""
			Creats and shows 1 conditions widget
		"""
		
		if self.conditionsWidget is None:
			self.conditionsWidget = ConditionsWidget(self.__columns, parent=self)
			self.conditionsWidget.closed.connect(lambda: setattr(self, 'conditionsWidget', None))
			self.conditionsWidget.toFilter.connect(self.handler)
			self.conditionsWidget.show()


class AbstractFilterWidget(QtWidgets.QDialog):
	"""
		Parent of filter widgets, which has 2 signals
			closed: when closing widget,
			toFilter: when accepting filter
	"""

	closed = QtCore.pyqtSignal()
	toFilter = QtCore.pyqtSignal(dict)

	def __init__(self, columns: dict, title: str="Параметры фильтра", parent: QtCore.QObject|None=None) -> None:
		"""
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param title: title of QDialog,
			:param parent: parent QObject for widget
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
		self.confirmButtons.accepted.connect(self.acceptFilter)
		self.confirmButtons.rejected.connect(self.close)
		self.confirmButtons.setCenterButtons(True)

	def acceptFilter(self):
		"""
			Handler Ok button
		"""

		if self.instructions:
			self.toFilter.emit(self.instructions)
		self.close()

	def closeEvent(self, event):
		"""
			Handler closing event
		"""

		self.closed.emit()
		self.instructions = {}
		super().closeEvent(event)


class SortingWidget(AbstractFilterWidget):
	"""
		Widget with sorting settings
	"""

	def __init__(self, columns: dict, parent: QtCore.QObject|None=None) -> None:
		"""
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param parent: parent QObject for widget
		"""

		super().__init__(columns, parent=parent)
		# type of the instruction
		self.instructions['type'] = Constants.SORTING
		# variable containing the last instruction sequence number
		self.__q = 0
		# QDialog setting
		self.setGeometry(*centerWidget(400, 75*(len(columns)+2)))
		# filling header fields
		for j, field in enumerate(['<b>Поле</b>', '<b>Порядок</b>', '<b>По возрастанию</b>', '<b>По убыванию</b>']):
			bufferElem = QtWidgets.QLabel(field, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
			self.gridLayout.addWidget(bufferElem, 0, j, QtCore.Qt.AlignCenter)
		# filling the settings
		for i, column in enumerate(columns, start=1):
			# column label
			bufferElem = QtWidgets.QLabel(column, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			self.gridLayout.addWidget(bufferElem, i, 0, QtCore.Qt.AlignCenter)
			# button group and spinbox
			bufferElem = QtWidgets.QButtonGroup(self.gridWidget)
			self.gridLayout.addWidget(spinBox:=QtWidgets.QSpinBox(self.gridWidget), i, 1, QtCore.Qt.AlignCenter)
			spinBox.setRange(0, 0)
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

	def updateSortOrder(self, rowId: int, value: int):
		"""
			Handler sorting order
		"""

		absentValue = set(range(1, self.__q + 1)) - {spinBox.value() for spinBox, _ in self.options}
		for i, [spinBox, _] in enumerate(self.options):
			if i != rowId and spinBox.value() == value:
				spinBox.setValue(absentValue.pop())
				break

	def addSortOrder(self, rowId: int):
		"""
			Handler new setting
		"""

		if (spinBox:=self.options[rowId][0]).value() == 0:
			spinBox.setEnabled(True)
			self.__q += 1
			for bufferSpinBox, _ in self.options:
				if bufferSpinBox.value() != 0 or bufferSpinBox == spinBox:
					bufferSpinBox.setRange(1, self.__q)
			spinBox.setValue(self.__q)


	def acceptFilter(self):
		"""
			Handler Ok button, which forms instructions
		"""

		for (column, columnType), [sortOrder, inputs] in zip(self.get_columns().items(), self.options):
			instruction = inputs.checkedId()
			if instruction != -1:
				self.instructions[column] = {'order': sortOrder.value(), 'id': list(self.get_columns().keys()).index(column), 
											 'option': Constants.ASCENDING if instruction == 0 else Constants.DESCENDING, 
											 'type': columnType}

		super().acceptFilter()

	def closeEvent(self, event):
		"""
			Handler closing event
		"""

		self.__q = 0
		super().closeEvent(event)


class ConditionsWidget(AbstractFilterWidget):
	"""
		Widget with conditions settings
	"""

	def __init__(self, columns: dict, parent: QtCore.QObject|None=None) -> None:
		"""
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param parent: parent QObject for widget
		"""

		super().__init__(columns, parent=parent)
		# type of the instruction
		self.instructions['type'] = Constants.CONDITIONS_SORTING
		# QDialog setting
		self.setGeometry(*centerWidget(400, 75*(len(columns)+2)))
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
					for j, labelName in zip([2, 3], ['Нижняя граница', 'Верхняя граница'] if columnType in [Constants.NUMERIC, Constants.FOREIGN_KEY] else ['Поиск по значению', 'Поиск по регулярке']):
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
						elif columnType == Constants.FOREIGN_KEY:
							inputLine.setValidator(validator:=QtGui.QRegularExpressionValidator(optionWidget))
							validator.setRegularExpression(QtCore.QRegularExpression(r'^\d+$'))

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
				case _:
					raise Exception(f"ConditionsWidget: 'Unrecognised column {columnType}'")

	def acceptFilter(self):
		"""
			Handler Ok button, which forms instructions
		"""
		for (column, columnType), inputs in zip(self.get_columns().items(), self.options):
			instructions = []
			match columnType:
				case Constants.NUMERIC:
					instructions = [float(buffer) if (buffer:=input_.text().strip()) and input_.hasAcceptableInput() else None for input_ in inputs]
				case Constants.FOREIGN_KEY:
					instructions = [int(buffer) if (buffer:=input_.text().strip()) and input_.hasAcceptableInput() else None for input_ in inputs]
				case Constants.TEXT:
					instructions = [buffer if (buffer:=input_.text().strip()) else None for input_ in inputs]
				case Constants.DATETIME:
					instructions = [buffer if (buffer:=input_.dateTime()) != Constants.DATETIME_DEFAULT and not buffer.isNull() else None for input_ in inputs]

			if [instruction for instruction in instructions if instruction or instruction == 0]:
				self.instructions[column] = {'id': list(self.get_columns().keys()).index(column), 'options': instructions, 'type': columnType}

		super().acceptFilter()
