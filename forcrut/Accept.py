from PyQt5 import QtWidgets
from .NewTransaction import AbstractOperationWindow
from Constants import Constants, fill_table
from functools import partial
from typing import Callable, Iterator


class OperationAccept(AbstractOperationWindow):
	"""
		Creating window of the operation Accept
	"""

	def init_widget(self):
		"""
			Fills tables according to the operaion template
		"""
		
		# info filed
		self.operationInfo.appendPlainText("На склад:")
		# necessary variables
		self.__db = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__db')
		self.__operation = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__operation')
		self.__operation_full_context = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__operation_full_context')
		self.__buffer = None
		self.__warehouse = -1
		self.__info_fields = self.__getattribute__(f'_{self.__class__.__bases__[0].__name__}__info_fields') | {0: 'На склад'}
		# filter button settings
		self.filterButton.setColumns(self.columns['goods'])
		self.tables[0].getData = lambda: self.getData(self.tables[0], len(self.columns['goods']))
		# combo box settings
		self.combo_boxes[0].addItem("Выбирете склад получатель", userData=self.__warehouse)
		self.combo_boxes[0].currentIndexChanged.connect(self.warehouseSelected)
		for bufferRow in self.__db.get_warehouses():
			self.combo_boxes[0].addItem(' '.join(map(str, bufferRow[1:])), userData=bufferRow[0])

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
			data = self.__buffer
		# fill the table
		fill_table(self.columns['goods'], data, self.tables[0], counter=True, counter_vals=self.__operation['context'], counter_handler=self.onCounterChanges)

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
		if self.__buffer is None:
			self.__buffer = list(map(list, self.__db.get_all_goods()))
		fill_table(self.columns['goods'], self.__buffer, self.tables[0], counter=True, counter_vals=self.__operation['context'], counter_handler=self.onCounterChanges)
		self.visible_content()

	def onCounterChanges(self, good_id: str|int, value: int):
		"""
			Process logic after counter is changed
			:param good_id: good id,
			:param value: combo box value
		"""

		# string good_id to the integer
		if isinstance(good_id, str):
			good_id = int(good_id)
		# for operation info
		self.__operation['context'][good_id] = value
		if self.__operation_full_context.get(good_id) is None:
			for bufferRow in self.__buffer:
				if bufferRow[0] == good_id:
					good_info = ' '.join(bufferRow[1:][j] for j, key in enumerate(self.columns['goods']) if key in ['articul', 'name'])
					break
			self.__operation_full_context[good_id] = {'count': value, 'good': good_info}
		else:
			self.__operation_full_context[good_id]['count'] = value
		if value == 0:
			del self.__operation['context'][good_id]
			del self.__operation_full_context[good_id]
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
		text = f"<h3>Склад: {self.get_info(self.__info_fields[0])}.</h3>"
		# create information message
		for good_id, good_info in self.__operation_full_context.items():
			text += f"<h6><pre>    {good_info['good']}, count={good_info['count']}, good_id={good_id}</pre></h6>"
		# create the confirm window
		super().acceptCreating(text)
