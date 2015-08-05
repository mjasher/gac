#! /usr/bin/env python

# System imports
from distutils.core import *
from distutils      import sysconfig

# Third-party modules - we depend on numpy for everything
import numpy

# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

# range extension module
mod_ezrange = Extension("_ezrange",
                  # "ezrange.i",
                #   ["ezrange_wrap.c","ezrange.c"],
                  ["ezrange.i","ezrange.c"],
                   include_dirs = [numpy_include],
                   extra_compile_args = ['-fopenmp','-fpic'],
                   extra_link_args = ['-lgomp']
                   )

# NumyTypemapTests setup
setup(  name        = "range function",
        description = "range takes an integer and returns an n element int array where each element is equal to its index",
        author      = "Egor Zindy",
        version     = "1.0",
        ext_modules = [mod_ezrange]
        )

