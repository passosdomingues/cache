# Configurações do Compilador
CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2
LIBS = -pthread

TARGETS = soma_threads soma_processos

all: $(TARGETS)

soma_threads: soma_threads.c
	$(CC) $(CFLAGS) soma_threads.c -o soma_threads $(LIBS)

soma_processos: soma_processos.c
	$(CC) $(CFLAGS) soma_processos.c -o soma_processos

# Executa ambos os programas exibindo as saídas contextuais
run: all
	./soma_threads
	./soma_processos

clean:
	rm -f $(TARGETS)

.PHONY: all run clean