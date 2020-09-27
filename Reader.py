import os,re

class Config:
    
    def __init__(self,file):
        self.texts = open(file).readlines()
        self.text = ''.join([x for x in self.texts if x[0] != '#')
        
        self.Model_name     = self.str('model_file_name')
        self.Lib_path       = self.str('library_path')
        self.Options        = self.str('Options')
        self.Corner         = self.list('corner')
        self.Attach_switch  = self.str('Attach_switch').lower()
        self.Corner_attach  = self.list('corner_attach')
        self.Device         = self.list('device')
        self.Vdd            = self.list('Vdd')
        self.Temp           = self.list('temperature')
        self.Etest          = self.list('Etest')
        self.Type           = self.str('mis/monte/typ').lower()
        self.MC_num         = eval(self.str('mc_number'))
        self.Dut            = self.block('dut_width/length/instance_params')
        
        if self.Type not in ['typ','mis','monte','mos_mc','noise_mc','sens']:
            input(' **Error** Analysis not support type: ' + self.Type); exit()
            
        if self.Type == 'mos_mc':
            if len(self.Device) < 2: input(' **Error** Must fill in two Devices.'); exit()
            self.Folder = '_'.join(['mc'] + self.Device)
        else:
            self.Device = self.Device[0]
            self.Folder = self.Device
            self.devtp = 1 if self.Device[0].lower() == 'n' else -1
            
        self.model_path = os.path.join(self.Lib_path, self.Model_name)
        # if model file is .lib, then neglect the corner list
        self.lib_flag = True if os.path.splitext(self.Model_name)[1] == '.lib' else False
        if self.lib_flag == False: self.Corner = ['']
        
        # set instance from the first line, remain is dut sizes
        self.Dut_Dic = {}
        self.Instance, self.Sizes = self.Dut[0], self.Dut[1:]
        for i, size in enumerate(self.Sizes):
            if self.dutype == 1:
                self.Dut_Dic[i+1] = {x.lower():y for x,y in zip(self.Instance, size)}
            elif self.dutype == 2:
                self.Dut_Dic[i+1] = {x.lower():y for (x,y) in re.findall('(\S+)\s*=\s*(\S+)',size)}
    
    def drop(self, key, line):
        try: return re.search(key + '\s*\|\s*(.+?)\s*\n', line, re.I).group(1)
        except: input(' **Error** Config reading failed: ' + key); exit()
        
    def split(self, key, line):
        m = re.search(key + '\s*\|(.*)\n', line, re.I)
        try: return re.findall('\S+', m.group(1))
        except: input(' **Error** Config reading failed: ' + key); exit()
        
    def matrix(self,text):
        self.dutype = 1
        list = []
        for line in text.split('\n'):
            temp = re.findall('\S+',line)
            if temp != []: list.append(temp)
        return list

    def row(self,text):
        self.dutype = 2
        list = []
        for line in text.split('\n'):
            if re.findall('\S+',line) != []:
                list.append(line)
        return list
        
    def str(self, key):
        return self.drop(key, self.text)
        
    def list(self,key):
        return self.split(key, self.text)
        
    def block(self,head):
        m = re.search(head + '\s*\|\s*(.*?)---', self.text, re.DOTALL)
        if m is not None:
            content = m.group(1)
            return self.row(content) if '=' in content else self.matrix(content)
                