# ==============================================================================
# 04_banco_de_dados.R
# Criando, Manipulando e Salvando Banco de Dados no R
# Baseado na Nota de Aula: Criando e salvando um banco de dados no Rcommander
# (Prof. Luiz Alberto Beijo)
# ==============================================================================

rm(list = ls())

cat("=== BANCO DE DADOS: QUANTIDADE DE PRINCÍPIO ATIVO (mg) ===\n\n")

# Dados da amostra de 8 frascos
principio_ativo <- c(4.5, 5.1, 4.8, 4.1, 4.7, 4.4, 4.5, 4.7)

# Criando um data.frame (banco de dados)
dados_farmaco <- data.frame(
  Frasco = 1:length(principio_ativo),
  Principio_Ativo_mg = principio_ativo
)

cat("--- Tabela do Banco de Dados ---\n")
print(dados_farmaco)
cat("\n")

cat("--- Resumo Estatístico do Banco de Dados ---\n")
print(summary(dados_farmaco$Principio_Ativo_mg))
cat("\n")

cat("Média:", mean(dados_farmaco$Principio_Ativo_mg), "mg\n")
cat("Desvio Padrão:", sd(dados_farmaco$Principio_Ativo_mg), "mg\n\n")

# Criar pasta data/ se não existir
if (!dir.exists("data")) {
  dir.create("data")
}

# Salvando banco de dados em formato CSV e RData
write.csv(dados_farmaco, file = "data/farmaco_amostra.csv", row.names = FALSE)
save(dados_farmaco, file = "data/farmaco_amostra.RData")

cat("Banco de dados salvo com sucesso em:\n")
cat("  - data/farmaco_amostra.csv\n")
cat("  - data/farmaco_amostra.RData\n")
