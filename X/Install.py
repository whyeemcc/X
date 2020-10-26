import os
import sys
import re

Xmodel_path = sys.path[0]

for dir in sys.path:
    m = re.search(r'.*Anaconda3$',dir,re.I)
    if m is not None:
        python_path = m.group()
        break

fnew = open(python_path + '/Scripts/runX.bat','w')
fnew.write('@echo off\n')
fnew.write('title %cd%\n')
fnew.write('python ' + Xmodel_path + '/X.py %*')
fnew.close()

input('install completed.')