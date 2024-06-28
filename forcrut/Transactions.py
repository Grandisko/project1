from PyQt5 import QtWidgets, QtCore
from .Constants import centerWidget, Constants
from .Filter import FilterButton, ConditionsWidget
from typing import Generator
from .NewTransaction import OperationWindow
from DB.DB import Database


class MainWindow(QtWidgets.QMainWindow):
	"""
		Main window with transactions and other functionality
	"""

	def __init__(self, user: int, params: dict, columns: dict, db: Database) -> None:
		"""
			:param user: user's id in database,
			:param params: dict of keys and boolean values
				inner: permission for INNER_OPERATIONS,
				outer: permission for OUTER_OPERATIONS,
				clients: permission to saw/edit clients,
				redact: permission to edit information,
				super: super-user;
			:param columns: dict of keys (columns' names) and values (their data types)
				Example, {'information': TEXT},
			:param db: Database of the app
		"""

		# QMainWindow init
		super().__init__()
		# set title and window dimensions
		self.setWindowTitle("Транзакции")
		self.setGeometry(*centerWidget(800, 600))
		# required fields
		self.__user = user
		self.__columns = columns
		self.super = params.get('super')
		self.redact = params.get('redact')
		self.__db = db
		# central widget settings
		self.centralWidget = QtWidgets.QWidget(self)
		self.centralWidget.setObjectName("MainContainer")
		self.setCentralWidget(self.centralWidget)
		# main layout
		self.mainLayout = QtWidgets.QGridLayout(self.centralWidget)
		self.mainLayout.setObjectName("Main-layout")
		for i in range(2, 5):
			self.mainLayout.setRowStretch(i, 1)
		# widget for label and operations' buttons
		bufferWidget = QtWidgets.QWidget(self.centralWidget)
		self.mainLayout.addWidget(bufferWidget, 0, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		bufferLayout = QtWidgets.QVBoxLayout(bufferWidget)
		label = QtWidgets.QLabel('Операции:', bufferWidget)
		label.setObjectName("labelOperations")
		bufferLayout.addWidget(label)
		# widget for operations' buttons
		self.operationsWidget = QtWidgets.QWidget(bufferWidget)
		bufferLayout.addWidget(self.operationsWidget)
		# form operations' buttons
		self.operations = QtWidgets.QButtonGroup(self.operationsWidget)
		bufferLayout = QtWidgets.QHBoxLayout(self.operationsWidget)
		if params.get('inner'):
			for operation_name, text in Constants.INNER_OPERATIONS.items():
				bufferElem = QtWidgets.QPushButton(text)
				bufferElem.setObjectName(operation_name)
				bufferElem.setText(text)
				bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
				# bufferElem.clicked.connect(self.__getattribute__(operation_name))
				bufferLayout.addWidget(bufferElem)
				self.operations.addButton(bufferElem, id=Constants.OPERATIONS_TYPES[operation_name])
		if params.get('sell'):
			bufferElem = QtWidgets.QPushButton("Продать{}товар".format(' ' if not params.get('inner') else '\n'))
			bufferElem.setObjectName('sellGoods')
			bufferElem.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
			# bufferElem.clicked.connect(self.sellGoods)
			bufferLayout.addWidget(bufferElem)
			self.operations.addButton(bufferElem, id=Constants.OPERATIONS_TYPES['sellGoods'])
		self.operations.buttonClicked[int].connect(self.createOperation)
		# widget for label and views' buttons
		bufferWidget = QtWidgets.QWidget(self.centralWidget)
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
		bufferElem.clicked.connect(lambda: self.openSource("stuffView"))
		viewButtonsLayout.addWidget(bufferElem, 0, 0)
		# form template-view button
		bufferElem = QtWidgets.QPushButton("Шаблон\nдоговора")
		bufferElem.setObjectName("templateView")
		bufferElem.clicked.connect(lambda: self.openSource("templateView"))
		viewButtonsLayout.addWidget(bufferElem, 0, 1)
		# form clients-view button if necessary
		if params.get('clients'):
			bufferElem = QtWidgets.QPushButton("Клиенты")
			bufferElem.setObjectName("clientsView")
			bufferElem.clicked.connect(lambda: self.openSource("clientsView"))
			viewButtonsLayout.addWidget(bufferElem, 1, 0, 1, 2)
		# form the table
		self.transactionsView = QtWidgets.QTableWidget(self.centralWidget)
		self.transactionsView.setMinimumSize(770, 390)
		self.transactionsView.setObjectName("transactionsView")
		self.transactionsView.setSortingEnabled(False)
		self.transactionsView.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.transactionsView.setWordWrap(True)
		self.mainLayout.addWidget(self.transactionsView, 2, 0, 3, 3)
		# adaptability of the table
		self.transactionsView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		self.transactionsView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
		# getData function to get data from the table
		def getData():
			for i in range(1, self.transactionsView.rowCount()):
				yield [self.transactionsView.verticalHeaderItem(i).text()] + \
				[buffer.text() if (buffer:=self.transactionsView.item(i, j)) else None for j in range(len(self.__columns))]
		self.transactionsView.getData = getData
		# form the filter button
		self.filterButton = FilterButton("Фильтр", self.__columns, table=self.transactionsView, parent=self.centralWidget, handler=self.reload)
		self.filterButton.setObjectName("dataFilter")
		self.filterButton.setMinimumSize(100, 30)
		# self.mainLayout.setRowMinimumHeight(1, 30)
		self.mainLayout.addWidget(self.filterButton, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
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

	def createOperation(self, operation_id: int):
		"""
			Creates new transaciton with operation
		"""

		# clicked button
		bufferButton = self.operations.button(operation_id)
		# turn off button
		bufferButton.setEnabled(False)
		# new operation window
		bufferNewOperation = OperationWindow(operation_id, bufferButton.text(), parent=self, user=self.__user, db=self.__db)
		# turn on the button after creating will be completed
		bufferNewOperation.closed.connect(lambda: bufferButton.setEnabled(True))
		# show the new operation window
		bufferNewOperation.show()

	def openSource(self, source_name: str) -> None:
		"""

		"""

		print(source_name)

	def retranslate(self):
		"""
			Possible for introducing another language
		"""

		pass

	def reload(self, data: Generator|None=None):
		"""
			Reload data in table by database or filter
		"""

		# set table's dimensions
		self.transactionsView.setColumnCount(len(self.__columns))
		self.transactionsView.setHorizontalHeaderLabels(self.__columns.keys())
		# decide get data by database or generator
		if data is None:
			data = self.__db.get_transactions()
		else:
			data = list(data)
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
	window = MainWindow({'inner': False, 'sell': True, 'clients': True})
	window.show()
	sys.exit(app.exec_())
