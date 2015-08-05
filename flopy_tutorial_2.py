__author__ = 'langevin'

import numpy as np
import flopy

# modflow_exe ='/home/mikey/Dropbox/gac/original_libraries/Unix/src/mf2005'
# modflow_exe ='/home/mikey/Dropbox/gac/pymake/mf2005_pymade'
modflow_exe ='/home/mikey/Dropbox/gac/pymake/functional_mf2005'
modelname = 'tutorial2'

# flopy.utils.HeadFile and flopy.utils.CellBudgetFile don't work on Mike's ubuntu laptop (michael.james.asher@gmail.com)
import fortranfile
def read_heads(file_name,nlay, nrow, ncol, nstp):
    ''' flopy's function to read in heads is broken '''
    f = fortranfile.FortranFile(file_name)
    heads = np.empty((nlay, nrow, ncol, sum(nstp)) ) #, dtype=np.float32)
    for i in range(sum(nstp)):
        for j in range(nlay):
            f.readReals() # not sure what this 10 value array is
            raw = f.readReals()
            heads[j,:,:,i] = np.reshape(raw, (nrow, ncol))

    f.close()
    return heads


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

def run():

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
    mf = flopy.modflow.Modflow(modelname, model_ws=modelname, exe_name=modflow_exe)
    # (modelname='modflowtest', namefile_ext='nam', version='mf2005', exe_name='mf2005.exe', listunit=2, model_ws='.', external_path=None, verbose=False, load=True, silent=0)


    dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc,
                                   top=ztop, botm=botm[1:],
                                   nper=nper, perlen=perlen, nstp=nstp,
                                   steady=steady)
    # (model, nlay=1, nrow=2, ncol=2, nper=1, delr=1.0, delc=1.0, laycbd=0, top=1, botm=0, perlen=1, nstp=1, tsmult=1, steady=True, itmuni=4, lenuni=2, extension='dis', unitnumber=11)

    bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)
    # (model, ibound=1, strt=1.0, ifrefm=True, ixsec=False, ichflg=False, stoper=None, hnoflo=-999.99, extension='bas', unitnumber=13)

    lpf = flopy.modflow.ModflowLpf(mf, hk=hk, vka=vka, sy=sy, ss=ss, laytyp=laytyp)
    # (model, laytyp=0, layavg=0, chani=1.0, layvka=0, laywet=0, ilpfcb=53, hdry=-1e+30, iwdflg=0, wetfct=0.1, iwetit=1, ihdwet=0, hk=1.0, hani=1.0, vka=1.0, ss=1e-05, sy=0.15, vkcb=0.0, wetdry=-0.01, storagecoefficient=False, constantcv=False, thickstrt=False, nocvcorrection=False, novfc=False, extension='lpf', unitnumber=15)

    # pcg = flopy.modflow.ModflowPcg(mf)
    sip = flopy.modflow.ModflowSip(mf, mxiter=100, hclose=1e-3)
    # (model, mxiter=200, nparm=5, accl=1, hclose=1e-05, ipcalc=1, wseed=0, iprsip=0, extension='sip', unitnumber=25)


    # Make list for stress period 1
    stageleft = 10.
    stageright = 10.
    bound_sp1 = []
    for il in xrange(nlay):
        condleft = hk * (stageleft - zbot) * delc
        condright = hk * (stageright - zbot) * delc
        for ir in xrange(nrow):
            bound_sp1.append([il, ir, 0, stageleft, condleft])
            bound_sp1.append([il, ir, ncol - 1, stageright, condright])
    print 'Adding ', len(bound_sp1), 'GHBs for stress period 1.'

    # Make list for stress period 2
    stageleft = 10.
    stageright = 0.
    condleft = hk * (stageleft - zbot) * delc
    condright = hk * (stageright - zbot) * delc
    bound_sp2 = []
    for il in xrange(nlay):
        for ir in xrange(nrow):
            bound_sp2.append([il, ir, 0, stageleft, condleft])
            bound_sp2.append([il, ir, ncol - 1, stageright, condright])
    print 'Adding ', len(bound_sp2), 'GHBs for stress period 2.'

    # We do not need to add a dictionary entry for stress period 3.
    # Flopy will automatically take the list from stess period 2 and apply it
    # to the end of the simulation, if necessary
    stress_period_data = {0: bound_sp1, 1: bound_sp2}

    # Create the flopy ghb object
    ghb = flopy.modflow.ModflowGhb(mf, stress_period_data=stress_period_data)

    # Create the well package
    # Remember to use zero-based layer, row, column indices!
    pumping_rate = -100.
    wel_sp1 = [[0, nrow/2 - 1, ncol/2 - 1, 0.]]
    wel_sp2 = [[0, nrow/2 - 1, ncol/2 - 1, 0.]]
    wel_sp3 = [[0, nrow/2 - 1, ncol/2 - 1, pumping_rate]]
    stress_period_data = {0: wel_sp1, 1: wel_sp2, 2: wel_sp3}
    wel = flopy.modflow.ModflowWel(mf, stress_period_data=stress_period_data)

    # Output control
    stress_period_data = {(0, 0): ['save head',
                                   'save drawdown',
                                   'save budget',
                                   'print head',
                                   'print budget']}
    save_head_every = 1
    oc = flopy.modflow.ModflowOc(mf, stress_period_data=stress_period_data)

    # Write the model input files
    mf.write_input()

    # Run the model
    success, mfoutput = mf.run_model(silent=False, pause=False)
    if not success:
        raise Exception('MODFLOW did not terminate normally.')

    # Imports
    import matplotlib.pyplot as plt
    import flopy.utils.binaryfile as bf

    # Create the headfile object
    # output_heads = read_heads(modelname+'/'+modelname+'.hds',nlay, nrow, ncol, nstp)
    headobj = bf.HeadFile(modelname+'/'+modelname+'.hds')
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



# Imports
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf

def plot():

    headobj = bf.HeadFile(modelname+'/'+modelname+'.hds')
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
    run()
    # plot()