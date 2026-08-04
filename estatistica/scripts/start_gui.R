# ==============================================================================
# scripts/start_gui.R
# Inicializador do RCommander (GUI) sem prompts e com encerramento automático
# ==============================================================================

if (interactive()) {
  # 1. Definir repositório CRAN padrão (nunca pede para escolher mirror)
  options(repos = c(CRAN = "https://cloud.r-project.org"))
  
  # 2. Configurar locale em português (PT-BR)
  Sys.setlocale("LC_ALL", "pt_BR.UTF-8")
  
  # 3. Configurar opções do RCommander (sem perguntas ao sair, encerra R ao fechar a janela)
  options(Rcmdr = list(
    quit.R.on.close = TRUE,   # Encerra o R ao fechar a janela (evita travar no terminal)
    ask.to.exit = FALSE,       # Não pede confirmação redundante para sair
    console.output = TRUE
  ))
  
  # 4. Carregar RCommander
  suppressMessages(library(Rcmdr))
}
