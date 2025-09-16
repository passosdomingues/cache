#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configurações
LOG_FILE="/var/log/mysql_controller.log"
MYSQL_SERVICE="mysql"
MYSQL_USER="root"

# Inicialização
init() {
    # Criar arquivo de log com permissões adequadas
    sudo touch "$LOG_FILE" 2>/dev/null || LOG_FILE="./mysql_controller.log"
    sudo chown $USER:$USER "$LOG_FILE" 2>/dev/null || true
    
    # Verificar se systemctl está disponível
    if ! command -v systemctl &> /dev/null; then
        print_message "$RED" "Erro: systemctl não encontrado. Este script requer systemd." "systemctl não encontrado" "❌"
        exit 1
    fi
}

# Função de logging
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Função para exibir mensagens formatadas
print_message() {
    local color=$1
    local message=$2
    local log_msg=$3
    local emoji=$4
    
    echo -e "${color}${emoji} ${message}${NC}"
    [[ -n "$log_msg" ]] && log "$log_msg"
}

# Tratamento de erros
error_handler() {
    local exit_code=$1
    local context=$2
    
    case $exit_code in
        0)
            return 0  # Sucesso
            ;;
        1)
            print_message "$RED" "Erro: Operação não permitida" "Erro de permissão em $context" "🔒"
            ;;
        2)
            print_message "$RED" "Erro: Serviço não encontrado" "Serviço não encontrado em $context" "🔍"
            ;;
        3)
            print_message "$RED" "Erro: Timeout na operação" "Timeout em $context" "⏰"
            ;;
        4)
            print_message "$RED" "Erro: Falha de conexão" "Falha de conexão em $context" "🔌"
            ;;
        *)
            print_message "$RED" "Erro desconhecido (código: $exit_code)" "Erro desconhecido $exit_code em $context" "❓"
            ;;
    esac
    
    return $exit_code
}

# Funções de serviço MySQL
mysql_start() {
    print_message "$GREEN" "Iniciando MySQL..." "Tentativa de iniciar MySQL" "▶"
    
    # Verificar se já está rodando
    if sudo systemctl is-active --quiet $MYSQL_SERVICE; then
        print_message "$YELLOW" "MySQL já está em execução" "Tentativa de iniciar MySQL já em execução" "ℹ"
        return 0
    fi
    
    # Tentar iniciar
    if sudo systemctl start $MYSQL_SERVICE; then
        # Aguardar inicialização completa
        for i in {1..10}; do
            if sudo systemctl is-active --quiet $MYSQL_SERVICE; then
                print_message "$GREEN" "MySQL iniciado com sucesso!" "MySQL iniciado com sucesso" "✓"
                return 0
            fi
            sleep 1
        done
        print_message "$YELLOW" "MySQL iniciado mas verificação de status demorou" "MySQL iniciado mas verificação demorou" "⚠"
        return 3
    else
        print_message "$RED" "Falha ao iniciar MySQL!" "Falha ao iniciar MySQL" "✗"
        return 1
    fi
}

mysql_stop() {
    print_message "$YELLOW" "Parando MySQL..." "Tentativa de parar MySQL" "⏹"
    
    # Verificar se já está parado
    if ! sudo systemctl is-active --quiet $MYSQL_SERVICE; then
        print_message "$YELLOW" "MySQL já está parado" "Tentativa de parar MySQL já parado" "ℹ"
        return 0
    fi
    
    # Tentar parar
    if sudo systemctl stop $MYSQL_SERVICE; then
        # Aguardar parada completa
        for i in {1..10}; do
            if ! sudo systemctl is-active --quiet $MYSQL_SERVICE; then
                print_message "$GREEN" "MySQL parado com sucesso!" "MySQL parado com sucesso" "✓"
                return 0
            fi
            sleep 1
        done
        print_message "$YELLOW" "MySQL parado mas verificação de status demorou" "MySQL parado mas verificação demorou" "⚠"
        return 3
    else
        print_message "$RED" "Falha ao parar MySQL!" "Falha ao parar MySQL" "✗"
        return 1
    fi
}

mysql_restart() {
    print_message "$BLUE" "Reiniciando MySQL..." "Tentativa de reiniciar MySQL" "🔄"
    
    if sudo systemctl restart $MYSQL_SERVICE; then
        print_message "$GREEN" "MySQL reiniciado com sucesso!" "MySQL reiniciado com sucesso" "✓"
        return 0
    else
        print_message "$RED" "Falha ao reiniciar MySQL!" "Falha ao reiniciar MySQL" "✗"
        return 1
    fi
}

mysql_status() {
    local status=$(sudo systemctl is-active $MYSQL_SERVICE 2>/dev/null)
    
    case $status in
        active)
            print_message "$GREEN" "MySQL está rodando" "Verificação de status: MySQL ativo" "✓"
            return 0
            ;;
        inactive)
            print_message "$RED" "MySQL está parado" "Verificação de status: MySQL inativo" "✗"
            return 2
            ;;
        *)
            print_message "$YELLOW" "Status do MySQL desconhecido ou serviço não encontrado" "Verificação de status: Status desconhecido" "?"
            return 2
            ;;
    esac
}

mysql_detailed_status() {
    print_message "$BLUE" "Status detalhado do MySQL:" "Solicitação de status detalhado" "🔍"
    
    if sudo systemctl status $MYSQL_SERVICE; then
        log "Status detalhado verificado"
        return 0
    else
        print_message "$RED" "Erro ao obter status detalhado" "Erro ao obter status detalhado" "❌"
        return 1
    fi
}

