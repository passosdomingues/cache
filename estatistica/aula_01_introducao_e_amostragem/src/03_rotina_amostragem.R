# ==============================================================================
# 03_rotina_amostragem.R
# Técnicas de Amostragem em R
# Baseado em R_rotina-amostragem.txt (Prof. Luiz Alberto Beijo)
# ==============================================================================

rm(list = ls())

# Garantir reprodutibilidade (opcional)
set.seed(42)

cat("=========================================================\n")
cat(" 1. Amostragem Simples ao Acaso\n")
cat("=========================================================\n")
# Exemplo nota de aula - 2.5.1
N <- 100  # Tamanho da POPULAÇÃO
n <- 10   # Tamanho da amostra

amostra_simples <- sample(N, n)  # Sorteando "n" elementos entre 1 e "N"
cat("População (N):", N, "\n")
cat("Amostra (n):", n, "\n")
cat("Elementos sorteados:", amostra_simples, "\n\n")

cat("=========================================================\n")
cat(" 2. Amostragem Estratificada\n")
cat("=========================================================\n")
# Exemplo nota de aula - sec 2.5.2
TE <- c(873, 386, 246, 186, 112)  # Tamanho dos estratos Ni
N <- 1803                         # Tamanho total da POPULAÇÃO
n <- 100                          # Tamanho total da amostra

ni <- n / N * TE                  # Proporção por estrato
ni2 <- round(ni, 0)               # Arredondando para número inteiro de elementos

cat("Tamanho dos estratos (TE):", TE, "\n")
cat("Tamanho da amostra por estrato (ni calculada):", round(ni, 2), "\n")
cat("Tamanho da amostra arredondada (ni2):", ni2, "\n")
cat("Soma das amostras dos estratos:", sum(ni2), "\n\n")

# Sorteio dos elementos dentro de cada estrato:
cat("Elementos sorteados em cada estrato:\n")
for (i in 1:length(TE)) {
  amostra_estrato <- sample(TE[i], ni2[i])
  cat(sprintf("  Estrato %d (tamanho %d, amostra %d): %s\n", 
              i, TE[i], ni2[i], paste(amostra_estrato, collapse = ", ")))
}
cat("\n")

cat("=========================================================\n")
cat(" 3. Amostragem Sistemática\n")
cat("=========================================================\n")
# Exemplo nota de aula - sec 2.5.3
N <- 6000
n <- 30

R_razao <- round(N / n, 0)        # Razão / passo de amostragem
sort_elem1 <- sample(R_razao, 1)   # Sorteio do 1º elemento entre 1 e R
posicao <- seq(sort_elem1, N, R_razao) # Sequência com saltos de tamanho R

cat("População (N):", N, "\n")
cat("Amostra (n):", n, "\n")
cat("Razão de amostragem (R = N/n):", R_razao, "\n")
cat("Primeiro elemento sorteado:", sort_elem1, "\n")
cat("Posições selecionadas na amostra sistemática:\n")
print(posicao)
