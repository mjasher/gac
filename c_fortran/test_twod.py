# http://docs.oracle.com/cd/E19957-01/806-3593/11_cfort.html

import subprocess

subprocess.call(['gcc','-c', 'twod_c.c'])
subprocess.call(['gfortran','twod_f.f', 'twod_c.o'])
subprocess.call(['./a.out'])