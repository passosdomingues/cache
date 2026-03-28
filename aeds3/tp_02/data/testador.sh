#!/bin/bash

# Garante que o script está a ser executado a partir da pasta 'data'
cd "$(dirname "$0")" || exit

# Verifica se a pasta codigo_base e o Makefile existem um nível acima
if [ ! -f "../codigo_base/Makefile" ]; then
    echo "Erro: Execute este script a partir da pasta 'data' (ex: tp_02/data)!"
    exit 1
fi

# Diretórios importantes relativos à pasta 'data'
CODIGO_DIR="../codigo_base"
INSTANCIAS_DIR="../instancias"

# Compila o código remotamente na pasta codigo_base
make -C $CODIGO_DIR --quiet

arquivos=($(ls -v $INSTANCIAS_DIR))
total=${#arquivos[@]}

while true; do
    clear
    echo "=========================================="
    echo " [AEDs 3] Testador e Orquestrador - tp_02 "
    echo "=========================================="
    echo "  1 a $total) Testar instância específica"
    echo "  99) RODAR TUDO E GERAR GRÁFICOS (CSV + Python)"
    echo "  0) Sair"
    echo "=========================================="
    
    read -p "Escolha uma opção: " opt

    if [ "$opt" = "0" ]; then
        echo "Limpando atalhos e saindo..."
        rm -f ../bla
        break
    
    # Opção 99: Orquestrador Automático
    elif [ "$opt" = "99" ]; then
        clear
        echo "Iniciando bateria de testes globais. Isto pode demorar alguns segundos..."
        # O CSV será gerado dentro da pasta data
        echo "Tamanho,TempoDP,TempoGuloso" > resultados.csv
        
        for arquivo in "${arquivos[@]}"; do
            # Extrai o tamanho N a partir do nome do arquivo
            tamanho=$(echo "$arquivo" | cut -d'-' -f1)
            
            echo -n "Processando $arquivo... "
            
            # Cria o link 'bla' na raiz da tp_02 (um nível acima da pasta data)
            ln -sf "$PWD/$INSTANCIAS_DIR/$arquivo" ../bla
            
            # Executa o make run remotamente, silenciando os avisos
            saida=$(make -C $CODIGO_DIR run 2>/dev/null)
            
            # Extração dos tempos usando AWK
            t_dp=$(echo "$saida" | awk '/Programação Dinâmica/{flag=1} flag && /Tempo:/{print $2; flag=0}')
            t_guloso=$(echo "$saida" | awk '/Guloso/{flag=1} flag && /Tempo:/{print $2; flag=0}')
            
            # Se conseguiu ler os valores, guarda no CSV
            if [ -n "$t_dp" ] && [ -n "$t_guloso" ]; then
                echo "$tamanho,$t_dp,$t_guloso" >> resultados.csv
                echo "Concluído (DP: ${t_dp}s, Guloso: ${t_guloso}s)"
            else
                echo "Erro ao extrair tempos!"
            fi
        done
        
        echo "------------------------------------------"
        echo "Testes concluídos! Gerando gráficos..."
        # Chama o script Python localmente na pasta data
        python3 gerador_graficos.py
        
        read -p "Dê [Enter] para voltar ao menu..."
    
    # Teste de uma instância singular
    elif [[ "$opt" =~ ^[0-9]+$ ]] && [ "$opt" -ge 1 ] && [ "$opt" -le "$total" ]; then
        idx=$((opt-1))
        arquivo_escolhido="${arquivos[$idx]}"
        
        clear
        echo "=========================================="
        echo " Executando: $arquivo_escolhido"
        echo "=========================================="
        
        ln -sf "$PWD/$INSTANCIAS_DIR/$arquivo_escolhido" ../bla
        make -C $CODIGO_DIR run
        
        echo ""
        read -p "Dê [Enter] para voltar ao menu..."
    else
        echo "❌ Opção inválida."
        sleep 1
    fi
done
