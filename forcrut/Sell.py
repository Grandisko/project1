from PyQt5 import QtWidgets, QtCore
from .NewTransaction import AbstractOperationWindow
from Constants import Constants, fill_table
from functools import partial
from typing import Callable, Iterator


class SellingContextKey(dict):
	"""
		Key of dict with information about sell-operation
	"""

	def __init__(self, wr_from: int|str):
		"""
			:param wr_from: warehouse id indicating which goods to sell from
		"""

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


class OperationSell(AbstractOperationWindow):
	"""

	"""

	def init_widget(self):
		"""
			Fills tables according to the operaion template
		"""

		self.operationInfo.appendPlainText("Клиент:\nСо склада:")
		
		self.__db = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__db')
		self.__operation = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__operation')
		self.__operation_full_context = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__operation_full_context')
		self.__buffer = {}
		self.__client = -1
		self.__warehouse = -1
		self.__info_fields = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__info_fields') | {0: 'Клиент', 1: 'Со склада'}

		self.filterButton.setColumns(self.columns['warehouse_goods'])
		self.tables[0].getData = lambda: self.getData(self.tables[0], len(self.columns['warehouse_goods']))

		self.combo_boxes[0].addItem("Выбирете клиента", userData=self.__client)
		self.combo_boxes[0].currentIndexChanged.connect(self.clientSelected)
		for bufferRow in self.__db.get_clients():
			self.combo_boxes[0].addItem(' '.join(map(str, bufferRow[1:])), userData=bufferRow[0])

		self.combo_boxes[1].addItem("Выбирете склад", userData=self.__warehouse)
		self.combo_boxes[1].currentIndexChanged.connect(self.warehouseSelected)
		for bufferRow in self.__db.get_warehouses():
			self.combo_boxes[1].addItem(' '.join(map(str, bufferRow[1:])), userData=bufferRow[0])

		self.tables[0].cellDoubleClicked.connect(self.onGoodsDoubleClicked)
		fill_table(self.columns['warehouse_goods'], [], self.tables[1])
		self.tables[1].cellDoubleClicked.connect(self.onRemoveGood)

	def reload(self, data: Iterator|Callable|list|None=None):
		"""

		"""

		if self.__warehouse == -1:
			return

		if data is None:
			data = self.__buffer[self.__warehouse]

		fill_table(self.columns['warehouse_goods'], data, self.tables[0], counter=True)

	def clientSelected(self, row: int):
		"""

		"""

		self.__client = self.combo_boxes[0].currentData()
		self.edit_info(self.__info_fields[0], '' if self.__client == -1 else self.combo_boxes[0].itemText(row))

	def warehouseSelected(self, row: int):
		"""

		"""

		self.__warehouse = self.combo_boxes[1].currentData()
		self.edit_info(self.__info_fields[1], '' if self.__warehouse == -1 else self.combo_boxes[1].itemText(row))
		#
		if self.__warehouse == -1:
			self.hide_content()
			return
		#
		if self.__buffer.get(self.__warehouse, None) is None:
			self.__buffer[self.__warehouse] = list(map(list, self.__db.get_warehouse_goods(self.__warehouse)))
		fill_table(self.columns['warehouse_goods'], self.__buffer[self.__warehouse], self.tables[0], counter=True)
		self.visible_content()

	def onRemoveGood(self, row: int, column: int):
		"""

		"""

		#
		if row == 0:
			return
		#
		bufferTable, to_remove_wr = self.tables[1], []
		good_id, count_ind = int(bufferTable.verticalHeaderItem(row).text()), list(self.columns['warehouse_goods'].keys()).index('count')
		#
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
							table.cellWidget(i, len(self.columns['warehouse_goods'])).setMaximum(int(table.item(i, count_ind).text()))
							break
					table = str_good_id = None
				del warehouse_goods[good_id]
				del self.__operation_full_context[SellingContextKey(self.combo_boxes[1].itemText(self.combo_boxes[1].findData(warehouse_info['from'])))]
				if not warehouse_goods:
					to_remove_wr.append(warehouse_info)
		#
		for warehouse_info in to_remove_wr:
			del self.__operation['context'][warehouse_info]
		
		bufferTable.removeRow(row)

		self.ready_to_accept()

	def onGoodsDoubleClicked(self, row: int, column: int):
		"""

		"""

		if row == 0 or column == (spin_box:=len(self.columns['warehouse_goods'])):
			return

		if self.__warehouse == -1:
			return

		table = self.tables[0]

		good_id, quantity = int(table.verticalHeaderItem(row).text()), table.cellWidget(row, spin_box).value()
		if quantity == 0:
			return

		operation_key = SellingContextKey(self.__warehouse)
		operation_full_context_key = SellingContextKey(self.combo_boxes[1].itemText(self.combo_boxes[1].findData(self.__warehouse)))

		self.__operation['context'].setdefault(operation_key, {})
		self.__operation_full_context.setdefault(operation_full_context_key, {})

		if self.__operation['context'][operation_key].get(good_id) is None:
			self.__operation['context'][operation_key][good_id] = 0
			self.__operation_full_context[operation_full_context_key][good_id] = {'count': 0}
			self.__operation_full_context[operation_full_context_key][good_id]['good'] = \
				' '.join([self.tables[0].item(row, j).text() for j in [i for i, key in enumerate(self.columns['warehouse_goods']) if key in ['articul', 'name']]])
		self.__operation['context'][operation_key][good_id] += quantity
		self.__operation_full_context[operation_full_context_key][good_id]['count'] += quantity
		#
		newLimit = int(table.item(row, count_ind:=list(self.columns['warehouse_goods'].keys()).index('count')).text()) - quantity
		for bufferRow in self.__buffer[self.__warehouse]:
			if bufferRow[0] == good_id:
				bufferRow[count_ind+1] = newLimit
				break
		#
		table.item(row, count_ind).setText(f"{newLimit}")
		spinBox = table.cellWidget(row, spin_box)
		spinBox.setRange(0, newLimit)
		spinBox.setValue(0)
		
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

		self.ready_to_accept()

	def acceptCreating(self):
		"""

		"""

		if self.__client == -1:
			QtWidgets.QMessageBox.warning(self, "Предупреждение", f"Для начала выберите клиента")
			return
		else:
			self.__operation['client'] = self.__client

		text = f"<h3>Клиент: {self.get_info(self.__info_fields[0])}.</h3>"
		# text = ""
		# create information message
		for transportation, transportation_context in self.__operation_full_context.items():
			text += f"<h3>Из склада {transportation['from']}:</h3>"
			for good_id, good_info in transportation_context.items():
				text += f"<h6><pre>    {good_info['good']}, count={good_info['count']}, good_id={good_id}</pre></h6>"
		
		super().acceptCreating(text)