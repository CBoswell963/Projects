#include <stdio.h>
#include <stdlib.h>
int main(int argc, char *argv[]) {
  if(argc != 2) {
    printf("Usage: ./practice_policy <filename>\n");
    return 1;
  }
  FILE *fp = fopen(argv[1], "r");
  if(fp == NULL) {
    printf("Cannot access file %s\n", argv[1]);
    return 1;
  }
  int c = fgetc(fp);
  while(c != EOF) {
    printf("%c", c);
    c = fgetc(fp);
  }
  fclose(fp);
  printf("Press enter to continue\n");
  char string[2];
  fgets(string, 2, stdin);
  return 0;
}
