
'''
following http://www.swig.org/tutorial.html
* write example.c
* write example.i
'''

import subprocess
subprocess.call(["swig", "-python", "example.i"])
subprocess.call(["gcc", "-fPIC", "-c", "example.c", "example_wrap.c", "-I/usr/include/python2.7"])
subprocess.call(["ld","-shared", "example.o", "example_wrap.o", "-o", "_example.so"])
 


import example
print example.fact(4)
print example.my_mod(23,7)
print example.cvar.My_variable + 4.5
