#include <stdio.h>

extern void setup_(char* name, int name_l);


int main()
{
  int a;

  // printf("Enter an integer\n");
  // scanf("%d", &a);
  a = 4;
 
  printf("Integer that you have entered is %d\n", a);

  char * name = "tutorial2";
  setup_(name, strlen(name));

  return 0;
}



