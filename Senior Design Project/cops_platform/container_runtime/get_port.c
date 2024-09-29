#include <stdio.h>
#include <string.h>
#define PREFIX "\"url\":\"http://127.0.0.1:"
/**
 * Prints the port from a JSON response to a curl command to avoid funky bash substring nonsense
 * @author Spencer Yoder
 */
int main() {
  char buffer[100];
  fgets(buffer, 100, stdin);
  char *port = strstr(buffer, PREFIX);
  if(port == NULL) {
    printf("-1");
    return 1;
  }
  port += strlen(PREFIX);
  port[strlen(port) - 3] = '\0';
  printf("%s", port);
  return 0;
}
