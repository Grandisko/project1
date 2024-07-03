from PyQt5 import QtCore, QtWidgets
import sqlite3
from forcrut.Constants import Constants
from forcrut.Filter import FilterButton
from DB.DB import Database

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.base_name= 'DB/database.db'

        self.table_name='Client'

        self.con = sqlite3.connect(self.base_name)
        self.cursor = self.con.cursor()



        # количество записей в данной таблице
        self.row_quantity: int = 0
        # количество колонок в данной таблице
        self.column_quantity: int = 0
        
        self.columns: list | None = None
        # Добавляемые/удаляемые ряды в таблицу Если передать sorted словарь, функция вернет отсортированный список ключей:
        self.adding_row  = {}
# =============================================================================
#         # удаляемые ряды в таблицу
#         self.del_row = set()
# =============================================================================
        # редактируемые ячейки в таблице
        self.replace_cell = []
        
        self.setObjectName("MainWindow")
        self.resize(1600, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.Filter_Button = QtWidgets.QPushButton(self.centralwidget)
        self.Filter_Button.setGeometry(QtCore.QRect(10, 20, 201, 30))
        self.Filter_Button.setObjectName("Filter_Button")
        self.Add_Button = QtWidgets.QPushButton(self.centralwidget)
        self.Add_Button.setGeometry(QtCore.QRect(620, 20, 30, 30))
        self.Add_Button.setObjectName("Add_Button")
        self.Add_Button.clicked.connect(self.add_Row)
        self.Rem_Button = QtWidgets.QPushButton(self.centralwidget)
        self.Rem_Button.setGeometry(QtCore.QRect(660, 20, 30, 30))
        self.Rem_Button.setObjectName("Rem_Button")
        self.Rem_Button.clicked.connect(self.delete_Row)
        

        self.Save_Button = QtWidgets.QPushButton(self.centralwidget)
        self.Save_Button.setGeometry(QtCore.QRect(430, 490, 75, 30))
        self.Save_Button.setObjectName("Save_Button")
        self.Cansel_Button = QtWidgets.QPushButton(self.centralwidget)
        self.Cansel_Button.setGeometry(QtCore.QRect(510, 490, 75, 30))
        self.Cansel_Button.setObjectName("Cansel_Button")
        self.Cansel_Button.clicked.connect(self.reset)
        self.setCentralWidget(self.centralwidget)
        
        self.Main_Table = QtWidgets.QTableWidget(self.centralwidget)
        self.Main_Table.setGeometry(QtCore.QRect(10, 60, 1500, 420))
        self.Main_Table.setObjectName("Main_Table")
        self.Main_Table.setColumnCount(0)
        self.Main_Table.setRowCount(0)
        self.Main_Table.setSortingEnabled(True)
        self.Main_Table.sortItems(0)
        self.Main_Table.cellChanged.connect(self.update_cell)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.add_table()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Clients"))
        self.Filter_Button.setText(_translate("MainWindow", "Filter"))
        self.Add_Button.setText(_translate("MainWindow", "+"))
        self.Rem_Button.setText(_translate("MainWindow", "-"))
        self.Save_Button.setText(_translate("MainWindow", "Save"))
        self.Cansel_Button.setText(_translate("MainWindow", "Cansel"))
        
    def add_table(self):
        self.del_row = set()

        DB1=self.cursor.execute(f'''SELECT * FROM {self.table_name} ''').fetchall()
        
        self.row_quantity = len(DB1)
        self.column_quantity = len(DB1[0])
        self.Main_Table.setRowCount(self.row_quantity)
        self.Main_Table.setColumnCount(self.column_quantity)


        self.columns = list(map(lambda elem: elem[0], self.cursor.execute("select name from pragma_table_info(?)", (self.table_name,)).fetchall()))

        # query = self.con.execute(f"PRAGMA table_info ({self.table_name})")
        # self.columns = [column[1] for column in query.fetchall()]
        self.Main_Table.setHorizontalHeaderLabels(self.columns)

        for i in range(self.row_quantity):
            for j in range(self.column_quantity):
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(DB1[i][j]))
                self.Main_Table.setItem(i, j, item)


    def reset(self):
        
        self.con.rollback()
        self.add_table()
            
    def update_cell(self, row_ind, column_ind):
                column_name = self.columns[column_ind]
                new_value= self.Main_Table.item(row_ind, column_ind).text()
                id_value = self.Main_Table.item(row_ind, self.columns.index("id")).text()
                self.cursor.execute(f"update {self.table_name} set {column_name} = ? where id = ?", (new_value, id_value))
                self.con.commit()

    def delete_Row(self):
        row = self.Main_Table.currentRow()
        if row in self.adding_row and self.adding_row.get(row):
            self.adding_row.pop(row)
        elif row == -1:
            return
        else:
            self.Main_Table.removeRow(row)
            self.row_quantity -= 1
            # self.adding_row = set(map(lambda ind: ind - 1 if ind > row else ind, self.del_row))
            
            self.Main_Table.setCurrentCell(-1, -1)
            
# =============================================================================
#             id_value = self.Main_Table.item(row, 0).text()
#             M = f"delete from {self.table_name} where {self.columns[0]} = '{id_value}'"
#             self.cursor.execute(M)
#             self.con.commit()
# =============================================================================
        
        
        

    def add_Row(self):
        row = self.Main_Table.currentRow()
        self.Main_Table.insertRow(row)
        self.del_row.add(self.row_quantity - 1)
        self.row_quantity += 1


            
            
            
            
            
            

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
