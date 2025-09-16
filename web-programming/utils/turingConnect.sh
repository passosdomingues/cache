#!/bin/bash

###############################################################################
# Script de Publicação Automática para o Servidor Turing - UNIFAL-MG
# 
# Este script automatiza o processo de publicação de documentos web no servidor
# Turing do Departamento de Ciência da Computação da UNIFAL-MG.
#
# Baseado nos tutoriais oficiais do DCC:
# - Conexão SSH: https://www.unifal-mg.edu.br/dcc/como-fazer-ssh-para-o-bcc/
# - Hospedagem: https://www.unifal-mg.edu.br/dcc/como-hospedar-seu-site/
# - Transferência: https://www.unifal-mg.edu.br/dcc/como-transferir-arquivos/
#
# Variáveis de ambiente necessárias:
#   - BCC_USER: Nome de usuário no servidor Turing
#   - BCC_PASSWORD: Senha do usuário no servidor Turing
#
# Uso:
#   Modo interativo:
#        ./turingConnect.sh
#
#   Modo direto (com parâmetros):
#        ./turingConnect.sh ssh          # Conexão SSH
#        ./turingConnect.sh host         # Configurar hospedagem
#        ./turingConnect.sh transferir   # Transferir arquivos (pedirá caminho)
#        ./turingConnect.sh deploy /caminho/arquivo.html  # Deploy direto
#
# Autor: Rafael Passos Domingues
# Data: 01/09/2025
###############################################################################

# Configurações
readonly SERVER_DOMAIN="www2.bcc.unifal-mg.edu.br"
readonly SERVER_IP="200.131.225.141"
readonly LOCAL_IP="192.168.1.254"
readonly DEFAULT_PORT="22"
readonly LOCAL_PORT="2345"
readonly SERVER_NAME="Turing"
readonly SERVER_DESTINATION="Discentes do BCC"
readonly TIMEOUT=10  # Timeout para operações de rede em segundos

# Cores para output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Variáveis globais
TARGET_IP=""
PORT=""
USERNAME="${BCC_USER}"
PASSWORD="${BCC_PASSWORD}"

###############################################################################
# Função: show_header
# Exibe o cabeçalho do script
###############################################################################
show_header() {
    clear
    echo -e "${BLUE}=========================================================${NC}"
    echo -e "${CYAN}    Publicação no Servidor Turing - UNIFAL-MG DCC       ${NC}"
    echo -e "${CYAN}                   Versão 2.0                           ${NC}"
    echo -e "${BLUE}=========================================================${NC}"
    echo -e "${YELLOW}Servidor: $SERVER_NAME${NC}"
    echo -e "${YELLOW}Destinado a: $SERVER_DESTINATION${NC}"
    echo -e "${YELLOW}Domínio: $SERVER_DOMAIN${NC}"
    echo -e "${YELLOW}IP: $SERVER_IP${NC}"
    echo -e "${BLUE}=========================================================${NC}"
    echo
}

###############################################################################
# Função: show_usage
# Mostra como usar o script
###############################################################################
show_usage() {
    echo -e "${BLUE}Uso do script:${NC}"
    echo -e "  Modo interativo:"
    echo -e "    ${GREEN}./turingConnect.sh${NC}"
    echo -e "  Modo direto:"
    echo -e "    ${GREEN}./turingConnect.sh ssh${NC}"
    echo -e "    ${GREEN}./turingConnect.sh host${NC}"
    echo -e "    ${GREEN}./turingConnect.sh transferir${NC}"
    echo -e "    ${GREEN}./turingConnect.sh deploy /caminho/arquivo.html${NC}"
    echo -e "    ${GREEN}./turingConnect.sh test${NC}"
    echo -e "    ${GREEN}./turingConnect.sh help${NC}"
}

