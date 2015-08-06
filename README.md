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
This initial investigation aims to replicate the simple model from Flopy's tutorial2 using only python wrapped Fortran routines. 

Having tried both SWIG and f2py (which wraps fortran in C first), ctypes (used extensively in Numpy) seems to be be the best way to interface python with c and fortran functions. You just describe the type of each function argument in python and there are no generated python/c wrappers. Fortran modules (in mf2005 but not mf2k) make life much more difficult, because you cannot simply wrap a function.

