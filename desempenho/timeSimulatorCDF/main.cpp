/*
    Exponential Time Simulator

    This program defines a C++ class to simulate random times
    that follow an exponential distribution using the inverse 
    CDF method. The class is object-oriented and can generate 
    either a single random time or a vector of multiple times. 

    The exponential distribution is commonly used to model 
    waiting times or lifetimes, where the probability density 
    function is given by:

        f(x) = lambda * exp(-lambda * x),  x >= 0

    Its cumulative distribution function (CDF) is:

        F(x) = 1 - exp(-lambda * x)

    The inverse CDF method allows us to generate random samples
    by transforming a uniformly distributed random variable U
    in the interval (0,1) as:

        x = -ln(U) / lambda

    Usage:
        1. Enter the rate parameter lambda (positive real number)
        2. Enter the number of samples to generate
        3. The program outputs the generated exponential times
           to the console. You can redirect it to a file to plot
           histograms or analyze the data.
*/

#include <iostream>
#include <vector>
#include <random>
#include <cmath>

using namespace std;

// Class to generate exponential random times
class ExponentialGenerator {
private:
    double lambda;  // Rate parameter
    mt19937 rng;  // Mersenne Twister random number generator
    uniform_real_distribution<double> uniform_dist;  // Uniform [0,1)

public:
    // Constructor: initializes lambda and RNG
    ExponentialGenerator(double lambda_value)
        : lambda(lambda_value), rng(random_device{}()), uniform_dist(0.0, 1.0) {}

    /* 
        Generate a single exponential random time.
        Uses the inverse CDF method: x = -ln(U)/lambda,
        where U is a uniform random number between 0 and 1.
    */
    double generate() {
        double u = uniform_dist(rng);  // Generate U in (0,1)
        return -log(u) / lambda;       // Transform using inverse CDF
    }

    /*
        Generate 'n' exponential random times and return as a vector.
    */
    vector<double> generate(int n) {
        vector<double> samples;
        samples.reserve(n);
        for (int i = 0; i < n; ++i) {
            samples.push_back(generate());
        }
        return samples;
    }
};

int main() {
    double lambda;
    int n_samples;

    // Ask the user for the exponential rate parameter
    cout << "Enter lambda (rate parameter): ";
    cin >> lambda;

    // Ask the user how many random times to generate
    cout << "Enter number of samples: ";
    cin >> n_samples;

    // Create an exponential generator object
    ExponentialGenerator generator(lambda);

    // Generate the exponential times
    vector<double> times = generator.generate(n_samples);

    // Output the generated times to the console
    cout << "Generated exponential times:\n";
    for (double t : times) {
        cout << t << "\n";
    }

    return 0;
}
