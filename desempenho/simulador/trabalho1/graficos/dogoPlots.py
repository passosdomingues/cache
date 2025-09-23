import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set_theme(style="whitegrid")
sns.set_context("talk")

# Arquivos e cenários
arquivos = [
    "relatorio_ocupacao_0800.csv",
    "relatorio_ocupacao_0900.csv",
    "relatorio_ocupacao_0950.csv",
    "relatorio_ocupacao_0999.csv"
]
ocupacoes = ["0.80", "0.90", "0.95", "0.999"]

# Leitura dos dados
dados = [pd.read_csv(f) for f in arquivos]
cores = sns.color_palette("tab10", n_colors=4)

# Criar diretório para salvar as imagens (se necessário)
import os
if not os.path.exists('graficos'):
    os.makedirs('graficos')

# --- 1. E[N] e E[W] ao longo do tempo para cada cenário ---
for i, df in enumerate(dados):
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=df['Tempo(s)'], y=df['E[N]'], label='E[N]', color=cores[0])
    sns.lineplot(x=df['Tempo(s)'], y=df['E[W]'], label='E[W]', color=cores[1])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Valor')
    plt.title(f"E[N] e E[W] ao longo do tempo - Ocupação {ocupacoes[i]}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'graficos/dogoPlots/en_ew_tempo_ocupacao_{ocupacoes[i]}.png', dpi=300, bbox_inches='tight')
    plt.close()

# --- 2. Todos os cenários juntos (log para 0.999) ---
plt.figure(figsize=(10, 5))
for i, df in enumerate(dados):
    y = np.log(df['E[N]']) if ocupacoes[i] == "0.999" else df['E[N]']
    sns.lineplot(x=df['Tempo(s)'], y=y, label=f"E[N] occ {ocupacoes[i]}", color=cores[i])
plt.xlabel('Tempo (s)')
plt.ylabel('E[N]')
plt.title("Comparativo E[N] todos os cenários")
plt.tight_layout()
plt.savefig('graficos/dogoPlots/comparativo_en_todos_cenarios.png', dpi=300, bbox_inches='tight')
plt.close()

plt.figure(figsize=(10, 5))
for i, df in enumerate(dados):
    y = np.log(df['E[W]']) if ocupacoes[i] == "0.999" else df['E[W]']
    sns.lineplot(x=df['Tempo(s)'], y=y, label=f"E[W] occ {ocupacoes[i]}", color=cores[i])
plt.xlabel('Tempo (s)')
plt.ylabel('E[W]')
plt.title("Comparativo E[W] todos os cenários")
plt.tight_layout()
plt.savefig('graficos/dogoPlots/comparativo_ew_todos_cenarios.png', dpi=300, bbox_inches='tight')
plt.close()

# --- 3. E[N] e E[W] vs tamanho da fila ---
for i, df in enumerate(dados):
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=df['Fila'], y=df['E[N]'], label='E[N]', color=cores[0])
    sns.lineplot(x=df['Fila'], y=df['E[W]'], label='E[W]', color=cores[1])
    plt.xlabel('Tamanho da fila')
    plt.ylabel('Valor')
    plt.title(f"E[N] e E[W] vs Fila - Ocupação {ocupacoes[i]}")
    plt.tight_layout()
    plt.savefig(f'graficos/dogoPlots/en_ew_vs_fila_ocupacao_{ocupacoes[i]}.png', dpi=300, bbox_inches='tight')
    plt.close()

# --- 4. Tamanho da fila ao longo do tempo ---
for i, df in enumerate(dados):
    plt.figure(figsize=(10, 5))
    sns.lineplot(x=df['Tempo(s)'], y=df['Fila'], label='Fila', color=cores[2])
    plt.xlabel('Tempo (s)')
    plt.ylabel('Tamanho da fila')
    plt.title(f"Tamanho da fila ao longo do tempo - Ocupação {ocupacoes[i]}")
    plt.tight_layout()
    plt.savefig(f'graficos/dogoPlots/fila_tempo_ocupacao_{ocupacoes[i]}.png', dpi=300, bbox_inches='tight')
    plt.close()

print("Todos os gráficos foram salvos na pasta 'graficos' com 300 DPI")
