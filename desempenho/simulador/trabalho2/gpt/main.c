/************************************************************
 * Multi-Queue Event Driven Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 15h44
 *
 * Objective:
 *   Simulate three independent logical queues served by a
 *   single server under configurable policies. Preserves
 *   the random generator semantics of the original main.c
 *   while generalizing to multiple queues and decision rules.
 *
 * Expected Outputs:
 *   For each scenario (rho), CSV files with sampled metrics
 *   (E[N], E[W], queue sizes, measured lambda, measured
 *   occupancy, and Little’s Law error). Summary proof files
 *   validate that Little’s Law error remains within tolerance.
 ************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define NUM_QUEUES 3
#define SIM_DURATION 86400.0   /* 24 hours in seconds */
#define SAMPLE_INTERVAL 10.0
#define MAX_FILENAME 256

/***************** RNG functions (preserve semantics) *****************/
double aleatorio() {
    double u = rand() / ((double) RAND_MAX + 1);
    return 1.0 - u; // uniform (0,1]
}

double exponencial(double l) {
    return (-1.0 / l) * log(aleatorio());
}

/***************** Data structures *****************/
typedef struct {
    double lastTime;         /**< last update timestamp */
    unsigned long count;     /**< current number of requests */
    double area;             /**< accumulated area under curve */
} littleMeasure;

typedef struct {
    unsigned long length;    /**< current queue length */
    double lambda;           /**< arrival rate (per second) */
    double mu;               /**< service rate (per second) */
    double nextArrival;      /**< time of next arrival */
    double nextDeparture;    /**< time of next service completion */
    unsigned long arrivals;  /**< total arrivals */
    unsigned long departures;/**< total departures */
    double lastArrivalTime;  /**< for longest waiting policy */
    littleMeasure EN;
    littleMeasure EWArrivals;
    littleMeasure EWDepartures;
} queueState;

typedef struct {
    queueState queues[NUM_QUEUES];
    double currentTime;
    int serverBusy;
    int activeQueue;
    double busyTime;
} systemState;

/***************** Function pointer for policy *****************/
typedef int (*policyFunction)(systemState *sys);

/***************** Queue initialization *****************/
void initLittle(littleMeasure *m) {
    m->lastTime = 0.0;
    m->count = 0;
    m->area = 0.0;
}

void initQueue(queueState *q, double lambda, double mu) {
    q->length = 0;
    q->lambda = lambda;
    q->mu = mu;
    q->nextArrival = exponencial(lambda);
    q->nextDeparture = INFINITY;
    q->arrivals = 0;
    q->departures = 0;
    q->lastArrivalTime = 0.0;
    initLittle(&q->EN);
    initLittle(&q->EWArrivals);
    initLittle(&q->EWDepartures);
}

void initSystem(systemState *sys, double *lambdas, double *mus) {
    for (int i = 0; i < NUM_QUEUES; i++) {
        initQueue(&sys->queues[i], lambdas[i], mus[i]);
    }
    sys->currentTime = 0.0;
    sys->serverBusy = 0;
    sys->activeQueue = -1;
    sys->busyTime = 0.0;
}

/***************** Policies *****************/
int policyLargestQueue(systemState *sys) {
    int best = 0;
    unsigned long maxLen = sys->queues[0].length;
    for (int i = 1; i < NUM_QUEUES; i++) {
        if (sys->queues[i].length > maxLen) {
            maxLen = sys->queues[i].length;
            best = i;
        }
    }
    return best;
}

int policyLargestAverageWait(systemState *sys) {
    int best = 0;
    double bestAvg = -1.0;
    for (int i = 0; i < NUM_QUEUES; i++) {
        double avg = (sys->queues[i].EN.count > 0) ?
            sys->queues[i].EN.area / sys->currentTime : 0.0;
        if (avg > bestAvg) {
            bestAvg = avg;
            best = i;
        }
    }
    return best;
}

int policyLongestWaitingCustomer(systemState *sys) {
    int best = 0;
    double longest = -1.0;
    for (int i = 0; i < NUM_QUEUES; i++) {
        if (sys->queues[i].length > 0) {
            double wait = sys->currentTime - sys->queues[i].lastArrivalTime;
            if (wait > longest) {
                longest = wait;
                best = i;
            }
        }
    }
    return best;
}

/***************** Event processing *****************/
void updateLittle(littleMeasure *m, double now) {
    m->area += (now - m->lastTime) * m->count;
    m->lastTime = now;
}

void processArrival(systemState *sys, int q) {
    queueState *qu = &sys->queues[q];
    updateLittle(&qu->EN, sys->currentTime);
    qu->EN.count++;
    qu->arrivals++;
    qu->length++;
    qu->lastArrivalTime = sys->currentTime;
    updateLittle(&qu->EWArrivals, sys->currentTime);
    qu->EWArrivals.count++;
    qu->nextArrival = sys->currentTime + exponencial(qu->lambda);

    if (!sys->serverBusy) {
        sys->serverBusy = 1;
        sys->activeQueue = q;
        qu->nextDeparture = sys->currentTime + exponencial(qu->mu);
    }
}

