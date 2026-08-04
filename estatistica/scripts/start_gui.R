# ==============================================================================
# scripts/start_gui.R
# Inicializador do RCommander (GUI) - Nota de Aula Prof. Luiz Alberto Beijo
# ==============================================================================

options(repos = c(CRAN = "https://cloud.r-project.org"))

options(Rcmdr = list(
  console.output = FALSE,   # Exibe os resultados na janela Output da GUI em azul
  log.width = 80,            # Largura da janela do script (80 carac.)
  log.height = 25,           # Altura da janela do script (25 linhas)
  output.height = 30,        # Altura da janela de output (30 linhas)
  messages.height = 3,       # Altura da janela de mensagens (3 linhas)
  quit.R.on.close = TRUE,    # Fecha a sessão do R ao fechar a janela da GUI
  ask.to.exit = FALSE        # Não pede confirmação ao fechar
))

suppressMessages(library(Rcmdr))
