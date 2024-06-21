from PyQt5 import QtWidgets, QtCore, QtGui
from Constants import centerWidget, Constants, COLUMNS
from functools import partial
from typing import Callable, Any


class FilterButton(QtWidgets.QToolButton):
	"""

	"""

	def __init__(self, text: str, columns: dict, dataHandler: Callable[[QtCore.QObject, dict], tuple[Any, ...]], parent: QtCore.QObject|None=None) -> None:
		"""

		"""
		
		super().__init__()
		# two types filtering data
		self.__columns = columns
		self.orderingWidget = None
		self.conditionsWidget = None
		self.handler = dataHandler
		#
		self.setText(text)
		if not parent is None:
			self.setParent(parent)
		# form popup menu for the filter button
		menu = QtWidgets.QMenu()
		menu.addAction('Сортировать').triggered.connect(self.sortData)
		menu.addAction('Фильтровать по условию').triggered.connect(self.sortDataBy)
		#
		self.setMenu(menu)
		self.setPopupMode(QtWidgets.QToolButton.InstantPopup)

	def sortData(self):
		if self.orderingWidget is None:
			self.orderingWidget = OrderingWidget(list(self.__columns.keys()), parent=self)
			self.orderingWidget.closed.connect(lambda: setattr(self, 'orderingWidget', None))
			self.orderingWidget.toFilter.connect(self.handler)
			self.orderingWidget.show()

	def sortDataBy(self):
		if self.conditionsWidget is None:
			self.conditionsWidget = ConditionsWidget(self.__columns, parent=self)
			self.conditionsWidget.closed.connect(lambda: setattr(self, 'conditionsWidget', None))
			self.conditionsWidget.toFilter.connect(self.handler)
			self.conditionsWidget.show()


class AbstractFilterWidget(QtWidgets.QDialog):
	"""

	"""

	closed = QtCore.pyqtSignal()
	toFilter = QtCore.pyqtSignal(dict)

	def __init__(self, columns: dict | list, title: str="Параметры фильтра", parent: QtCore.QObject|None=None) -> None:
		"""

		"""

		super().__init__(parent)
		
		#
		self.instructions = {}
		self.options = []
		self.get_columns = lambda: columns
		#
		self.setWindowTitle(title)

		self.mainLayout = QtWidgets.QVBoxLayout(self)

		self.gridWidget = QtWidgets.QWidget(self)
		self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
		self.mainLayout.addWidget(self.gridWidget)

		self.confirmButtons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok , parent=self)
		self.confirmButtons.setObjectName("Options")
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Ok).setText("Ок")
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Cancel).setText("Отмена")
		self.mainLayout.addWidget(self.confirmButtons)
		self.confirmButtons.accepted.connect(self.acceptFilter)
		self.confirmButtons.rejected.connect(self.close)
		self.confirmButtons.setCenterButtons(True)

	def acceptFilter(self):
		if self.instructions:
			print("To send:", self.instructions)
			self.toFilter.emit(self.instructions)
		self.close()

	def closeEvent(self, event):
		"""
		
		"""

		self.closed.emit()
		self.instructions = {}
		self.close()


class OrderingWidget(AbstractFilterWidget):
	"""

	"""

	def __init__(self, columns: list, parent: QtCore.QObject|None=None) -> None:
		super().__init__(columns, parent=parent)

		self.setGeometry(*centerWidget(400, 75*(len(columns)+2)))

		for j, field in enumerate(['<b>Поле</b>', '<b>По возрастанию</b>', '<b>По убыванию</b>']):
			bufferElem = QtWidgets.QLabel(field, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
			self.gridLayout.addWidget(bufferElem, 0, j)
		
		for i, column in enumerate(columns, start=1):

			bufferElem = QtWidgets.QLabel(column, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			
			self.gridLayout.addWidget(bufferElem, i, 0)

			bufferElem = QtWidgets.QButtonGroup(self.gridWidget)
			self.options.append(bufferElem)
			self.gridLayout.addWidget(btn1:=QtWidgets.QRadioButton("", self.gridWidget), i, 1)
			bufferElem.addButton(btn1, 0)
			
			self.gridLayout.addWidget(btn2:=QtWidgets.QRadioButton("", self.gridWidget), i, 2)
			bufferElem.addButton(btn2, 1)
			
			# bufferElem.buttonClicked[int].connect(partial(self.updateInstructions, i-1))

	def updateInstructions(self, rowId: int, buttonId: int):
		self.instructions[self.get_columns()[rowId]] = buttonId
		print("Update:", self.instructions)

	def acceptFilter(self):
		for column, inputs in zip(COLUMNS.keys(), self.options):

			instruction = inputs.checkedId()

			if instruction != -1:
				self.instructions[column] = instruction

		super().acceptFilter()


class ConditionsWidget(AbstractFilterWidget):
	"""

	"""

	def __init__(self, columns: dict, parent: QtCore.QObject|None=None) -> None:
		super().__init__(columns, parent=parent)

		self.setGeometry(*centerWidget(400, 75*(len(columns)+2)))

		for j, field in enumerate(['<b>Поле</b>', '<b>Тип</b>', '<b>Первая опция</b>', '<b>Вторая опция</b>']):
			bufferElem = QtWidgets.QLabel(field, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
			self.gridLayout.addWidget(bufferElem, 0, j)

		for i, (column, columnType) in enumerate(columns.items(), start=1):
			self.options.append([])
			bufferElem = QtWidgets.QLabel(column, parent=self.gridWidget)
			bufferElem.setWordWrap(True)
			self.gridLayout.addWidget(bufferElem, i, 0)
			bufferElem = QtWidgets.QLabel(Constants.TYPES[columnType], parent=self.gridWidget)
			self.gridLayout.addWidget(bufferElem, i, 1)
			
			match columnType:
				case Constants.NUMERIC | Constants.TEXT:

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

						self.gridLayout.addWidget(optionWidget, i, j)
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
						inputDate.setDateTime(Constants.DEFAULT_DATETIME)  # QtCore.QDateTime.currentDateTime()
						self.gridLayout.addWidget(optionWidget, i, j)
				case _:
					raise Exception(f"ConditionsWidget: 'Unrecognised column {columnType}'")

	def acceptFilter(self):
		for (column, columnType), inputs in zip(COLUMNS.items(), self.options):
			instructions = []
			match columnType:
				case Constants.NUMERIC:
					instructions = [float(buffer) if (buffer:=input_.text().strip()) and input_.hasAcceptableInput() else None for input_ in inputs]
				case Constants.TEXT:
					instructions = [buffer if (buffer:=input_.text().strip()) else None for input_ in inputs]
				case Constants.DATETIME:
					instructions = [buffer if (buffer:=input_.dateTime()) != Constants.DEFAULT_DATETIME else None for input_ in inputs]

			if any(instructions):
				self.instructions[column] = instructions

		super().acceptFilter()
