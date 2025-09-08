#!/bin/bash

# Função para exibir o menu principal
exibir_menu() {
    clear
    echo "========================================"
    echo "   Instalação de Dois Sites WordPress"
    echo "========================================"
    echo "1) Preparar ambiente"
    echo "2) Baixar e descompactar WordPress"
    echo "3) Criar bancos de dados MySQL"
    echo "4) Configurar Apache"
    echo "5) Completar instalação do WordPress"
    echo "6) Sair"
    echo -n "Escolha uma opção [1-6]: "
}

# Função para preparar o ambiente
preparar_ambiente() {
    echo "Criando diretórios para os sites..."
    sudo mkdir -p /var/www/html/primeiro_site /var/www/html/segundo_site
    sudo chown -R www-data:www-data /var/www/html/primeiro_site /var/www/html/segundo_site
    sudo chmod -R 755 /var/www/html/primeiro_site /var/www/html/segundo_site
    echo "Ambiente preparado com sucesso!"
    read -p "Pressione Enter para continuar..."
}

# Função para baixar e descompactar o WordPress
baixar_wordpress() {
    echo "Baixando e descompactando o WordPress..."
    for site in primeiro_site segundo_site; do
        cd /var/www/html/$site
        sudo wget https://br.wordpress.org/latest-pt_BR.tar.gz
        sudo tar -xvzf latest-pt_BR.tar.gz --strip-components=1
        sudo rm latest-pt_BR.tar.gz
    done
    echo "WordPress instalado nos diretórios dos sites!"
    read -p "Pressione Enter para continuar..."
}

# Função para criar bancos de dados MySQL
criar_bancos_dados() {
    echo "Criando bancos de dados MySQL..."
    sudo mysql -u root -p <<EOF
CREATE DATABASE primeiro_site;
CREATE DATABASE segundo_site;
CREATE USER 'usuario_primeiro'@'localhost' IDENTIFIED BY 'senha_segura';
CREATE USER 'usuario_segundo'@'localhost' IDENTIFIED BY 'senha_segura';
GRANT ALL PRIVILEGES ON primeiro_site.* TO 'usuario_primeiro'@'localhost';
GRANT ALL PRIVILEGES ON segundo_site.* TO 'usuario_segundo'@'localhost';
FLUSH PRIVILEGES;
EOF
    echo "Bancos de dados criados com sucesso!"
    read -p "Pressione Enter para continuar..."
}

# Função para configurar o Apache
configurar_apache() {
    echo "Configurando Apache para os sites..."
    for site in primeiro_site segundo_site; do
        sudo bash -c "cat > /etc/apache2/sites-available/$site.conf <<EOF
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html/$site
    ServerName localhost
    ServerAlias localhost/$site
    ErrorLog \${APACHE_LOG_DIR}/error.log
    CustomLog \${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF"
        sudo a2ensite $site.conf
    done
    sudo systemctl restart apache2
    echo "Apache configurado e reiniciado com sucesso!"
    read -p "Pressione Enter para continuar..."
}

# Função para completar a instalação do WordPress
completar_instalacao() {
    echo "Acesse os sites para completar a instalação do WordPress:"
    echo "1) http://localhost/primeiro_site"
    echo "2) http://localhost/segundo_site"
    echo "Siga as instruções de instalação fornecendo os detalhes do banco de dados."
    read -p "Pressione Enter após completar a instalação..."
}

# Loop principal do menu
while true; do
    exibir_menu
    read opcao
    case $opcao in
        1) preparar_ambiente ;;
        2) baixar_wordpress ;;
        3) criar_bancos_dados ;;
        4) configurar_apache ;;
        5) completar_instalacao ;;
        6) echo "Saindo..."; exit 0 ;;
        *) echo "Opção inválida!"; read -p "Pressione Enter para tentar novamente..." ;;
    esac
done
