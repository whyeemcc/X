import os,sys
import time
from Setting import *

class Mining():

    def __init__(self,cfg):
        self.cfg = cfg
        self.Etest_Unit = self.Etest_Unit()

    def wr(self,f,x):
        return f.write(x+'\n')

    def unit(self,Etest):
        m = re.search('\$unit(\(.+\))', open(Etest+'.sp').read(), re.I)
        if m is not None: return Etest + m.group(1)
        else:             return Etest

    def Etest_Unit(self):
        temp = []
        for Etest in self.cfg.Etest:
            if self.cfg.Type in ['typ','sens']: temp += [self.unit(Etest)]
            else:                               temp += [self.unit(Etest)+'_median', self.unit(Etest)+'_sigma']
        return temp

    def median(self,list):
        list.sort()
        if len(list) % 2 == 0: return (list[int(len(list)/2-1)] + list[int(len(list)/2)])/2
        else:                  return list[int((len(list)-1)/2)]

    def std(self,list):
        mean = sum(list)/len(list)
        std_list = [(x-mean)**2 for x in list]
        return (sum(std_list)/(len(list)-1))**0.5

    def raw_list(self,list):
        temp = []
        for x in list:
            try:    temp += [eval(x)]
            except: pass
        return temp

    def median_std(self,list):
        list = self.raw_list(list)
        return ['%s' % self.median(list), '%s' % self.std(list)]

    def median_std_mis(self,Etest,listA,listB):
        import json
        with open('../bin/mis/misType.jsonx','r') as f:
            misType = json.load(f)

        type = misType[Etest]

        listA = self.raw_list(listA)
        listB = self.raw_list(listB)

        if type == 'Delta':   list = [A-B for A,B in zip(listA,listB)]
        elif type == 'Ratio': list = [(A-B)/((A+B)/2) for A,B in zip(listA,listB)]

        return ['%s' % self.median(listA + listB), '%s' % self.std(list)]

    def extract_data(self):
        dic = {}

        for Etest in self.cfg.Etest:
            f = open(Etest + meas); Result = f.read()

            if self.cfg.Type in ['typ','sens','noise_mc'] and self.cfg.dutype == 1:
                dic[Etest] = hunter_meas(Etest,Result)

            elif self.cfg.Type in ['typ','sens'] and self.cfg.dutype == 2:
                for i,size in enumerate(self.cfg.Sizes):
                    dic[Etest+str(i+1)] = hunter_meas(Etest+str(i+1),Result)

            elif self.cfg.Type == 'monte':
                for i,size in enumerate(self.cfg.Sizes):
                    dic[Etest+str(i+1)] = hunter_meas(Etest+str(i+1),Result)

            elif self.cfg.Type == 'mis':
                for i,size in enumerate(self.cfg.Sizes):
                    dic[Etest+str(i+1)+'_a'] = hunter_meas(Etest+str(i+1)+'_a',Result)
                    dic[Etest+str(i+1)+'_b'] = hunter_meas(Etest+str(i+1)+'_b',Result)

            elif self.cfg.Type == 'mos_mc':
                for i,size in enumerate(self.cfg.Sizes):
                    dic[Etest+str(i+1)+'_n'] = hunter_meas(Etest+str(i+1)+'_n',Result)
                    dic[Etest+str(i+1)+'_p'] = hunter_meas(Etest+str(i+1)+'_p',Result)
            f.close()
        return dic

    def record_data(self,dic,csv,portion,np=''):

        if self.cfg.Type in ['typ','sens'] and self.cfg.dutype == 1:
            start = portion*len(self.cfg.Sizes)
            for n,size in enumerate(self.cfg.Sizes):
                list = size[:]
                for Etest in self.cfg.Etest:
                    try:                list += [dic[Etest][start+n]]
                    except IndexError:  list += [' ']
                self.wr(csv,','.join(list))

        elif self.cfg.Type in ['typ','sens'] and self.cfg.dutype == 2:
            start = portion
            for n,size in enumerate(self.cfg.Sizes):
                list = [size]
                for Etest in self.cfg.Etest:
                    try:                list += [dic[Etest+str(n+1)][start]]
                    except IndexError:  list += [' ']
                self.wr(csv,','.join(list))

        elif self.cfg.Type == 'mis':
            start = portion*self.cfg.MC_num
            for n,size in enumerate(self.cfg.Sizes):
                list = size[:] if self.cfg.dutype == 1 else [size]
                for Etest in self.cfg.Etest:
                    try:
                        listA = dic[Etest + str(n+1) + '_a'][start : start + self.cfg.MC_num]
                        listB = dic[Etest + str(n+1) + '_b'][start : start + self.cfg.MC_num]
                        list += self.median_std_mis(Etest,listA,listB)
                    except IndexError:
                        list += ['','']
                self.wr(csv,','.join(list))

        elif self.cfg.Type == 'monte':   
            start = portion*self.cfg.MC_num
            for n,size in enumerate(self.cfg.Sizes):
                list = size[:] if self.cfg.dutype == 1 else [size]
                for Etest in self.cfg.Etest:
                    list += self.median_std(dic[Etest + str(n+1)][start : start + self.cfg.MC_num])
                self.wr(csv,','.join(list))

                for m in range(self.cfg.MC_num):
                    list2 = ['' for x in size]; list2[-1] = str(m+1)
                    for Etest in self.cfg.Etest:
                        try:                list2 += [dic[Etest + str(n+1)][start + m],'']
                        except IndexError:  list2 += ['','']
                    list2.pop()
                    self.wr(csv,','.join(list2))

        elif self.cfg.Type == 'mos_mc':   
            start = portion*self.cfg.MC_num
            for n,size in enumerate(self.cfg.Sizes):
                list = size[:] if self.cfg.dutype == 1 else [size]
                for Etest in self.cfg.Etest:
                    list += self.median_std(dic[Etest + str(n+1) + '_' + np][start : start + self.cfg.MC_num])
                self.wr(csv,','.join(list))

                for m in range(self.cfg.MC_num):
                    list2 = ['' for x in size]; list2[-1] = str(m+1)
                    for Etest in self.cfg.Etest:
                        try:                list2 += [dic[Etest + str(n+1) + '_' + np][start + m],'']
                        except IndexError:  list2 += ['','']
                    list2.pop()
                    self.wr(csv,','.join(list2))

        elif self.cfg.Type == 'noise_mc':
            start = portion*len(self.cfg.Sizes)*self.cfg.MC_num
            for n,size in enumerate(self.cfg.Sizes):
                lump = n*self.cfg.MC_num
                list = size[:]
                for Etest in self.cfg.Etest:
                    list += self.median_std(dic[Etest][start + lump : start + lump + self.cfg.MC_num])
                self.wr(csv,','.join(list))

                for m in range(self.cfg.MC_num):
                    list2 = ['' for x in size]; list2[-1] = str(m+1)
                    for Etest in self.cfg.Etest:
                        try:                list2 += [dic[Etest][start + lump + m],'']
                        except IndexError:  list2 += ['','']
                    list2.pop()
                    self.wr(csv,','.join(list2))

    def head(self,csv,device):
        self.wr(csv,'Model: ' + self.cfg.model_path)
        self.wr(csv,'Cfg: ' + cfg_File)
        self.wr(csv,'Simulator: ' + system + ' + ' + engine)
        self.wr(csv,'Device: ' + device)

    def condition(self,csv,cor,temp,vdd):
        self.wr(csv,'')
        self.wr(csv,'Corner: ' + cor)
        self.wr(csv,'Temp: ' + temp)
        self.wr(csv,'Vdd: ' + vdd)

        if self.cfg.dutype == 1:   self.wr(csv,','.join([x for x in self.cfg.Instance + self.Etest_Unit]))
        elif self.cfg.dutype == 2: self.wr(csv,','.join(['Dut'] + self.Etest_Unit))

        return csv

    def record_block(self,dic,csv_file,device,np):
        with open(csv_file,'w') as csv:
            self.head(csv,device)
            for i,cor in enumerate(self.cfg.Corner):
                for j,temp in enumerate(self.cfg.Temp):
                    for k,vdd in enumerate(self.cfg.Vdd):
                        portion = i*len(self.cfg.Temp)*len(self.cfg.Vdd) + j*len(self.cfg.Vdd) + k
                        all_cor = ' & '.join([cor] + self.cfg.Corner_attach) if self.cfg.Attach_switch == 'on' else cor
                        self.condition(csv,all_cor,temp,vdd)
                        self.record_data(dic,csv,portion,np)

    def save(self):
        dic = self.extract_data()
        time_now = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime())
        os.chdir('../')

        if self.cfg.Type != 'mos_mc':
            csv_file = r'X_output_{}_{}_{}.csv'.format(abbr,cfg_File,time_now)
            self.record_block(dic,csv_file,self.cfg.Device,'')
            open_csv(csv_file)
        elif self.cfg.Type == 'mos_mc':
            for np,device in zip(['n','p'], self.cfg.Device):
                csv_file = r'X_output_{}_mc_{}_{}_{}.csv'.format(abbr,np,cfg_File,time_now)
                self.record_block(dic,csv_file,device,np)
                open_csv(csv_file)


    def del_temp(self):
        postfix_list = [
        '.ac',
        '.ic',
        '.ma',
        '.pa',
        '.st',
        '.sw',
        '.ms',
        '.ac',
        '.ic',
        '.model_info'
        ]

        for fname in os.listdir(self.cfg.Folder):
            m = re.search(r'(\..+?)\d+',fname)
            if m is not None:
                if m.group(1) in postfix_list:
                    try:    os.remove(self.cfg.Folder + '/' + fname)
                    except: pass

    if __name__ == '__main__':
        pass