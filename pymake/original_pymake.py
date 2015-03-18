#! /usr/bin/env python
"""
originally: Make the binary executable for MODFLOW-USG.
"""
__author__ = "Christian D. Langevin"
__date__ = "March 20, 2014"
__version__ = "1.0.0"
__maintainer__ = "Christian D. Langevin"
__email__ = "langevin@usgs.gov"
__status__ = "Production"

import os
import subprocess
import shutil
import sys
import getopt
from dag import order_source_files, order_c_source_files

def compilewin(srcfiles, fc, compileflags, target, makeclean, platform):
    """
    Make target on Windows OS
    """
    if 'ifort' in fc:
        cpvars = os.environ.get('IFORT_COMPILER13') + 'bin/compilervars.bat'
    f = open('compileusg.bat', 'w')
    line = 'call ' + '"' + os.path.normpath(cpvars) + '" ' + platform + '\n'
    f.write(line)

    #build object files
    for srcfile in srcfiles:
        cmd = fc + ' '
        for switch in compileflags:
            cmd += switch + ' '
        cmd += '-c' + ' '
        cmd += srcfile
        cmd += '\n'
        f.write(cmd)

    #build executable
    cmd = fc + ' '
    for switch in compileflags:
        cmd += switch + ' '
    cmd += '-o' + ' ' + target + ' ' + '*.obj' + '\n'
    f.write(cmd)
    f.close()

    #run the batch file
    subprocess.check_call(['compileusg.bat', ],)
    return

def compilemac(srcfiles, fc, compileflags, cc, cflags, target, makeclean): # mja 
    """
    Make target on Mac OS or Linux
    """
    syslibs = ['-lc']

    #build object files
    objfiles = []
    for srcfile in srcfiles:
        cmdlist = []
        if srcfile.endswith('.c') or srcfile.endswith('.cpp'):        #mja
            cmdlist.append(cc)      #mja
            for switch in cflags:       #mja
                cmdlist.append(switch)      #mja
        else:           #mja
            cmdlist.append(fc)
            for switch in compileflags:
                cmdlist.append(switch)
        cmdlist.append('-c')
        cmdlist.append(srcfile)
        print 'check call: ', cmdlist
        subprocess.check_call(cmdlist)
        srcname, srcext = os.path.splitext(srcfile)
        srcname = srcname.split(os.path.sep)[-1]
        objfiles.append(srcname + '.o')

    #build executable
    cmd = fc + ' '
    cmdlist = []
    cmdlist.append(fc)
    for switch in compileflags:
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

def main(argv):
    """
    Create the binary executable(s)
    """
    
    # parse command line aruments
    inputdir = '../src'
    outputfile = 'pymade'
    try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
      print 'test.py -i <inputdir> -o <outputfile>'
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputdir> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputdir = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
    print 'Input file is "', inputdir
    print 'Output file is "', outputfile

    makeclean = True
    target = outputfile #mja

    #remove the target if it already exists
    try:
        os.remove(target)
    except:
        pass    
    
    #copy the original source to a pymake_tempdir_src directory
    # srcdir_origin = os.path.join('..', 'src')
    srcdir_origin = os.path.abspath(inputdir) # mja
    try:
        shutil.rmtree('pymake_tempdir_src')
    except:
        pass
    shutil.copytree(srcdir_origin, 'pymake_tempdir_src')
    srcdir_temp = os.path.join('.', 'pymake_tempdir_src')
        
    #create a list of all c(pp), f and f90 source files
    templist = os.listdir(srcdir_temp)
    cfiles = [] # mja
    srcfiles = []
    for f in templist:
        if f.endswith('.f') or f.endswith('.f90'):
            srcfiles.append(f)
        elif f.endswith('.c') or f.endswith('.cpp'): #mja
            cfiles.append(f)    #mja


    srcfileswithpath = []
    for srcfile in srcfiles:
        s = os.path.join(srcdir_temp, srcfile)
        srcfileswithpath.append(s)


    cfileswithpath = [] #mja
    for srcfile in cfiles:  #mja
        s = os.path.join(srcdir_temp, srcfile)  #mja
        cfileswithpath.append(s)        #mja

    #order the source files using the directed acyclic graph in dag.py
    orderedsourcefiles = order_source_files(srcfileswithpath) + order_c_source_files(cfileswithpath) #mja

    platform = sys.platform
    if platform.lower() == 'darwin' or platform.lower() == 'linux2': #mja
        fc = 'gfortran'
        compileflags = ['-O2', '-fopenmp', 'fPIC']
        objext = '.o'
        
        cc = 'gcc' #mja
        cflags = ['-D_UF', '-O3', '-fopenmp', 'fPIC'] #mja

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
            compilemac(orderedsourcefiles, fc, compileflags, cc, cflags, target, makeclean) # mja
        except:
            print 'Error.  Could not build target...'
       
    else:
        fc = 'ifort.exe'
        #production version compile flags
        compileflags = [
                       '-O2',
                       '-heap-arrays:0',
                       '-fpe:0',
                       '-traceback',
                       ]
        objext = '.obj'
        
        #create a 32-bit executable
        try:
            compilewin(orderedsourcefiles, fc, compileflags, target, makeclean,
                  'ia32')
        except:
            print 'Error.  Could not build 32-bit target...'

        #create a 64-bit executable
        try:
            compilewin(orderedsourcefiles, fc, compileflags, target+'_x64', 
                  makeclean, 'intel64')
        except:
            print 'Error.  Could not build 64-bit target...'
                  
    #clean things up
    if makeclean:
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
    main(sys.argv[1:])



    
