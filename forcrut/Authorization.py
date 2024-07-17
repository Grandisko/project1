from PyQt5 import QtWidgets, QtCore
from Constants import center_widget
from .Transactions import MainWindow as Transactions
from DB.DB import TABLES, Database


class AuthorizationWindow(QtWidgets.QDialog):
	"""
		QDialog window with authorization
	"""

	def __init__(self) -> None:
		# QDialog init
		super().__init__()
		# QDialog settings
		self.setWindowTitle("Вход в систему")
		self.setGeometry(*center_widget(400, 300))
		# database
		self.__db = Database()
		# widget for a 'log in' field
		self.mainLayout = QtWidgets.QVBoxLayout(self)
		self.viewButtonsWidget = QtWidgets.QWidget(self)
		self.mainLayout.addWidget(self.viewButtonsWidget)
		# layout of the 'log in' field
		fieldLayout = QtWidgets.QVBoxLayout(self.viewButtonsWidget)
		# label of a login input line
		bufferElem = QtWidgets.QLabel("Логин", self.viewButtonsWidget)
		bufferElem.setObjectName("loginLabel")
		fieldLayout.addWidget(bufferElem)
		# the login input line
		self.loginInput = QtWidgets.QLineEdit(self.viewButtonsWidget)
		self.loginInput.setPlaceholderText("Введите логин")
		self.loginInput.setMaxLength(25)
		fieldLayout.addWidget(self.loginInput)
		# label of a password input line
		bufferElem = QtWidgets.QLabel("Пароль", self.viewButtonsWidget)
		bufferElem.setObjectName("passwordLabel")
		fieldLayout.addWidget(bufferElem)
		# the password input line
		self.passwordInput = QtWidgets.QLineEdit(self.viewButtonsWidget)
		self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Password)
		self.passwordInput.setPlaceholderText("Введите пароль")
		fieldLayout.addWidget(self.passwordInput)
		# the password action representation
		self.passwordAction = self.passwordInput.addAction(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton), QtWidgets.QLineEdit.TrailingPosition)
		self.passwordAction.setCheckable(True)
		self.passwordAction.triggered.connect(self.changeState)
		# label with error if log in failed
		self.warning = QtWidgets.QLabel("", self.viewButtonsWidget)
		self.warning.setObjectName("warningLabel")
		self.warning.setWordWrap(True)  
		self.warning.setAlignment(QtCore.Qt.AlignCenter)
		fieldLayout.addWidget(self.warning)
		# button to verificate entered data
		self.confirmButtons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok, parent=self)
		self.confirmButtons.setObjectName("Ok")
		self.confirmButtons.accepted.connect(self.verificate)
		self.confirmButtons.setCenterButtons(True)
		self.mainLayout.addWidget(self.confirmButtons)

	def changeState(self, normalMode: bool):
		"""
			Change view of password field:
				normal view <-> password view.
			:param normalMode: is normal mode on
		"""

		self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Password if normalMode else QtWidgets.QLineEdit.Normal)
		self.passwordAction.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton if normalMode else QtWidgets.QStyle.SP_DialogCloseButton))

	def verificate(self) -> None:
		"""
			Confirm the received login and password
		"""

		# get input data
		response = self.__db.get_admin_params(self.loginInput.text(), self.passwordInput.text())
		# check response
		if response is None:
			self.passwordInput.clear()
			self.warning.setText("<b style='color: red'>Введенный логин или пароль не привязан ни к какому аккаунту. Введите правильные данные.</b>")
			return
		bufferColumns = TABLES['Transactions']
		bufferColumns.pop('id')
		# create main window
		self.window = Transactions(response.pop('id'), response, bufferColumns, db=self.__db)
		self.close()
		self.window.show()

	def retranslate(self):
		"""
			Possible for introducing another language
		"""
		
		pass


if __name__ == '__main__':
	import sys
	app = QtWidgets.QApplication(sys.argv)
	window = AuthorizationWindow()
	window.show()
	sys.exit(app.exec_())
