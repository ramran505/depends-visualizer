#include "advanced_math.h"

namespace AdvancedMath {
    int factorial(int n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
}
