import os
import sys
import time
from Reader import Config
from Netlist import Net
from Mining import Mining
from Setting import *

cfg = Config(cfg_File)

def generate_netlist():
    net = Net(cfg)
    for Etest in cfg.Etest:
        net.save(Etest)        

def run_netlist():
    printColor('Xmodel Processing...    v0.90',SKYBLUE)
    printColor('--- load cfg: ' + cfg.cfg_Name + ' ---',YELLOW)
    printColor('<' + cfg.Folder + '>',PINK)
    
    os.chdir(cfg.path_Folder)
    time1 = time.time()
    for Etest in cfg.Etest:
        engine_run(Etest)
        fault_check(Etest + log)
        print(Etest + ' ...done')
    time2 = time.time()
    printColor('----------- time: {:.2f}s'.format(time2-time1),GREEN)

def extract_data():
    mining = Mining(cfg)
    try:
        mining.save()
    except:
        print('Failed in Extraction!')
    mining.del_temp()
    
if __name__ == '__main__':    
    generate_netlist()
    #run_netlist()
    #extract_data()
    