from PyQt5 import QtCore, QtWidgets
from Constants import centerWidget, Constants, generateContract
from .Filter import FilterButton
from DB.DB import Database, TABLES
from typing import Callable, Iterator, Generator
from datetime import datetime


def createTransaction(operation_id: int, operation_name: str, user: int, db: Database, parent: QtCore.QObject|None=None) -> QtWidgets.QDialog:
	"""
		Function that creates window with new transaction's settings according to the type of the operation to be created
	"""
	
	match operation_id:
		case Constants.OPERATION_RELOCATE:
			from .Relocate import OperationRelocate
			operation_class = OperationRelocate
		case Constants.OPERATION_SELL:
			from .Sell import OperationSell
			operation_class = OperationSell
		case Constants.OPERATION_ACCEPT:
			from .Accept import OperationAccept
			operation_class = OperationAccept
		case Constants.OPERATION_WRITE_OFF:
			from .WriteOff import OperationWriteOff
			operation_class = OperationWriteOff
		
	return operation_class(operation_id, operation_name, user, db, parent)


class ConfirmCreatingBox(QtWidgets.QDialog):
	"""
		MessageBox to confirm creating a new transaction
	"""

	def __init__(self, title: str, message: str, parent: QtCore.QObject|None=None):
		"""
			:param title: title of the window
			:param message: information on the window
			:param parent: to whom to attach
		"""
		
		# QDialog settings
		super().__init__(parent)
		self.setWindowTitle(title)
		self.setGeometry(*centerWidget(550, 200))
		# main layout
		bufferLayout = QtWidgets.QVBoxLayout(self)
		# information of the box
		self.info = QtWidgets.QTextEdit(message)
		self.info.setAlignment(QtCore.Qt.AlignCenter)
		bufferLayout.addWidget(self.info)
		# confirm and reject buttons
		self.confirmButtons = QtWidgets.QDialogButtonBox(
			QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok, parent=self
			)
		self.confirmButtons.setObjectName("Options")
		okButton = self.confirmButtons.button(QtWidgets.QDialogButtonBox.Ok)
		okButton.setText("Ок")
		okButton.setDefault(True)
		okButton.setFocus()
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Cancel).setText("Отмена")
		self.confirmButtons.setMinimumHeight(30)
		bufferLayout.addWidget(self.confirmButtons)
		self.confirmButtons.accepted.connect(self.accept)
		self.confirmButtons.rejected.connect(self.reject)
		self.confirmButtons.setCenterButtons(True)

	@staticmethod
	def question(parent, title, message):
		"""
			Creates question ConfirmCreatingBox
		"""

		dialog = ConfirmCreatingBox(title, message, parent)
		result = dialog.exec_()
		return result == QtWidgets.QDialog.Accepted


