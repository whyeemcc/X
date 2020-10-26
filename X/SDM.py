import os
import sys
import time
import json
import numpy as np
from Reader import Config
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QPushButton
from qtpy.QtCore import Qt
from PyQt5.QtGui import QBrush,QColor

if  len(sys.argv) == 1: cfg_File = r'xxx.cfg'
elif len(sys.argv) > 1: cfg_File = sys.argv[1]
 
cfg = Config(cfg_File)

try:
    with open(cfg.path_Folder + '/diff_statistic.jsonx'):
        diff_statistic = json.load(f)
except:
    input(' **Error** not found file: diff_statistic.jsonx; pls run diff mode firstly.'); exit()

rnd_var_all = cfg.list('rnd_var_all')
rnd_var_cal = cfg.list('rnd_var_cal')
rnd_var_cal_sqrt = [x+'_sqrt' for x in rnd_var_cal]
rnd_var_fix = [x for x in rnd_var_all if x not in rnd_var_cal]
 
Header = cfg.Instance_raw + rnd_var_cal + rnd_var_cal_sqrt
row_count = len(cfg.Sizes)
col_count = len(Header) 
 
 
def solve(matrix, target):
    coeff = np.matrix(matrix)**-1*np.matrix(target)
    return coeff
 
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        self.table = QTableWidget(self)
        self.table.move(20, 20)
        self.table.setColumnCount(col_count)
        self.table.setFixedHeight(800)
        self.table.setFixedWidth(1650)
        self.table.setHorizontalHeaderLabels(Header)  #设置行表头
 
        self.size_inital_insert()
 
        #self.table.itemChanged.connect(self.table_update)
        self.table.itemActivated.connect(self.matrix_solve)
 
        self.button_Solve()
        self.button_Save()
 
        QTableWidget.resizeColumnsToContents(self.table) # auto col width
        QTableWidget.resizeRowsToContents(self.table) # auto row width
 
        self.setWindowTitle('SDM Tuning')
        self.setGeometry(50, 50, 1700, 900)
        self.show()

    def button_Solve(self):
        self.solve_button = QPushButton(self)
        self.solve_button.move(700, 850)
        self.solve_button.setFixedWidth(100)
        self.solve_button.setFixedHeight(32)
        self.solve_button.clicked.connect(self.matrix_solve)
        self.solve_button.setText("Solve")

    def button_Save(self):
        self.save_button = QPushButton(self)
        self.save_button.move(1000, 850)
        self.save_button.setFixedWidth(100)
        self.save_button.setFixedHeight(32)
        self.save_button.clicked.connect(self.save)
        self.save_button.setText("Save")

    def size_inital_insert(self):
        for row,size in enumerate(cfg.Sizes):
            self.table.insertRow(row) # insert new row
            
            for col,value in enumerate(size):
                item = QTableWidgetItem(value)
                self.table.setItem(row,col,item) # write in Item
                
                if cfg.Instance_raw[col] not in cfg.Etest:
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # select only, not edit
        
    def matrix_solve(self):
        try:
            for row in range(row_count):
                matrix, target = [], []
                for etest in cfg.Etest:
                    col = Header.index(etest)
                    matrix += [[diff_statistic[etest + str(i+1)][rnd]**2 for rnd in rnd_var_cal]]
                    fix_sum  = [diff_statistic[etest + str(i+1)][rnd]**2 for rnd in rnd_var_fix]
                    target += [[eval(self.table.item(row,col).text())**2 - sum(fix_sum)]]                
                
                result = solve(matrix, target)                
                for k,rnd in enumerate(rnd_var_cal):
                    col_rnd = Header.index(rnd)
                    item = QTableWidgetItem("%.3f" % result[k,0])
                    item.setForeground(QBrush(QColor(255,0,0)))
                    self.table.setItem(row, col_rnd, item)
                    item.setFlags(Qt,ItemIsSelectable | Qt.ItemIsEnabled)
                
                for k,rnd in enumerate(rnd_var_cal):
                    col_var_sqrt = Header.Index(rnd + '_sqrt')
                    item = QTableWidgetItem("%.4f" % np.sqrt(result[k,0]) if result[k,0]>=0 else "")
                    item.setForeground(QBrush(QColor(0,176,80)))
                    self.table.setItem(row, col_rnd_sqrt, item)
        except:
            print(" **Error** Matrix solve failed.")
            
    def save(self):
        time_now = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime())
        csv_file = cfg.path_Output + '/X_output_{}_sdm_coeff_{}.csv'.format(cfg.Device, time_now)
        
        with open(csv_file,'w') as csv:
            csv.write('Model: ' + cfg.model_path + '\n')
            csv.write('Cfg: '   + cfg.cfg_Name   + '\n')
            csv.write('Device: '+ cfg.Device     + '\n')
            csv.write('Vdd: '   + cfg.Vdd[0]     + '\n')
            csv.write('Temp: '  + cfg.Temp[0]    + '\n')
            csv.writelines('.'.join(Header)+'\n')
            
            for row in range(row_count):
                row_list = [self.table.item(row,col).text() for col in range(col_count)]
                csv.write(','.join(row_list)+'\n')
            
            csv.close()
        os.system(csv_file)
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = Window()
    sys.exit(app.exec_())
    