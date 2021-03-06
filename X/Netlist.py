import re,os

class Net:
    
    def __init__(self,cfg):
        self.cfg = cfg
        os.chdir(self.cfg.path_Bin)
    
    def lib_attach_add(self,type,corner):
        Text = "{} '{}' {}\n".format(type, self.cfg.model_path, corner)
        if self.cfg.Attach_switch == 'on':
            for cor_att in self.cfg.Corner_attach:
                Text += "{} '{}' {}\n".format(type, self.cfg.model_path, cor_att)
        return Text

    def drop_brackt(self,Text):
        # <W>/<L> -> W/L
        try:    return re.sub(r'<(.+?)>',r'\1',Text)
        except: return Text

    def instanceV(self,Text,size):
        # XM D G 0 0 plvt_ckt NFIN=2 L=0.01u W=0.042u
        if   self.cfg.dutype == 1: z = ' '.join('{}={}{}'.format(x,y,o) for x,y,o in zip(self.cfg.Instance, size, self.cfg.size_unit))
        elif self.cfg.dutype == 2: z = size
        return re.sub('dev_param',z,Text)
        
    def measureV(self,Text,i):
        # <W>/<L> -> 0.096u/0.008u
        all = re.findall(r'<(.+?)>',Text)
        for x in all:
            try:    Text = re.sub(r'<%s>' % x, self.cfg.Dut_Dic[i][x.lower()], Text)
            except: Text = re.sub(r'<%s>' % x, x, Text)
        return Text

    def set_MODEL(self,Etest):
        Text = Etest + ' Simulation\n'
        Text += '.option %s' % self.cfg.Options + ' nomod ' + '\n'

        if self.cfg.lib_flag: Text += self.lib_attach_add('.lib', self.cfg.Corner[0])
        else:                 Text += ".inc '%s'\n" % self.cfg.model_path

        Text += '.TEMP %s\n' % self.cfg.Temp[0]
        return Text

    def set_DEVICE(self,Etest):
        try:
            if   self.cfg.Mode == 'mis':      Text = open('mis/'+Etest).read()
            elif self.cfg.Mode == 'mos_mc':   Text = open('mos_mc/'+Etest).read()
            elif self.cfg.Mode == 'dcmatch':  Text = open('dcmatch/'+Etest).read()
            elif self.cfg.Mode == 'noise_mc': Text = open('noise_mc/'+Etest).read()
            else: Text = open(Etest).read()
        except:
            print(' **Error**: Etest not found in bin/%s: %s' % (self.cfg.Mode, Etest)); exit()

        # replace .param
        params = re.findall('\.param\s*(\w+)\s*\n', Text, re.I)
        for p in params:
            if p == 'devtp': v = self.cfg.devtp
            elif p == 'vdd': v = self.cfg.Vdd[0]
            else           : v = self.cfg.str(p)
            Text = re.sub('\.param ' + p + '\s*?\n', '.param {}={}\n'.format(p,v), Text)

        # record Instance_Discard
        self.Instance_Discard = []
        for i in self.cfg.Instance:
            if i.lower() not in [x.lower() for x in params]:
                self.Instance_Discard += [i]

        # sweep type
        if self.cfg.Mode in ['typ','dcmatch'] and self.cfg.dutype == 1:
            swp_type = 'sweep data=sweep_instance'
        elif self.cfg.Mode in ['typ','dcmatch'] and self.cfg.dutype == 2:
            swp_type = ''
        elif self.cfg.Mode in ['noise_mc','mis','monte','mos_mc']:
            swp_type = 'sweep monte=%s' % self.cfg.MC_num
        elif self.cfg.Mode in ['diff']:
            swp_type = 'sweep data=sweep_rand'
        try:
            Text = re.sub(r'(\.(dc\s|ac\s).*)\s*\n',r'\1 '+swp_type+'\n\n', Text, flags=re.I)
        except:
            pass

        # model name
        if self.cfg.Mode == 'mos_mc':
            Text = re.sub('model_name_n', self.cfg.Device[0], Text)
            Text = re.sub('model_name_p', self.cfg.Device[1], Text)
        else:
            Text = re.sub('model_name', self.cfg.Device, Text)

        # device
        if self.cfg.Mode in ['typ','noise_mc','dcmatch'] and self.cfg.dutype == 1:
            Text = re.sub('dev_param', ' '.join(['{}={}'.format(i,i) for i in self.Instance_Discard]), Text)
            Text = re.sub('~','',Text)
            Text = self.drop_brackt(Text)
            Text = self.device_iteration(Text)
        else:
            Net_Lines = Text.split('\n')
            Text = '\n'.join([line for line in Net_Lines if '~' not in line and '\t' != line])
            Dut_block = '\n'.join([line for line in Net_Lines if '~' in line or '\t' == line])
            Text = self.device_iteration(Text,Dut_block)

        return Text + '\n'

    def device_iteration(self,Text,Dut_block=''):

        if self.cfg.Mode in ['typ','dcmatch'] and self.cfg.dutype == 1:
            Text += '\n.data sweep_instance\n'
            Text += '+%s\n' % '\t'.join(self.cfg.Instance)
            for i,size in enumerate(self.cfg.Sizes):
                Text += '+%s\t$%s\n' % ('\t'.join(j+o for j,o in zip(size,self.cfg.size_unit)), i+1)
            Text += '.enddata\n'

        elif self.cfg.Mode == 'typ' and self.cfg.dutype == 2:
            for i,size in enumerate(self.cfg.Sizes):
                Dut_new = re.sub(r'~', str(i+1), Dut_block)
                Dut_new = self.instanceV(Dut_new, size)
                Dut_new = self.measureV(Dut_new, i+1)
                Text += '\n' + Dut_new + '\n'

        elif self.cfg.Mode == 'noise_mc' and self.cfg.dutype == 1:
            for i,size in enumerate(self.cfg.Sizes):
                if i > 0:
                    Text += '\n.alter'
                Text += '\n.param ' + ' '.join(['%s=%s%s' % (m,n,o) for m,n,o in zip(self.cfg.Instance, size, self.cfg.size_unit)])

        elif self.cfg.Mode in ['monte','mis','mos_mc']:
            for i,size in enumerate(self.cfg.Sizes):
                Dut_new = re.sub(r'~', str(i+1), Dut_block)
                Dut_new = self.instanceV(Dut_new, size)
                Dut_new = self.measureV(Dut_new, i+1)
                Text += '\n' + Dut_new + '\n'
                
        elif self.cfg.Mode in ['diff']:
            for i,size in enumerate(self.cfg.Sizes):
                Dut_new = re.sub(r'~', str(i+1), Dut_block)
                Dut_new = self.instanceV(Dut_new, size)
                Dut_new = self.measureV(Dut_new, i+1)
                Text += '\n' + Dut_new + '\n'
                
            rnd_count = len(self.cfg.list('rnd_var_all'))
            Text += '\n.data sweep_rand\n'
            Text += '+%s\n' % '\t'.join(self.cfg.list('rnd_var_all'))
            
            for i in range(1 + 2*rnd_count):
                if i == 0:
                    Text += '+' + '\t\t\t'.join(['0']*rnd_count + ['$%s\n'%(i+1)])
                else:
                    if   i % 2 != 0: Text += '+' + '\t\t\t'.join(['1'  if j+1 == (i+1)/2 else '0' for j in range(rnd_count)] + ['$%s\n'%(i+1)])
                    elif i % 2 == 0: Text += '+' + '\t\t\t'.join(['-1' if j+1 == i/2     else '0' for j in range(rnd_count)] + ['$%s\n'%(i+1)])
            Text += '.enddata\n'
            
        else:
            # Mode = dcmatch & dutype == 2      .acmatch i(vg) set to only 1 command.
            # Mode = noise_mc & dutype == 2     .noise only analysis one port.
            print(' **Error** dut format does not support Analysis Mode: ' + self.cfg.Mode); exit()

        return Text + '\n'

    def alter_condition(self):
        Text = ''
        for i,cor in enumerate(self.cfg.Corner):
            if i != 0:
                Text += '.alter\n'
                Text += self.lib_attach_add('.del lib', self.cfg.Corner[i-1])
                Text += self.lib_attach_add('.lib', self.cfg.Corner[i])

            for j,temp in enumerate(self.cfg.Temp):
                vdd_list = self.cfg.Vdd if i+j != 0 else self.cfg.Vdd[1:]
                for k,vdd in enumerate(vdd_list):
                    if i == 0 or j+k != 0: Text += '.alter\n'
                    Text += '.TEMP ' + temp + '\n'
                    Text += '.param vdd=' + vdd + '\n'
        return Text

    def combine(self,Etest):
        return self.set_MODEL(Etest) + self.set_DEVICE(Etest) + self.alter_condition() + '.end\n'

    def save(self,Etest):
        Text = self.combine(Etest)

        if not os.path.exists(self.cfg.path_Output): os.mkdir(self.cfg.path_Output)      
        if not os.path.exists(self.cfg.path_Folder): os.mkdir(self.cfg.path_Folder)

        with open(self.cfg.path_Folder + '/' + Etest + '.sp','w') as sp:
            sp.write(Text)
