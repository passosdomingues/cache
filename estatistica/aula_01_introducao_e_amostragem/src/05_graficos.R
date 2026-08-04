# ==============================================================================
# 05_graficos.R
# Geração e Exportação de Gráficos em R
# Baseado na disciplina de Estatística (Prof. Luiz Alberto Beijo)
# ==============================================================================

rm(list = ls())

cat("=== GERAÇÃO E EXPORTAÇÃO DE GRÁFICOS EM R ===\n\n")

# Garantir diretório reports/
if (!dir.exists("reports")) {
  dir.create("reports")
}

# Dados de exemplo (Princípio Ativo de Fármaco + Amostra Normal)
set.seed(42)
dados_farmaco <- c(4.5, 5.1, 4.8, 4.1, 4.7, 4.4, 4.5, 4.7)
amostra_normal <- rnorm(100, mean = 50, sd = 10)

# 1. Gráfico de Histograma (Base R)
png("reports/01_histograma.png", width = 800, height = 600, res = 120)
hist(amostra_normal, 
     main = "Histograma de Frequências (Distribuição Normal)",
     xlab = "Valores Medidos", 
     ylab = "Frequência Absoluta",
     col = "#4A90E2", 
     border = "white")
dev.off()
cat("-> Gráfico salvo: reports/01_histograma.png\n")

# 2. Boxplot (Gráfico de Caixa)
png("reports/02_boxplot.png", width = 800, height = 600, res = 120)
boxplot(dados_farmaco, 
        main = "Boxplot - Principio Ativo em Fármacos (mg)",
        ylab = "Princípio Ativo (mg)",
        col = "#50E3C2", 
        border = "#2C3E50")
dev.off()
cat("-> Gráfico salvo: reports/02_boxplot.png\n")

# 3. Gráfico de Dispersão com ggplot2 (Pacote Avançado)
if (requireNamespace("ggplot2", quietly = TRUE)) {
  library(ggplot2)
  
  df <- data.frame(
    Frasco = 1:length(dados_farmaco),
    Principio_Ativo = dados_farmaco
  )
  
  p <- ggplot(df, aes(x = Frasco, y = Principio_Ativo)) +
    geom_point(color = "#E74C3C", size = 4) +
    geom_line(color = "#3498DB", linetype = "dashed") +
    geom_hline(yintercept = mean(dados_farmaco), color = "#2ECC71", linetype = "solid", linewidth = 1) +
    labs(title = "Concentração de Princípio Ativo por Frasco",
         subtitle = "Linha verde representa a Média (4.6 mg)",
         x = "Número do Frasco",
         y = "Princípio Ativo (mg)") +
    theme_minimal()
  
  ggsave("reports/03_ggplot_dispersao.png", plot = p, width = 7, height = 5, dpi = 150)
  cat("-> Gráfico ggplot2 salvo: reports/03_ggplot_dispersao.png\n")
}

cat("\nGráficos gerados com sucesso na pasta reports/!\n")
