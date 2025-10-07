#!/bin/bash
SEEDS=(123 456 789)
RHOS=(0.80 0.90 0.95 0.999)
POLICIES=(1 2 3)
MU=1.0

mkdir -p results

for policy in "${POLICIES[@]}"; do
  for rho in "${RHOS[@]}"; do
    for seed in "${SEEDS[@]}"; do
      echo "Running: Policy=$policy, Rho=$rho, Seed=$seed"
      ./bin/simulator $MU $MU $MU $policy $rho $seed
    done
  done
done
