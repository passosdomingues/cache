# Makefile for Queueing System Simulator
# Author: Rafael Passos Domingues
# Last Update: 2025 Sep 25 16h07

CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2 -g
TARGET = simulator
SOURCES = simulator.c
HEADERS = simulator.h

.PHONY: all clean compile run-batch run-interactive test valgrind-check install-deps help

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
	rm -rf results
	@echo "Clean completed."

# Run batch simulations
run-batch: compile
	@echo "Running batch simulations for 4 occupancy scenarios..."
	./$(TARGET) --batch

# Run interactive mode
run-interactive: compile
	@echo "Interactive mode not available in this version."
	@echo "Use: make run-batch"

# Quick test
test: compile
	@echo "Running quick test..."
	./$(TARGET) --batch

# Help message
help:
	@echo "Queueing System Simulator Build System"
	@echo "======================================"
	@echo "Targets:"
	@echo "  all           - Clean, compile and run batch simulations (default)"
	@echo "  clean         - Remove built files and results"
	@echo "  compile       - Compile the simulator only"
	@echo "  run-batch     - Compile and run 4 occupancy scenarios"
	@echo "  test          - Quick test with batch mode"
