#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Análise Científica Avançada para Dados de Simulação de Filas
Análise com normalização global, entropia de Shannon e visualizações 3D
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from scipy.optimize import curve_fit
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class AnaliseCientificaAvancada:
    def __init__(self, usarEscalaLogTempo=False, mostrar_graficos_interativos=True):
        self.usarEscalaLogTempo = usarEscalaLogTempo
        self.mostrar_graficos_interativos = mostrar_graficos_interativos
        self.dadosPorCenario = {}
        self.dadosNormalizados = {}
        self.expressoesAnaliticas = {}
        self.entropias = {}
        self.configurarVisualizacoes()
        self.criarDiretoriosSaida()
        self.scaler = StandardScaler()

    def configurarVisualizacoes(self):
        """Configura o estilo visual dos gráficos"""
        sns.set(style="whitegrid", palette="husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['axes.labelsize'] = 14

    def criarDiretoriosSaida(self):
        """Cria a estrutura de diretórios para armazenar os resultados"""
        diretorios = [
            'graficos/analiseGlobal/individuais', 
            'graficos/analiseGlobal/comparativos', 
            'graficos/analiseGlobal/tendencia', 
            'graficos/analiseGlobal/fila',
            'graficos/analiseGlobal/ocupacao',
            'graficos/analiseGlobal/correlacao',
            'graficos/analiseGlobal/distribuicao',
            'graficos/analiseGlobal/relacoes',
            'graficos/analiseGlobal/3d',
            'graficos/analiseGlobal/entropia',
            'graficos/analiseGlobal/estatistica'
        ]
        for d in diretorios:
            Path(d).mkdir(parents=True, exist_ok=True)

    def carregarDados(self, caminhosArquivos):
        """Carrega os dados de simulação a partir dos arquivos CSV"""
        todos_dados = []
        
        for caminho in caminhosArquivos:
            if Path(caminho).exists():
                nome = Path(caminho).stem.replace('dados_', '')
                dados = pd.read_csv(caminho)
                dados['Cenario'] = nome
                self.dadosPorCenario[nome] = dados
                todos_dados.append(dados)
                print(f"Dados carregados: {nome} ({len(dados)} registros)")
            else:
                print(f"Arquivo não encontrado: {caminho}")
        
        if todos_dados:
            self.dadosCompletos = pd.concat(todos_dados, ignore_index=True)
            return True
        return False

    def normalizarDadosGlobalmente(self):
        """Aplica normalização global a todas as variáveis numéricas"""
        colunas_numericas = ['Tempo', 'NumeroMedioRequisicoes', 'TempoMedioEspera', 
                            'TamanhoFila', 'Ocupacao']
        
        # Ajusta o scaler com todos os dados
        self.scaler.fit(self.dadosCompletos[colunas_numericas])
        
        # Aplica a normalização a cada cenário
        for nome, dados in self.dadosPorCenario.items():
            dados_normalizados = dados.copy()
            dados_normalizados[colunas_numericas] = self.scaler.transform(dados[colunas_numericas])
            self.dadosNormalizados[nome] = dados_normalizados
            
        print("Normalização global aplicada a todos os cenários")

    def calcular_entropia_shannon(self, dados, coluna='TamanhoFila', remover_transiente=True):
        """
        Calcula a Entropia de Shannon para quantificar a imprevisibilidade do sistema
        H(X) = -Σ p(x) * log2(p(x))
        """
        # Remove os primeiros 20% dos dados (transiente)
        if remover_transiente:
            n_remover = int(0.2 * len(dados))
            dados_estacionarios = dados.iloc[n_remover:].copy()
        else:
            dados_estacionarios = dados.copy()
        
        # Calcula a distribuição de probabilidade
        distribuicao = dados_estacionarios[coluna].value_counts(normalize=True)
        
        # Calcula a entropia
        entropia = -np.sum(distribuicao * np.log2(distribuicao + 1e-10))
        
        return entropia, distribuicao

    def calcular_entropia_janela_deslizante(self, dados, coluna='TamanhoFila', janela=100):
        """
        Calcula a entropia de Shannon em janela deslizante para análise temporal
        """
        entropia = []
        tempo_entropia = []
        
        for i in range(janela, len(dados)):
            janela_dados = dados[coluna].iloc[i-janela:i]
            contagem = janela_dados.value_counts(normalize=True)
            H = -np.sum(contagem * np.log2(contagem + 1e-10))
            entropia.append(H)
            tempo_entropia.append(dados['Tempo'].iloc[i])
        
        return pd.DataFrame({'Tempo': tempo_entropia, 'Entropia': entropia})

    def analisar_entropia_cenarios(self):
        """Calcula e analisa a entropia de Shannon para todos os cenários"""
        resultados = []
        
        for nome, dados in self.dadosPorCenario.items():
            # Calcula a entropia
            entropia, distribuicao = self.calcular_entropia_shannon(dados)
            self.entropias[nome] = entropia
            
            # Estatísticas adicionais
            dados_estacionarios = dados.iloc[int(0.2 * len(dados)):]
            media = dados_estacionarios['TamanhoFila'].mean()
            desvio_padrao = dados_estacionarios['TamanhoFila'].std()
            assimetria = dados_estacionarios['TamanhoFila'].skew()
            
            resultados.append({
                'Cenario': nome,
                'Ocupacao': dados_estacionarios['Ocupacao'].mean(),
                'Entropia': entropia,
                'Media_Tamanho_Fila': media,
                'Desvio_Padrao': desvio_padrao,
                'Assimetria': assimetria,
                'Estados_Unicos': len(distribuicao)
            })
            
            print(f"Cenário {nome}: Entropia = {entropia:.4f} bits")
        
        # Cria DataFrame com resultados
        self.resultados_entropia = pd.DataFrame(resultados)
        
        # Salva resultados
        self.resultados_entropia.to_csv("resultados_entropia.csv", index=False)
        print("Resultados de entropia salvos em 'resultados_entropia.csv'")
        
        return self.resultados_entropia

    def plotar_entropia_vs_ocupacao(self):
        """Gráfico de entropia em função da ocupação"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Ordena por ocupação
        dados_ordenados = self.resultados_entropia.sort_values('Ocupacao')
        
        # Plot
        ax.plot(dados_ordenados['Ocupacao'], dados_ordenados['Entropia'], 'bo-', linewidth=2, markersize=8)
        
        # Adiciona rótulos
        for i, row in dados_ordenados.iterrows():
            ax.annotate(row['Cenario'], (row['Ocupacao'], row['Entropia']), 
                       xytext=(5, 5), textcoords='offset points')
        
        ax.set_xlabel('Ocupação (ρ)')
        ax.set_ylabel('Entropia de Shannon (bits)')
        ax.set_title('Entropia do Sistema vs Ocupação')
        ax.grid(True, alpha=0.3)
        
        # Adiciona linha de tendência
        z = np.polyfit(dados_ordenados['Ocupacao'], dados_ordenados['Entropia'], 1)
        p = np.poly1d(z)
        ax.plot(dados_ordenados['Ocupacao'], p(dados_ordenados['Ocupacao']), "r--", alpha=0.7, 
               label=f'Tendência: y={z[0]:.2f}x+{z[1]:.2f}')
        ax.legend()
        
        plt.tight_layout()
        caminho = "graficos/analiseGlobal/entropia/entropia_vs_ocupacao.png"
        fig.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Gráfico de entropia vs ocupação salvo: {caminho}")

    def plotar_distribuicoes_entropia(self):
        """Gráficos das distribuições de tamanho de fila para cada cenário"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Distribuição do Tamanho da Fila por Cenário', fontsize=16, fontweight='bold')
        
        axes = axes.ravel()
        
        for i, (nome, dados) in enumerate(self.dadosPorCenario.items()):
            if i >= 4:
                break
                
            # Remove transiente
            dados_estacionarios = dados.iloc[int(0.2 * len(dados)):]
            
            # Plot histograma
            n_bins = min(50, len(dados_estacionarios['TamanhoFila'].unique()))
            axes[i].hist(dados_estacionarios['TamanhoFila'], bins=n_bins, density=True, alpha=0.7, color='skyblue')
            
            # Adiciona linha KDE
            sns.kdeplot(dados_estacionarios['TamanhoFila'], ax=axes[i], color='darkblue', linewidth=2)
            
            # Configurações do gráfico
            axes[i].set_title(f'{nome} (Entropia: {self.entropias.get(nome, 0):.3f} bits)')
            axes[i].set_xlabel('Tamanho da Fila')
            axes[i].set_ylabel('Densidade de Probabilidade')
            axes[i].grid(True, alpha=0.3)
            
            # Adiciona estatísticas
            media = dados_estacionarios['TamanhoFila'].mean()
            mediana = dados_estacionarios['TamanhoFila'].median()
            axes[i].axvline(media, color='red', linestyle='--', label=f'Média: {media:.2f}')
            axes[i].axvline(mediana, color='green', linestyle='--', label=f'Mediana: {mediana:.2f}')
            axes[i].legend()
        
        plt.tight_layout()
        caminho = "graficos/analiseGlobal/entropia/distribuicoes_tamanho_fila.png"
        fig.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Gráficos de distribuição salvos: {caminho}")

    def plotar_evolucao_entropia_temporal(self):
        """Gráfico da evolução temporal da entropia para cada cenário"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for nome, dados in self.dadosPorCenario.items():
            # Calcula entropia em janela deslizante
            df_entropia = self.calcular_entropia_janela_deslizante(dados, janela=100)
            
            # Plot
            ax.plot(df_entropia['Tempo'], df_entropia['Entropia'], label=nome, linewidth=2)
        
        ax.set_xlabel('Tempo')
        ax.set_ylabel('Entropia de Shannon (bits)')
        ax.set_title('Evolução Temporal da Entropia do Sistema')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        caminho = "graficos/analiseGlobal/entropia/evolucao_temporal_entropia.png"
        fig.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Gráfico de evolução temporal da entropia salvo: {caminho}")

    def gerarGraficos3DComEntropia(self):
        """Gera visualizações 3D com dados normalizados e coloridos por entropia"""
        for nome, dados in self.dadosNormalizados.items():
            # Calcula entropia para colorização
            if nome not in self.entropias:
                entropia, _ = self.calcular_entropia_shannon(self.dadosPorCenario[nome])
                self.entropias[nome] = entropia
            
            # Cria array com valor constante de entropia para todos os pontos
            entropia_array = np.full(len(dados), self.entropias[nome])
            
            fig = plt.figure(figsize=(20, 16))
            
            # 1. Tempo vs E[N] vs E[W] (colorido por Entropia)
            ax1 = fig.add_subplot(231, projection='3d')
            sc1 = ax1.scatter(
                dados['Tempo'], dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'],
                c=entropia_array, cmap='viridis', alpha=0.6, s=20
            )
            ax1.set_xlabel('Tempo (Normalizado)')
            ax1.set_ylabel('E[N] (Normalizado)')
            ax1.set_zlabel('E[W] (Normalizado)')
            ax1.set_title(f'Tempo vs E[N] vs E[W] (Entropia) - {nome}')
            fig.colorbar(sc1, ax=ax1, label='Entropia (bits)')
            
            # 2. Tempo vs Tamanho da Fila vs E[W] (colorido por Entropia)
            ax2 = fig.add_subplot(232, projection='3d')
            sc2 = ax2.scatter(
                dados['Tempo'], dados['TamanhoFila'], dados['TempoMedioEspera'],
                c=entropia_array, cmap='plasma', alpha=0.6, s=20
            )
            ax2.set_xlabel('Tempo (Normalizado)')
            ax2.set_ylabel('Tamanho da Fila (Normalizado)')
            ax2.set_zlabel('E[W] (Normalizado)')
            ax2.set_title(f'Tempo vs Tamanho Fila vs E[W] (Entropia) - {nome}')
            fig.colorbar(sc2, ax=ax2, label='Entropia (bits)')
            
            # 3. Tempo vs E[N] vs Tamanho da Fila (colorido por Entropia)
            ax3 = fig.add_subplot(233, projection='3d')
            sc3 = ax3.scatter(
                dados['Tempo'], dados['NumeroMedioRequisicoes'], dados['TamanhoFila'],
                c=entropia_array, cmap='inferno', alpha=0.6, s=20
            )
            ax3.set_xlabel('Tempo (Normalizado)')
            ax3.set_ylabel('E[N] (Normalizado)')
            ax3.set_zlabel('Tamanho da Fila (Normalizado)')
            ax3.set_title(f'Tempo vs E[N] vs Tamanho Fila (Entropia) - {nome}')
            fig.colorbar(sc3, ax=ax3, label='Entropia (bits)')
            
            # 4. Ocupação vs E[N] vs E[W] (colorido por Entropia)
            ax4 = fig.add_subplot(234, projection='3d')
            sc4 = ax4.scatter(
                dados['Ocupacao'], dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'],
                c=entropia_array, cmap='cool', alpha=0.6, s=20
            )
            ax4.set_xlabel('Ocupação (Normalizada)')
            ax4.set_ylabel('E[N] (Normalizado)')
            ax4.set_zlabel('E[W] (Normalizado)')
            ax4.set_title(f'Ocupação vs E[N] vs E[W] (Entropia) - {nome}')
            fig.colorbar(sc4, ax=ax4, label='Entropia (bits)')
            
            # 5. Ocupação vs Tamanho da Fila vs E[W] (colorido por Entropia)
            ax5 = fig.add_subplot(235, projection='3d')
            sc5 = ax5.scatter(
                dados['Ocupacao'], dados['TamanhoFila'], dados['TempoMedioEspera'],
                c=entropia_array, cmap='spring', alpha=0.6, s=20
            )
            ax5.set_xlabel('Ocupação (Normalizada)')
            ax5.set_ylabel('Tamanho da Fila (Normalizado)')
            ax5.set_zlabel('E[W] (Normalizado)')
            ax5.set_title(f'Ocupação vs Tamanho Fila vs E[W] (Entropia) - {nome}')
            fig.colorbar(sc5, ax=ax5, label='Entropia (bits)')
            
            # 6. E[N] vs E[W] vs Tamanho da Fila (colorido por Entropia)
            ax6 = fig.add_subplot(236, projection='3d')
            sc6 = ax6.scatter(
                dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'], dados['TamanhoFila'],
                c=entropia_array, cmap='autumn', alpha=0.6, s=20
            )
            ax6.set_xlabel('E[N] (Normalizado)')
            ax6.set_ylabel('E[W] (Normalizado)')
            ax6.set_zlabel('Tamanho da Fila (Normalizado)')
            ax6.set_title(f'E[N] vs E[W] vs Tamanho Fila (Entropia) - {nome}')
            fig.colorbar(sc6, ax=ax6, label='Entropia (bits)')
            
            plt.tight_layout()
            caminho = f"graficos/analiseGlobal/3d/visualizacao_3d_entropia_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            print(f"Gráficos 3D com entropia salvos: {caminho}")
            
            if self.mostrar_graficos_interativos:
                plt.show()
            else:
                plt.close(fig)

    def gerarMatrizCorrelacao(self):
        """Gera matriz de correlação apenas com colunas numéricas"""
        for nome, dados in self.dadosNormalizados.items():
            # Seleciona apenas colunas numéricas
            colunas_numericas = dados.select_dtypes(include=[np.number]).columns.tolist()
            dados_numericos = dados[colunas_numericas]
            
            fig, ax = plt.subplots(figsize=(10,8))
            sns.heatmap(dados_numericos.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            ax.set_title(f'Matriz de Correlação (Normalizada) - {nome}', fontweight='bold')
            plt.tight_layout()
            caminho = f"graficos/analiseGlobal/correlacao/matriz_correlacao_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Matriz de correlação normalizada salva: {caminho}")

    def gerarGraficosComparativosGlobais(self):
        """Gera gráficos comparativos globais com dados normalizados"""
        # Combina todos os dados normalizados
        todos_dados_normalizados = []
        for nome, dados in self.dadosNormalizados.items():
            dados_com_cenario = dados.copy()
            dados_com_cenario['Cenario'] = nome
            todos_dados_normalizados.append(dados_com_cenario)
        
        dados_combinados = pd.concat(todos_dados_normalizados, ignore_index=True)
        
        # E[N] e E[W] em função do tempo (todos os cenários)
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Comparação Global de E[N] e E[W] em Função do Tempo (Normalizados)', fontweight='bold')
        
        sns.lineplot(x='Tempo', y='NumeroMedioRequisicoes', hue='Cenario', data=dados_combinados, ax=axes[0], alpha=0.7)
        axes[0].set_title('E[N] - Número Médio de Requisições')
        axes[0].set_ylabel('E[N] (Normalizado)')
        
        sns.lineplot(x='Tempo', y='TempoMedioEspera', hue='Cenario', data=dados_combinados, ax=axes[1], alpha=0.7)
        axes[1].set_title('E[W] - Tempo Médio de Espera')
        axes[1].set_xlabel('Tempo (Normalizado)')
        axes[1].set_ylabel('E[W] (Normalizado)')
        
        plt.tight_layout()
        caminho = "graficos/analiseGlobal/comparativos/comparacao_global_en_ew_tempo.png"
        fig.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Gráfico comparativo global E[N]/E[W] vs tempo salvo: {caminho}")
        
        # E[N] e E[W] em função do tamanho da fila (todos os cenários)
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle('Comparação Global de E[N] e E[W] em Função do Tamanho da Fila (Normalizados)', fontweight='bold')
        
        sns.scatterplot(x='TamanhoFila', y='NumeroMedioRequisicoes', hue='Cenario', data=dados_combinados, ax=axes[0], alpha=0.6)
        axes[0].set_title('E[N] vs Tamanho da Fila')
        axes[0].set_xlabel('Tamanho da Fila (Normalizado)')
        axes[0].set_ylabel('E[N] (Normalizado)')
        
        sns.scatterplot(x='TamanhoFila', y='TempoMedioEspera', hue='Cenario', data=dados_combinados, ax=axes[1], alpha=0.6)
        axes[1].set_title('E[W] vs Tamanho da Fila')
        axes[1].set_xlabel('Tamanho da Fila (Normalizado)')
        axes[1].set_ylabel('E[W] (Normalizado)')
        
        plt.tight_layout()
        caminho = "graficos/analiseGlobal/comparativos/comparacao_global_en_ew_fila.png"
        fig.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Gráfico comparativo global E[N]/E[W] vs tamanho da fila salvo: {caminho}")
        
        # Tamanho da fila em função da ocupação (todos os cenários)
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.scatterplot(x='Ocupacao', y='TamanhoFila', hue='Cenario', data=dados_combinados, ax=ax, alpha=0.6)
        ax.set_title('Comparação Global: Tamanho da Fila vs Ocupação (Normalizados)', fontweight='bold')
        ax.set_xlabel('Ocupação (Normalizada)')
        ax.set_ylabel('Tamanho da Fila (Normalizado)')
        plt.tight_layout()
        caminho = "graficos/analiseGlobal/comparativos/comparacao_global_fila_ocupacao.png"
        fig.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Gráfico comparativo global tamanho da fila vs ocupação salvo: {caminho}")

    def executarAnaliseCompleta(self, caminhosArquivos, mu=1.0):
        """Executa a análise completa dos dados de simulação"""
        print("Iniciando análise científica avançada...")
        
        # Carrega dados
        if not self.carregarDados(caminhosArquivos):
            print("Nenhum dado foi carregado.")
            return
        
        # Aplica normalização global
        self.normalizarDadosGlobalmente()
        
        # Calcula e analisa entropia
        self.analisar_entropia_cenarios()
        
        # Gera gráficos de entropia
        self.plotar_entropia_vs_ocupacao()
        self.plotar_distribuicoes_entropia()
        self.plotar_evolucao_entropia_temporal()
        
        # Gera gráficos 3D com entropia
        self.gerarGraficos3DComEntropia()
        
        # Gera matrizes de correlação
        self.gerarMatrizCorrelacao()
        
        # Gera gráficos comparativos globais
        self.gerarGraficosComparativosGlobais()
        
        print("Análise completa concluída.")


def main():
    # Configuração principal
    arquivos = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv',
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    # Cria analisador
    analisador = AnaliseCientificaAvancada(mostrar_graficos_interativos=True)
    
    # Executa análise completa
    analisador.executarAnaliseCompleta(arquivos, mu=1.0)


if __name__ == "__main__":
    main()
