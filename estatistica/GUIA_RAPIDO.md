# ⚡ Como Usar nas Próximas Aulas

Este guia rápido explica como utilizar os atalhos do `Makefile`, abrir a interface gráfica do **RCommander**, e criar novas aulas na sua workstation de Estatística.

---

## 1. 🖥️ Interface Gráfica e Console Interativo

Para facilitar a sua vida, adicionei regras no `Makefile` principal:

| Comando | Descrição |
| :--- | :--- |
| **`make gui`** (ou `make rcmdr`) | **Abre a Interface Gráfica do RCommander diretamente!** |
| **`make r`** (ou `make console`) | Abre o console interativo do R no terminal |
| **`make graficos`** | Gera todos os gráficos da Aula 01 na pasta `reports/` |

---

## 2. 📁 Criando uma Nova Aula Automaticamente

Quando tiver uma nova aula (por exemplo, a Aula 02 de Probabilidade), execute na raiz do projeto:

```bash
make nova-aula N=02 NAME=probabilidade
```

> [!TIP]
> Isso criará automaticamente a pasta `aula_02_probabilidade/` contendo:
> - `Makefile` próprio pré-configurado
> - Pasta `src/` com `main.R` inicial
> - Pastas `data/` e `reports/` prontas
> - `README.md` explicativo da aula

---

## 3. Resumo de Comandos da Raiz (`estatistica/`)

| Comando | Ação |
| :--- | :--- |
| `make gui` | Abre o RCommander (Interface Gráfica) |
| `make nova-aula N=XX NAME=nome` | Cria o projeto de uma nova aula a partir do template |
| `make aula-01` | Executa todos os scripts da Aula 01 |
| `make graficos` | Gera os gráficos (histograma, boxplot, ggplot2) |
| `make run-all` | Executa **todas as aulas** do repositório em sequência |
| `make check-env` | Verifica o ambiente do R e versões instaladas |
| `make clean` | Limpa dados gerados e relatórios de todas as aulas |
