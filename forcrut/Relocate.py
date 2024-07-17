from PyQt5 import QtWidgets
from .NewTransaction import AbstractOperationWindow
from Constants import Constants, fill_table
from functools import partial
from typing import Callable, Iterator


class RelocationContextKey(dict):
	"""
		Key of dict with information relocation-operation
	"""

	def __init__(self, wr_from: int|str, wr_to: int|str, flag: bool|None=None) -> None:
		"""
			:param wr_from: warehouse id/info indicating which goods to relocate from,
			:param wr_to: warehouse id/info indicating which goods to relocate to,
			:param flag: 'sign' analog when wr_from and wr_to are strings
		"""

		super().__init__()
		if isinstance(wr_from, int) and isinstance(wr_to, int):
			self['from'], self['to'] = min(wr_from, wr_to), max(wr_from, wr_to)
			self['sign'] = 1 if self['from'] == wr_from else -1
		elif isinstance(wr_from, str) and isinstance(wr_to, str):
			if flag is None:
				raise ValueError("RelocationContextKey: flag must be boolean when wr_from and wr_to are strings")
			self['from'], self['to'] = (wr_from, wr_to) if flag else (wr_to, wr_from)

	def __hash__(self) -> int:
		"""
			Hash method
		"""

		return hash((self['from'], self['to']))

	def __eq__(self, other) -> bool:
		"""
			Equality of objects is checked by hash
		"""

		return hash(self) == hash(other)


