#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Análise e Visualização Interativa de Entropia para Dados de Simulação de Filas.
Gera gráficos 3D com sliders de tempo e salva animações como vídeos MP4.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

class VisualizacaoEntropiaInterativa:
    """
    Classe para carregar dados, calcular entropia e gerar visualizações
    3D interativas e animações da evolução da entropia ao longo do tempo.
    """
    def __init__(self, mostrar_graficos_interativos=True):
        self.mostrar_graficos_interativos = mostrar_graficos_interativos
        self.dadosPorCenario = {}
        self.configurar_visualizacoes()
        self.criar_diretorios_saida()

    def configurar_visualizacoes(self):
        """Configura o estilo visual dos gráficos."""
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['figure.figsize'] = (18, 10)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        # Certifique-se de que o caminho para o ffmpeg está correto para o seu sistema
        # Em sistemas Linux, geralmente é '/usr/bin/ffmpeg'
        plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'

    def criar_diretorios_saida(self):
        """Cria a estrutura de diretórios para armazenar os resultados."""
        Path("videos/entropia").mkdir(parents=True, exist_ok=True)
        Path("graficos/entropia_interativa").mkdir(parents=True, exist_ok=True)

    def carregar_e_preparar_dados(self, caminhos_arquivos, janela_entropia=100):
        """
        Carrega os dados dos arquivos CSV, calcula a entropia para cada cenário
        e armazena os resultados processados.
        """
        print("Iniciando carregamento e preparação de dados...")
        for caminho in caminhos_arquivos:
            if Path(caminho).exists():
                nome_cenario = Path(caminho).stem.replace('dados_', '')
                dados = pd.read_csv(caminho).sort_values('Tempo').reset_index(drop=True)
                
                print(f"  - Calculando entropia para o cenário: {nome_cenario} (Janela: {janela_entropia})")
                df_entropia = self._calcular_entropia(dados, 'TamanhoFila', janela_entropia)
                
                # Une os dados originais com a entropia calculada
                dados_com_entropia = pd.merge_asof(
                    dados,
                    df_entropia,
                    on='Tempo',
                    direction='nearest'
                ).dropna() # Remove linhas onde a entropia não pôde ser calculada
                
                self.dadosPorCenario[nome_cenario] = dados_com_entropia
                print(f"  - Cenário '{nome_cenario}' carregado com {len(dados_com_entropia)} registros.")
            else:
                print(f"AVISO: Arquivo não encontrado: {caminho}")

    def _calcular_entropia(self, dados, coluna, janela):
        """
        [CORRIGIDO] Calcula a entropia de Shannon em uma janela deslizante.
        H = -Σ p(x) * log2(p(x))
        """
        if len(dados) < janela:
            return pd.DataFrame({'Tempo': [], 'Entropia': []})

        def calculate_shannon_entropy(window_series):
            """Função aplicada a cada janela para calcular a entropia."""
            # `window_series` é uma pd.Series com os dados da janela atual
            counts = window_series.value_counts(normalize=True)
            if counts.empty:
                return np.nan
            # Fórmula da Entropia de Shannon
            entropy = -np.sum(counts * np.log2(counts + 1e-12)) # Adiciona epsilon para evitar log(0)
            return entropy

        # Aplica a função que retorna um único valor (float) para cada janela
        entropia_series = (
            dados[coluna]
            .rolling(window=janela, min_periods=janela) # Garante janelas completas
            .apply(calculate_shannon_entropy, raw=False) # raw=False para passar a Series
            .rename('Entropia')
        )
        
        # Cria o DataFrame de resultado, removendo NaNs iniciais
        df_entropia = pd.DataFrame(entropia_series).dropna()
        # Adiciona a coluna 'Tempo' correspondente aos índices válidos
        df_entropia['Tempo'] = dados.loc[df_entropia.index, 'Tempo']
        
        return df_entropia

    def gerar_grafico_entropia_3d_interativo(self, nome_cenario):
        """
        Gera uma figura 3D interativa com um slider de tempo para visualizar
        a evolução da entropia e outras métricas.
        """
        if nome_cenario not in self.dadosPorCenario or self.dadosPorCenario[nome_cenario].empty:
            print(f"Erro: Dados insuficientes para o cenário '{nome_cenario}'.")
            return

        dados = self.dadosPorCenario[nome_cenario]
        
        fig = plt.figure(figsize=(22, 12))
        fig.suptitle(f'Análise de Entropia 3D Interativa - Cenário: {nome_cenario.upper()}', fontsize=18, fontweight='bold')
        
        # Define os subplots 3D
        ax1 = fig.add_subplot(1, 3, 1, projection='3d')
        ax2 = fig.add_subplot(1, 3, 2, projection='3d')
        ax3 = fig.add_subplot(1, 3, 3, projection='3d')
        
        fig.subplots_adjust(bottom=0.2)
        
        # --- Configuração dos Eixos ---
        axes = [ax1, ax2, ax3]
        labels = [
            ('TamanhoFila', 'Ocupacao', 'Entropia'),
            ('NumeroMedioRequisicoes', 'TempoMedioEspera', 'Entropia'),
            ('Tempo', 'TamanhoFila', 'Entropia')
        ]
        titles = [
            'Entropia vs. Tamanho da Fila e Ocupação',
            'Entropia vs. E[N] e E[W]',
            'Evolução da Entropia e Fila no Tempo'
        ]
        
        for ax, (xlabel, ylabel, zlabel), title in zip(axes, labels, titles):
            ax.set_xlabel(xlabel, fontweight='bold')
            ax.set_ylabel(ylabel, fontweight='bold')
            ax.set_zlabel(zlabel, fontweight='bold')
            ax.set_title(title, pad=20)

        # Normaliza a Entropia para o mapeamento de cores
        norm = plt.Normalize(vmin=dados['Entropia'].min(), vmax=dados['Entropia'].max())
        cmap = plt.get_cmap('viridis')

        # --- Criação do Slider ---
        ax_slider = fig.add_axes([0.2, 0.05, 0.65, 0.03])
        tempo_min, tempo_max = int(dados['Tempo'].min()), int(dados['Tempo'].max())
        
        slider = Slider(
            ax=ax_slider,
            label='Tempo',
            valmin=tempo_min,
            valmax=tempo_max,
            valinit=tempo_min,
            valstep=max(1, (tempo_max - tempo_min) // 200) # Define 200 passos
        )

        # --- Função de Atualização para o Slider ---
        scatter_plots = []
        for ax, (x_col, y_col, z_col) in zip(axes, labels):
            sc = ax.scatter([], [], [], c=[], cmap=cmap, norm=norm, s=20, alpha=0.7)
            scatter_plots.append(sc)
        
        # Adiciona a colorbar
        cbar = fig.colorbar(scatter_plots[0], ax=axes, shrink=0.6, pad=0.1)
        cbar.set_label('Nível de Entropia', fontweight='bold')

        def update(val):
            tempo_atual = slider.val
            dados_filtrados = dados[dados['Tempo'] <= tempo_atual]
            
            if dados_filtrados.empty: return
            
            for sc, (x_col, y_col, z_col) in zip(scatter_plots, labels):
                sc._offsets3d = (dados_filtrados[x_col], dados_filtrados[y_col], dados_filtrados[z_col])
                sc.set_array(dados_filtrados['Entropia'])
            
            fig.canvas.draw_idle()

        slider.on_changed(update)
        update(tempo_min) # Inicializa o gráfico

        if self.mostrar_graficos_interativos:
            plt.show()

    def gerar_animacao_entropia_3d(self, nome_cenario, frames=200):
        """
        Gera uma animação MP4 da evolução dos gráficos 3D de entropia.
        """
        if nome_cenario not in self.dadosPorCenario or self.dadosPorCenario[nome_cenario].empty:
            print(f"Erro: Dados insuficientes para animar o cenário '{nome_cenario}'.")
            return

        dados = self.dadosPorCenario[nome_cenario]
        caminho_video = f"videos/entropia/animacao_entropia_{nome_cenario}.mp4"
        
        print(f"Iniciando geração de vídeo para '{nome_cenario}'... (Isso pode levar alguns minutos)")

        fig = plt.figure(figsize=(22, 12))
        fig.suptitle(f'Animação da Entropia 3D - Cenário: {nome_cenario.upper()}', fontsize=18, fontweight='bold')
        
        ax1 = fig.add_subplot(1, 3, 1, projection='3d')
        ax2 = fig.add_subplot(1, 3, 2, projection='3d')
        ax3 = fig.add_subplot(1, 3, 3, projection='3d')

        axes = [ax1, ax2, ax3]
        labels = [
            ('TamanhoFila', 'Ocupacao', 'Entropia'),
            ('NumeroMedioRequisicoes', 'TempoMedioEspera', 'Entropia'),
            ('Tempo', 'TamanhoFila', 'Entropia')
        ]
        titles = [
            'Entropia vs. Tamanho da Fila e Ocupação',
            'Entropia vs. E[N] e E[W]',
            'Evolução da Entropia e Fila no Tempo'
        ]
        
        scatter_plots = []
        norm = plt.Normalize(vmin=dados['Entropia'].min(), vmax=dados['Entropia'].max())
        cmap = plt.get_cmap('viridis')
        
        for ax, (xlabel, ylabel, zlabel), title in zip(axes, labels, titles):
            ax.set_xlabel(xlabel, fontweight='bold')
            ax.set_ylabel(ylabel, fontweight='bold')
            ax.set_zlabel(zlabel, fontweight='bold')
            ax.set_title(title, pad=20)
            sc = ax.scatter([], [], [], c=[], cmap=cmap, norm=norm, s=20, alpha=0.7)
            scatter_plots.append(sc)
            ax.set_xlim(dados[xlabel].min(), dados[xlabel].max())
            ax.set_ylim(dados[ylabel].min(), dados[ylabel].max())
            ax.set_zlim(dados[zlabel].min(), dados[zlabel].max())
            
        cbar = fig.colorbar(scatter_plots[0], ax=axes, shrink=0.6, pad=0.1)
        cbar.set_label('Nível de Entropia', fontweight='bold')
        
        time_text = fig.text(0.5, 0.05, '', ha='center', fontsize=14, fontweight='bold')

        def animate(i):
            tempo_max = dados['Tempo'].max()
            tempo_atual = (i / frames) * tempo_max
            dados_filtrados = dados[dados['Tempo'] <= tempo_atual]

            if dados_filtrados.empty: return scatter_plots
            
            for sc, (x_col, y_col, z_col) in zip(scatter_plots, labels):
                sc._offsets3d = (dados_filtrados[x_col], dados_filtrados[y_col], dados_filtrados[z_col])
                sc.set_array(dados_filtrados['Entropia'])

            time_text.set_text(f'Tempo: {int(tempo_atual)}')
            
            for ax in axes:
                ax.view_init(elev=30., azim=i * 0.5)

            return scatter_plots

        anim = FuncAnimation(fig, animate, frames=frames, interval=50, blit=False)
        writer = FFMpegWriter(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        
        anim.save(caminho_video, writer=writer)
        print(f"Vídeo salvo com sucesso em: {caminho_video}")
        plt.close(fig)

def main():
    """
    Função principal para executar a análise e visualização.
    """
    arquivos_csv = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv',
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    analisador = VisualizacaoEntropiaInterativa(mostrar_graficos_interativos=True)
    
    analisador.carregar_e_preparar_dados(arquivos_csv)
    
    for cenario in analisador.dadosPorCenario.keys():
        print(f"\n--- Processando Cenário: {cenario.upper()} ---")
        
        # Gera o gráfico interativo com slider
        analisador.gerar_grafico_entropia_3d_interativo(cenario)
        
        # Gera a animação em MP4
        analisador.gerar_animacao_entropia_3d(cenario, frames=200)

if __name__ == "__main__":
    main()
