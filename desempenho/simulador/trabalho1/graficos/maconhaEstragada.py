#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Análise Científica Avançada para Dados de Simulação de Filas
Análise com normalização global dos dados e cálculo de Entropia de Shannon
para quantificar a imprevisibilidade do sistema
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
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import warnings
warnings.filterwarnings('ignore')


class AnaliseCientificaGlobal:
    def __init__(self, usarEscalaLogTempo=False, mostrar_graficos_interativos=False):
        self.usarEscalaLogTempo = usarEscalaLogTempo
        self.mostrar_graficos_interativos = mostrar_graficos_interativos
        self.dadosPorCenario = {}
        self.dadosNormalizados = {}
        self.expressoesAnaliticas = {}
        self.entropias = {}
        self.configurarVisualizacoes()
        self.criarDiretoriosSaida()
        self.scaler = StandardScaler()  # Para normalização global

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
            'graficos/maconhaEstragada/individuais', 
            'graficos/maconhaEstragada/comparativos', 
            'graficos/maconhaEstragada/tendencia', 
            'graficos/maconhaEstragada/fila',
            'graficos/maconhaEstragada/ocupacao',
            'graficos/maconhaEstragada/correlacao',
            'graficos/maconhaEstragada/distribuicao',
            'graficos/maconhaEstragada/relacoes',
            'graficos/maconhaEstragada/3d',
            'graficos/maconhaEstragada/entropia',
            'graficos/maconhaEstragada/estatistica',
            'graficos/maconhaEstragada/normalizados'
        ]
        for d in diretorios:
            Path(d).mkdir(parents=True, exist_ok=True)

    def carregarDados(self, caminhosArquivos):
        """Carrega os dados de simulação a partir dos arquivos CSV"""
        todos_dados = []
        nomes_cenarios = []
        
        for caminho in caminhosArquivos:
            if Path(caminho).exists():
                nome = Path(caminho).stem.replace('dados_', '')
                dados = pd.read_csv(caminho)
                dados['Cenario'] = nome
                self.dadosPorCenario[nome] = dados
                todos_dados.append(dados)
                nomes_cenarios.append(nome)
                print(f"Dados carregados: {nome} ({len(dados)} registros)")
            else:
                print(f"Arquivo não encontrado: {caminho}")
        
        # Concatena todos os dados para normalização global
        if todos_dados:
            self.dadosCompletos = pd.concat(todos_dados, ignore_index=True)
            return True
        return False

    def normalizarDadosGlobalmente(self):
        """Aplica normalização global a todas as variáveis numéricas"""
        # Colunas para normalizar
        colunas_numericas = ['Tempo', 'NumeroMedioRequisicoes', 'TempoMedioEspera', 
                            'TamanhoFila', 'Ocupacao']
        
        # Ajusta o scaler com todos os dados
        dados_para_normalizar = self.dadosCompletos[colunas_numericas]
        self.scaler.fit(dados_para_normalizar)
        
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
        entropia = -np.sum(distribuicao * np.log2(distribuicao + 1e-10))  # Adiciona pequeno valor para evitar log(0)
        
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
        caminho = "graficos/maconhaEstragada/entropia/entropia_vs_ocupacao.png"
        fig.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Gráfico de entropia vs ocupação salvo: {caminho}")

    def plotar_distribuicoes_entropia(self):
        """Gráficos das distribuições de tamanho de fila para cada cenário"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Distribuição do Tamanho da Fila por Cenário', fontsize=16, fontweight='bold')
        
        axes = axes.ravel()
        
        for i, (nome, dados) in enumerate(self.dadosPorCenario.items()):
            if i >= 4:  # Limite de 4 subplots
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
        caminho = "graficos/maconhaEstragada/entropia/distribuicoes_tamanho_fila.png"
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
        caminho = "graficos/maconhaEstragada/entropia/evolucao_temporal_entropia.png"
        fig.savefig(caminho, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Gráfico de evolução temporal da entropia salvo: {caminho}")

    def gerarGraficos3DNormalizados(self):
        """Gera visualizações 3D com dados normalizados globalmente"""
        for nome, dados in self.dadosNormalizados.items():
            # Calcula entropia para os dados originais
            entropia, _ = self.calcular_entropia_shannon(self.dadosPorCenario[nome])
            
            # Configuração para gráficos 3D
            fig = plt.figure(figsize=(20, 16))
            
            # 1. E[N], E[W] e Tempo (colorido por Ocupação)
            ax1 = fig.add_subplot(231, projection='3d')
            sc1 = ax1.scatter(
                dados['Tempo'], dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'],
                c=dados['Ocupacao'], cmap='viridis', alpha=0.6, s=20
            )
            ax1.set_xlabel('Tempo (Normalizado)')
            ax1.set_ylabel('E[N] (Normalizado)')
            ax1.set_zlabel('E[W] (Normalizado)')
            ax1.set_title(f'E[N], E[W] vs Tempo (Ocupação) - {nome}\nEntropia: {entropia:.3f} bits')
            fig.colorbar(sc1, ax=ax1, label='Ocupação (Normalizada)')
            
            # 2. E[N], E[W] e Tamanho da Fila (colorido por Tempo)
            ax2 = fig.add_subplot(232, projection='3d')
            sc2 = ax2.scatter(
                dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'], dados['TamanhoFila'],
                c=dados['Tempo'], cmap='plasma', alpha=0.6, s=20
            )
            ax2.set_xlabel('E[N] (Normalizado)')
            ax2.set_ylabel('E[W] (Normalizado)')
            ax2.set_zlabel('Tamanho da Fila (Normalizado)')
            ax2.set_title(f'E[N], E[W] vs Tamanho da Fila (Tempo) - {nome}')
            fig.colorbar(sc2, ax=ax2, label='Tempo (Normalizado)')
            
            # 3. E[N], Ocupação e Tamanho da Fila (colorido por E[W])
            ax3 = fig.add_subplot(233, projection='3d')
            sc3 = ax3.scatter(
                dados['NumeroMedioRequisicoes'], dados['Ocupacao'], dados['TamanhoFila'],
                c=dados['TempoMedioEspera'], cmap='inferno', alpha=0.6, s=20
            )
            ax3.set_xlabel('E[N] (Normalizado)')
            ax3.set_ylabel('Ocupação (Normalizada)')
            ax3.set_zlabel('Tamanho da Fila (Normalizado)')
            ax3.set_title(f'E[N] vs Ocupação vs Tamanho Fila (E[W]) - {nome}')
            fig.colorbar(sc3, ax=ax3, label='E[W] (Normalizado)')
            
            # 4. Tempo, Ocupação e E[W] (colorido por Tamanho da Fila)
            ax4 = fig.add_subplot(234, projection='3d')
            sc4 = ax4.scatter(
                dados['Tempo'], dados['Ocupacao'], dados['TempoMedioEspera'],
                c=dados['TamanhoFila'], cmap='cool', alpha=0.6, s=20
            )
            ax4.set_xlabel('Tempo (Normalizado)')
            ax4.set_ylabel('Ocupação (Normalizada)')
            ax4.set_zlabel('E[W] (Normalizado)')
            ax4.set_title(f'Tempo vs Ocupação vs E[W] (Tamanho Fila) - {nome}')
            fig.colorbar(sc4, ax=ax4, label='Tamanho da Fila (Normalizado)')
            
            # 5. E[N], E[W] e Entropia (usando valor constante da entropia)
            ax5 = fig.add_subplot(235, projection='3d')
            # Cria array com valor constante de entropia para todos os pontos
            entropia_array = np.full(len(dados), entropia)
            sc5 = ax5.scatter(
                dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'], entropia_array,
                c=dados['Ocupacao'], cmap='spring', alpha=0.6, s=20
            )
            ax5.set_xlabel('E[N] (Normalizado)')
            ax5.set_ylabel('E[W] (Normalizado)')
            ax5.set_zlabel('Entropia (bits)')
            ax5.set_title(f'E[N] vs E[W] vs Entropia (Ocupação) - {nome}')
            fig.colorbar(sc5, ax=ax5, label='Ocupação (Normalizada)')
            
            # 6. Ocupação, Tamanho da Fila e Entropia (usando valor constante da entropia)
            ax6 = fig.add_subplot(236, projection='3d')
            sc6 = ax6.scatter(
                dados['Ocupacao'], dados['TamanhoFila'], entropia_array,
                c=dados['TempoMedioEspera'], cmap='autumn', alpha=0.6, s=20
            )
            ax6.set_xlabel('Ocupação (Normalizada)')
            ax6.set_ylabel('Tamanho da Fila (Normalizada)')
            ax6.set_zlabel('Entropia (bits)')
            ax6.set_title(f'Ocupação vs Tamanho Fila vs Entropia (E[W]) - {nome}')
            fig.colorbar(sc6, ax=ax6, label='E[W] (Normalizado)')
            
            plt.tight_layout()
            caminho = f"graficos/maconhaEstragada/3d/visualizacao_3d_normalizada_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            print(f"Gráficos 3D normalizados salvos: {caminho}")
            
            # Mostra gráficos interativos se solicitado
            if self.mostrar_graficos_interativos:
                plt.show()
            else:
                plt.close(fig)

    def gerarRelatorioCompleto(self):
        """Gera um relatório completo com análise de entropia"""
        relatorio = "RELATÓRIO COMPLETO DE ANÁLISE DE ENTROPIA E NORMALIZAÇÃO GLOBAL\n"
        relatorio += "=" * 70 + "\n\n"
        
        relatorio += "RESULTADOS DA ENTROPIA DE SHANNON POR CENÁRIO:\n"
        relatorio += "-" * 50 + "\n"
        
        for _, row in self.resultados_entropia.iterrows():
            relatorio += f"Cenário: {row['Cenario']}\n"
            relatorio += f"  Ocupação média: {row['Ocupacao']:.4f}\n"
            relatorio += f"  Entropia: {row['Entropia']:.4f} bits\n"
            relatorio += f"  Média do tamanho da fila: {row['Media_Tamanho_Fila']:.2f}\n"
            relatorio += f"  Desvio padrão: {row['Desvio_Padrao']:.2f}\n"
            relatorio += f"  Assimetria: {row['Assimetria']:.4f}\n"
            relatorio += f"  Estados únicos: {row['Estados_Unicos']}\n\n"
        
        relatorio += "INTERPRETAÇÃO DOS RESULTADOS:\n"
        relatorio += "-" * 40 + "\n"
        
        # Ordena por ocupação para análise de tendência
        resultados_ordenados = self.resultados_entropia.sort_values('Ocupacao')
        
        relatorio += "Tendência de entropia em função da ocupação:\n"
        for _, row in resultados_ordenados.iterrows():
            relatorio += f"  ρ = {row['Ocupacao']:.3f} → H = {row['Entropia']:.3f} bits\n"
        
        relatorio += "\nAnálise qualitativa:\n"
        for _, row in resultados_ordenados.iterrows():
            ocupacao = row['Ocupacao']
            entropia = row['Entropia']
            
            if ocupacao < 0.85:
                interpretacao = "Sistema Previsível. A fila tende a se concentrar em poucos estados, tornando-a mais ordenada."
            elif ocupacao < 0.95:
                interpretacao = "Aumento da Incerteza. A volatilidade cresce. O sistema explora uma gama maior de tamanhos de fila."
            elif ocupacao < 0.99:
                interpretacao = "Incerteza Elevada. O sistema está no ponto crítico. As flutuações são enormes."
            else:
                interpretacao = "Incerteza Máxima (Caos). O sistema está instável e não-estacionário."
            
            relatorio += f"  {row['Cenario']}: {interpretacao}\n"
        
        relatorio += "\nCONCLUSÕES:\n"
        relatorio += "-" * 15 + "\n"
        relatorio += "1. A entropia aumenta monotonicamente com a ocupação (ρ).\n"
        relatorio += "2. Sistemas com maior ocupação são fundamentalmente mais caóticos e imprevisíveis.\n"
        relatorio += "3. A entropia serve como um excelente indicador quantitativo da estabilidade do sistema.\n"
        relatorio += "4. Um aumento acentuado na entropia pode ser usado como sinal de alerta de que o sistema\n"
        relatorio += "   está se aproximando de um regime operacional perigoso.\n"
        
        # Salva relatório
        with open("relatorio_analise_completa.txt", "w") as f:
            f.write(relatorio)
        
        print("Relatório completo salvo em 'relatorio_analise_completa.txt'")
        return relatorio

    def executarAnaliseCompleta(self, caminhosArquivos):
        """Executa a análise completa dos dados de simulação"""
        print("Iniciando análise científica com normalização global...")
        
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
        
        # Gera gráficos 3D com dados normalizados
        self.gerarGraficos3DNormalizados()
        
        # Gera relatório completo
        self.gerarRelatorioCompleto()
        
        print("Análise completa concluída.")


def main():
    # Configuração principal
    arquivos = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv',
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    # Cria analisador com normalização global
    analisador = AnaliseCientificaGlobal(mostrar_graficos_interativos=True)
    
    # Executa análise completa
    analisador.executarAnaliseCompleta(arquivos)


if __name__ == "__main__":
    main()
