/**
 * @file testharness.c
 * @brief Test harness for validating the simulator against Little's Law.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This program provides a test harness to systematically run the simulator
 * across multiple scenarios (policies, occupancies) and seeds. It reads the
 * final `littleError` from each simulation run's output CSV, calculates
 * aggregate statistics (mean, median, stddev), and asserts that the mean
 * absolute error is below a defined tolerance. This serves as a proof of
 * the simulator's numerical correctness.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <assert.h>
#include <sys/stat.h>

#define MAX_SEEDS 100
#define TOLERANCE 1e-3

// --- Helper Function Prototypes ---
double getLastLittleError(const char* filename);
int compareDoubles(const void* a, const void* b);
void runAndAnalyzeScenario(int policyId, double rho, const long seeds[], int numSeeds);

/**
 * @brief Main entry point for the test harness.
 */
int main() {
    mkdir("results", 0755);

    const long seeds[] = {101, 202, 303, 404, 505};
    const int numSeeds = sizeof(seeds) / sizeof(seeds[0]);
    const double rhos[] = {0.80, 0.90, 0.95, 0.999};
    const int numRhos = sizeof(rhos) / sizeof(rhos[0]);
    const int policies[] = {1, 2, 3};
    const int numPolicies = sizeof(policies) / sizeof(policies[0]);

    printf("Starting Test Harness...\n");
    printf("Tolerance for Mean Absolute Little's Error: %.5f\n\n", TOLERANCE);

    for (int p = 0; p < numPolicies; p++) {
        for (int r = 0; r < numRhos; r++) {
            runAndAnalyzeScenario(policies[p], rhos[r], seeds, numSeeds);
        }
    }

    printf("\nTest Harness finished. All scenarios passed.\n");
    return 0;
}

/**
 * @brief Runs a simulation for each seed in a scenario and analyzes the results.
 */
void runAndAnalyzeScenario(int policyId, double rho, const long seeds[], int numSeeds) {
    double errors[MAX_SEEDS];
    char command[512];
    char simFilename[256];
    char proofFilename[256];
    double sum = 0.0, sumSq = 0.0, sumAbs = 0.0;

    printf("--- Analyzing Scenario: Policy=%d, Rho=%.4f ---\n", policyId, rho);

    for (int i = 0; i < numSeeds; i++) {
        // Run the simulator
        sprintf(command, "./bin/simulator 1.0 1.0 1.0 %d %.4f %ld > /dev/null", policyId, rho, seeds[i]);
        system(command);

        // Read the result
        sprintf(simFilename, "results/sim_policy%d_rho%.4f_seed%ld.csv", policyId, rho, seeds[i]);
        errors[i] = getLastLittleError(simFilename);
        
        sum += errors[i];
        sumSq += errors[i] * errors[i];
        sumAbs += fabs(errors[i]);
    }

    // Calculate statistics
    double mean = sum / numSeeds;
    double meanAbs = sumAbs / numSeeds;
    double stddev = sqrt((sumSq / numSeeds) - (mean * mean));

    // Sort for median, min, max
    qsort(errors, numSeeds, sizeof(double), compareDoubles);
    double median = (numSeeds % 2 == 0) ? (errors[numSeeds/2 - 1] + errors[numSeeds/2]) / 2.0 : errors[numSeeds/2];
    double minErr = errors[0];
    double maxErr = errors[numSeeds - 1];

    // Write proof file
    sprintf(proofFilename, "results/proof_policy%d_rho%.4f.txt", policyId, rho);
    FILE* proofFile = fopen(proofFilename, "w");
    fprintf(proofFile, "Validation for Policy=%d, Rho=%.4f\n", policyId, rho);
    fprintf(proofFile, "-------------------------------------\n");
    fprintf(proofFile, "Seeds Run: %d\n", numSeeds);
    fprintf(proofFile, "Mean Little's Error:   %e\n", mean);
    fprintf(proofFile, "Median Little's Error: %e\n", median);
    fprintf(proofFile, "StdDev Little's Error: %e\n", stddev);
    fprintf(proofFile, "Min Little's Error:    %e\n", minErr);
    fprintf(proofFile, "Max Little's Error:    %e\n", maxErr);
    fprintf(proofFile, "Mean ABSOLUTE Error:   %e\n", meanAbs);
    fprintf(proofFile, "Tolerance:             %e\n", TOLERANCE);
    fprintf(proofFile, "Result:                %s\n", (meanAbs < TOLERANCE) ? "PASS" : "FAIL");
    fclose(proofFile);

    printf("  Mean Absolute Error: %e. Result: %s\n", meanAbs, (meanAbs < TOLERANCE) ? "PASS" : "FAIL");

    // Assert the condition
    assert(meanAbs < TOLERANCE);
}

/**
 * @brief Reads the very last value in the last column of a CSV file.
 */
double getLastLittleError(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Could not open file %s\n", filename);
        return NAN;
    }
    
    char line[1024];
    char lastLine[1024] = "";
    
    // Read to the end to get the last line
    while (fgets(line, sizeof(line), file)) {
        strcpy(lastLine, line);
    }
    fclose(file);

    if (strlen(lastLine) == 0) return NAN;

    // Find the last comma
    char* lastComma = strrchr(lastLine, ',');
    if (lastComma) {
        return atof(lastComma + 1);
    }
    
    return NAN;
}


/**
 * @brief Comparison function for qsort.
 */
int compareDoubles(const void* a, const void* b) {
    double da = *(const double*)a;
    double db = *(const double*)b;
    return (da > db) - (da < db);
}
