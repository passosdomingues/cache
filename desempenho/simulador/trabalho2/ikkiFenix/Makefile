# =============================================================================
# Advanced Queueing System Simulator - Optimized Build System
# =============================================================================

# Compiler and flags
CXX := g++
CXX_STD := c++17

# Optimization levels
RELEASE_FLAGS := -O3 -march=native -flto -DNDEBUG
DEBUG_FLAGS := -O0 -g3 -DDEBUG -fsanitize=address -fsanitize=undefined
PROFILE_FLAGS := -O2 -g -pg -fno-omit-frame-pointer

# Warning flags
WARN_FLAGS := -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wdouble-promotion \
              -Wformat=2 -Wnull-dereference -Wlogical-op -Wduplicated-cond \
              -Wduplicated-branches -Wrestrict

# Standard flags
STD_FLAGS := -std=$(CXX_STD) -pthread
INCLUDE_FLAGS := -Iinclude -I.

# Linker flags
LDFLAGS_RELEASE := -flto -s -static-libgcc -static-libstdc++
LDFLAGS_DEBUG := -fsanitize=address -fsanitize=undefined
LDFLAGS_PROFILE := -pg

# Directories
SRC_DIR := src
BUILD_DIR := build
BIN_DIR := out/bin
TEST_DIR := tests
CONFIG_DIR := config
RESULTS_DIR := results
ANALYSIS_DIR := analysis

# Source files
MAIN_SRC := $(SRC_DIR)/main.cpp
SIMULATOR_SRC := $(SRC_DIR)/simulator.cpp
RNG_SRC := $(SRC_DIR)/rng.cpp
QUEUE_SRC := $(SRC_DIR)/queue.cpp
MEASUREMENT_WINDOW_SRC := $(SRC_DIR)/measurement_window.cpp
LITTLES_LAW_SRC := $(SRC_DIR)/littles_law.cpp
POLICIES_SRC := $(SRC_DIR)/policies.cpp
EVENTS_SRC := $(SRC_DIR)/events.cpp
CONFIG_SRC := $(SRC_DIR)/config.cpp
CSV_WRITER_SRC := $(SRC_DIR)/csv_writer.cpp
BATCH_HARNESS_SRC := $(SRC_DIR)/batch_harness.cpp