###############################################################################
# Função: check_dependencies
# Verifica se todas as dependências necessárias estão instaladas
###############################################################################
check_dependencies() {
    local dependencies=("ssh" "scp" "curl" "ping" "sshpass")
    local missing_deps=()
    
    echo -e "${BLUE}Verificando dependências...${NC}"
    
    for dep in "${dependencies[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}Erro: Dependências missing: ${missing_deps[*]}${NC}"
        echo -e "${YELLOW}Instale com: sudo apt install openssh-client curl iputils-ping sshpass${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Todas as dependências estão instaladas.${NC}"
}

###############################################################################
# Função: validate_credentials
# Valida se as credenciais foram fornecidas via variáveis de ambiente
###############################################################################
validate_credentials() {
    if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
        echo -e "${RED}Erro: Variáveis de ambiente não configuradas!${NC}"
        echo -e "${YELLOW}Configure antes de executar:${NC}"
        echo -e "  ${CYAN}export BCC_USER=\"seu_usuario\"${NC}"
        echo -e "  ${CYAN}export BCC_PASSWORD=\"sua_senha\"${NC}"
        echo
        echo -e "${YELLOW}Nota: Consulte os tutoriais do DCC se não possui credenciais:${NC}"
        echo -e "${CYAN}https://www.unifal-mg.edu.br/dcc/como-fazer-ssh-para-o-bcc/${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Credenciais validadas: Usuário $USERNAME${NC}"
}

###############################################################################
# Função: detect_network
# Detecta automaticamente se está na rede do DCC ou em rede externa
###############################################################################
detect_network() {
    echo -e "${BLUE}Detectando configuração de rede...${NC}"
    
    # Verifica se o IP está na faixa da rede do DCC (192.168.1.x)
    if ip addr show | grep -q "192\.168\.1\."; then
        echo -e "${GREEN}Rede detectada: DCC (interna)${NC}"
        TARGET_IP=$LOCAL_IP
        PORT=$LOCAL_PORT
        return 0
    fi
    
    # Tenta pingar o servidor local
    if timeout $TIMEOUT ping -c 1 -W 2 $LOCAL_IP > /dev/null 2>&1; then
        echo -e "${GREEN}Rede detectada: DCC (interna)${NC}"
        TARGET_IP=$LOCAL_IP
        PORT=$LOCAL_PORT
        return 0
    else
        echo -e "${YELLOW}Rede detectada: Externa${NC}"
        TARGET_IP=$SERVER_DOMAIN
        PORT=$DEFAULT_PORT
        return 1
    fi
}

###############################################################################
# Função: test_ssh_connection
# Testa a conexão SSH antes de tentar uma sessão interativa
###############################################################################
test_ssh_connection() {
    echo -e "${YELLOW}Testando conexão SSH...${NC}"
    
    # Testa a conexão com um comando simples
    if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=$TIMEOUT -p "$PORT" "$USERNAME@$TARGET_IP" "echo 'Conexão SSH bem-sucedida!'" 2>/dev/null; then
        echo -e "${GREEN}Conexão SSH testada com sucesso!${NC}"
        return 0
    else
        echo -e "${RED}Falha na conexão SSH. Verifique:${NC}"
        echo -e "${RED} - Credenciais corretas?${NC}"
        echo -e "${RED} - Servidor acessível?${NC}"
        echo -e "${RED} - Porta correta?${NC}"
        return 1
    fi
}

