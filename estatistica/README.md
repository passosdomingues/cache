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

# ⚡ Como Usar nas Próximas Aulas

Este guia rápido explica como criar novas aulas e gerenciar a sua workstation de Estatística em R.

---

## 1. Criando uma Nova Aula Automaticamente

Quando você tiver uma nova aula (por exemplo, a Aula 02 de Probabilidade), basta executar o comando abaixo na **raiz do projeto** (`/home/rafael/github/cache/estatistica`):

```bash
make nova-aula N=02 NAME=probabilidade
```

> [!TIP]
> **O que isso faz?**
> O comando acima criará automaticamente a pasta `aula_02_probabilidade/` contendo:
> - `Makefile` próprio pré-configurado
> - Pasta `src/` com `main.R` inicial
> - Pastas `data/` e `reports/` prontas
> - `README.md` explicativo da aula

---

## 2. Comandos Principais do Repositório

### Na Raiz do Projeto (`estatistica/`)

| Comando | Ação |
| :--- | :--- |
| `make nova-aula N=XX NAME=nome` | Cria o projeto de uma nova aula a partir do template |
| `make aula-01` | Executa todos os scripts da Aula 01 |
| `make run-all` | Executa **todas as aulas** do repositório em sequência |
| `make check-env` | Verifica o ambiente do R e versões instaladas |
| `make clean` | Limpa dados gerados e relatórios de todas as aulas |

---

### Dentro da Pasta de Uma Aula Específica (ex: `aula_01_introducao_e_amostragem/`)

```bash
cd aula_01_introducao_e_amostragem

make help      # Exibe os comandos disponíveis para a aula
make run-all   # Executa os scripts da aula
make clean     # Limpa arquivos gerados na aula
```
