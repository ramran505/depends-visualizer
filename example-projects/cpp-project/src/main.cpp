#include "logger.h"
#include "math_utils.h"
#include "advanced_math.h"

int main() {
    Logger::log("Starting the app...");

    int a = 10, b = 20;
    int sum = add(a, b);
    Logger::log("Sum: " + std::to_string(sum));

    int factorial = AdvancedMath::factorial(5);
    Logger::log("Factorial: " + std::to_string(factorial));

    return 0;
}
