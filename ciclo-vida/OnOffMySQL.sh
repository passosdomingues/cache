#!/bin/bash

while true; do
    echo "0. quit"
    echo "1. start"
    echo "2. stop"
    echo "3. status"
    read -p "Escolha uma opção: " opcao

    case $opcao in
        0)
            echo "Saindo..."
            exit 0
            ;;
        1)
            sudo systemctl start mysql
            echo "MySQL iniciado."
            ;;
        2)
            sudo systemctl stop mysql
            echo "MySQL parado."
            ;;
        3)
            sudo systemctl status mysql
            ;;
        *)
            echo "Opção inválida."
            ;;
    esac
done

