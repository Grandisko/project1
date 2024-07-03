import os
import sys
from PyQt5.QtWidgets import QApplication
from .Authorization import AuthorizationWindow


# added directory with app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"forcrut")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"Dima")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"DB")))


app = QApplication(sys.argv)
window = AuthorizationWindow()
window.show()
