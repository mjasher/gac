"""
thanks to http://stackoverflow.com/questions/15875533/using-python-ctypes-to-interface-fortran-with-python
"""

# import subprocess
# compile_cmd = 'gfortran -shared -fPIC  -g -o test.so test.f90'
# subprocess.check_call(compile_cmd.split())

"""
TODO
* need to pass everything from .bas file to mf2005.f RUN
    eg. IXSEC=0 ICHFLG=0 IFREFM=0 IPRTIM=0 STOPER=0.0 LLOC=1
* resolve lay, row, col vs col, row, lay
* get rid of allocate routines alltogether!

for KPER in range(NPER):
    for KSTP in range(NSTP[KPER]):
        for KITER in range(MXITER):
            approximate_solution()
            if converged(): 
                break

        save_appropriate_output()

"""



# from ctypes import ctypes.c_char_p, c_long, c_float, byref, CDLL, POINTER
import ctypes
import numpy as np


# verbatim from flopy tutorial2
# =============================
# Model domain and grid definition
Lx = 1000.
Ly = 1000.
ztop = 0.
zbot = -50.
nlay = 1
nrow = 10
ncol = 10
delr = Lx / ncol
delc = Ly / nrow
delv = (ztop - zbot) / nlay
botm = np.linspace(ztop, zbot, nlay + 1)
hk = 1.
vka = 1.
sy = 0.1
ss = 1.e-4
laytyp = 1

# Variables for the BAS package
# Note that changes from the previous tutorial!
ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
strt = 10. * np.ones((nlay, nrow, ncol), dtype=np.float32)

# Time step parameters
nper = 3
perlen = [1, 100, 100]
nstp = [1, 100, 100]
steady = [True, False, False]

# Flopy objects
modelname = 'tutorial2'
# mf_exe = '/home/mikey/Dropbox/gac/pymake/mf2005_pymade'
# #mf_exe = '/home/mikey/Dropbox/gac/original_libraries/Unix/src/mf2005'
# mf = flopy.modflow.Modflow(modelname, exe_name=mf_exe)
# dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc,
#                                top=ztop, botm=botm[1:],
#                                nper=nper, perlen=perlen, nstp=nstp,
#                                steady=steady)
# bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)
# lpf = flopy.modflow.ModflowLpf(mf, hk=hk, vka=vka, sy=sy, ss=ss, laytyp=laytyp)
# pcg = flopy.modflow.ModflowPcg(mf)

# Make list for stress period 1
stageleft = 10.
stageright = 10.
bound_sp1 = []
for il in range(nlay):
    condleft = hk * (stageleft - zbot) * delc
    condright = hk * (stageright - zbot) * delc
    for ir in range(nrow):
        bound_sp1.append([il, ir, 0, stageleft, condleft])
        bound_sp1.append([il, ir, ncol - 1, stageright, condright])
print('Adding ', len(bound_sp1), 'GHBs for stress period 1.')

# Make list for stress period 2
stageleft = 10.
stageright = 0.
condleft = hk * (stageleft - zbot) * delc
condright = hk * (stageright - zbot) * delc
bound_sp2 = []
for il in range(nlay):
    for ir in range(nrow):
        bound_sp2.append([il, ir, 0, stageleft, condleft])
        bound_sp2.append([il, ir, ncol - 1, stageright, condright])
print('Adding ', len(bound_sp2), 'GHBs for stress period 2.')

# We do not need to add a dictionary entry for stress period 3.
# Flopy will automatically take the list from stress period 2 and apply it
# to the end of the simulation
stress_period_data = {0: bound_sp1, 1: bound_sp2}

# =============================


# ncol = 10
# nrow = 10
# nlay = 1

ibound = np.ones((ncol,nrow,nlay))
strt = 10.0*np.ones((ncol,nrow,nlay))
hnoflo = -999.0
# name = "../tutorial2/tutorial2"


# ibound[1:3,1:3,:] = 0


# print a
# print "SUM", numpy.sum(a)

# ibound_c_types = (c_float*(ncol*nrow*nlay))()
# ibound_c_types[:] = ibound.flatten()
# tot = c_float()

