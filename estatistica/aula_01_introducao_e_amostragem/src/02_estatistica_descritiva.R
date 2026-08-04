# ==============================================================================
# 02_estatistica_descritiva.R
# Estatística Descritiva e Medidas Resumo no R
# Baseado na Nota de Aula: Introdução ao Software R (Prof. Luiz Alberto Beijo)
# ==============================================================================

rm(list = ls())

cat("=== ESTATÍSTICA DESCRITIVA E MEDIDAS RESUMO ===\n\n")

# 1. Vetor de Dados Exemplo 1
x1 <- c(4, 5, 5, 7, 9, 10)
cat("Vetor x1:", x1, "\n")
cat("Somatório sum(x1):", sum(x1), "\n\n")

# 2. Vetor de Dados Exemplo 2
x2 <- c(1, 2, 3, 4, 5)
cat("Vetor x2:", x2, "\n")
cat("Média mean(x2):", mean(x2), "\n")
cat("Variância var(x2):", var(x2), "\n")
cat("Desvio Padrão sd(x2):", sd(x2), "\n")
cat("Mínimo e Máximo range(x2):", range(x2), "\n\n")

# 3. Vetor com Dados não ordenados (Mediana)
x3 <- c(1, 2, 18, 7, 6)
cat("Vetor x3 (com outlier):", x3, "\n")
cat("Mediana median(x3):", median(x3), "\n\n")

# 4. Resumo dos Dados (summary)
cat("--- Resumo Estatístico Completo summary(x3) ---\n")
print(summary(x3))
