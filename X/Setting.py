import re,os,sys,platform

system = platform.system()

if len(sys.argv) == 1:  abbr, cfg_File = 'hsp', 'xxxx.cfg'
elif len(sys.argv) > 1: abbr, cfg_File = sys.argv[1], sys.argv[2]
    
path_cfg, cfg_File = os.path.split(cfg_File)

if   abbr == 'hsp': engine = 'hspice';    meas = '.lis';     curve = '.lis';   log = '.lis'
elif abbr == 'spe': engine = 'spectre';   meas = '.measure'; curve = '.print'; log = '.out'
elif abbr == 'afs': engine = 'fastspice'; meas = '.log';     curve = '.log';   log = '.log'

if system == 'Windows' and engine == 'hspice': os.system('start/MIN hspice -C')

def engine_run(etest):    
    if   system == 'Windows' and abbr == 'hsp': os.system('start/WAIT/MIN hspice -C -i {}.sp -o {}'.format(etest,etest))        
    elif system == 'Linux'   and abbr == 'hsp': os.system('gnome-terminal --disable-factory -x bash -c "hspice -i {}.sp -o {}"'.format(etest,etest))
    elif system == 'Linux'   and abbr == 'spe': os.system('gnome-terminal --disable-factory -x bash -c "spectre +spice {}.sp"'.format(etest))
    elif system == 'Linux'   and abbr == 'afs': os.system('gnome-terminal --disable-factory -x bash -c "afs {}.sp"'.format(etest))
    else: input(' **Error** {} + {} not support yet!'.format(system,abbr)); exit()
    
def hunter_meas(param,Text):
    if   engine == 'hspice':    return re.findall(r'\W' + param + r'\s*=\s*(.*?)\s', Text, re.I)
    elif engine == 'spectre':   return re.findall(r'\W' + param + r'.*?=\s*(.*?)\s', Text, re.DOTALL|re.I)
    elif engine == 'fastspice': return re.findall(r'\W' + param + r'\s*=\s*(.*?)\s', Text, re.I)
    
def fault_check(log_File):
    content = open(log_File).read()
    if   engine == 'hspice':    m = re.search('\*\*(error|warning)\*\*.*\n', content, re.I)
    elif engine == 'spectre':   m = re.search('ERROR:.*\n', content, re.I)
    elif engine == 'fastspice': m = None
    if m is not None: printColor('\n'+m.group(), RED)
    
def open_csv(csv_file):
    if   system == 'Windows': os.system('"{}"'.format(csv_file))
    elif system == 'Linux':   os.system('gedit "{}"'.format(csv_file))
    
def hunter_curve(Text):
    list = []
    for block in re.findall(r'\nx\n.*?\ny\n', Text, re.DOTALL):
        n = re.findall(r'((-|\+)?\d+(\.\d+)?((e|E)(-|\+)?\d+)?)\s\n', block)
        list.append([x[0] for x in n])
    return list
    
RED = 0x0c; BLUE = 0x09; GREEN = 0x0a; SKYBLUE = 0x0b; PINK = 0x0d; YELLOW = 0x0e; WHITE = 0x0f; DARKWHITE = 0x07
if system == 'Windows':
    import ctypes
    # get handle
    STD_OUTPUT_HANDLE = -11
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    
    def set_cmd_text_color(color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle,color)
        return Bool
        
    def printColor(mess,code):
        set_cmd_text_color(code)
        sys.stdout.write(mess+'\n')
        set_cmd_text_color(DARKWHITE)
elif system == 'Linux':
    printColor = lambda x,code: print(x)
    