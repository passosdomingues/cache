# Author: Rafael Passos Domingues
# Last Update: 2025 Sep 25 15:20
# Purpose: Build system for low-level C simulator

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -g
LDFLAGS =
LDLIBS = -lm

SRC_DIR = src
BUILD_DIR = build
BIN_DIR = bin

TARGET = simulator

SRCS = $(SRC_DIR)/main.c
OBJS = $(BUILD_DIR)/main.o
EXEC = $(BIN_DIR)/$(TARGET)

.PHONY: all clean compile run

# all agora faz tudo: clean -> compile -> run
all: clean compile run

compile: $(EXEC)

$(EXEC): $(OBJS) | $(BIN_DIR)
	$(CC) $(CFLAGS) $(LDFLAGS) $(OBJS) -o $@ $(LDLIBS)

$(BUILD_DIR)/main.o: $(SRCS) | $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

run: $(EXEC)
	./$(EXEC)

clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)

