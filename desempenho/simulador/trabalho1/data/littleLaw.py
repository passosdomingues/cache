import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuração do estilo dos gráficos
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Cores para os diferentes cenários
cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

# Nomes dos arquivos e rótulos
arquivos = [
    'dados_ocupacao_080.csv',
    'dados_ocupacao_090.csv',
    'dados_ocupacao_095.csv',
    'dados_ocupacao_0999.csv'
]

rotulos = [
    'Ocupação = 0.80',
    'Ocupação = 0.90',
    'Ocupação = 0.95',
    'Ocupação = 0.999'
]

# Criar figura com subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('Métricas da Lei de Little por Cenário de Ocupação', fontsize=16, fontweight='bold')

# Dicionário para armazenar todos os dados
todos_dados = {}

# Ler e plotar dados de cada arquivo
for i, (arquivo, rotulo, cor) in enumerate(zip(arquivos, rotulos, cores)):
    try:
        # Ler dados do arquivo CSV
        dados = pd.read_csv(arquivo)
        todos_dados[rotulo] = dados
        
        # Calcular eixos para subplot
        linha = i // 2
        coluna = i % 2
        
        # Plotar E[N] - Número médio de requisições no sistema
        axs[linha, coluna].plot(dados['Tempo'], dados['NumeroMedioRequisicoes'], 
                               color=cor, linewidth=2, label='E[N]')
        
        # Plotar E[W] - Tempo médio de espera no sistema
        axs[linha, coluna].plot(dados['Tempo'], dados['TempoMedioEspera'], 
                               color=cor, linewidth=2, linestyle='--', label='E[W]')
        
        # Configurar subplot
        axs[linha, coluna].set_title(rotulo, fontweight='bold')
        axs[linha, coluna].set_xlabel('Tempo (segundos)')
        axs[linha, coluna].set_ylabel('Métricas')
        axs[linha, coluna].legend()
        axs[linha, coluna].grid(True, alpha=0.3)
        
        # Adicionar texto com valores finais
        texto = f"E[N] final: {dados['NumeroMedioRequisicoes'].iloc[-1]:.2f}\nE[W] final: {dados['TempoMedioEspera'].iloc[-1]:.2f}"
        axs[linha, coluna].text(0.02, 0.98, texto, transform=axs[linha, coluna].transAxes,
                               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
    except FileNotFoundError:
        print(f"Arquivo {arquivo} não encontrado. Execute primeiro o simulador em C.")

# Ajustar layout
plt.tight_layout()
plt.savefig('metricas_little.png', dpi=300, bbox_inches='tight')
plt.show()

# Criar gráficos comparativos
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Gráfico comparativo de E[N]
for (rotulo, dados), cor in zip(todos_dados.items(), cores):
    ax1.plot(dados['Tempo'], dados['NumeroMedioRequisicoes'], 
             color=cor, linewidth=2, label=rotulo)

ax1.set_title('Comparação de E[N] entre Cenários', fontweight='bold')
ax1.set_xlabel('Tempo (segundos)')
ax1.set_ylabel('E[N] - Número médio de requisições no sistema')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Gráfico comparativo de E[W]
for (rotulo, dados), cor in zip(todos_dados.items(), cores):
    ax2.plot(dados['Tempo'], dados['TempoMedioEspera'], 
             color=cor, linewidth=2, label=rotulo)

ax2.set_title('Comparação de E[W] entre Cenários', fontweight='bold')
ax2.set_xlabel('Tempo (segundos)')
ax2.set_ylabel('E[W] - Tempo médio de espera no sistema')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('comparacao_metricas.png', dpi=300, bbox_inches='tight')
plt.show()

# Gráfico de ocupação ao longo do tempo
fig3, ax = plt.subplots(figsize=(12, 7))

for (rotulo, dados), cor in zip(todos_dados.items(), cores):
    ax.plot(dados['Tempo'], dados['Ocupacao'], 
            color=cor, linewidth=2, label=rotulo)

ax.set_title('Evolução da Ocupação do Sistema', fontweight='bold')
ax.set_xlabel('Tempo (segundos)')
ax.set_ylabel('Ocupação')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('evolucao_ocupacao.png', dpi=300, bbox_inches='tight')
plt.show()

print("Gráficos salvos como:")
print("- metricas_little.png (gráficos individuais por cenário)")
print("- comparacao_metricas.png (comparação entre cenários)")
print("- evolucao_ocupacao.png (evolução da ocupação)")