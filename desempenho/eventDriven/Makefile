# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -std=c++17 -Wall -O2

# Target executable
TARGET = main

# Source files
SRCS = main.cpp

# Build rule
all: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET)

# Clean build files
clean:
	rm -f $(TARGET) *.o

# Run the main
run: $(TARGET)
	./$(TARGET)