mysql_connections() {
    print_message "$PURPLE" "Verificando conexões ativas..." "Verificação de conexões ativas" "🔗"
    
    if command -v mysqladmin &> /dev/null; then
        if sudo mysqladmin processlist 2>/dev/null; then
            log "Conexões ativas verificadas"
            return 0
        else
            print_message "$RED" "Não foi possível verificar conexões. MySQL pode não estar rodando." "Falha ao verificar conexões" "⚠"
            return 4
        fi
    else
        print_message "$RED" "mysqladmin não encontrado" "mysqladmin não encontrado" "❌"
        return 2
    fi
}

mysql_version() {
    print_message "$CYAN" "Verificando versão do MySQL..." "Verificação de versão" "ℹ"
    
    if command -v mysql &> /dev/null; then
        if sudo mysql --version 2>/dev/null; then
            log "Versão do MySQL verificada"
            return 0
        else
            print_message "$YELLOW" "Não foi possível verificar a versão do MySQL." "Falha ao verificar versão" "⚠"
            return 1
        fi
    else
        print_message "$RED" "mysql não encontrado" "mysql não encontrado" "❌"
        return 2
    fi
}

mysql_test_connection() {
    print_message "$WHITE" "Testando conexão com MySQL..." "Teste de conexão com MySQL" "📡"
    
    if command -v mysqladmin &> /dev/null; then
        if sudo mysqladmin ping -u ${MYSQL_USER} 2>/dev/null | grep -q "alive"; then
            print_message "$GREEN" "Conexão com MySQL bem-sucedida!" "Teste de conexão bem-sucedido" "✓"
            return 0
        else
            print_message "$RED" "Falha na conexão com MySQL" "Teste de conexão falhou" "✗"
            return 4
        fi
    else
        print_message "$RED" "mysqladmin não encontrado" "mysqladmin não encontrado para teste de conexão" "❌"
        return 2
    fi
}

mysql_logs() {
    print_message "$YELLOW" "Exibindo logs do MySQL..." "Visualização de logs do MySQL" "📄"
    
    if sudo journalctl -u $MYSQL_SERVICE -n 20 --no-pager; then
        log "Logs do MySQL visualizados"
        return 0
    else
        print_message "$RED" "Erro ao exibir logs do MySQL" "Erro ao exibir logs do MySQL" "❌"
        return 1
    fi
}

# Funções de UI
show_header() {
    clear
    echo -e "${BLUE}==================================================${NC}"
    echo -e "${BLUE}           MySQL Controller v4.0${NC}"
    echo -e "${BLUE}==================================================${NC}"
    mysql_status
    echo -e "${BLUE}==================================================${NC}"
}

show_menu() {
    echo -e "0. Sair"
    echo -e "1. ${GREEN}Iniciar${NC} MySQL"
    echo -e "2. ${RED}Parar${NC} MySQL"
    echo -e "3. ${BLUE}Reiniciar${NC} MySQL"
    echo -e "4. ${YELLOW}Status${NC} rápido"
    echo -e "5. ${CYAN}Status${NC} detalhado (systemctl)"
    echo -e "6. ${PURPLE}Conexões${NC} ativas"
    echo -e "7. ${WHITE}Testar${NC} conexão"
    echo -e "8. ${GREEN}Versão${NC} do MySQL"
    echo -e "9. Visualizar ${YELLOW}logs${NC} do MySQL"
    echo -e "10. Visualizar ${BLUE}logs${NC} do controlador"
    echo -e "${BLUE}==================================================${NC}"
}

show_controller_logs() {
    print_message "$YELLOW" "Últimas 20 entradas do log:" "Visualização do log do controlador" "📄"
    if [ -f "$LOG_FILE" ]; then
        tail -20 "$LOG_FILE"
    else
        print_message "$RED" "Arquivo de log não encontrado!" "Tentativa de visualizar log inexistente" "⚠"
        return 1
    fi
}

# Main
main() {
    init
    
    while true; do
        show_header
        show_menu
        read -p "Escolha uma opção (0-10): " opcao

        case $opcao in
            0)
                print_message "$GREEN" "Saindo..." "Script finalizado pelo usuário" "👋"
                exit 0
                ;;
            1)
                mysql_start
                error_handler $? "iniciar MySQL"
                ;;
            2)
                mysql_stop
                error_handler $? "parar MySQL"
                ;;
            3)
                mysql_restart
                error_handler $? "reiniciar MySQL"
                ;;
            4)
                mysql_status
                error_handler $? "verificar status MySQL"
                ;;
            5)
                mysql_detailed_status
                error_handler $? "verificar status detalhado MySQL"
                ;;
            6)
                mysql_connections
                error_handler $? "verificar conexões MySQL"
                ;;
            7)
                mysql_test_connection
                error_handler $? "testar conexão MySQL"
                ;;
            8)
                mysql_version
                error_handler $? "verificar versão MySQL"
                ;;
            9)
                mysql_logs
                error_handler $? "visualizar logs MySQL"
                ;;
            10)
                show_controller_logs
                error_handler $? "visualizar logs do controlador"
                ;;
            *)
                print_message "$RED" "Opção inválida!" "Tentativa com opção inválida: $opcao" "❌"
                ;;
        esac

        echo -e "\nPressione Enter para continuar..."
        read
    done
}

# Tratamento de sinais
trap 'print_message "$RED" "Script interrompido pelo usuário" "Script interrompido pelo sinal" "⚠"; exit 1' INT TERM

# Execução principal
main "$@"
