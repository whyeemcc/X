import os,sys,platform

system = platform.system()
abbr = 'hsp' if len(sys.argv) == 1 else sys.argv[1]

path = os.path.join(sys.path[0], '../'); os.chdir(path)

cfg_remain = [x for x in os.listdir(path) if x[-4:] == '.cfg']
cfg_select = []

def Show(cfg_remain, cfg_select):
    if system == 'Windows': o = os.system('cls')
    elif system == 'Linux': o = os.system('clear')
    
    print('\n---------------- Xmodel ----------------')
    for i,cfg in enumerate(cfg_remain):
        print(' {}: {}'.format(i+1,cfg))
    print('\n---------------- Select ----------------')
    for cfg in cfg_select:
        print(' ' + cfg)
    print('\n----------------------------------------')
    print(' press Enter to run\n')
    
Show(cfg_remain, cfg_select)    

while True:
    x = input('Select: ')
    
    if x == '': break
    
    try: x = int(x)
    except ValueError: continue
    
    if x > len(cfg_remain): continue
    
    cfg_select.append(cfg_remain[x-1])
    del cfg_remain[x-1]
    Show(cfg_remain, cfg_select)
    
for cfg in cfg_select:
    os.chdir(path + '/X')
    os.system('python X.py {} "{}"'.format(abbr,cfg))
    