def run():


    # should be list of (type, value) tuples, order matching that of RUN subroutine in mf2005.f
    fortran_types, fortran_args = zip(*[
        (ctypes.POINTER(ctypes.c_long), ctypes.c_long(ncol)),
        (ctypes.POINTER(ctypes.c_long), ctypes.c_long(nrow)),
        (ctypes.POINTER(ctypes.c_long), ctypes.c_long(nlay)),
        (ctypes.POINTER(ctypes.c_float), ctypes.c_float(hnoflo)),
        (np.ctypeslib.ndpointer(dtype=np.long,
                            # ndim=3,
                             shape=(ncol,nrow,nlay),
                             flags='F_CONTIGUOUS'), ibound.astype(dtype=np.long, order="F")),
        (np.ctypeslib.ndpointer(dtype=np.float64,
                                     shape=(ncol,nrow,nlay),
                                     flags='F_CONTIGUOUS'), strt.astype(dtype=np.float64, order="F")),
        (ctypes.c_char_p, modelname),
        (ctypes.c_long, len(modelname))
    ])


    mf2005 = ctypes.CDLL('./../pymake/mf2005.so')
    mf2005.run_.argtypes = fortran_types 
    run_result = mf2005.run_(*fortran_args)


def run_in_process():
    from multiprocessing import Process

    # def f(name):
    #     print 'hello', name
    # p = Process(target=f, args=('bob',))

    # using another process means this python program doesn't stop with mf2005.f STOP
    p = Process(target=run)
    p.start()
    p.join()



"""
===============================================
"""

# Imports
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf
import numpy as np
modelname = 'tutorial2'
Lx = 1000.
Ly = 1000.
ztop = 0.
zbot = -50.
nlay = 1
nrow = 10
ncol = 10
delr = Lx / ncol
delc = Ly / nrow

def plot():

    headobj = bf.HeadFile(modelname+'.hds')
    times = headobj.get_times()

    # Setup contour parameters
    levels = np.arange(1, 10, 1)
    extent = (delr/2., Lx - delr/2., delc/2., Ly - delc/2.)
    print 'Levels: ', levels
    print 'Extent: ', extent

    # Well point
    wpt = ((float(ncol/2)-0.5)*delr, (float(nrow/2-1)+0.5)*delc)
    wpt = (450., 550.)

    # Make the plots
    mytimes = [1.0, 101.0, 201.0]
    for iplot, time in enumerate(mytimes):
        print '*****Processing time: ', time
        # head = output_heads[:,:,:,time-1]
        head = headobj.get_data(totim=time)
        #Print statistics
        print 'Head statistics'
        print '  min: ', head.min()
        print '  max: ', head.max()
        print '  std: ', head.std()

        #Create the plot
        #plt.subplot(1, len(mytimes), iplot + 1, aspect='equal')
        plt.subplot(1, 1, 1, aspect='equal')
        plt.title('stress period ' + str(iplot + 1))
        plt.imshow(head[0, :, :], extent=extent, cmap='BrBG', vmin=0., vmax=10.)
        plt.colorbar()
        CS = plt.contour(np.flipud(head[0, :, :]), levels=levels, extent=extent,
                         zorder=10)
        plt.clabel(CS, inline=1, fontsize=10, fmt='%1.1f', zorder=11)
        mfc = 'None'
        if (iplot+1) == len(mytimes):
            mfc='black'
        plt.plot(wpt[0], wpt[1], lw=0, marker='o', markersize=8, 
                 markeredgewidth=0.5,
                 markeredgecolor='black', markerfacecolor=mfc, zorder=9)
        plt.text(wpt[0]+25, wpt[1]-25, 'well', size=12, zorder=12)
        plt.show()

    plt.show()

    # Plot the head versus time
    idx = (0, nrow/2 - 1, ncol/2 - 1)
    # ts = output_heads[0, nrow/2 - 1, ncol/2 - 1,:]
    ts = headobj.get_ts(idx)
    plt.subplot(1, 1, 1)
    ttl = 'Head at cell ({0},{1},{2})'.format(idx[0] + 1, idx[1] + 1, idx[2] + 1)
    plt.title(ttl)
    plt.xlabel('time')
    plt.ylabel('head')
    plt.plot(ts[:,1])
    plt.show()



if __name__ == '__main__':


    run_in_process()
    plot()