class AbstractOperationWindow(QtWidgets.QDialog):
	"""
		QDialog window with creation new operation
	"""

	closed = QtCore.pyqtSignal()
	# newTransaction = QtCore.pyqtSignal()  # TODO нужен ли он вообще

	def __init__(self, operation_id: int, operation_name: str, user: int, db: Database, parent: QtCore.QObject|None=None) -> None:
		"""
			:param operation_id: operation id from OPERATIONS_TYPES,
			:param operation_name: operation name,
			:param user: user's id in database,
			:param parent: parent QObject for widget,
			:param db: Database of the app
		"""
		
		# QDialog init
		super().__init__(parent)
		# QDialog settings
		self.setWindowTitle("Новая транзакция")
		self.setGeometry(*centerWidget(800, 600))
		# necessary variables
		self.__operation = dict()
		self.__operation['operation'] = ' '.join(operation_name.lower().split())
		self.__operation['type'] = operation_id
		self.__operation['context'] = {}
		self.__operation_full_context = {}
		self.__user = user
		self.__db = db
		self.columns = {}
		self.__info_fields = {}
		# form all possible columns
		self.columns['warehouse'] = TABLES['Warehouse'].copy()
		self.columns['warehouse'].pop('id')
		self.columns['goods'] = TABLES['Goods'].copy()
		self.columns['goods'].pop('id')
		self.columns['warehouse_goods'] = TABLES['Goods'].copy() | {'count': Constants.NUMERIC, 'expire_date': Constants.DATETIME}
		self.columns['warehouse_goods'].pop('id')
		# main layout
		self.mainLayout = QtWidgets.QGridLayout(self)
		# rows' counter
		row = 0
		# layout with information about new transaction
		bufferLayout = QtWidgets.QVBoxLayout()
		self.mainLayout.addLayout(bufferLayout, row, 0, 1, 2)
		# label for the information
		bufferLayout.addWidget(bufferLabel:=QtWidgets.QLabel('Операция', self))
		bufferLabel.setObjectName("operationLabel")
		bufferLabel.setFixedHeight(20)
		# text plain for the infromtaion
		self.operationInfo = QtWidgets.QPlainTextEdit(self)
		self.operationInfo.setObjectName("operationInfo")
		self.operationInfo.setPlainText(f"Операция: {self.__operation['operation']}")
		self.operationInfo.setReadOnly(True)
		self.operationInfo.setFixedHeight(80)
		bufferLayout.addWidget(self.operationInfo)
		# layout with check box contract opening
		bufferLayout = QtWidgets.QHBoxLayout()
		self.mainLayout.addLayout(bufferLayout, row, 2, QtCore.Qt.AlignCenter)
		# label for the check box
		bufferLayout.addWidget(bufferLabel:=QtWidgets.QLabel('Хотите ли вы просмотреть договор после сохранения операции?', self))
		bufferLabel.setWordWrap(True)
		bufferLabel.setMinimumSize(190, 60)
		bufferLabel.setAlignment(QtCore.Qt.AlignCenter)
		# the check box itself
		self.contractView = QtWidgets.QCheckBox("", self)
		bufferLayout.addWidget(self.contractView)
		self.contractView.setChecked(True)
		row += 1
		# create the required number of tables
		match operation_id:
			case  Constants.OPERATION_ACCEPT:
				self.__tables_interface = [(True, "<h3>Доступный товар</h3>")]
				combo_boxes_q = 1
			case Constants.OPERATION_RELOCATE:
				self.__tables_interface = [(True, "<h3>Доступный товар склада</h3>")]
				combo_boxes_q = 2
			case Constants.OPERATION_WRITE_OFF:
				self.__tables_interface = [(True, "<h3>Доступный товар склада</h3>"), (False, "<h3>К списанию</h3>")]
				combo_boxes_q = 1
			case Constants.OPERATION_SELL:
				self.__tables_interface = [(True, "<h3>Доступный товар склада</h3>"), (False, "<h3>Корзина</h3>")]
				combo_boxes_q = 2
		# combo boxes with choice
		self.combo_boxes = []
		bufferLayout = QtWidgets.QHBoxLayout()
		self.mainLayout.addLayout(bufferLayout, row, 0, 1, 3)
		for _ in range(combo_boxes_q):
			self.combo_boxes.append(bufferComboBox:=QtWidgets.QComboBox(self))
			bufferComboBox.setEditable(True)
			bufferComboBox.setMaxVisibleItems(20)
			bufferComboBox.setFixedWidth(350)
			bufferLayout.addWidget(bufferComboBox, QtCore.Qt.AlignCenter)
		row += 1
		# form tables
		self.tables, self.layouts = [], []
		for i, (table_interface, table_label) in enumerate(self.__tables_interface):
			# layout for the table and its label
			containerLayout = QtWidgets.QVBoxLayout()
			self.layouts.append(containerLayout)
			# table's label
			bufferLabel = QtWidgets.QLabel(table_label)
			bufferLabel.setAlignment(QtCore.Qt.AlignCenter)
			containerLayout.addWidget(bufferLabel)
			# create table itself
			bufferTable = self.new_table(i, self)
			# form the filter button if necessary
			if table_interface:
				self.filterButton = FilterButton("Фильтр", [], table=bufferTable, parent=self, handler=self.reload)
				self.filterButton.setObjectName("dataFilter")
				self.filterButton.setFixedSize(100, 30)
				self.mainLayout.addWidget(self.filterButton, row, 0, QtCore.Qt.AlignLeft)
				row += 1
			# table settings
			if table_interface:
				for i in range(row, row+3):
					self.mainLayout.setRowStretch(i, 1)
			else:
				bufferTable.setMaximumHeight(120)
			# add table to the main layout
			self.mainLayout.addLayout(containerLayout, row, 0, 3, 3)
			row += 3
			# container layout settings
			containerLayout.setContentsMargins(0, 0, 0, 0)
			containerLayout.setSpacing(0)
			containerLayout.addWidget(bufferTable)
			# add table to the tables
			self.tables.append(bufferTable)
			# form the reload button if necessary
			if table_interface:
				self.reloadButton = QtWidgets.QPushButton("Обновить", self)
				self.reloadButton.setObjectName("reloadTable")
				self.reloadButton.setFixedSize(100, 30)
				self.reloadButton.clicked.connect(lambda: self.reload())
				self.mainLayout.addWidget(self.reloadButton, row, 2, QtCore.Qt.AlignRight)
				row += 1
		# hide table and buttons (filter, reload)
		self.hide_content()
		# special operation's window method
		self.init_widget()
		# buttons (Ok, Cancel)
		self.confirmButtons = QtWidgets.QDialogButtonBox(
			QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok, parent=self
			)
		self.confirmButtons.setObjectName("Options")
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Ok).setText("Ок")
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Cancel).setText("Отмена")
		self.mainLayout.setRowMinimumHeight(row, 30)
		self.mainLayout.addWidget(self.confirmButtons, row, 0, 1, 3)
		self.confirmButtons.accepted.connect(self.acceptCreating)
		self.confirmButtons.rejected.connect(self.close)
		self.confirmButtons.setCenterButtons(True)
		row += 1

	def hide_content(self):
		"""
			Hides tables, filter and reload buttons
		"""

		for layout in self.layouts:
			for i in range(layout.count()):
				widget = layout.itemAt(i).widget()
				if widget:
					widget.hide()
		self.filterButton.setHidden(True)
		self.reloadButton.setHidden(True)

	def visible_content(self):
		"""
			Makes visible tables, filter and reload buttons
		"""

		for layout in self.layouts:
			for i in range(layout.count()):
				widget = layout.itemAt(i).widget()
				if widget:
					widget.show()
		self.filterButton.setVisible(True)
		self.reloadButton.setVisible(True)

	def ready_to_accept(self):
		"""
			Method should be used to set the button 'Ok' to be enabled
		"""
		
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(bool(self.__operation['context']))

	def edit_info(self, field: str, value: str):
		"""
			Edits the information in self.operationInfo according to the field by the value
			:param field: name of the operation info's field is gоt,
			:param value: new field value
		"""

		bufferInfo = self.operationInfo.toPlainText().split('\n')
		for i in range(len(bufferInfo)):
			bufferField = bufferInfo[i].split(':')[0].strip()
			if bufferField == field:
				bufferInfo[i] = bufferField + f': {value}'
				break
		self.operationInfo.setPlainText('\n'.join(bufferInfo))

	def get_info(self, field: str):
		"""
			Gets field from the self.operationInfo
			:param field: name of the operation info's field is gоt
		"""

		for i in range(len(bufferInfo:=self.operationInfo.toPlainText().split('\n'))):
			bufferField = list(map(lambda part: part.strip(), bufferInfo[i].split(':')))
			if bufferField[0] == field:
				return bufferField[1] if bufferField[1] else None

	def init_widget(self):
		"""
			Method that is overridden in child classes
		"""		

		pass

	def getData(self, table: QtWidgets.QTableWidget, len_columns: int) -> Generator:
		"""
			Returns data from the QTableWidget
			:param table: table from which getting data,
			:param len_columns: number of elements in header of the table that is got
		"""

		for i in range(1, table.rowCount()):
			yield [table.verticalHeaderItem(i).text()] + \
			[buffer.text() if (buffer:=table.item(i, j)) else None for j in range(len_columns)]

	def new_table(self, table_id: int, parent: QtCore.QObject|None=None) -> QtWidgets.QTableWidget:
		"""
			Creates new empty table
			:param table_id: integer that's used as object name for the table
		"""

		# form the table
		bufferTable = QtWidgets.QTableWidget(parent)
		bufferTable.setObjectName(f"table_{table_id}")
		bufferTable.setSortingEnabled(False)
		bufferTable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		bufferTable.setWordWrap(True)
		# adaptability of the table
		bufferTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		# TODO troubles with rows to contents
		# bufferTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
		# bufferTable.resizeRowsToContents()
		# bufferTable.resizeColumnsToContents()
		# bufferTable.update()

		return bufferTable

	def acceptCreating(self, text: str):
		"""
			Handler Ok button, which creates new transactions
			:param text: message of the confirm box question
		"""
		
		# create question box to confirm creating of a new transaction
		reply = ConfirmCreatingBox.question(
			self, "Подтверждение создания операции", text
			)
		# create a new transaction
		if reply:
			# error is occured -> critical box with it
			try:
				# raise Exception("Something went wrong")
				# TODO отправка данных для создания транзакции
				self.__operation = self.__operation | {'who': self.__user, 'datetime': datetime.now().strftime(Constants.DATETIME_DATETIME_FORMAT)}
				print(f"emit({self.__operation})")
				bufferText = text.replace('<h3>', '').replace('</h3>', '\n').replace('<h6>', '').replace('</h6>', '\n')
				generate_contract(self.__operation['type'], self.__operation['operation'], self.__operation['datetime'], bufferText, to_open=True)
				QtWidgets.QMessageBox.information(self, "Успешно", "Операция прошла успешно!")
			except Exception as err:
				QtWidgets.QMessageBox.critical(self, "Ошибка", f"При выполнении операции возникла ошибка:\n'{err}'!")
			# close window
			self.close()

	def reload(self, *args, **kwargs):
		"""
			Method that is overridden in child classes
		"""

		pass

	def closeEvent(self, event):
		"""
			Close event of the window
		"""

		self.closed.emit()
		self.filterButton.close()
		super().closeEvent(event)


if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = OperationWindow()
	window.show()
	sys.exit(app.exec_())
