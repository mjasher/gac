"""
thanks to http://stackoverflow.com/questions/15875533/using-python-ctypes-to-interface-fortran-with-python
"""

# import subprocess
# compile_cmd = 'gfortran -shared -fPIC  -g -o test.so test.f90'
# subprocess.check_call(compile_cmd.split())


# from ctypes import ctypes.c_char_p, c_long, c_float, byref, CDLL, POINTER
import ctypes
mf2005 = ctypes.CDLL('./../pymake/mf2005.so')

import numpy as np

ncol = 10
nrow = 10
nlay = 1
ibound = np.ones((ncol,nrow,nlay), dtype=np.long, order="F")
strt = 10.0*np.ones((ncol,nrow,nlay), dtype=np.float64, order="F")
hnoflo = -9999.0

# ibound[1:3,1:3,:] = 0

name = "../tutorial2/tutorial2"

# print a
# print "SUM", numpy.sum(a)

# ibound_c_types = (c_float*(ncol*nrow*nlay))()
# ibound_c_types[:] = ibound.flatten()
# tot = c_float()



mf2005.setup_.argtypes = [
							ctypes.POINTER(ctypes.c_float), 
							ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long), 
							np.ctypeslib.ndpointer(dtype=np.long,
												# ndim=3,
                                                 shape=(ncol,nrow,nlay),
                                                 flags='F_CONTIGUOUS'),
												np.ctypeslib.ndpointer(dtype=np.float64,
												# ndim=3,
                                                 shape=(ncol,nrow,nlay),
                                                 flags='F_CONTIGUOUS'),
							ctypes.c_char_p, ctypes.c_long
							]

mf2005.setup_(
	ctypes.c_float(hnoflo), 
	ctypes.c_long(ncol), ctypes.c_long(nrow), ctypes.c_long(nlay), 
	ibound,
	strt,
	name, len(name)
	)


# mf2005.setup_(np.float64(hnoflo), np.long(nlay), np.long(nrow), np.long(ncol), ibound, strt, name, len(name))
# mf2005.setup_(byref(c_float(hnoflo)), byref(c_long(nlay)), byref(c_long(nrow)), byref(c_long(ncol)), ibound, strt, name, len(name))
# mf2005.setup_( byref(ibound_c_types), byref(tot), byref(c_long(nlay)), byref(c_long(nrow)), byref(c_long(ncol)) )
