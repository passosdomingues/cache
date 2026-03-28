#!/bin/bash

# ==============================================================================
# Cores ANSI para Terminal
# ==============================================================================
C_CYAN='\033[1;36m'
C_GREEN='\033[1;32m'
C_YELLOW='\033[1;33m'
C_RED='\033[1;31m'
C_RESET='\033[0m'

# Garante que o script está a ser executado a partir da pasta 'data'
cd "$(dirname "$0")" || exit

if [ ! -f "../codigo_base/Makefile" ]; then
    echo -e "${C_RED}[ERRO CRITICO] Execute este script a partir da pasta 'data'!${C_RESET}"
    exit 1
fi

CODIGO_DIR="../codigo_base"
INSTANCIAS_DIR="../instancias"

# Define o caminho do interpretador Python (usa o VENV se existir)
if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    PYTHON_CMD="python3"
fi

# Compila o código remotamente na pasta codigo_base usando o Makefile SAGRADO
make -C $CODIGO_DIR --quiet

arquivos=($(ls -v $INSTANCIAS_DIR))
total=${#arquivos[@]}

while true; do
    clear
    echo -e "${C_CYAN}==========================================${C_RESET}"
    echo -e "${C_CYAN} [AEDs 3] ORQUESTRADOR TÁTICO - tp_02     ${C_RESET}"
    echo -e "${C_CYAN}==========================================${C_RESET}"
    echo -e "  ${C_YELLOW}1 a $total)${C_RESET} Testar instância cirurgicamente"
    echo -e "  ${C_GREEN}99)${C_RESET} RODAR BATERIA COMPLETA (Extração + Gráficos)"
    echo -e "  ${C_RED}0)${C_RESET} Abortar e limpar rastros"
    echo -e "${C_CYAN}==========================================${C_RESET}"
    
    read -p "Aguardando comando: " opt

    if [ "$opt" = "0" ]; then
        echo -e "${C_YELLOW}Limpando atalhos dinâmicos (symlinks)...${C_RESET}"
        rm -f ../bla
        echo -e "${C_GREEN}Sistema limpo. Saindo.${C_RESET}"
        break
    
    # Orquestrador Automático
    elif [ "$opt" = "99" ]; then
        clear
        echo -e "${C_CYAN}[SISTEMA] Iniciando varredura global. Processando...${C_RESET}"
        echo "Tamanho,TempoDP,TempoGuloso" > benchmarks.csv
        
        for arquivo in "${arquivos[@]}"; do
            tamanho=$(echo "$arquivo" | cut -d'-' -f1)
            echo -ne "Processando lote ${C_YELLOW}$arquivo${C_RESET}... "
            
            # Symlink injetado nas sombras
            ln -sf "$PWD/$INSTANCIAS_DIR/$arquivo" ../bla
            
            # Compilação e execução cega do professor
            saida=$(make -C $CODIGO_DIR run 2>/dev/null)
            
            # Parsing via AWK
            t_dp=$(echo "$saida" | awk '/Programação Dinâmica/{flag=1} flag && /Tempo:/{print $2; flag=0}')
            t_guloso=$(echo "$saida" | awk '/Guloso/{flag=1} flag && /Tempo:/{print $2; flag=0}')
            
            if [ -n "$t_dp" ] && [ -n "$t_guloso" ]; then
                echo "$tamanho,$t_dp,$t_guloso" >> benchmarks.csv
                echo -e "${C_GREEN}Sucesso${C_RESET} (DP: ${t_dp}s | Gul: ${t_guloso}s)"
            else
                echo -e "${C_RED}Falha de extração!${C_RESET}"
            fi
        done
        
        echo -e "${C_CYAN}------------------------------------------${C_RESET}"
        echo -e "${C_CYAN}[SISTEMA] Extração concluída. Invocando renderização visual...${C_RESET}"
        
        # Chama o Python usando o VENV
        $PYTHON_CMD gerador_graficos.py
        
        echo ""
        read -p "Pressione [Enter] para retornar ao terminal base..."
    
    # Instância Singular
    elif [[ "$opt" =~ ^[0-9]+$ ]] && [ "$opt" -ge 1 ] && [ "$opt" -le "$total" ]; then
        idx=$((opt-1))
        arquivo_escolhido="${arquivos[$idx]}"
        
        clear
        echo -e "${C_CYAN}==========================================${C_RESET}"
        echo -e " Alvo selecionado: ${C_YELLOW}$arquivo_escolhido${C_RESET}"
        echo -e "${C_CYAN}==========================================${C_RESET}"
        
        ln -sf "$PWD/$INSTANCIAS_DIR/$arquivo_escolhido" ../bla
        make -C $CODIGO_DIR run
        
        echo ""
        read -p "Pressione [Enter] para retornar ao terminal base..."
    else
        echo -e "${C_RED}[ERRO] Comando não reconhecido.${C_RESET}"
        sleep 1
    fi
done
