from PyQt5 import QtWidgets, QtCore
from .NewTransaction import AbstractOperationWindow
from Constants import Constants, fill_table
from functools import partial
from typing import Callable, Iterator


class WritingOffContextKey(dict):
	"""
		Key of dict with information about write off-operation
	"""

	def __init__(self, wr_from: int|str):
		"""
			:param wr_from: warehouse id indicating which goods to write off from
		"""

		super().__init__()
		self['from'] = wr_from

	def __hash__(self):
		"""
			Hash method
		"""

		return hash(self['from'])

	def __eq__(self, other):
		"""
			Equality of objects is checked by hash
		"""

		return hash(self) == hash(other)


class OperationWriteOff(AbstractOperationWindow):
	"""
		Creating window of the operation Write off
	"""

	def init_widget(self):
		"""
			Fills tables according to the operaion template
		"""

		# info filed
		self.operationInfo.appendPlainText("Со склада:")
		# necessary variables
		self.__db = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__db')
		self.__operation = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__operation')
		self.__operation_full_context = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__operation_full_context')
		self.__buffer = {}
		self.__warehouse = -1
		self.__info_fields = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__info_fields') | {0: 'Со склада'}
		# filter button settings
		self.filterButton.setColumns(self.columns['warehouse_goods'])
		self.tables[0].getData = lambda: self.getData(self.tables[0], len(self.columns['warehouse_goods']))
		# combo box settings
		self.combo_boxes[0].addItem("Выбирете склад", userData=self.__warehouse)
		self.combo_boxes[0].currentIndexChanged.connect(self.warehouseSelected)
		for bufferRow in self.__db.get_warehouses():
			self.combo_boxes[0].addItem(' '.join(map(str, bufferRow[1:])), userData=bufferRow[0])
		# fill table and set settings
		self.tables[0].cellDoubleClicked.connect(self.onGoodsDoubleClicked)
		fill_table(self.columns['warehouse_goods'], [], self.tables[1])
		self.tables[1].cellDoubleClicked.connect(self.onRemoveGood)

	def reload(self, data: Iterator|Callable|list|None=None):
		"""
			Reload data in table
			:param data: object with data to fill into table
		"""

		# skip action
		if self.__warehouse == -1:
			return
		# fill empty variable data
		if data is None:
			data = self.__buffer[self.__warehouse]
		# fill the table
		fill_table(self.columns['warehouse_goods'], data, self.tables[0], counter=True)

	def warehouseSelected(self, row: int):
		"""
			Process logic after warehouse was selected
			:param row: warehouse row index in the combo box
		"""

		# edit info about operation
		self.__warehouse = self.combo_boxes[0].currentData()
		self.edit_info(self.__info_fields[0], '' if self.__warehouse == -1 else self.combo_boxes[0].itemText(row))
		# skip action
		if self.__warehouse == -1:
			self.hide_content()
			return
		# fill the table
		if self.__buffer.get(self.__warehouse, None) is None:
			self.__buffer[self.__warehouse] = list(map(list, self.__db.get_warehouse_goods(self.__warehouse)))
		fill_table(self.columns['warehouse_goods'], self.__buffer[self.__warehouse], self.tables[0], counter=True)
		self.visible_content()

	def onRemoveGood(self, row: int, column: int):
		"""
			Process logic after double click on good in the buffer-table
			:param row: good row index in the table,
			:param column: good column index in the table
		"""

		# skip action, row with 'id'
		if row == 0:
			return
		# necessary variables
		bufferTable, to_remove_wr = self.tables[1], []
		good_id, count_ind = int(bufferTable.verticalHeaderItem(row).text()), list(self.columns['warehouse_goods'].keys()).index('count')
		# remove row from the buffer-table
		for warehouse_info, warehouse_goods in self.__operation['context'].items():
			if good_id in warehouse_goods:
				for bufferRow in self.__buffer[warehouse_info['from']]:
					if bufferRow[0] == good_id:
						bufferRow[count_ind+1] += warehouse_goods[good_id]
						break
				if warehouse_info['from'] == self.__warehouse:
					table, str_good_id = self.tables[0], str(good_id)
					for i in range(1, table.rowCount()):
						if table.verticalHeaderItem(i).text() == str_good_id:
							table.item(i, count_ind).setText(str(int(table.item(i, count_ind).text()) + warehouse_goods[good_id]))
							break
					table = str_good_id = None
				del warehouse_goods[good_id]
				del self.__operation_full_context[WritingOffContextKey(self.combo_boxes[0].itemText(self.combo_boxes[0].findData(warehouse_info['from'])))]
				if not warehouse_goods:
					to_remove_wr.append(warehouse_info)
		# delete additional information in self.__operation['context']
		for warehouse_info in to_remove_wr:
			del self.__operation['context'][warehouse_info]
		# delete row from visualisation
		bufferTable.removeRow(row)
		# change or not the 'Ok' button availability
		self.ready_to_accept()

	def onGoodsDoubleClicked(self, row: int, column: int):
		"""
			Process logic after double click on good in the goods-table
			:param row: good row index in the table,
			:param column: good column index in the table
		"""

		# skip action, rows with 'id' and combo_box
		if row == 0 or column == (spin_box:=len(self.columns['warehouse_goods'])):
			return
		# skip action
		if self.__warehouse == -1:
			return
		# necessary variables
		table = self.tables[0]
		good_id, quantity = int(table.verticalHeaderItem(row).text()), table.cellWidget(row, spin_box).value()
		# skip action
		if quantity == 0:
			return
		# create operation keys
		operation_key = WritingOffContextKey(self.__warehouse)
		operation_full_context_key = WritingOffContextKey(self.combo_boxes[0].itemText(self.combo_boxes[0].findData(self.__warehouse)))
		# avoid errors (KeyError)
		self.__operation['context'].setdefault(operation_key, {})
		self.__operation_full_context.setdefault(operation_full_context_key, {})
		# form self.__operation['context']
		if self.__operation['context'][operation_key].get(good_id) is None:
			self.__operation['context'][operation_key][good_id] = 0
			self.__operation_full_context[operation_full_context_key][good_id] = {'count': 0}
			self.__operation_full_context[operation_full_context_key][good_id]['good'] = \
				' '.join([self.tables[0].item(row, j).text() for j in [i for i, key in enumerate(self.columns['warehouse_goods']) if key in ['articul', 'name']]])
		self.__operation['context'][operation_key][good_id] += quantity
		self.__operation_full_context[operation_full_context_key][good_id]['count'] += quantity
		# new quantity of the good
		newLimit = int(table.item(row, count_ind:=list(self.columns['warehouse_goods'].keys()).index('count')).text()) - quantity
		for bufferRow in self.__buffer[self.__warehouse]:
			if bufferRow[0] == good_id:
				bufferRow[count_ind+1] = newLimit
				break
		# change spin box settings
		table.item(row, count_ind).setText(f"{newLimit}")
		spinBox = table.cellWidget(row, spin_box)
		spinBox.setRange(0, newLimit)
		spinBox.setValue(0)
		# change visualisation quantity of the good
		bufferTable, good_id = self.tables[1], str(good_id)
		i = 0
		for i in range(1, bufferTable.rowCount()):
			if bufferTable.verticalHeaderItem(i).text() == good_id:
				bufferTable.item(i, count_ind).setText(str(int(bufferTable.item(i, count_ind).text()) + quantity))
				quantity = 0
				break
		i += 1
		if quantity != 0:
			bufferTable.insertRow(i)
			bufferTable.setVerticalHeaderItem(i, QtWidgets.QTableWidgetItem(table.verticalHeaderItem(row)))
			for j in range(len(self.columns['warehouse_goods'])):
				if j != count_ind:
					bufferTable.setItem(i, j, QtWidgets.QTableWidgetItem(table.item(row, j)))
				else:
					bufferItem = QtWidgets.QTableWidgetItem(str(quantity))
					bufferItem.setTextAlignment(QtCore.Qt.AlignCenter)
					bufferTable.setItem(i, j, bufferItem)
		# change or not the 'Ok' button availability
		self.ready_to_accept()

	def acceptCreating(self):
		"""
			Processes Ok button, which creates transaction
		"""

		# skip action or continue
		if self.__warehouse == -1:
			QtWidgets.QMessageBox.warning(self, "Предупреждение", f"Для начала выберите склад")
			return
		else:
			self.__operation['warehouse'] = self.__warehouse
		# text of the confirm message
		text = ""
		# create information message
		for transportation, transportation_context in self.__operation_full_context.items():
			text += f"<h3>Из склада {transportation['from']}:</h3>"
			for good_id, good_info in transportation_context.items():
				text += f"<h6><pre>    {good_info['good']}, count={good_info['count']}, good_id={good_id}</pre></h6>"
		# create the confirm window
		super().acceptCreating(text)
