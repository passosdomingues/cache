# ==============================================================================
# 01_operacoes_basicas.R
# Operações Básicas e Funções Aritméticas no R
# Baseado na Nota de Aula: Introdução ao Software R (Prof. Luiz Alberto Beijo)
# ==============================================================================

# Limpar memória do R antes de iniciar análises
rm(list = ls())

cat("=== OPERAÇÕES BÁSICAS E OPERADORES NO R ===\n\n")

# 1. Operadores Aritméticos
a <- 25
b <- 35
soma <- a + b
subtracao <- a - b
multiplicacao <- a * b
divisao <- a / b
potencia <- a ^ 2

cat("--- Aritmética ---\n")
cat("Soma (25 + 35):", soma, "\n")
cat("Subtração (25 - 35):", subtracao, "\n")
cat("Multiplicação (25 * 35):", multiplicacao, "\n")
cat("Divisão (25 / 35):", divisao, "\n")
cat("Potenciação (25 ^ 2):", potencia, "\n\n")

# 2. Operadores Lógicos
cat("--- Operadores Lógicos ---\n")
cat("25 == 35:", 25 == 35, "\n")
cat("25 < 35:", 25 < 35, "\n")
cat("25 > 35:", 25 > 35, "\n")
cat("25 <= 35:", 25 <= 35, "\n")
cat("25 >= 35:", 25 >= 35, "\n")
cat("25 != 35:", 25 != 35, "\n\n")

# 3. Funções Aritméticas e Matemáticas
x <- 16
y <- 2.7182818

cat("--- Funções Matemáticas ---\n")
cat("sqrt(16) [Raiz Quadrada]:", sqrt(x), "\n")
cat("log(10, base=10) [Logaritmo Base 10]:", log(10, 10), "\n")
cat("log(10) [Logaritmo Neperiano/Natural]:", log(10), "\n")
cat("exp(1) [Exponencial e^1]:", exp(1), "\n")
cat("sin(pi/2) [Seno de pi/2 radianos]:", sin(pi/2), "\n")
cat("asin(1) [Arco-seno de 1]:", asin(1), "\n")
cat("abs(-42) [Módulo/Valor Absoluto]:", abs(-42), "\n")
