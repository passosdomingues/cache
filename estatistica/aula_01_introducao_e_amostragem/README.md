# Aula 01: Introdução ao Software R, Estatística Descritiva e Amostragem

Esta pasta contém o projeto completo correspondente à primeira aula da disciplina de Estatística (Prof. Luiz Alberto Beijo).

---

## 📁 Estrutura do Projeto da Aula 01

```
aula_01_introducao_e_amostragem/
├── Makefile                      # Automação de execução da Aula 01
├── README.md                     # Documentação da Aula 01
├── material/                     # Materiais de suporte (PDFs, TXT)
│   └── R_rotina-amostragem.txt
├── src/                          # Códigos fonte em R
│   ├── 00_hello_world.R          # Hello World & Teste do R
│   ├── 01_operacoes_basicas.R    # Operadores aritméticos, lógicos e funções
│   ├── 02_estatistica_descritiva.R# Média, mediana, variância, desvio padrão
│   ├── 03_rotina_amostragem.R    # Amostragem simples, estratificada e sistemática
│   └── 04_banco_de_dados.R       # Criação e manipulação de data.frame
├── data/                         # Saída de dados (CSVs, RData)
└── reports/                      # Relatórios da aula
```

---

## 🚀 Como Executar

Dentro desta pasta, utilize os comandos `make`:

```bash
make help        # Lista os comandos disponíveis
make run-all     # Executa todos os scripts da aula
make amostragem  # Executa apenas os exercícios de amostragem
```
