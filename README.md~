Flopy writes input files for MODFLOW using python. JacqFlow gets rid of text input files all together.
This inititial investigation aims to replicate the simple model from tutorial2 using only python and f2py wrapped Fortran routines. 

Simmply wrapping each module with f2py doesn't seem to work. For example try
```
f2py -c -m gwf2bas7 gwf2bas7.f
```

f2py wraps fortran in c first, so the best approach seems to be to section mf2005.f into a number of fortran subroutines, wrap those in c functions, then wrap those c functions in python using swig.

Fortran and c are okay together, see
http://docs.oracle.com/cd/E19957-01/806-3593/11_cfort.html
http://alignment.hep.brandeis.edu/Software/Mixing/Mixing_Manual.html

SWIG wraps c fine, see
http://wiki.scipy.org/Cookbook/SWIG_NumPy_examples

## Method
------------------
1. cut main program in mf2005.f into a bunch of subroutines
2. wrap these subroutines in c functions
    * change "allocate and read" (AR) subroutines to take input straight from python rather than reading text file inputs
    * change "output" (OT) subroutines to return data to python rather than writing text/binary files
3. wrap these c functions in python
4. bingo

Rather than 
data -> python (flopy) -> text inputs -> fortran read (AR subroutines) -> discretized equations -> fortran solve

data -> python (jacqflow) -> discretized equations -> fortran solve





## Building blocks
------------------

### SWIG, numpy and c
swig_numpy

### c and Fortran
c_fortran

### "complex" compiling
pymake

## Dependencies
------------------

### Download (MODFLOW)[http://water.usgs.gov/ogw/modflow/MODFLOW.html#downloads].

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

### Download (FloPy3)[https://github.com/modflowpy/flopy]

Copy flopy-master/examples/Tutorial02/tutorial02.py and edit to flopy_tutorial_2.py



