from PyQt5 import QtWidgets, QtCore
from Constants import centerWidget, Constants, COLUMNS
from Transactions import Window as Transactions


def LogIn(login: str, password: str) -> dict | None:
	"""
		Immitation of login and password verification
	"""
	
	return {'inner': True, 'sell': True, 'clients': True, 'redact': True, 'super': True}


class Window(QtWidgets.QDialog):
	"""
		QDialog window with authorization
	"""

	def __init__(self) -> None:
		# QDialog init
		super().__init__()
		# QDialog settings
		self.setWindowTitle("Вход в систему")
		self.setGeometry(*centerWidget(400, 300))
		# widget for a 'log in' field
		mainLayout = QtWidgets.QVBoxLayout(self)
		self.viewButtonsWidget = QtWidgets.QWidget(self)
		self.viewButtonsWidget.setGeometry(70, 40, 261, 141)
		mainLayout.addWidget(self.viewButtonsWidget)
		# layout of the 'log in' field
		fieldLayout = QtWidgets.QVBoxLayout(self.viewButtonsWidget)
		# label of a login input line
		bufferElem = QtWidgets.QLabel("Логин", self.viewButtonsWidget)
		bufferElem.setObjectName("loginLabel")
		fieldLayout.addWidget(bufferElem)
		# the login input line
		self.loginInput = QtWidgets.QLineEdit(self.viewButtonsWidget)
		self.loginInput.setPlaceholderText("Введите логин")
		self.loginInput.setMaxLength(25)  # TODO
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
		fieldLayout.addWidget(self.warning)
		# button to verificate entered data
		bufferElem = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok, parent=self)
		bufferElem.setObjectName("Ok")
		bufferElem.setGeometry(30, 240, 341, 32)
		bufferElem.clicked.connect(self.verificate)
		bufferElem.setCenterButtons(True)
		mainLayout.addWidget(bufferElem)

	def changeState(self, normalMode: bool):
		"""
			Change view of password field:
				normal view <-> password view.
			:param normalMode: is normal mode on
		"""

		self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Password if normalMode else QtWidgets.QLineEdit.Normal)
		self.passwordAction.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton if normalMode else QtWidgets.QStyle.SP_DialogCloseButton))

	def verificate(self, flag:bool) -> None:
		"""
			Confirm the received login and password
		"""

		response = LogIn(self.loginInput.text(), self.passwordInput.text())
		if response is None:
			self.passwordInput.clear()
			self.warning.setText("<b style='color: red'>Введенный логин или пароль не привязан ни к какому аккаунту. Введите правильные данные.</b>")
			self.viewButtonsWidget.setGeometry(70, 40, 261, 171)
			return
		self.window = Transactions(response, COLUMNS)
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
	window = Window()
	window.show()
	sys.exit(app.exec_())
