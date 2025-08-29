#!/bin/bash

# Configurações
SERVER_IP="200.131.225.141"  # Externo
LOCAL_IP="192.168.1.254"     # Rede DCC
PORT="2345"
DOMAIN="www2.bcc.unifal-mg.edu.br"
REMOTE_PATH="~/"  # Substituir se necessário

echo "=== Publicação no Servidor Turing ==="

# Verificar se está na rede do DCC
read -p "Está na rede do DCC? (s/n): " is_dcc

if [ "$is_dcc" = "s" ] || [ "$is_dcc" = "S" ]; then
    TARGET_IP=$LOCAL_IP
else
    TARGET_IP=$DOMAIN
    PORT="22"  # Porta padrão para conexões externas
fi

# Coletar credenciais
read -p "Usuário: " username
read -s -p "Senha: " password
echo

# 1. Ajustar permissões do diretório home (via SSH)
echo "Ajustando permissões do diretório..."
sshpass -p "$password" ssh -p $PORT $username@$TARGET_IP "chmod 755 ~"

# 2. Transferência de arquivos
read -p "Diretório local dos arquivos para upload: " local_dir
if [ -d "$local_dir" ]; then
    echo "Iniciando upload..."
    sshpass -p "$password" scp -r -P $PORT "$local_dir" $username@$TARGET_IP:$REMOTE_PATH
else
    echo "Erro: Diretório local não encontrado!"
    exit 1
fi

# 3. Verificar estrutura remota
echo "Verificando estrutura de arquivos no servidor..."
sshpass -p "$password" ssh -p $PORT $username@$TARGET_IP "ls -la ~/"

echo "Concluído! Acesse: http://$DOMAIN/~$username"