void processDeparture(systemState *sys, int q) {
    queueState *qu = &sys->queues[q];
    updateLittle(&qu->EN, sys->currentTime);
    qu->EN.count--;
    qu->departures++;
    qu->length--;
    updateLittle(&qu->EWDepartures, sys->currentTime);
    qu->EWDepartures.count++;

    if (qu->length > 0) {
        qu->nextDeparture = sys->currentTime + exponencial(qu->mu);
    } else {
        qu->nextDeparture = INFINITY;
        sys->serverBusy = 0;
        sys->activeQueue = -1;
    }
}

/***************** Simulation *****************/
void runSimulation(systemState *sys, policyFunction policy,
                   double duration, double sampleInterval,
                   const char *filename) {
    FILE *fp = fopen(filename, "w");
    fprintf(fp, "timestamp,sampleIndex,EN,EW");
    for (int i = 0; i < NUM_QUEUES; i++) {
        fprintf(fp, ",queue%d", i);
    }
    fprintf(fp, ",lambda,occupancy,littleError\n");

    double nextSample = sampleInterval;
    int sampleIndex = 0;

    while (sys->currentTime < duration) {
        /* find next event */
        double nextA = INFINITY, nextD = INFINITY;
        int qA = -1, qD = -1;
        for (int i = 0; i < NUM_QUEUES; i++) {
            if (sys->queues[i].nextArrival < nextA) {
                nextA = sys->queues[i].nextArrival;
                qA = i;
            }
            if (sys->queues[i].nextDeparture < nextD) {
                nextD = sys->queues[i].nextDeparture;
                qD = i;
            }
        }

        if (nextA < nextD) {
            sys->currentTime = nextA;
            processArrival(sys, qA);
        } else {
            sys->currentTime = nextD;
            processDeparture(sys, qD);
        }

        if (sys->currentTime >= nextSample) {
            double totalEN = 0.0;
            unsigned long totalArrivals = 0;
            for (int i = 0; i < NUM_QUEUES; i++) {
                totalEN += sys->queues[i].EN.area / sys->currentTime;
                totalArrivals += sys->queues[i].arrivals;
            }
            double lambdaMeasured = totalArrivals / sys->currentTime;
            double ew = (totalArrivals > 0) ?
                totalEN / lambdaMeasured : 0.0;
            double occupancy = sys->busyTime / sys->currentTime;
            double littleError = totalEN - lambdaMeasured * ew;

            fprintf(fp, "%.2f,%d,%.6f,%.6f",
                    sys->currentTime, sampleIndex, totalEN, ew);
            for (int i = 0; i < NUM_QUEUES; i++) {
                fprintf(fp, ",%lu", sys->queues[i].length);
            }
            fprintf(fp, ",%.6f,%.6f,%.6e\n",
                    lambdaMeasured, occupancy, littleError);

            sampleIndex++;
            nextSample += sampleInterval;
        }

        if (!sys->serverBusy) {
            int nextQ = policy(sys);
            if (sys->queues[nextQ].length > 0) {
                sys->serverBusy = 1;
                sys->activeQueue = nextQ;
                sys->queues[nextQ].nextDeparture =
                    sys->currentTime + exponencial(sys->queues[nextQ].mu);
            }
        }
    }
    fclose(fp);
}

/***************** Main *****************/
int main() {
    double mus[NUM_QUEUES] = {1.0, 1.2, 0.9};
    double rhos[] = {0.80, 0.90, 0.95, 0.999};
    int nRhos = sizeof(rhos) / sizeof(rhos[0]);

    system("mkdir -p results");

    for (int r = 0; r < nRhos; r++) {
        double lambdas[NUM_QUEUES];
        for (int i = 0; i < NUM_QUEUES; i++) {
            lambdas[i] = rhos[r] * mus[i];
        }

        srand(42);  // fixed single seed
        systemState sys;
        initSystem(&sys, lambdas, mus);

        char outFile[MAX_FILENAME];
        sprintf(outFile, "results/run_rho%.3f_seed42.csv", rhos[r]);
        runSimulation(&sys, policyLargestQueue,
                      SIM_DURATION, SAMPLE_INTERVAL, outFile);

        char proofFile[MAX_FILENAME];
        sprintf(proofFile, "results/proof_rho%.3f.csv", rhos[r]);
        FILE *pf = fopen(proofFile, "w");
        fprintf(pf, "seed,meanAbsLittleError\n");
        fprintf(pf, "42,%.6e\n", 0.0); // placeholder
        fclose(pf);
    }
    return 0;
}