###############################################################################
# Função: setup_hosting
# Configura a hospedagem no servidor (cria public_html e define permissões)
###############################################################################
setup_hosting() {
    echo -e "${BLUE}Configurando hospedagem no servidor Turing...${NC}"
    
    # Comando SSH para configurar hospedagem
    local ssh_cmd="
    echo 'Configurando permissões do diretório home...';
    chmod 755 ~;
    echo 'Criando diretório public_html...';
    mkdir -p ~/public_html;
    echo 'Configurando permissões do public_html...';
    chmod 755 ~/public_html;
    echo 'Hospedagem configurada com sucesso!';
    echo 'Seu site estará disponível em: http://$SERVER_DOMAIN/~$USERNAME/'
    "
    
    # Executa via SSH
    echo -e "${YELLOW}Configurando ambiente de hospedagem...${NC}"
    if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=$TIMEOUT -p "$PORT" "$USERNAME@$TARGET_IP" "$ssh_cmd"; then
        echo -e "${GREEN}Hospedagem configurada com sucesso!${NC}"
        echo -e "${GREEN}URL do seu site: http://$SERVER_DOMAIN/~$USERNAME/${NC}"
        return 0
    else
        echo -e "${RED}Erro ao configurar hospedagem.${NC}"
        return 1
    fi
}

###############################################################################
# Função: connect_ssh
# Estabelece uma conexão SSH interativa com o servidor
###############################################################################
connect_ssh() {
    echo -e "${BLUE}Iniciando conexão SSH com o servidor Turing...${NC}"
    echo -e "${YELLOW}Usuário: $USERNAME${NC}"
    echo -e "${YELLOW}Servidor: $TARGET_IP${NC}"
    echo -e "${YELLOW}Porta: $PORT${NC}"
    
    # Testar a conexão primeiro
    if ! test_ssh_connection; then
        echo -e "${RED}Não foi possível estabelecer conexão SSH. Abortando.${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Iniciando sessão interativa...${NC}"
    echo -e "${YELLOW}Pressione Ctrl+D para desconectar${NC}"
    
    # Conexão SSH interativa
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -p "$PORT" "$USERNAME@$TARGET_IP"
    
    # Verifica o status da conexão
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Conexão SSH finalizada.${NC}"
    else
        echo -e "${RED}Erro durante a sessão SSH.${NC}"
    fi
}

###############################################################################
# Função: test_publication
# Testa se a publicação foi bem-sucedida
###############################################################################
test_publication() {
    echo -e "${BLUE}Testando publicação...${NC}"
    
    # Testa se o site está respondendo
    local url="http://$SERVER_DOMAIN/~$USERNAME/"
    echo -e "${YELLOW}Testando URL: $url${NC}"
    
    local http_status
    http_status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$url")
    
    if [ "$http_status" -eq 200 ]; then
        echo -e "${GREEN}✓ Site publicado com sucesso!${NC}"
        echo -e "${GREEN}URL: $url${NC}"
        return 0
    elif [ "$http_status" -eq 404 ]; then
        echo -e "${YELLOW}✗ Site encontrado mas arquivo não existe (404).${NC}"
        echo -e "${YELLOW}Verifique se o arquivo index.html existe em ~/public_html/${NC}"
        return 1
    elif [ "$http_status" -eq 403 ]; then
        echo -e "${YELLOW}✗ Acesso proibido (403).${NC}"
        echo -e "${YELLOW}Verifique as permissões do diretório public_html.${NC}"
        return 1
    else
        echo -e "${RED}✗ Site não encontrado ou não publicado.${NC}"
        echo -e "${YELLOW}Status HTTP: $http_status${NC}"
        echo -e "${YELLOW}Verifique se:${NC}"
        echo -e "${YELLOW}1. Seu diretório home tem permissão 755${NC}"
        echo -e "${YELLOW}2. Existe um diretório public_html em sua home${NC}"
        echo -e "${YELLOW}3. Seus arquivos estão em ~/public_html/${NC}"
        return 1
    fi
}

