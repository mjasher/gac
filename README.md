Groundwater Analysis Code
===========================

This package aims to semi translate [MODFLOW](http://water.usgs.gov/ogw/modflow/MODFLOW.html#downloads) into Python. The intention is for the computationally expensive routines (the solvers) to remain in Fortran but to use Python for the finicky construction of the discretized flow equation matrices from the various forms of input data.
While [FloPy](https://github.com/modflowpy/flopy) writes input files for MODFLOW using python. GAC aims to get rid of text input files all together.
Rather than 
```
data -> python (flopy) -> text inputs -> Fortran read (AR subroutines) -> discretized equations -> Fortran solve
```
we want something along the lines of
```
data -> python (GAC) -> discretized equations -> Fortran solve
```
This initial investigation aims to replicate the simple model from tutorial2 using only python wrapped Fortran routines. 

Simmply wrapping each module with f2py doesn't seem to work. For example try
```
f2py -c -m gwf2bas7 gwf2bas7.f
```

f2py wraps Fortran in c first, so the best approach seems to be to section mf2005.f into a number of Fortran subroutines, wrap those in c functions, then wrap those c functions in python using swig.

Fortran and c are okay together, see
http://docs.oracle.com/cd/E19957-01/806-3593/11_cfort.html
http://alignment.hep.brandeis.edu/Software/Mixing/Mixing_Manual.html

SWIG wraps c fine, see
http://wiki.scipy.org/Cookbook/SWIG_NumPy_examples

Method
------------------
1. cut main program in mf2005.f into a bunch of subroutines
2. wrap these subroutines in c functions
    * change "allocate and read" (AR) subroutines to take input straight from python rather than reading text file inputs
    * change "output" (OT) subroutines to return data to python rather than writing text/binary files
3. wrap these c functions in python
4. bingo


Building blocks
------------------

### SWIG, numpy and c
swig_numpy

### c and Fortran
c_fortran

### "complex" compiling
pymake

Dependencies
------------------

### [MODFLOW](http://water.usgs.gov/ogw/modflow/MODFLOW.html#downloads).

In Unix/src/makefile 
```
# mja F90FLAGS=
F90FLAGS= -fopenmp
# mja F90= f90
F90= gfortran
```

In Unix/src/openspec.inc
```
      DATA FORM/'UNFORMATTED'/
C mja    DATA FORM/'BINARY'/
```

### [FloPy3](https://github.com/modflowpy/flopy)

Copy flopy-master/examples/Tutorial02/tutorial02.py and edit to flopy_tutorial_2.py

Details
--------------------

run flopy_tutorial_2.py

run pymake 
    inputdir = '../original_libraries/Unix/src/'
    outputfile = 'mf2005_pymade'

    # inputdir = '../src/'
    # outputfile = 'gac_pymade'

edit src/mf2005.f
to  SUBROUTINE SETUP(FNAMEC)
pymake should then find main_c.c executes

./../pymake/gac_pymade
# from flopy_tutorial_2 import plot
# plot()


GWF2BAS7AR and SGWF2BAS7ARDIS

      FORTRAN: NCOL, NROW, NLAY
      C: NLAY, NROW, NCOL


It turns out ctypes can be a lot simpler than swig. You just do the "interface file" in python and there is no generated python/c wrappers. 

An issue is that mf2005 calls USTOP with calls fortran STOP, this prevents return to python, but removing it messses up some data. 
TODO???!!! is it okay to put STOP in another function? what does it do exactly?
Easy: just launch new process using multiprocessing


STRUCTURE
Figure 3–1. Flowchart of program to simulate ground-water flow.