class OperationRelocate(AbstractOperationWindow):
	"""
		Creating window of the operation Relocate
	"""

	def init_widget(self):
		"""
			Fills tables according to the operaion template
		"""

		# info fields
		self.operationInfo.appendPlainText("Со склада:\nНа склад:")
		# necessary variables
		self.__db = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__db')
		self.__operation = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__operation')
		self.__operation_full_context = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__operation_full_context')
		self.__buffer = {}
		self.__warehouses = {0: -1, 1: -1}
		self.__info_fields = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__info_fields') | {0: 'Со склада', 1: 'На склад'}
		# table settings
		self.filterButton.setColumns(self.columns['warehouse_goods'])
		self.tables[0].getData = lambda: self.getData(self.tables[0], len(self.columns['warehouse_goods']))
		# combo boxes settings
		combo_boxes = [("Выберите склад отправки", self.__db.get_warehouses), ("Выберите склад получатель", self.__db.get_warehouses)]
		for i, (bufferComboBox, (name, handler)) in enumerate(zip(self.combo_boxes, combo_boxes)):
			bufferComboBox.addItem(name, userData=self.__warehouses[i])
			bufferComboBox.currentIndexChanged.connect(partial(self.warehouseSelected, comboBoxId=i))
			for bufferRow in handler():
				bufferComboBox.addItem(' '.join(map(str, bufferRow[1:])), userData=bufferRow[0])
		# set handler for double clicking on good
		self.tables[0].cellDoubleClicked.connect(self.onGoodsDoubleClicked)

	def reload(self, data: Iterator|Callable|list|None=None):
		"""
			Reload data in table
			:param data: object with data to fill into table
		"""

		# skip row with 'id'
		if self.__warehouses[0] == -1:
			return
		# process data parameter
		if data is None:
			data = self.__buffer[self.__warehouses[0]]

		fill_table(self.columns['warehouse_goods'], data, self.tables[0], counter=True)

	def warehouseSelected(self, row: int, comboBoxId: int):
		"""
			Process logic after warehouse was selected,
			:param row: warehouse row index in the combo box,
			:param comboBoxId: index of the clicked combo box in self.combo_boxes
		"""

		# edit info about operation
		self.edit_info(self.__info_fields[comboBoxId], '')
		# skip action
		if (warehouse_id:=self.combo_boxes[comboBoxId].currentData()) == -1:
			if comboBoxId == 0:
				self.hide_content()
			self.__warehouses[comboBoxId] = -1
			return
		# skip action
		if warehouse_id == self.__warehouses[1^comboBoxId]:
			QtWidgets.QMessageBox.warning(self, "Ошибка", f"\tПеремещение товара\nмежду одним и тем же складом невозможно")
			self.combo_boxes[comboBoxId].setCurrentIndex(0)
			self.__warehouses[comboBoxId] = -1
			return
		# edit info about operation
		self.__warehouses[comboBoxId] = warehouse_id
		self.edit_info(self.__info_fields[comboBoxId], self.combo_boxes[comboBoxId].itemText(row))
		# fill the table if the edited table is first in self.tables
		if comboBoxId == 0:
			if self.__buffer.get(warehouse_id, None) is None:
				self.__buffer[warehouse_id] = list(map(list, self.__db.get_warehouse_goods(warehouse_id)))
			fill_table(self.columns['warehouse_goods'], self.__buffer[warehouse_id], self.tables[0], counter=True)
			self.visible_content()

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
		if self.__warehouses[0] == -1 or self.__warehouses[0] == self.__warehouses[1]:
			return
		elif self.__warehouses[1] == -1:
			QtWidgets.QMessageBox.warning(self, "Предупреждение", f"Для начала укажите склад,\nна который переместить товар")
			return
		# necessary variables
		table = self.tables[0]
		good_id, quantity = int(table.verticalHeaderItem(row).text()), table.cellWidget(row, spin_box).value()
		# skip action
		if quantity == 0:
			return
		# create operation keys
		operation_key = RelocationContextKey(self.__warehouses[0], self.__warehouses[1])
		operation_full_context_key = RelocationContextKey(self.combo_boxes[0].itemText(self.combo_boxes[0].findData(self.__warehouses[0])), self.combo_boxes[1].itemText(self.combo_boxes[1].findData(self.__warehouses[1])), flag=self.__warehouses[0] < self.__warehouses[1])
		# avoid errors (KeyError)
		self.__operation['context'].setdefault(operation_key, {})
		self.__operation_full_context.setdefault(operation_full_context_key, {})
		# form self.__operation['context']
		if self.__operation['context'][operation_key].get(good_id) is None:
			self.__operation['context'][operation_key][good_id] = 0
			self.__operation_full_context[operation_full_context_key][good_id] = {'count': 0}
			self.__operation_full_context[operation_full_context_key][good_id]['good'] = \
				' '.join([self.tables[0].item(row, j).text() for j in [i for i, key in enumerate(self.columns['warehouse_goods']) if key in ['articul', 'name']]])
		self.__operation['context'][operation_key][good_id] += operation_key['sign']*quantity
		self.__operation_full_context[operation_full_context_key][good_id]['count'] += operation_key['sign']*quantity
		# delete 'sign' key from key
		del operation_key['sign']
		# check operation info if necessary
		if self.__operation['context'][operation_key][good_id] == 0:
			del self.__operation['context'][operation_key][good_id]
			del self.__operation_full_context[operation_full_context_key][good_id]
			if not self.__operation['context'][operation_key]:
				del self.__operation['context'][operation_key]
				del self.__operation_full_context[operation_full_context_key]
		# new quantity of the good
		newLimit = int(table.item(row, count_ind:=list(self.columns['warehouse_goods'].keys()).index('count')).text()) - quantity
		# rewrite quantity in self.__warehouses[0]
		for bufferRow in self.__buffer[self.__warehouses[0]]:
			if bufferRow[0] == good_id:
				bufferRow[count_ind+1] = newLimit
				break
		# create buffer entry if there's not one
		if self.__buffer.get(self.__warehouses[1], None) is None:
			self.__buffer[self.__warehouses[1]] = list(map(list, self.__db.get_warehouse_goods(self.__warehouses[1])))
		# rewrite quantity in self.__warehouses[0]
		for bufferRow in self.__buffer[self.__warehouses[1]]:
			if bufferRow[0] == good_id:
				bufferRow[count_ind+1] += quantity
				break
		# change spin box settings
		table.item(row, count_ind).setText(f"{newLimit}")
		spinBox = table.cellWidget(row, spin_box)
		spinBox.setRange(0, newLimit)
		spinBox.setValue(0)
		# change or not the 'Ok' button availability
		self.ready_to_accept()

	def acceptCreating(self):
		"""
			Processes Ok button, which creates transaction
		"""

		# text of the confirm message
		text = ""
		# create information message
		for transportation, transportation_context in self.__operation_full_context.items():
			bufferTextAcs = bufferTextDesc = ""
			for good_id, good_info in transportation_context.items():
				if good_info['count'] > 0:
					bufferTextAcs += f"<h6><pre>    {good_info['good']}, count={good_info['count']}, good_id={good_id}</pre></h6>"
				else:
					bufferTextDesc += f"<h6><pre>    {good_info['good']}, count={-1*good_info['count']}, good_id={good_id}</pre></h6>"
			if bufferTextAcs:
				text += f"<h3>Из склада {transportation['from']} на склад {transportation['to']}:</h3>" + bufferTextAcs
			if bufferTextDesc:
				text += f"<h3>Из склада {transportation['to']} на склад {transportation['from']}:</h3>" + bufferTextDesc
		# create the confirm window
		super().acceptCreating(text)
