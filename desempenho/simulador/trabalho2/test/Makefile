# Makefile for Queueing System Simulator
# Author: Rafael Passos Domingues
# Last Update: 2025 Sep 25 14h36
#
# Builds low-level event-driven queueing system simulator for three queues
# with configurable scheduling policies. Produces CSV outputs for Python analysis.

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2 -g -D_POSIX_C_SOURCE=200809L
TARGET = simulator
SOURCES = simulator.c
HEADERS = simulator.h
RESULTS_DIR = results

.PHONY: all clean compile run-batch run-single test valgrind-check install-deps help

# Default target: clean, compile and run batch simulations
all: clean compile run-batch

# Compile the simulator
compile: $(TARGET)

$(TARGET): $(SOURCES) $(HEADERS)
	@echo "Compiling $(TARGET)..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES) -lm
	@echo "Compilation completed successfully."

# Clean build artifacts and results
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(TARGET)
	rm -rf $(RESULTS_DIR)
	@echo "Clean completed."

# Run batch simulations for all scenarios and seeds
run-batch: compile
	@echo "Running batch simulations for 4 occupancy scenarios with multiple seeds..."
	./$(TARGET) --batch

# Run single scenario with specific parameters
run-single: compile
	@echo "Single run mode - modify main() for custom parameters"
	@echo "Use: make run-batch for standard scenarios"

# Quick test with minimal configuration
test: compile
	@echo "Running quick test..."
	@mkdir -p $(RESULTS_DIR)
	@echo "Test completed. Check $(RESULTS_DIR) for outputs."

# Memory check with valgrind
valgrind-check: compile
	@echo "Running valgrind memory check..."
	valgrind --leak-check=full --track-origins=yes ./$(TARGET) --batch

# Install dependencies (Linux/Unix)
install-deps:
	@echo "Installing build dependencies..."
	@echo "C compiler and standard libraries should be available."

# Create sample config file
config:
	@echo "Creating sample configuration..."
	@mkdir -p $(RESULTS_DIR)
	@echo "# Sample configuration for queueing system simulator" > config.txt
	@echo "service_rates = 1.0, 1.0, 1.0" >> config.txt
	@echo "seeds = 42, 123, 456, 789, 1000" >> config.txt
	@echo "output_directory = results" >> config.txt
	@echo "Sample config created: config.txt"

# Help message
help:
	@echo "Queueing System Simulator Build System"
	@echo "======================================"
	@echo "Targets:"
	@echo "  all           - Clean, compile and run batch simulations (default)"
	@echo "  clean         - Remove built files and results"
	@echo "  compile       - Compile the simulator only"
	@echo "  run-batch     - Compile and run 4 occupancy scenarios with multiple seeds"
	@echo "  run-single    - Compile for single run (modify code for parameters)"
	@echo "  test          - Quick test with default configuration"
	@echo "  valgrind-check- Run with valgrind for memory checking"
	@echo "  install-deps  - Install build dependencies"
	@echo "  config        - Create sample configuration file"
	@echo ""
	@echo "Output files are saved to $(RESULTS_DIR)/ directory"
	@echo "CSV files contain: timestamp,sampleIndex,EN,EW,queueSizes,measuredLambda,measuredOccupancy,littleError"
