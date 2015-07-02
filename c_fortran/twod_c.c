#include <stdio.h>

extern void qref_( int[1][3][4], int*, int*, int*, int*);

extern void vecref_( int[], int * );

extern void cstring_(char[7], int[3]);

int main()
{
  int a;

  // printf("Enter an integer\n");
  // scanf("%d", &a);
  a = 4;
 
  printf("Integer that you have entered is %d\n", a);

  // 2D array

  // int m[20][10] = ... ;
  int m[1][3][4] = {{  
	 {0, 1, 2, 3} ,   /*  initializers for row indexed by 0 */
	 {4, 5, 6, 7} ,   /*  initializers for row indexed by 1 */
	 {8, 9, 10, 11}   /*  initializers for row indexed by 2 */
	}};
  int sum = 0;
  int X = 1;
  int Y = 3;
  int Z = 4;
  qref_( m, &sum , &X, &Y, &Z);

  printf("The sum is %d\n", sum);

  // 1D array

  int vsum;
  int v[9] = {1,2,3,4,5,0,0,0,0};
  vecref_( v, &vsum );
  printf("The vec sum is %d\n", vsum);

  // string - dodgy, remember c terminates with null character, CALL SUBRA ('A string'//CHAR(0))


  char s[7] = "short";
  int b[3] = {1,2,3};
  cstrng_( s, &b[1], 7L );

  return 0;
}



