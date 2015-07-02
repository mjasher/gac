#include <stdio.h>

// extern void setup_(char* name, int name_l, float* GACHNOFLO, int* GACIBOUND, float* GACSTRT);
extern void setup_(char* , float* , int[1][10][10] , float[1][10][10], int);


int main()
{

  char * name = "../tutorial2/tutorial2";

  float GACHNOFLO = 0.0;
  // int NLAY = 1;
  // int NROW = 10;
  // int NCOL = 10;

  int GACIBOUND[1][10][10] = {{ 
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1},
  	{1, 1, 1, 1, 1, 1, 1, 1, 1, 1}
	}};

  float GACSTRT[1][10][10] = {{ 
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0},
  	{10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0}
	}};

  setup_(name, &GACHNOFLO, GACIBOUND, GACSTRT, strlen(name));
  // setup_(name, strlen(name));

  return 0;
}



