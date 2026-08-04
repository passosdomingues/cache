# Disciplina de Estatística em R 📊

Este repositório é uma **Workstation modular** organizada para acompanhar todas as aulas, exercícios e projetos da disciplina de Estatística.

---

## 📁 Estrutura de Diretórios

```
estatistica/
├── Makefile                          # Makefile principal (gerencia todas as aulas)
├── README.md                         # Guia do repositório
├── .gitignore                        # Arquivos ignorados pelo Git
├── env/                              # Ambiente R compartilhado (R 4.5.3)
├── templates/                        # Modelo padronizado para novas aulas
│   ├── Makefile
│   ├── README.md
│   └── src/main.R
│
└── aula_01_introducao_e_amostragem/  # Projeto individual da Aula 01
    ├── Makefile                      # Makefile específico da Aula 01
    ├── README.md                     # Teoria e documentação da Aula 01
    ├── material/                     # PDFs e notas de aula
    ├── src/                          # Scripts R da Aula 01
    ├── data/                         # Arquivos de dados (.csv, .RData)
    └── reports/                      # Relatórios da Aula 01
```

---

## 🚀 Como Utilizar

### 1. Executando as Aulas
Você pode rodar os comandos a partir da raiz ou entrando em qualquer pasta de aula específica:

- **Executar a Aula 01**:
  ```bash
  make aula-01
  ```

- **Executar todas as aulas do curso**:
  ```bash
  make run-all
  ```

- **Verificar ambiente R**:
  ```bash
  make check-env
  ```

### 2. Criando uma Nova Aula (Exemplo: Aula 02)
Para criar a estrutura de uma nova aula automaticamente com o seu próprio `Makefile`, utilize o comando:

```bash
make nova-aula N=02 NAME=probabilidade
```

Isso criará a pasta `aula_02_probabilidade/` pronta com `Makefile`, `src/main.R`, `data/` e `reports/`.
