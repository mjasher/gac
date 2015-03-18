#from numpy import ones, zeros, empty
import numpy as np
from flopy.mbase import Package
from flopy.utils import util_2d,util_3d

class ModflowSwi(Package):
    'Salt Water Intrusion (SWI) package class'
    def __init__(self, model, npln=1, istrat=1, iswizt=53, nprn=1, toeslope=0.05, tipslope=0.05, \
                 zetamin=0.005, delzeta=0.05, nu=0.025, zeta=[], ssz=[], isource=0, extension='swi', fname_output='swi.zta'):
        """
        Package constructor.

        """
        Package.__init__(self, model) # Call ancestor's init to set self.parent
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        self.unit_number = [29,53]
        self.extension = extension
        self.file_name = [ self.parent.name + '.' + self.extension, fname_output ]
        self.name = [ 'SWI', 'DATA(BINARY)' ]
        self.heading = '# Salt Water Intrusion package file for MODFLOW-2000, generated by Flopy.'
        self.npln = npln
        self.istrat = istrat
        self.iswizt = iswizt
        self.nprn = nprn
        self.toeslope = toeslope
        self.tipslope = tipslope
        self.zetamin = zetamin
        self.delzeta = delzeta
        # Create arrays so that they have the correct size
        if self.istrat == 1:
            #self.nu = empty( self.npln+1 )
            self.nu = util_2d(model,(self.npln+1,),np.float32,nu,name='nu')
        else:
            #self.nu = empty( self.npln+2 )
            self.nu = util_2d(model,(self.npln+2,),np.float32,nu,name='nu')
        self.zeta = []
        for i in range(nlay):
            #self.zeta.append( empty((nrow, ncol, self.npln)) )
            self.zeta
        #self.ssz = empty((nrow, ncol, nlay))
        #self.isource = empty((nrow, ncol, nlay),dtype='int32')
        # Set values of arrays
        #self.assignarray_old( self.nu, nu )
        #for i in range(nlay):
        #    self.assignarray_old( self.zeta[i], zeta[i] )
        #self.assignarray_old( self.ssz, ssz )
        #self.assignarray_old( self.isource, isource )
        for i in range(nlay):           
            self.zeta.append(util_2d(model,(self.npln,nrow,ncol),np.float32,zeta[i],name='zeta_'+str(i+1)))        
        self.ssz = util_3d(model,(nlay,nrow,ncol),np.float32,ssz,name='ssz')        
        self.isource = util_3d(model,(nlay,nrow,ncol),np.int,isource,name='isource')
        self.parent.add_package(self)


    def __repr__( self ):
        return 'Salt Water Intrusion package class'


    def write_file(self):
        """
        Write the package input file.

        """
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        # Open file for writing
        f_swi = open(self.fn_path, 'w')
        # First line: heading
        #f_swi.write('%s\n' % self.heading)  # Writing heading not allowed in SWI???
        f_swi.write( '%10d%10d%10d%10d\n' % (self.npln, self.istrat, self.iswizt, self.nprn) )
        f_swi.write( '%10f%10f%10f%10f\n' % (self.toeslope, self.tipslope, self.zetamin, self.delzeta) )
        self.parent.write_array_old( f_swi, self.nu, self.unit_number[0], True, 13, 20 )
        for isur in range(self.npln):
            #for ilay in range(nlay):
                #self.parent.write_array_old( f_swi, self.zeta[ilay][:,:,isur], self.unit_number[0], True, 13, ncol )
            f_swi.write(self.zeta[isur].get_file_entry())
        #for ilay in range(nlay):
        #        self.parent.write_array_old( f_swi, self.ssz[:,:,ilay], self.unit_number[0], True, 13, ncol )
        f_swi.write(self.ssz.get_file_entry())
        #for ilay in range(nlay):
        #        self.parent.write_array_old( f_swi, self.isource[:,:,ilay], self.unit_number[0], True, 13, ncol )
        f_swi.write(self.isource.get_file_entry())

        # Close file
        f_swi.close()

