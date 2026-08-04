# ==============================================================================
# scripts/start_gui.R
# Inicializador do RCommander (GUI) com janela de Output ativa (Nota de Aula Prof. Luiz)
# ==============================================================================

if (interactive()) {
  # 1. Repositório CRAN padrão
  options(repos = c(CRAN = "https://cloud.r-project.org"))
  
  # 2. Configurar locale em português (PT-BR)
  Sys.setlocale("LC_ALL", "pt_BR.UTF-8")
  
  # 3. Configurações da Interface do RCommander (Recomendações da Nota de Aula)
  #    - console.output = FALSE (Exibe resultados na janela de Output da GUI, não no terminal)
  #    - log.height = 25 (Altura da janela de Script)
  #    - output.height = 30 (Altura da janela de Output)
  #    - messages.height = 3 (Altura da janela de Mensagens)
  options(Rcmdr = list(
    console.output = FALSE,    # Ativa a aba/janela "Output" dentro do RCommander
    log.width = 80,            # Largura da janela do script
    log.height = 25,           # Altura da janela do script
    output.height = 30,        # Altura da janela de output
    messages.height = 3,       # Altura da janela de mensagens
    quit.R.on.close = TRUE,    # Encerra o R ao fechar a janela
    ask.to.exit = FALSE        # Não pede confirmação ao fechar
  ))
  
  # 4. Carregar RCommander
  suppressMessages(library(Rcmdr))
}
