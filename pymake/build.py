import subprocess

subprocess.call(['gfortran', '-O2', '-fopenmp', '-fPIC', '-c', './pymake_tempdir_src/mf2005.f'])