from PyQt5 import QtCore, QtGui, QtWidgets
from .Constants import centerWidget, Constants
from .Filter import FilterButton


class OperationWindow(QtWidgets.QDialog):
	"""
		QDialog window with creation new operation
	"""

	closed = QtCore.pyqtSignal()
	# newTransaction = QtCore.pyqtSignal()  # TODO нужен ли он вообще

	def __init__(self, operation_id: int, operation_name: str, user: int, parent: QtCore.QObject|None=None) -> None:
		"""
			:param operation_id: operation id from OPERATIONS_TYPES,
			:param operation_name: operation name,
			:param user: user's id in database,
			:param parent: parent QObject for widget
		"""
		
		# QDialog init
		super().__init__(parent)
		# QDialog settings
		self.setWindowTitle("Новая транзакция")
		self.setGeometry(*centerWidget(800, 600))
		# necessary variables
		self.__operation = dict.fromkeys(['type', 'field1', 'field2'])
		self.__operation['type'] = ' '.join(operation_name.lower().split())
		self.__buffer = None
		# main layout
		self.mainLayout = QtWidgets.QGridLayout(self)
		for i in range(8):
			self.mainLayout.setRowStretch(i, 1)
		#
		bufferWidget = QtWidgets.QWidget(self)
		self.mainLayout.addWidget(bufferWidget, 0, 0, 1, 2)
		bufferLayout = QtWidgets.QVBoxLayout(bufferWidget)
		#
		bufferLayout.addWidget(bufferLabel:=QtWidgets.QLabel('Операция', bufferWidget))
		bufferLabel.setObjectName("operationLabel")
		#
		self.operationInfo = QtWidgets.QPlainTextEdit(self)
		self.operationInfo.setObjectName("operationInfo")
		self.operationInfo.setPlainText(f"Операция: {self.__operation['type']}\n")
		self.operationInfo.setReadOnly(True)
		palette = self.operationInfo.palette()
		palette.setColor(QtGui.QPalette.Highlight, palette.color(QtGui.QPalette.Base))
		palette.setColor(QtGui.QPalette.HighlightedText, palette.color(QtGui.QPalette.Text))
		self.operationInfo.setPalette(palette)
		bufferLayout.addWidget(self.operationInfo)
		# 
		bufferWidget = QtWidgets.QWidget(self)
		self.mainLayout.addWidget(bufferWidget, 0, 2, QtCore.Qt.AlignCenter)
		bufferLayout = QtWidgets.QHBoxLayout(bufferWidget)
		#
		bufferLayout.addWidget(bufferLabel:=QtWidgets.QLabel('Хотите ли вы просмотреть договор после сохранения операции?', bufferWidget))
		bufferLabel.setWordWrap(True)
		bufferLabel.setMinimumSize(190, 60)
		bufferLabel.setAlignment(QtCore.Qt.AlignCenter)
		#
		self.contractView = QtWidgets.QCheckBox("", bufferWidget)
		bufferLayout.addWidget(self.contractView)
		self.contractView.setChecked(True)
		# form the filter button
		self.filterButton = FilterButton("Фильтр", [], parent=self, dataHandler=self.reload)
		self.filterButton.setObjectName("dataFilter")
		self.filterButton.setMinimumSize(100, 30)
		self.mainLayout.addWidget(self.filterButton, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
		# form the first table
		self.field1 = QtWidgets.QTableWidget(self)
		self.field1.setObjectName("field1")
		self.field1.setSortingEnabled(False)
		self.field1.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.field1.setWordWrap(True)
		self.mainLayout.addWidget(self.field1, 2, 0, 3, 3)
		# form the second table
		self.field2 = QtWidgets.QTableWidget(self)
		self.field2.setObjectName("field2")
		self.field2.setSortingEnabled(False)
		self.field2.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.field2.setWordWrap(True)
		self.mainLayout.addWidget(self.field2, 5, 0, 3, 3)
		# form the reload button
		self.reloadButton = QtWidgets.QPushButton("Обновить", self)
		self.reloadButton.setObjectName("reloadTable")
		self.reloadButton.setMinimumSize(100, 30)
		self.mainLayout.setRowMinimumHeight(8, 30)
		self.reloadButton.clicked.connect(lambda: self.reload())
		self.mainLayout.addWidget(self.reloadButton, 8, 2, QtCore.Qt.AlignRight)
		# buttons (Ok, Cancel)
		self.confirmButtons = QtWidgets.QDialogButtonBox(
			QtWidgets.QDialogButtonBox.StandardButton.Cancel | QtWidgets.QDialogButtonBox.StandardButton.Ok, parent=self
			)
		self.confirmButtons.setObjectName("Options")
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Ok).setText("Ок")
		self.confirmButtons.button(QtWidgets.QDialogButtonBox.Cancel).setText("Отмена")
		self.mainLayout.setRowMinimumHeight(9, 30)
		self.mainLayout.addWidget(self.confirmButtons, 9, 0, 1, 3)
		self.confirmButtons.accepted.connect(self.acceptFilter)
		self.confirmButtons.rejected.connect(self.close)
		self.confirmButtons.setCenterButtons(True)

	def acceptFilter(self):
		"""
			Handler Ok button, which sends new transactions
		"""
		# TODO добавление описания транзакции
		reply = QtWidgets.QMessageBox.question(
			self, "Подтверждение", "Вы хотите выполнить данную операцию?", 
			QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes
			)

		if reply == QtWidgets.QMessageBox.Yes:
			#
			try:
				# raise Exception("Something went wrong")
				QtWidgets.QMessageBox.information(self, "Успешно", "Операция прошла успешно!")
				# self.newTransaction.emit()
				self.close()
			except Exception as err:
				QtWidgets.QMessageBox.information(self, "Ошибка", f"При выполнении операции возникла ошибка:\n'{err}'!")

	def reload(self):
		"""

		"""

		pass

	def closeEvent(self, event):
		"""

		"""

		self.closed.emit()
		super().closeEvent(event)


if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = OperationWindow()
	window.show()
	sys.exit(app.exec_())
