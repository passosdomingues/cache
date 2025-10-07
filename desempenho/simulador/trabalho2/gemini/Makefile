#
# Project: M/M/1 Multi-Queue Simulator
# Author: Rafael Passos Domingues
# Last Update: 2025 Sep 25 14h36
#
# Purpose:
# This Makefile builds the event-driven C simulator and its corresponding
# test harness. It compiles all source files and links them into two
# executables: 'simulator' and 'testharness'.
#

# Compiler and flags
CC = gcc
CFLAGS = -Wall -Wextra -Iinclude -g -O2 -lm
LDFLAGS = -lm

# Directories
SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin
INCLUDE_DIR = include
RESULTS_DIR = results

# Source files
SIM_SOURCES = $(SRC_DIR)/main.c $(SRC_DIR)/simulator.c $(SRC_DIR)/queue.c $(SRC_DIR)/policies.c $(SRC_DIR)/rng.c
TEST_SOURCES = $(SRC_DIR)/testharness.c $(SRC_DIR)/simulator.c $(SRC_DIR)/queue.c $(SRC_DIR)/policies.c $(SRC_DIR)/rng.c

# Object files
SIM_OBJS = $(patsubst $(SRC_DIR)/%.c,$(OBJ_DIR)/%.o,$(SIM_SOURCES))
TEST_OBJS = $(patsubst $(SRC_DIR)/%.c,$(OBJ_DIR)/%.o,$(TEST_SOURCES))

# Executables
SIM_TARGET = $(BIN_DIR)/simulator
TEST_TARGET = $(BIN_DIR)/testharness

# Default target
all: $(SIM_TARGET) $(TEST_TARGET)

# Rule to build the simulator
$(SIM_TARGET): $(SIM_OBJS)
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "Simulator executable created at $@"

# Rule to build the test harness
$(TEST_TARGET): $(TEST_OBJS)
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)
	@echo "Test harness executable created at $@"

# Rule to compile source files into object files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(@D)
	$(CC) $(CFLAGS) -c $< -o $@

# Create results directory
dirs:
	@mkdir -p $(RESULTS_DIR)

# Clean up build artifacts
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf $(OBJ_DIR) $(BIN_DIR)

.PHONY: all clean dirs
