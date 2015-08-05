#! /usr/bin/env python
"""
Make the binary executable for MODFLOW-USG

Originally by Christian D. Langevin (langevin@usgs.gov)
"""

import os
import subprocess
import shutil
import sys
import getopt
from dag import order_source_files, order_c_source_files


def compilenix(srcfiles, fc, fflags, cc, cflags, target):  
    """
    Make target on Mac OS or Linux
    """
    syslibs = ['-lc']

    #build object files
    objfiles = []
    for srcfile in srcfiles:
        srcname, srcext = os.path.splitext(srcfile)
        filename = srcname.split(os.path.sep)[-1]
        cmdlist = []

        # save time by compiling only if source is more recently changed than .o
        # TODO what about dependancies?
        # if os.path.exists(srcname+'.o'):
        #     if os.path.getmtime(srcfile) < os.path.getmtime(srcname+'.o'):
        #         objfiles.append(srcname + '.o')
        #         continue
        
        if srcfile.endswith('.c') or srcfile.endswith('.cpp'):  
            
            # checks if already exists, remove
            # if os.path.exists(srcname+'.o') and os.path.getmtime(srcfile) < os.path.getmtime(srcname+'.o'):
                # objfiles.append(srcname + '.o')
                # continue
            
            cmdlist.append(cc)     
            for switch in cflags:      
                cmdlist.append(switch)     
        elif srcfile.endswith('.f') or srcfile.endswith('.f90'):
            
            # checks if already exists, remove
            # print srcfile
            # if os.path.exists(srcname+'.o') and  os.path.getmtime(srcfile) < os.path.getmtime(srcname+'.o'):
                # objfiles.append(srcname + '.o')
                # continue
            
            cmdlist.append(fc)
            for switch in fflags:
                cmdlist.append(switch)
        else:
            continue
        cmdlist.append('-c')
        cmdlist.append(srcfile)
        cmdlist.append('-o')
        cmdlist.append(srcname+'.o')
        cmdlist.append('-J')
        cmdlist.append(  os.path.dirname(srcfile) )
        print 'check call: ', cmdlist
        subprocess.check_call(cmdlist)

        objfiles.append(srcname + '.o')

    #build executable
    cmd = fc + ' '
    cmdlist = []
    cmdlist.append(fc)
    for switch in fflags:
        cmd += switch + ' '
        cmdlist.append(switch)
    cmd += '-o' + ' ' + target + ' ' + '*.obj'
    cmdlist.append('-o')
    cmdlist.append(os.path.join('.',target))
    for objfile in objfiles:
        cmdlist.append(objfile)
    for switch in syslibs:
        cmdlist.append(switch)
    print 'check call: ', cmdlist
    subprocess.check_call(cmdlist)
    return


def main(inputdir, outputfile):
    """
    Create the binary executable(s)
    """
    print 'Input file is "', inputdir
    print 'Output file is "', outputfile

    # makeclean = True
    target = outputfile #mja

    #remove the target if it already exists
    try:
        os.remove(target)
    except:
        pass    
    
    #copy the original source to a pymake_tempdir_src directory
    # srcdir_origin = os.path.join('..', 'src')
    srcdir_origin = os.path.abspath(inputdir) # mja
    # deletes old, remove
    try:
        shutil.rmtree('pymake_tempdir_src')
    except:
        pass
    shutil.copytree(srcdir_origin, 'pymake_tempdir_src')
    srcdir_temp = os.path.abspath(os.path.join('pymake_tempdir_src'))
        
    #create a list of all c(pp), f and f90 source files
    templist = os.listdir(srcdir_temp)
    cfiles = [] 
    ffiles = []
    for f in templist:
        if f.endswith('.f') or f.endswith('.f90'):
            ffiles.append(os.path.join(srcdir_temp, f))
        elif f.endswith('.c') or f.endswith('.cpp'): 
            cfiles.append(os.path.join(srcdir_temp, f))

    #order the source files using the directed acyclic graph in dag.py
    orderedsourcefiles = order_source_files(ffiles) + order_c_source_files(cfiles) 

    platform = sys.platform
    if platform.lower() == 'darwin' or platform.lower() == 'linux2': 
        fc = 'gfortran'
        fflags = ['-O2', '-fopenmp', '-fPIC']
        objext = '.o'
        
        cc = 'gcc' 
        cflags = ['-D_UF', '-O3', '-fopenmp', '-fPIC'] 

        # NOTE: this is just for MODFLOW
        #need to change openspec.inc 
        fname = os.path.join(srcdir_temp, 'openspec.inc')
        f = open(fname, 'w')
        f.write(
'''c -- created by makebin.py   
      CHARACTER*20 ACCESS,FORM,ACTION(2)
      DATA ACCESS/'STREAM'/
      DATA FORM/'UNFORMATTED'/
      DATA (ACTION(I),I=1,2)/'READ','READWRITE'/
c -- end of include file
'''
        )
        f.close()

        try:
            compilenix(orderedsourcefiles, fc, fflags, cc, cflags, target) # mja
        except:
            print 'Error.  Could not build target...'
    else:
        print "ERROR: Windows not supported. See original file."

    #clean things up
    if False:
        print 'making clean...'
        filelist = os.listdir('.')
        delext = ['.mod', objext]
        for f in filelist:
            for ext in delext:
                if f.endswith(ext):
                    os.remove(f)
        shutil.rmtree(srcdir_temp)

    print 'Done...'
    return

if __name__ == "__main__":  
    # parse command line aruments
    # try:
    #   opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    # except getopt.GetoptError:
    #   print 'test.py -i <inputdir> -o <outputfile>'
    #   sys.exit(2)
    # for opt, arg in opts:
    #   if opt == '-h':
    #      print 'test.py -i <inputdir> -o <outputfile>'
    #      sys.exit()
    #   elif opt in ("-i", "--ifile"):
    #      inputdir = arg
    #   elif opt in ("-o", "--ofile"):
    #      outputfile = arg  
    
    # inputdir = '../original_libraries/Unix/src/'
    # outputfile = 'mf2005_pymade'

    # inputdir = '../src/'
    # outputfile = 'gac_pymade'

    inputdir = "../functional_modflow/"
    outputfile = "functional_mf2005"

    main(inputdir, outputfile)



    
