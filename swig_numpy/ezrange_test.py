import subprocess

subprocess.call(['python', 'setup.py', 'build'])

'''
this does something like
for fortran_file in ["gwf2bas7.f", "utl7.f"]:
	subprocess.call(["gfortran", "-c", "-fPIC", "-fopenmp", fortran_file])
subprocess.call(["swig", "-python", "example.i"])
subprocess.call(["gcc", "-c",  "-fPIC", "example.c", "example_wrap.c", "-I/usr/include/python2.7"])
# subprocess.call(["ld","-shared", "example.o", "example_wrap.o", "-o", "_example.so"])
subprocess.call(["gfortran","-shared", "utl7.o", "gwf2bas7.o", "example.o", "example_wrap.o",  "-o", "_example.so"])
'''

subprocess.call(['cp', '/home/mikey/Dropbox/gac/swig_numpy/build/lib.linux-x86_64-2.7/_ezrange.so', '.'])

# jacqFLOW

import ezrange
print "range 10", ezrange.range(10)

import numpy
a = numpy.array([1,2,3],'d')
ezrange.inplace(a)
print a

