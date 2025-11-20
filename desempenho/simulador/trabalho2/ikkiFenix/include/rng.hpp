#ifndef RNG_HPP
#define RNG_HPP

#include <cstdlib>
#include <cmath>

/**
 * @brief Random Number Generator with exact numeric semantics
 * 
 * Preserves the exact computation from original C code:
 * - Uniform random in (0,1] using rand()
 * - Exponential via inverse transform: -ln(u)/λ
 */
class RNG {
private:
    static bool seeded;

public:
    /**
     * @brief Set random seed (uses srand)
     * @param seed Random seed (default: 42)
     */
    static void setSeed(unsigned long seed = 42);
    
    /**
     * @brief Generate uniform random number in (0,1]
     * @return double Random number in range (0,1]
     */
    static double generateUniformRandom();
    
    /**
     * @brief Generate exponential random number
     * @param rateParameter λ - Rate parameter
     * @return double Exponentially distributed random variate
     */
    static double generateExponentialRandom(double rateParameter);
};

#endif // RNG_HPP