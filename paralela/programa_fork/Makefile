# Define o compilador
CC = gcc

# Define as flags de compilação (mostra todos os avisos)
CFLAGS = -Wall -Wextra

# Nome do executável de saída
TARGET = programa_fork

# Regra padrão que será executada ao digitar apenas 'make'
all: $(TARGET)

# Regra para compilar o executável
$(TARGET): main.c
	$(CC) $(CFLAGS) -o $(TARGET) main.c

# Regra utilitária para rodar o programa automaticamente
run: all
	./$(TARGET)

# Regra para limpar os arquivos gerados pela compilação
clean:
	rm -f $(TARGET)