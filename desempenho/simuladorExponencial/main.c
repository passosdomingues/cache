#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

/*
 * Generates a random number in the interval (0,1]
 */
double generateRandom() {
    double u = rand() / ((double) RAND_MAX + 1.0);
    return 1.0 - u;
}

/*
 * Returns an exponentially distributed random variable
 * with rate lambda using inverse transform sampling.
 */
double exponential(double lambda) {
    return (-1.0 / lambda) * log(generateRandom());
}

/*
 * Returns the minimum of two double values.
 */
double min(double a, double b) {
    return (a < b) ? a : b;
}

/*
 * Main simulation function for a single-server queue.
 */
int main() {
    srand(time(NULL));  // Seed RNG

    // Simulation parameters
    double currentTime = 0.0;
    double simulationTime = 86400.0;  // 24 hours in seconds

    // Inputs from user
    double avgInterArrivalTime;
    double avgServiceTime;

    printf("Informe a media de tempo entre requisicoes (segundos): ");
    scanf("%lf", &avgInterArrivalTime);
    double lambdaArrival = 1.0 / avgInterArrivalTime;

    printf("Informe a media de tempo para atendimento (segundos): ");
    scanf("%lf", &avgServiceTime);
    double lambdaService = 1.0 / avgServiceTime;

    // Simulation state variables
    double nextArrivalTime = exponential(lambdaArrival);
    double nextDepartureTime = 0.0;

    unsigned long int queueLength = 0;
    unsigned long int maxQueueLength = 0;

    // Stats collection
    unsigned long int totalArrivals = 0;
    double sumInterArrivalTimes = 0.0;

    unsigned long int totalServices = 0;
    double sumServiceTimes = 0.0;

    // For average queue size calculation
    double lastEventTime = 0.0;
    double weightedQueueTime = 0.0;

    /*
     * Main event loop
     */
    while (currentTime < simulationTime) {
        // Determine next event time
        if (queueLength > 0) {
            currentTime = min(nextArrivalTime, nextDepartureTime);
        } else {
            currentTime = nextArrivalTime;
        }

        // Update time-weighted queue statistics
        double timeSinceLastEvent = currentTime - lastEventTime;
        weightedQueueTime += queueLength * timeSinceLastEvent;
        lastEventTime = currentTime;

        // ===== Arrival Event =====
        if (currentTime == nextArrivalTime) {
            totalArrivals++;
            queueLength++;
            if (queueLength > maxQueueLength) {
                maxQueueLength = queueLength;
            }

            // If queue was idle, start service immediately
            if (queueLength == 1) {
                double serviceDuration = exponential(lambdaService);
                nextDepartureTime = currentTime + serviceDuration;
                sumServiceTimes += serviceDuration;
                totalServices++;
            }

            // Schedule next arrival
            double interArrival = exponential(lambdaArrival);
            nextArrivalTime = currentTime + interArrival;
            sumInterArrivalTimes += interArrival;
        }
        // ===== Departure Event =====
        else {
            queueLength--;
            if (queueLength > 0) {
                double serviceDuration = exponential(lambdaService);
                nextDepartureTime = currentTime + serviceDuration;
                sumServiceTimes += serviceDuration;
                totalServices++;
            }
        }

        // Debug print for each step (optional)
        /*
        printf("Current time: %.2f\n", currentTime);
        printf("Queue length: %lu\n", queueLength);
        printf("-------------------------------------\n");
        getchar(); // Uncomment for step-by-step debugging
        */
    }

    /*
     * Final Metrics Output
     */
    printf("\n===== SIMULATION RESULTS =====\n");
    printf("Total simulation time: %.2f seconds\n", simulationTime);

    // Média entre requisições
    if (totalArrivals > 1) {
        double avgInterArrival = sumInterArrivalTimes / (totalArrivals - 1);
        printf("Media entre requisicoes: %.2f segundos\n", avgInterArrival);
    } else {
        printf("Not enough arrivals to compute media entre requisicoes.\n");
    }

    // Média dos tempos de serviço
    if (totalServices > 0) {
        double avgService = sumServiceTimes / totalServices;
        printf("Media dos tempos de servico: %.2f segundos\n", avgService);
    } else {
        printf("No services completed to compute media dos tempos de servico.\n");
    }

    // Tamanho máximo da fila
    printf("Tamanho maximo da fila: %lu\n", maxQueueLength);

    // Tamanho médio da fila
    double avgQueueSize = weightedQueueTime / simulationTime;
    printf("Tamanho medio da fila: %.2f\n", avgQueueSize);

    return 0;
}
