import os
import sys
from PyQt5.QtWidgets import QApplication
from .Authorization import AuthorizationWindow


# added directories
for directory in map(os.path.abspath, filter(os.path.isdir, os.listdir(os.path.dirname(os.path.dirname(__file__))))):
	if directory not in sys.path:
		sys.path.append(directory)

app = QApplication(sys.argv)
window = AuthorizationWindow()
window.show()
