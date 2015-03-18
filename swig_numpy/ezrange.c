#include "ezrange.h"

void range(int *rangevec, int n)
{
    int i;

    for (i=0; i< n; i++)
        rangevec[i] = i;
}

#include <stdio.h>

void inplace(double *invec, int n)
{
    int i;

    for (i=0; i<n; i++)
    {
        invec[i] = 2*invec[i];
    }
}