# Test source files
TEST_SRCS := $(wildcard $(TEST_DIR)/*.cpp)

# Object files (release)
RELEASE_OBJ_DIR := $(BUILD_DIR)/release/obj
RELEASE_OBJS := $(patsubst $(SRC_DIR)/%.cpp,$(RELEASE_OBJ_DIR)/%.o,$(wildcard $(SRC_DIR)/*.cpp))

# Object files (debug)
DEBUG_OBJ_DIR := $(BUILD_DIR)/debug/obj
DEBUG_OBJS := $(patsubst $(SRC_DIR)/%.cpp,$(DEBUG_OBJ_DIR)/%.o,$(wildcard $(SRC_DIR)/*.cpp))

# Object files (profile)
PROFILE_OBJ_DIR := $(BUILD_DIR)/profile/obj
PROFILE_OBJS := $(patsubst $(SRC_DIR)/%.cpp,$(PROFILE_OBJ_DIR)/%.o,$(wildcard $(SRC_DIR)/*.cpp))

# Test object files
TEST_OBJ_DIR := $(BUILD_DIR)/test/obj
TEST_OBJS := $(patsubst $(TEST_DIR)/%.cpp,$(TEST_OBJ_DIR)/%.o,$(TEST_SRCS))

# Executables
SIMULATOR_RELEASE := $(BIN_DIR)/simulator
SIMULATOR_DEBUG := $(BIN_DIR)/simulator_debug
SIMULATOR_PROFILE := $(BIN_DIR)/simulator_profile
TEST_EXECUTABLE := $(BIN_DIR)/test_simulator

# Default build type
BUILD_TYPE ?= release

# =============================================================================
# Build Rules
# =============================================================================

# Default target
.PHONY: all
all: release

# Release build
.PHONY: release
release: CXXFLAGS := $(STD_FLAGS) $(RELEASE_FLAGS) $(WARN_FLAGS) $(INCLUDE_FLAGS)
release: LDFLAGS := $(LDFLAGS_RELEASE)
release: $(SIMULATOR_RELEASE)

# Debug build
.PHONY: debug
debug: CXXFLAGS := $(STD_FLAGS) $(DEBUG_FLAGS) $(WARN_FLAGS) $(INCLUDE_FLAGS)
debug: LDFLAGS := $(LDFLAGS_DEBUG)
debug: $(SIMULATOR_DEBUG)

# Profile build
.PHONY: profile
profile: CXXFLAGS := $(STD_FLAGS) $(PROFILE_FLAGS) $(WARN_FLAGS) $(INCLUDE_FLAGS)
profile: LDFLAGS := $(LDFLAGS_PROFILE)
profile: $(SIMULATOR_PROFILE)

# Main simulator executable (release)
$(SIMULATOR_RELEASE): $(RELEASE_OBJS) | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $(RELEASE_OBJS) $(LDFLAGS)
	@echo "Release build complete: $@"
	@echo "Executable size:" $(shell du -h $@ | cut -f1)

# Debug simulator executable
$(SIMULATOR_DEBUG): $(DEBUG_OBJS) | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $(DEBUG_OBJS) $(LDFLAGS)
	@echo "Debug build complete: $@"

# Profile simulator executable
$(SIMULATOR_PROFILE): $(PROFILE_OBJS) | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $(PROFILE_OBJS) $(LDFLAGS)
	@echo "Profile build complete: $@"

# Test executable
.PHONY: test
test: CXXFLAGS := $(STD_FLAGS) $(DEBUG_FLAGS) $(WARN_FLAGS) $(INCLUDE_FLAGS)
test: LDFLAGS := $(LDFLAGS_DEBUG)
test: $(TEST_EXECUTABLE)

$(TEST_EXECUTABLE): $(DEBUG_OBJS) $(TEST_OBJS) | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) -o $@ $(DEBUG_OBJS) $(TEST_OBJS) $(LDFLAGS)
	@echo "Test build complete: $@"

# =============================================================================
# Object File Rules
# =============================================================================

# Release object files
$(RELEASE_OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(RELEASE_OBJ_DIR)
	@$(CXX) $(CXXFLAGS) -c $< -o $@

# Debug object files
$(DEBUG_OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(DEBUG_OBJ_DIR)
	@$(CXX) $(CXXFLAGS) -c $< -o $@

# Profile object files
$(PROFILE_OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(PROFILE_OBJ_DIR)
	@$(CXX) $(CXXFLAGS) -c $< -o $@

# Test object files
$(TEST_OBJ_DIR)/%.o: $(TEST_DIR)/%.cpp | $(TEST_OBJ_DIR)
	@$(CXX) $(CXXFLAGS) -c $< -o $@

# =============================================================================
# Directory Creation
# =============================================================================

$(RELEASE_OBJ_DIR):
	@mkdir -p $@

$(DEBUG_OBJ_DIR):
	@mkdir -p $@

$(PROFILE_OBJ_DIR):
	@mkdir -p $@

$(TEST_OBJ_DIR):
	@mkdir -p $@

$(BIN_DIR):
	@mkdir -p $@

$(RESULTS_DIR)/comprehensive_analysis:
	@mkdir -p $@

$(RESULTS_DIR)/tests:
	@mkdir -p $@

# =============================================================================
# Analysis and Utility Targets
# =============================================================================

.PHONY: analysis
analysis: $(RESULTS_DIR)/comprehensive_analysis
	@echo "Running Python analysis..."
	cd $(ANALYSIS_DIR) && python run_analysis.py

.PHONY: run-sample
run-sample: release
	@echo "Running sample simulation..."
	./$(SIMULATOR_RELEASE) --config $(CONFIG_DIR)/simulator.cfg

.PHONY: run-batch
run-batch: release
	@echo "Running batch simulations..."
	./$(SIMULATOR_RELEASE) --batch

.PHONY: run-tests
run-tests: test
	@echo "Running test suite..."
	./$(TEST_EXECUTABLE)

.PHONY: valgrind-check
valgrind-check: debug
	@echo "Running valgrind memory check..."
	valgrind --leak-check=full --track-origins=yes --show-leak-kinds=all ./$(SIMULATOR_DEBUG) --config $(CONFIG_DIR)/simulator.cfg

.PHONY: profile-run
profile-run: profile
	@echo "Profiling simulation..."
	./$(SIMULATOR_PROFILE) --config $(CONFIG_DIR)/simulator.cfg
	gprof ./$(SIMULATOR_PROFILE) gmon.out > profiling_results.txt
	@echo "Profile results saved to profiling_results.txt"

.PHONY: benchmark
benchmark: release
	@echo "Running benchmark..."
	time ./$(SIMULATOR_RELEASE) --config $(CONFIG_DIR)/simulator.cfg

# =============================================================================
# Development Tools
# =============================================================================

.PHONY: format
format:
	@echo "Formatting code..."
	find $(SRC_DIR) $(TEST_DIR) include -name "*.cpp" -o -name "*.hpp" | xargs clang-format -i -style=file

.PHONY: lint
lint:
	@echo "Linting code..."
	cppcheck --enable=all --suppress=missingIncludeSystem -I include $(SRC_DIR) $(TEST_DIR)

.PHONY: coverage
coverage: debug
	@echo "Generating code coverage..."
	$(CXX) $(STD_FLAGS) -O0 -g --coverage -I include $(wildcard $(SRC_DIR)/*.cpp) $(TEST_SRCS) -o $(BIN_DIR)/coverage_test
	./$(BIN_DIR)/coverage_test
	lcov --capture --directory . --output-file coverage.info
	genhtml coverage.info --output-directory coverage_report
	@echo "Coverage report generated in coverage_report/"

# =============================================================================
# Clean Targets
# =============================================================================

.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR) $(BIN_DIR) *.out *.gcda *.gcno coverage.info coverage_report profiling_results.txt gmon.out

.PHONY: distclean
distclean: clean
	@echo "Deep cleaning..."
	rm -rf $(RESULTS_DIR)/*.csv $(RESULTS_DIR)/comprehensive_analysis/* $(RESULTS_DIR)/tests/*

.PHONY: veryclean
veryclean: distclean
	@echo "Nuclear clean..."
	rm -rf *.log *.tmp *.cache

# =============================================================================
# Dependency Generation
# =============================================================================

DEPENDENCY_FILES := $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.d,$(wildcard $(SRC_DIR)/*.cpp))

-include $(DEPENDENCY_FILES)

$(BUILD_DIR)/%.d: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	@$(CXX) $(STD_FLAGS) $(INCLUDE_FLAGS) -MM -MT $(patsubst $(SRC_DIR)/%.cpp,$(RELEASE_OBJ_DIR)/%.o,$<) -MT $(patsubst $(SRC_DIR)/%.cpp,$(DEBUG_OBJ_DIR)/%.o,$<) -MT $(patsubst $(SRC_DIR)/%.cpp,$(PROFILE_OBJ_DIR)/%.o,$<) $< > $@

# =============================================================================
# Info Targets
# =============================================================================

.PHONY: info
info:
	@echo "Build Configuration:"
	@echo "  Compiler: $(CXX)"
	@echo "  C++ Standard: $(CXX_STD)"
	@echo "  Source Directory: $(SRC_DIR)"
	@echo "  Build Directory: $(BUILD_DIR)"
	@echo "  Bin Directory: $(BIN_DIR)"
	@echo "  Release Flags: $(RELEASE_FLAGS)"
	@echo "  Debug Flags: $(DEBUG_FLAGS)"
	@echo "  Warning Flags: $(WARN_FLAGS)"

.PHONY: help
help:
	@echo "Advanced Queueing System Simulator - Build System"
	@echo ""
	@echo "Build Targets:"
	@echo "  all/release    - Build optimized release version (default)"
	@echo "  debug          - Build with debug symbols and sanitizers"
	@echo "  profile        - Build for profiling"
	@echo "  test           - Build and run test suite"
	@echo ""
	@echo "Utility Targets:"
	@echo "  run-sample     - Run sample simulation"
	@echo "  run-batch      - Run batch simulations"
	@echo "  analysis       - Run Python analysis pipeline"
	@echo "  benchmark      - Performance benchmark"
	@echo "  valgrind-check - Memory leak detection"
	@echo "  profile-run    - Generate profiling data"
	@echo ""
	@echo "Clean Targets:"
	@echo "  clean          - Remove build artifacts"
	@echo "  distclean      - Remove build artifacts and results"
	@echo "  veryclean      - Remove all generated files"
	@echo ""
	@echo "Development:"
	@echo "  format         - Format source code"
	@echo "  lint           - Static code analysis"
	@echo "  coverage       - Generate code coverage report"
	@echo ""
	@echo "Info:"
	@echo "  info           - Show build configuration"
	@echo "  help           - Show this help message"

# =============================================================================
# Special Targets
# =============================================================================

.SILENT: info help
.DEFAULT_GOAL := all

# Print build info at start
$(shell echo "Building with $(CXX) [$(BUILD_TYPE)]" > /dev/null)