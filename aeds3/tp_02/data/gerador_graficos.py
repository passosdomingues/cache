import os
import csv
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict

print("Plotando gráficos em tons de cinza para artigo com Seaborn...")

# 1. Cria a pasta 'graficos' se ela não existir
pasta_saida = "graficos"
os.makedirs(pasta_saida, exist_ok=True)

# 2. Leitura dos dados do CSV
dados_dp = defaultdict(list)
dados_guloso = defaultdict(list)

try:
    with open('benchmarks.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader) # Salta o cabeçalho
        for row in reader:
            tamanho = int(row[0])
            dados_dp[tamanho].append(float(row[1]))
            dados_guloso[tamanho].append(float(row[2]))
except FileNotFoundError:
    print("Erro: O arquivo benchmarks.csv não foi encontrado. Rode o testador primeiro.")
    exit(1)

# Processamento das médias e memória
tamanhos = np.array(sorted(dados_dp.keys()))
tempo_dp_avg = np.array([np.mean(dados_dp[t]) for t in tamanhos])
tempo_guloso_avg = np.array([np.mean(dados_guloso[t]) for t in tamanhos])

memoria_dp = (tamanhos ** 2) * 8 / 1024 
memoria_guloso = np.array([1] * len(tamanhos))

# ==========================================
# CONFIGURAÇÃO DE ESTILO SEABORN PARA ARTIGO
# ==========================================
# style="whitegrid" dá um fundo branco com linhas de grade suaves
sns.set_theme(style="ticks", rc={"axes.grid": True, "grid.linestyle": ":", "grid.color": "#cccccc"})
# context="paper" ajusta o tamanho das fontes e linhas para artigos científicos
sns.set_context("paper", font_scale=1.2)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Estilos definidos para garantir a distinção no P&B:
# DP: Preto sólido, linha contínua, marcador de círculo ('o')
# Guloso: Cinza escuro, linha tracejada, marcador de quadrado ('s')
estilo_dp = {'color': 'black', 'linestyle': '-', 'marker': 'o', 'markersize': 6, 'linewidth': 1.5}
estilo_guloso = {'color': '#555555', 'linestyle': '--', 'marker': 's', 'markersize': 6, 'linewidth': 1.5}

# ----------------- GRÁFICO 1: TEMPO -----------------
axes[0].plot(tamanhos, tempo_dp_avg, label='Prog. Dinâmica', **estilo_dp)
axes[0].plot(tamanhos, tempo_guloso_avg, label='Algoritmo Guloso', **estilo_guloso)

axes[0].set_title('Tempo de Execução vs. Tamanho da Entrada', fontweight='bold')
axes[0].set_xlabel('Tamanho da Entrada (N)')
axes[0].set_ylabel('Tempo (Segundos)')
axes[0].legend(frameon=True, edgecolor='black')

# ----------------- GRÁFICO 2: MEMÓRIA -----------------
axes[1].plot(tamanhos, memoria_dp, label='Prog. Dinâmica', **estilo_dp)
axes[1].plot(tamanhos, memoria_guloso, label='Algoritmo Guloso', **estilo_guloso)

axes[1].set_title('Consumo de Memória vs. Tamanho da Entrada', fontweight='bold')
axes[1].set_xlabel('Tamanho da Entrada (N)')
axes[1].set_ylabel('Memória (KB)')
axes[1].set_yscale('log') # Escala logarítmica para memória
axes[1].legend(frameon=True, edgecolor='black')

# Despine remove as bordas superior e direita para um visual mais limpo (padrão Tufte/Acadêmico)
sns.despine()

plt.tight_layout()

# 3. Salva na pasta 'graficos' com 300 DPI e remove bordas brancas sobressalentes
caminho_arquivo = os.path.join(pasta_saida, "desempenho_algoritmos_pb.png")
plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight')

print(f"Sucesso! Gráfico de alta qualidade salvo em: {caminho_arquivo}")
# plt.show() # Descomente esta linha se quiser que o gráfico também abra numa janela
