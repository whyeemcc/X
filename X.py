import os
import sys
import time
from Reader import Config
from Netlist import Net
from Mining import Mining
from Setting import *

path_Xmodel = os.path.join(sys.path[0],'../')
if path_cfg == '': path_cfg = path_Xmodel

os.chdir(path_cfg); cfg = Config(cfg_File)

def generate_netlist():
    net = Net(cfg)
    os.chdir(path_Xmodel + '/bin')
    for Etest in cfg.Etest:
        net.save(path_cfg,Etest)
        os.chdir(path_Xmodel + '/bin')

def run_netlist():
    printColor('Xmodel Processing...',SKYBLUE)
    printColor('--- load cfg: ' + cfg_File + ' ---',YELLOW)
    printColor('<' + cfg.Folder + '>',PINK)
    
    os.chdir(path_cfg + '/output/' + cfg.Folder)
    time1 = time.time()
    for Etest in cfg.Etest:
        engine_run(Etest)
        fault_check(Etest + log)
        print(Etest + '...done')
    time2 = time.time()
    printColor('----------- time: {:.2f}s'.format(time2-time1),GREEN)

def extract_data():
    os.chdir(path_cfg + '/output/' + cfg.Folder)
    mining = Mining(cfg)
    try:
        mining.save()
    except:
        print('Failed in Extraction!')
    mining.del_temp()
    
if __name__ == '__main__':
    generate_netlist()
    run_netlist()
    extract_data()
    