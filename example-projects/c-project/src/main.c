#include <stdio.h>
#include "math_utils.h"
#include "logger.h"

int main() {
    int a = 10, b = 5;
    log_info("Starting calculation...");
    printf("Sum: %d\n", add(a, b));
    printf("Difference: %d\n", subtract(a, b));
    log_info("Calculation finished.");
    return 0;
}
