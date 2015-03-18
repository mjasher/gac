%module ezrange

%{
    #define SWIG_FILE_WITH_INIT
    #include "ezrange.h"
%}

%include "numpy.i"

%init %{
    import_array();
%}

%apply (int* ARGOUT_ARRAY1, int DIM1) {(int* rangevec, int n)}

%apply (double* INPLACE_ARRAY1, int DIM1) {(double* invec, int n)}

%include "ezrange.h"


