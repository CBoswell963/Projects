#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/wait.h> 
int main() {
  printf("Running as coordinator\n");
  printf("Attempting to get grades:\n");
  char *args[] = {"./my_cat", "data/grades.txt", NULL};
  if(fork() > 0) {
    wait(NULL);
    printf("Attempting to get users:\n");
    args[1] = "data/users.txt";
    if(fork() == 0) {
      execvp(args[0], args);
      return 0;
    }
  } else {
    execvp(args[0], args);
    return 0;
  }
}
