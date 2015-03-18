#include <stdio.h>

extern void setup_();


int main()
{
  int a;

  // printf("Enter an integer\n");
  // scanf("%d", &a);
  a = 4;
 
  printf("Integer that you have entered is %d\n", a);

  setup_();

  return 0;
}