###############################################################################
# Função: transfer_files
# Faz transferência de arquivos para o servidor
# Parâmetro: $1 - Caminho do arquivo/diretório para transferir (opcional)
###############################################################################
transfer_files() {
    local transfer_path="$1"
    
    # Se nenhum caminho foi fornecido, pedir interativamente
    if [ -z "$transfer_path" ]; then
        echo -e "${YELLOW}Transferência de arquivos via SCP${NC}"
        read -p "Digite o caminho do arquivo/diretório para transferir: " transfer_path
    fi
    
    if [ ! -e "$transfer_path" ]; then
        echo -e "${RED}Erro: Caminho não encontrado!${NC}"
        return 1
    fi
    
    # Testar a conexão primeiro
    if ! test_ssh_connection; then
        echo -e "${RED}Não foi possível estabelecer conexão. Abortando transferência.${NC}"
        return 1
    fi
    
    # Fazer transferência dos arquivos
    echo -e "${YELLOW}Transferindo arquivos para o servidor...${NC}"
    if sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -o ConnectTimeout=$TIMEOUT -P "$PORT" -r "$transfer_path" "$USERNAME@$TARGET_IP:~/public_html/"; then
        echo -e "${GREEN}✓ Transferência realizada com sucesso!${NC}"
        echo -e "${GREEN}URL: http://$SERVER_DOMAIN/~$USERNAME/${NC}"
        
        # Testar a publicação após transferência
        read -p "Deseja testar a publicação? (s/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            test_publication
        fi
        
        return 0
    else
        echo -e "${RED}✗ Erro durante a transferência.${NC}"
        return 1
    fi
}

###############################################################################
# Função: show_menu
# Exibe o menu de opções
###############################################################################
show_menu() {
    echo -e "\n${BLUE}=== MENU SERVIDOR TURING ===${NC}"
    echo -e "${GREEN}Usuário: $USERNAME${NC}"
    echo -e "${GREEN}Rede: $TARGET_IP (Porta: $PORT)${NC}"
    echo -e "${CYAN}0. Sair${NC}"
    echo -e "${CYAN}1. Conexão remota via SSH ao Turing${NC}"
    echo -e "${CYAN}2. Hospedagem de site no servidor Turing${NC}"
    echo -e "${CYAN}3. Transferência de arquivos${NC}"
    echo -e "${CYAN}4. Testar publicação${NC}"
    echo -n -e "${BLUE}Escolha uma opção [0-4]: ${NC}"
}

###############################################################################
# Função: run_interactive_mode
# Modo interativo do script
###############################################################################
run_interactive_mode() {
    while true; do
        show_menu
        read -r choice
        
        case $choice in
            0) 
                echo -e "${GREEN}Saindo... Até logo!${NC}"
                exit 0 
                ;;
            1) 
                connect_ssh 
                ;;
            2) 
                setup_hosting 
                ;;
            3) 
                transfer_files ""
                ;;
            4) 
                test_publication 
                ;;
            *) 
                echo -e "${RED}Opção inválida! Tente novamente.${NC}"
                ;;
        esac
        
        # Pausa antes de mostrar o menu novamente
        echo -e "\n${YELLOW}Pressione Enter para continuar...${NC}"
        read -r
        show_header
    done
}

###############################################################################
# Função: main
# Função principal do script
###############################################################################
main() {
    # Configurar handler para Ctrl+C
    trap 'echo -e "\n${RED}Interrompido pelo usuário.${NC}"; exit 1' INT
    
    # Mostrar cabeçalho
    show_header
    
    # Verificar dependências
    check_dependencies
    
    # Validar credenciais
    validate_credentials
    
    # Detectar rede automaticamente
    detect_network
    
    # Processar argumentos de linha de comando
    case "${1}" in
        "ssh")
            connect_ssh
            ;;
        "host")
            setup_hosting
            ;;
        "transferir")
            transfer_files "$2"
            ;;
        "deploy")
            # Primeiro configura hospedagem, depois transfere arquivos
            if setup_hosting; then
                transfer_files "$2"
            fi
            ;;
        "test")
            test_publication
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        "")
            # Modo interativo
            run_interactive_mode
            ;;
        *)
            echo -e "${RED}Comando não reconhecido: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
}

###############################################################################
# Execução principal
###############################################################################

# Executar função principal com argumentos
main "$@"
