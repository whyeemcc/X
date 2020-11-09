import os,sys,re

class Config:
    
    def __init__(self, cfg_File):
        self.texts = open(cfg_File).readlines()
        self.text = ''.join([x for x in self.texts if x[0] != '#'])

        self.Model_name    = self.str('model_file_name')
        self.Lib_path      = self.str('library_path')
        self.Options       = self.str('Options')
        self.Corner        = self.list('corner')
        self.Attach_switch = self.str('Attach_switch').lower()
        self.Corner_attach = self.list('corner_attach')
        self.Device        = self.list('device')
        self.Vdd           = self.list('Vdd')
        self.Temp          = self.list('temperature')
        self.Etest         = self.list('Etest')
        self.Mode          = self.str('Analysis_Mode').lower()
        self.MC_num        = eval(self.str('mc_number'))
        self.Dut           = self.block('dut_width/length/instance_params')

        self.path(cfg_File)    
        self.size()    
        self.check()    
            
    def path(self,cfg_File):
        self.Device = self.Device[0] if self.Mode != 'mos_mc' else self.Device
        self.Folder = self.Device if self.Mode != 'mos_mc' else '_'.join(['mc'] + self.Device)
        self.model_path = os.path.join(self.Lib_path, self.Model_name)
        
        self.path_Xmodel = os.path.join(sys.path[0],'../')
        
        self.path_cfg, self.cfg_Name = os.path.split(cfg_File)
        if self.path_cfg == '': self.path_cfg = self.path_Xmodel
        
        self.path_Bin    = self.path_Xmodel + '/bin'
        self.path_Output = self.path_cfg + '/output'
        self.path_Folder = self.path_cfg + '/output/' + self.Folder
    
    def size(self):
        # get instance from the first line, remain is dut sizes
        self.Instance_raw, self.Sizes = self.Dut[0], self.Dut[1:]

        self.size_unit, self.Instance = [], []
        for x in self.Instance_raw:
            try:
                self.size_unit.append(re.search(r'\((.*)\)',x).group(1))
                self.Instance.append(x.split('(')[0])
            except:
                self.size_unit.append('')
                self.Instance.append(x)

        self.Dut_Dic = {}
        for i, size in enumerate(self.Sizes):
            if   self.dutype == 1: self.Dut_Dic[i+1] = {x.lower():y+o for x,y,o in zip(self.Instance, size, self.size_unit)}
            elif self.dutype == 2: self.Dut_Dic[i+1] = {x.lower():y for (x,y) in re.findall('(\S+)\s*=\s*(\S+)',size)}
    
    def check(self):
        # if model file is .lib, then neglect the corner list
        self.lib_flag = True if os.path.splitext(self.Model_name)[1] == '.lib' else False
        if self.lib_flag == False: self.Corner = ['']
        # mos_mc no need devtp
        if self.Mode != 'mos_mc':
            self.devtp = 1 if self.Device[0].lower() == 'n' else -1
        # if Mode is mos_mc, need at-least 2 devices
        if self.Mode == 'mos_mc' and len(self.Device) < 2:
            input(' **Error** Must fill in two Devices.'); exit()
        # only support these Modes:
        if self.Mode not in ['typ','mis','monte','diff','mos_mc','noise_mc','dcmatch']:
            input(' **Error** Analysis not support Mode: ' + self.Mode); exit()
        # size col count
        if self.dutype == 1:
            len_inst = len(self.Instance_raw)
            for size in self.Sizes:
                if len(size) != len_inst: input(' **Error** size in cfg not match instance'); exit()
        # diff only support 1 vdd/temp/cor
        if self.Mode == 'diff':
            if self.str('save_diff_json') == 'yes':
                if len(self.Vdd + self.Temp + self.Corner) > 3: input(' **Error** save diff_statis.json only support single vdd/temp/cor'); exit()

    def drop(self, key, line):
        try:    return re.search(key + '\s*\|\s*(.+?)\s*\n', line, re.I).group(1)
        except: input(' **Error** Missing config item: ' + key); exit()

    def split(self, key, line):
        m = re.search(key + '\s*\|(.*)\n', line, re.I)
        try:    return re.findall('\S+', m.group(1))
        except: input(' **Error** Missing config item: ' + key); exit()

    def matrix(self, text):
        self.dutype = 1
        list = []
        for line in text.split('\n'):
            temp = re.findall('\S+',line)
            if temp != []: list.append(temp)
        return list

    def row(self, text):
        self.dutype = 2
        list = []
        for line in text.split('\n'):
            if re.findall('\S+',line) != []:
                list.append(line)
        return list

    def str(self, key):
        return self.drop(key, self.text)

    def list(self, key):
        return self.split(key, self.text)

    def block(self, head):
        m = re.search(head + '\s*\|\s*(.*?)---', self.text, re.DOTALL)
        if m is not None:
            content = m.group(1)
            return self.row(content) if '=' in content else self.matrix(content)
                