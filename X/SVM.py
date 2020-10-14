import os
import sys
import time
import numpy as np
from Reader import Config
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QPushButton
from qtpy.QtCore import Qt
 
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
 
        self.table = QTableWidget(self)
        self.table.move(20, 20)
        self.table.setColumnCount(3)
        self.table.setFixedHeight(300)
        self.table.setFixedWidth(500)
        #self.table.setSelectionBehavior(QAbstractItemView.SelectRows) #设置表格的选取方式是行选取
        #self.table.setSelectionMode(QAbstractItemView.SingleSelection) #设置选取方式为单个选取
        self.table.setHorizontalHeaderLabels(Header) #设置行表头
        self.table.verticalHeader().setVisible(False)#隐藏列表头
 
        self.table_insert()
 
        #self.table.itemChanged.connect(self.table_update)
 
        self.button_solve()
        self.button_save()
 
        self.setGeometry(200, 200, 570, 400)
        self.show()

    def button_solve(self):
        self.solve_button = QPushButton(self)
        self.solve_button.move(230, 350)
        self.solve_button.setFixedWidth(100)
        self.solve_button.setFixedHeight(32)
        self.solve_button.clicked.connect(self.matrix_solve)
        self.solve_button.setText("Solve")

    def button_save(self):
        self.save_button = QPushButton(self)
        self.save_button.move(230, 350)
        self.save_button.setFixedWidth(100)
        self.save_button.setFixedHeight(32)
        self.save_button.clicked.connect(self.save)
        self.save_button.setText("Save")

    #insert,只是简单插入一个固定数据
    def table_insert(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
 
        item_id = QTableWidgetItem("1")
        item_id.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 设置物件的状态为只可被选择（未设置可编辑）
 
        item_name = QTableWidgetItem("door") #我们要求它可以修改，所以使用默认的状态即可
 
        item_pos = QTableWidgetItem("(1,2)")
        item_pos.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # 设置物件的状态为只可被选择

        self.table.setItem(row, 0, item_id)
        self.table.setItem(row, 1, item_name)
        self.table.setItem(row, 2, item_pos)
        #以下可以加入保存数据到数据的操作
 
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Window()
    sys.exit(app.exec_())
    