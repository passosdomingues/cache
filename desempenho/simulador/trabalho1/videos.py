#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Análise Científica Avançada para Dados de Simulação de Filas
Com gráficos interativos com sliders e geração de vídeos MP4
Inclui análise estatística avançada, entropia e visualizações 3D
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from scipy.optimize import curve_fit
from scipy import stats
from scipy.special import boxcox, inv_boxcox
from statsmodels.graphics.gofplots import qqplot
import warnings
warnings.filterwarnings('ignore')


class AnaliseInterativaCompleta:
    def __init__(self, usarEscalaLogTempo=False, mostrar_graficos_interativos=False):
        self.usarEscalaLogTempo = usarEscalaLogTempo
        self.mostrar_graficos_interativos = mostrar_graficos_interativos
        self.dadosPorCenario = {}
        self.expressoesAnaliticas = {}
        self.configurarVisualizacoes()
        self.criarDiretoriosSaida()

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
            'graficos/interativos', 
            'videos',
            'graficos/interativos/individuais', 
            'graficos/interativos/comparativos', 
            'graficos/interativos/tendencia', 
            'graficos/interativos/fila',
            'graficos/interativos/ocupacao',
            'graficos/interativos/correlacao',
            'graficos/interativos/distribuicao',
            'graficos/interativos/relacoes',
            'graficos/interativos/3d',
            'graficos/interativos/entropia',
            'graficos/interativos/estatistica',
            'graficos/interativos/transformacoes'
        ]
        for d in diretorios:
            Path(d).mkdir(parents=True, exist_ok=True)

    def carregarDados(self, caminhosArquivos):
        """Carrega os dados de simulação a partir dos arquivos CSV"""
        for caminho in caminhosArquivos:
            if Path(caminho).exists():
                nome = Path(caminho).stem.replace('dados_', '')
                self.dadosPorCenario[nome] = pd.read_csv(caminho)
                print(f"Dados carregados: {nome} ({len(self.dadosPorCenario[nome])} registros)")
            else:
                print(f"Arquivo não encontrado: {caminho}")

    def calcular_entropia(self, dados, coluna='TamanhoFila', janela=100):
        """
        Calcula a entropia de Shannon para uma distribuição de estados em janela deslizante
        usando a fórmula: H = -Σ p(x) * log2(p(x))
        """
        entropia = []
        tempo_entropia = []
        
        for i in range(janela, len(dados)):
            janela_dados = dados[coluna].iloc[i-janela:i]
            contagem = janela_dados.value_counts(normalize=True)
            H = -np.sum(contagem * np.log2(contagem + 1e-10))  # Adiciona pequeno valor para evitar log(0)
            entropia.append(H)
            tempo_entropia.append(dados['Tempo'].iloc[i])
        
        return pd.DataFrame({'Tempo': tempo_entropia, 'Entropia': entropia})

    # ---------- ANÁLISE ESTATÍSTICA AVANÇADA ----------
    class AnaliseEstatistica:
        """Classe interna para análise estatística robusta dos dados de fila"""
        
        def __init__(self, dados, nome_cenario, remover_transiente=True, percentual_transiente=0.2):
            self.dados_originais = dados
            self.nome_cenario = nome_cenario
            self.remover_transiente = remover_transiente
            self.percentual_transiente = percentual_transiente
            self.dados_estacionarios = None
            self.dados_transformados = {}
            self.resultados = {}
            self.lambda_boxcox = None

        def remover_transiente_inicial(self):
            """Remove a porção inicial dos dados (transiente) para análise do estado estacionário"""
            n_remover = int(self.percentual_transiente * len(self.dados_originais))
            self.dados_estacionarios = self.dados_originais.iloc[n_remover:].copy()
            print(f"Removidas {n_remover} amostras iniciais (transiente)")

        def calcular_estatisticas_descritivas(self, dados, nome):
            """Calcula estatísticas descritivas robustas para os dados"""
            return {
                'media': dados.mean(),
                'mediana': dados.median(),
                'desvio_padrao': dados.std(),
                'assimetria': dados.skew(),
                'curtose': dados.kurtosis(),
                'variancia': dados.var(),
                'minimo': dados.min(),
                'maximo': dados.max(),
                'percentil_5': dados.quantile(0.05),
                'percentil_25': dados.quantile(0.25),
                'percentil_75': dados.quantile(0.75),
                'percentil_95': dados.quantile(0.95),
                'percentil_99': dados.quantile(0.99)
            }

        def aplicar_transformacoes(self):
            """Aplica transformações para normalizar dados assimétricos"""
            dados = self.dados_estacionarios['TamanhoFila']
            
            # Transformação logarítmica (adiciona 1 para evitar log(0))
            self.dados_transformados['log'] = np.log1p(dados)
            
            # Transformação raiz quadrada
            self.dados_transformados['sqrt'] = np.sqrt(dados)
            
            # Transformação Box-Cox (requer dados positivos)
            if (dados > 0).all():
                self.dados_transformados['boxcox'], self.lambda_boxcox = stats.boxcox(dados)
            else:
                # Se há zeros, adiciona 1 para tornar todos positivos
                self.dados_transformados['boxcox'], self.lambda_boxcox = stats.boxcox(dados + 1)
            
            # Transformação Yeo-Johnson (funciona com dados negativos e zeros)
            self.dados_transformados['yeojohnson'], self.lambda_yeojohnson = stats.yeojohnson(dados)

        def testar_normalidade(self, dados, nome):
            """Executa testes de normalidade para avaliar distribuição dos dados"""
            # Teste de Kolmogorov-Smirnov
            stat_ks, p_ks = stats.kstest(dados, 'norm', args=(np.mean(dados), np.std(dados)))
            
            # Teste de Shapiro-Wilk (para amostras menores)
            stat_sw, p_sw = stats.shapiro(dados)
            
            # Teste de Anderson-Darling
            result_ad = stats.anderson(dados, dist='norm')
            stat_ad = result_ad.statistic
            # Obtém o valor crítico para α=0.05
            critical_val = result_ad.critical_values[2]  # Índice 2 corresponde a α=0.05
            
            return {
                'ks_statistic': stat_ks, 'ks_pvalue': p_ks,
                'sw_statistic': stat_sw, 'sw_pvalue': p_sw,
                'ad_statistic': stat_ad, 'ad_critical_5pct': critical_val,
                'eh_normal': p_sw > 0.05 and stat_ad < critical_val
            }

        def executar_analise_completa(self):
            """Executa la análisis estadístico completo"""
            if self.remover_transiente:
                self.remover_transiente_inicial()
            else:
                self.dados_estacionarios = self.dados_originais
            
            # Estatísticas descritivas para dados originais
            self.resultados['estatisticas_originais'] = self.calcular_estatisticas_descritivas(
                self.dados_estacionarios['TamanhoFila'], 'Original'
            )
            
            # Aplica transformaciones
            self.aplicar_transformacoes()
            
            # Testa normalidade para dados originais e transformados
            self.resultados['normalidade_original'] = self.testar_normalidade(
                self.dados_estacionarios['TamanhoFila'], 'Original'
            )
            
            for nome_transf, dados_transf in self.dados_transformados.items():
                self.resultados[f'normalidade_{nome_transf}'] = self.testar_normalidade(
                    dados_transf, nome_transf.capitalize()
                )
                self.resultados[f'estatisticas_{nome_transf}'] = self.calcular_estatisticas_descritivas(
                    pd.Series(dados_transf), nome_transf.capitalize()
                )
            
            return self.resultados

        def gerar_relatorio_estatistico(self):
            """Gera um relatório textual com os resultados estatísticos"""
            relatorio = f"RELATÓRIO ESTATÍSTICO - {self.nome_cenario.upper()}\n"
            relatorio += "=" * 60 + "\n\n"
            
            # Estatísticas descritivas
            relatorio += "ESTATÍSTICAS DESCRITIVAS (Tamanho da Fila):\n"
            relatorio += "-" * 50 + "\n"
            stats = self.resultados['estatisticas_originais']
            relatorio += f"Média: {stats['media']:.4f}\n"
            relatorio += f"Mediana: {stats['mediana']:.4f}\n"
            relatorio += f"Desvio Padrão: {stats['desvio_padrao']:.4f}\n"
            relatorio += f"Assimetria: {stats['assimetria']:.4f}\n"
            relatorio += f"Curtose: {stats['curtose']:.4f}\n"
            relatorio += f"Percentil 95%: {stats['percentil_95']:.4f}\n"
            relatorio += f"Percentil 99%: {stats['percentil_99']:.4f}\n\n"
            
            # Testes de normalidade
            relatorio += "TESTES DE NORMALIDADE (Kolmogorov-Smirnov, Shapiro-Wilk, Anderson-Darling):\n"
            relatorio += "-" * 80 + "\n"
            
            for nome, teste in [(k, v) for k, v in self.resultados.items() if k.startswith('normalidade_')]:
                nome_display = nome.replace('normalidade_', '').capitalize()
                relatorio += f"{nome_display}:\n"
                relatorio += f"  Kolmogorov-Smirnov: estatística={teste['ks_statistic']:.4f}, p-value={teste['ks_pvalue']:.4f}\n"
                relatorio += f"  Shapiro-Wilk: estatística={teste['sw_statistic']:.4f}, p-value={teste['sw_pvalue']:.4f}\n"
                relatorio += f"  Anderson-Darling: estatística={teste['ad_statistic']:.4f}, crítico(5%)={teste['ad_critical_5pct']:.4f}\n"
                relatorio += f"  Distribuição Normal: {'SIM' if teste['eh_normal'] else 'NÃO'}\n\n"
            
            # Recomendações baseadas na análise
            relatorio += "RECOMENDAÇÕES ESTATÍSTICAS:\n"
            relatorio += "-" * 40 + "\n"
            
            assimetria = stats['assimetria']
            if abs(assimetria) < 0.5:
                relatorio += "• Os dados apresentam assimetria moderada. Transformações podem não ser necessárias.\n"
            elif 0.5 <= abs(assimetria) < 1.0:
                relatorio += "• Os dados apresentam assimetria significativa. Considere transformações suaves (raiz quadrada).\n"
            else:
                relatorio += "• Os dados apresentam assimetria forte. Transformações logarítmicas ou Box-Cox são recomendadas.\n"
            
            # Identifica a melhor transformação
            melhor_transf = None
            menor_assimetria = float('inf')
            for nome, stats_transf in [(k, v) for k, v in self.resultados.items() if k.startswith('estatisticas_')]:
                assimetria_transf = abs(stats_transf['assimetria'])
                if assimetria_transf < menor_assimetria:
                    menor_assimetria = assimetria_transf
                    melhor_transf = nome.replace('estatisticas_', '')
            
            relatorio += f"• Melhor transformação para normalidade: {melhor_transf.capitalize()}\n"
            
            return relatorio

        def gerar_graficos_estatisticos(self, diretorio_saida):
            """Gera gráficos estatísticos para análise de distribuição"""
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle(f'Análise Estatística - {self.nome_cenario}', fontsize=16, fontweight='bold')
            
            # Dados originais
            dados_orig = self.dados_estacionarios['TamanhoFila']
            
            # Histograma e KDE
            sns.histplot(dados_orig, kde=True, ax=axes[0, 0], color='skyblue')
            axes[0, 0].set_title('Distribuição do Tamanho da Fila')
            axes[0, 0].set_xlabel('Tamanho da Fila')
            axes[0, 0].set_ylabel('Densidade')
            
            # QQ-Plot
            qqplot(dados_orig, line='s', ax=axes[0, 1])
            axes[0, 1].set_title('Q-Q Plot (Distribuição Normal)')
            
            # Boxplot
            sns.boxplot(y=dados_orig, ax=axes[0, 2])
            axes[0, 2].set_title('Boxplot do Tamanho da Fila')
            axes[0, 2].set_ylabel('Tamanho da Fila')
            
            # Gráfico de transformações
            transformacoes = list(self.dados_transformados.keys())[:3]  # Mostra as 3 primeiras transformações
            cores = ['red', 'green', 'blue']
            
            for i, (transf, cor) in enumerate(zip(transformacoes, cores)):
                dados_transf = self.dados_transformados[transf]
                sns.histplot(dados_transf, kde=True, ax=axes[1, i], color=cor, alpha=0.7, label=transf)
                axes[1, i].set_title(f'Distribuição ({transf.upper()})')
                axes[1, i].set_xlabel(f'Tamanho da Fila ({transf})')
                axes[1, i].set_ylabel('Densidade')
            
            plt.tight_layout()
            caminho = f"{diretorio_saida}/analise_estatistica_{self.nome_cenario}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            # Gráfico de comparação de assimetria
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            assimetrias = [self.resultados['estatisticas_originais']['assimetria']]
            nomes = ['Original']
            
            for transf in transformacoes:
                assimetrias.append(self.resultados[f'estatisticas_{transf}']['assimetria'])
                nomes.append(transf.upper())
            
            ax2.bar(nomes, assimetrias, color=['skyblue', 'lightgreen', 'lightcoral', 'gold'])
            ax2.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='Simetria perfeita')
            ax2.set_title('Coeficiente de Assimetria por Transformação')
            ax2.set_ylabel('Coeficiente de Assimetria')
            ax2.legend()
            
            caminho2 = f"{diretorio_saida}/comparacao_assimetria_{self.nome_cenario}.png"
            fig2.savefig(caminho2, dpi=300, bbox_inches='tight')
            plt.close(fig2)

    def executar_analise_estatistica_avancada(self):
        """Executa análise estatística avançada para todos os cenários"""
        print("Iniciando análise estatística avançada...")
        
        for nome, dados in self.dadosPorCenario.items():
            print(f"Analisando estatisticamente cenário: {nome}")
            
            analise = self.AnaliseEstatistica(dados, nome)
            resultados = analise.executar_analise_completa()
            
            # Gera relatório textual
            relatorio = analise.gerar_relatorio_estatistico()
            with open(f"relatorio_estatistico_{nome}.txt", "w") as f:
                f.write(relatorio)
            print(f"Relatório estatístico salvo: relatorio_estatistico_{nome}.txt")
            
            # Gera gráficos estatísticos
            analise.gerar_graficos_estatisticos("graficos/interativos/estatistica")
            print(f"Gráficos estatísticos salvos para {nome}")

    # ---------- GRÁFICOS 3D ----------
    def gerarGraficos3D(self):
        """Gera visualizações 3D interativas dos dados de simulação"""
        for nome, dados in self.dadosPorCenario.items():
            if 'Entropia' not in dados.columns:
                # Calcula entropia se ainda não existir
                df_entropia = self.calcular_entropia(dados, 'TamanhoFila', 100)
                dados = pd.merge_asof(
                    dados.sort_values('Tempo'), 
                    df_entropia.sort_values('Tempo'), 
                    on='Tempo', 
                    direction='nearest'
                )
            
            # Configuração para gráficos 3D
            fig = plt.figure(figsize=(20, 16))
            
            # 1. E[N], E[W] e Tempo (colorido por Entropia)
            ax1 = fig.add_subplot(231, projection='3d')
            sc1 = ax1.scatter(
                dados['Tempo'], dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'],
                c=dados['Entropia'], cmap='viridis', alpha=0.6, s=20
            )
            ax1.set_xlabel('Tempo')
            ax1.set_ylabel('E[N]')
            ax1.set_zlabel('E[W]')
            ax1.set_title(f'E[N], E[W] vs Tempo (Entropia) - {nome}')
            fig.colorbar(sc1, ax=ax1, label='Entropia')
            
            # 2. E[N], E[W] e Tamanho da Fila (colorido por Entropia)
            ax2 = fig.add_subplot(232, projection='3d')
            sc2 = ax2.scatter(
                dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'], dados['TamanhoFila'],
                c=dados['Entropia'], cmap='plasma', alpha=0.6, s=20
            )
            ax2.set_xlabel('E[N]')
            ax2.set_ylabel('E[W]')
            ax2.set_zlabel('Tamanho da Fila')
            ax2.set_title(f'E[N], E[W] vs Tamanho da Fila (Entropia) - {nome}')
            fig.colorbar(sc2, ax=ax2, label='Entropia')
            
            # 3. E[N], E[W] e Ocupação (colorido por Entropia)
            ax3 = fig.add_subplot(233, projection='3d')
            sc3 = ax3.scatter(
                dados['NumeroMedioRequisicoes'], dados['TempoMedioEspera'], dados['Ocupacao'],
                c=dados['Entropia'], cmap='inferno', alpha=0.6, s=20
            )
            ax3.set_xlabel('E[N]')
            ax3.set_ylabel('E[W]')
            ax3.set_zlabel('Ocupação')
            ax3.set_title(f'E[N], E[W] vs Ocupação (Entropia) - {nome}')
            fig.colorbar(sc3, ax=ax3, label='Entropia')
            
            # 4. Entropia, Tamanho da Fila e Tempo (colorido por Ocupação)
            ax4 = fig.add_subplot(234, projection='3d')
            sc4 = ax4.scatter(
                dados['Tempo'], dados['TamanhoFila'], dados['Entropia'],
                c=dados['Ocupacao'], cmap='cool', alpha=0.6, s=20
            )
            ax4.set_xlabel('Tempo')
            ax4.set_ylabel('Tamanho da Fila')
            ax4.set_zlabel('Entropia')
            ax4.set_title(f'Entropia vs Tamanho da Fila vs Tempo (Ocupação) - {nome}')
            fig.colorbar(sc4, ax=ax4, label='Ocupação')
            
            # 5. E[N], Ocupação e Entropia (colorido por Tempo)
            ax5 = fig.add_subplot(235, projection='3d')
            sc5 = ax5.scatter(
                dados['NumeroMedioRequisicoes'], dados['Ocupacao'], dados['Entropia'],
                c=dados['Tempo'], cmap='spring', alpha=0.6, s=20
            )
            ax5.set_xlabel('E[N]')
            ax5.set_ylabel('Ocupação')
            ax5.set_zlabel('Entropia')
            ax5.set_title(f'E[N] vs Ocupação vs Entropia (Tempo) - {nome}')
            fig.colorbar(sc5, ax=ax5, label='Tempo')
            
            # 6. E[W], Ocupação e Entropia (colorido por Tamanho da Fila)
            ax6 = fig.add_subplot(236, projection='3d')
            sc6 = ax6.scatter(
                dados['TempoMedioEspera'], dados['Ocupacao'], dados['Entropia'],
                c=dados['TamanhoFila'], cmap='autumn', alpha=0.6, s=20
            )
            ax6.set_xlabel('E[W]')
            ax6.set_ylabel('Ocupação')
            ax6.set_zlabel('Entropia')
            ax6.set_title(f'E[W] vs Ocupação vs Entropia (Tamanho Fila) - {nome}')
            fig.colorbar(sc6, ax=ax6, label='Tamanho da Fila')
            
            plt.tight_layout()
            caminho = f"graficos/interativos/3d/visualizacao_3d_completa_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            print(f"Gráficos 3D salvos: {caminho}")
            
            # Mostra gráficos interativos se solicitado
            if self.mostrar_graficos_interativos:
                plt.show()
            else:
                plt.close(fig)

    # ---------- GRÁFICOS INTERATIVOS COM SLIDERS ----------
    def criar_grafico_EN_EW_interativo(self, nome, dados):
        """Cria gráfico de E[N] e E[W] ao longo do tempo com slider"""
        fig, ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.25)
        
        # Plot inicial (vazio)
        line_EN, = ax.plot([], [], 'b-', alpha=0.7, linewidth=2, label='E[N]')
        line_EW, = ax.plot([], [], 'r-', alpha=0.7, linewidth=2, label='E[W]')
        point_EN = ax.scatter([], [], color='blue', s=100, zorder=5)
        point_EW = ax.scatter([], [], color='red', s=100, zorder=5)
        
        ax.set_xlabel('Tempo')
        ax.set_ylabel('Valor')
        ax.set_title(f'E[N] e E[W] ao longo do Tempo - {nome}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(dados['Tempo'].min(), dados['Tempo'].max())
        ax.set_ylim(min(dados['NumeroMedioRequisicoes'].min(), dados['TempoMedioEspera'].min()) - 0.1,
                   max(dados['NumeroMedioRequisicoes'].max(), dados['TempoMedioEspera'].max()) + 0.1)
        
        # Adicionar slider
        ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
        slider = Slider(ax_slider, 'Tempo', dados['Tempo'].min(), dados['Tempo'].max(), 
                       valinit=dados['Tempo'].min(), valfmt='%1.2f')
        
        def update(val):
            tempo = slider.val
            idx = (dados['Tempo'] - tempo).abs().argmin()
            
            # Atualizar linhas até o ponto atual
            line_EN.set_data(dados['Tempo'].iloc[:idx+1], dados['NumeroMedioRequisicoes'].iloc[:idx+1])
            line_EW.set_data(dados['Tempo'].iloc[:idx+1], dados['TempoMedioEspera'].iloc[:idx+1])
            
            # Atualizar pontos atuais
            point_EN.set_offsets(np.c_[dados['Tempo'].iloc[idx], dados['NumeroMedioRequisicoes'].iloc[idx]])
            point_EW.set_offsets(np.c_[dados['Tempo'].iloc[idx], dados['TempoMedioEspera'].iloc[idx]])
            
            fig.canvas.draw_idle()
        
        slider.on_changed(update)
        
        # Inicializar
        update(dados['Tempo'].min())
        
        # Botão para reset
        resetax = plt.axes([0.8, 0.1, 0.1, 0.03])
        button = Button(resetax, 'Reset', hovercolor='0.975')
        
        def reset(event):
            slider.reset()
        button.on_clicked(reset)
        
        plt.savefig(f'graficos/interativos/EN_EW_tempo_interativo_{nome}.png', dpi=300, bbox_inches='tight')
        
        if self.mostrar_graficos_interativos:
            plt.show()
        else:
            plt.close(fig)
            
        return fig, slider

    def criar_grafico_fila_ocupacao_interativo(self, nome, dados):
        """Cria gráfico de Tamanho da Fila vs Ocupação com slider"""
        fig, ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.25)
        
        # Plot inicial (vazio)
        scat = ax.scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        point = ax.scatter([], [], color='red', s=100, zorder=5)
        
        ax.set_xlabel('Ocupação')
        ax.set_ylabel('Tamanho da Fila')
        ax.set_title(f'Tamanho da Fila vs Ocupação - {nome}')
        ax.grid(True, alpha=0.3)
        
        # Adicionar slider
        ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
        slider = Slider(ax_slider, 'Tempo', dados['Tempo'].min(), dados['Tempo'].max(), 
                       valinit=dados['Tempo'].min(), valfmt='%1.2f')
        
        def update(val):
            tempo = slider.val
            idx = (dados['Tempo'] - tempo).abs().argmin()
            
            # Dados até o tempo atual
            dados_ate_agora = dados.iloc[:idx+1]
            
            # Atualizar scatter plot
            scat.set_offsets(np.c_[dados_ate_agora['Ocupacao'], dados_ate_agora['TamanhoFila']])
            scat.set_array(dados_ate_agora['Tempo'].values)
            
            # Atualizar ponto atual
            point.set_offsets(np.c_[dados_ate_agora['Ocupacao'].iloc[-1], dados_ate_agora['TamanhoFila'].iloc[-1]])
            
            # Atualizar limites
            ax.set_xlim(dados['Ocupacao'].min() - 0.01, dados['Ocupacao'].max() + 0.01)
            ax.set_ylim(dados['TamanhoFila'].min() - 1, dados['TamanhoFila'].max() + 1)
            
            fig.canvas.draw_idle()
        
        slider.on_changed(update)
        
        # Inicializar
        update(dados['Tempo'].min())
        
        # Adicionar barra de cores
        plt.colorbar(scat, ax=ax, label='Tempo')
        
        # Botão para reset
        resetax = plt.axes([0.8, 0.1, 0.1, 0.03])
        button = Button(resetax, 'Reset', hovercolor='0.975')
        
        def reset(event):
            slider.reset()
        button.on_clicked(reset)
        
        plt.savefig(f'graficos/interativos/fila_ocupacao_interativo_{nome}.png', dpi=300, bbox_inches='tight')
        
        if self.mostrar_graficos_interativos:
            plt.show()
        else:
            plt.close(fig)
            
        return fig, slider

    def criar_grafico_relacoes_interativo(self, nome, dados):
        """Cria gráfico de relações entre variáveis com slider"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        plt.subplots_adjust(bottom=0.25)
        
        # Plot inicial (vazio)
        scat1 = axes[0, 0].scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        scat2 = axes[0, 1].scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        scat3 = axes[1, 0].scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        scat4 = axes[1, 1].scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        
        point1 = axes[0, 0].scatter([], [], color='red', s=100, zorder=5)
        point2 = axes[0, 1].scatter([], [], color='red', s=100, zorder=5)
        point3 = axes[1, 0].scatter([], [], color='red', s=100, zorder=5)
        point4 = axes[1, 1].scatter([], [], color='red', s=100, zorder=5)
        
        axes[0, 0].set_xlabel('Ocupação')
        axes[0, 0].set_ylabel('E[N]')
        axes[0, 0].set_title('E[N] vs Ocupação')
        
        axes[0, 1].set_xlabel('Ocupação')
        axes[0, 1].set_ylabel('E[W]')
        axes[0, 1].set_title('E[W] vs Ocupação')
        
        axes[1, 0].set_xlabel('Tamanho da Fila')
        axes[1, 0].set_ylabel('E[N]')
        axes[1, 0].set_title('E[N] vs Tamanho da Fila')
        
        axes[1, 1].set_xlabel('Tamanho da Fila')
        axes[1, 1].set_ylabel('E[W]')
        axes[1, 1].set_title('E[W] vs Tamanho da Fila')
        
        for ax in axes.flat:
            ax.grid(True, alpha=0.3)
        
        # Adicionar slider
        ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
        slider = Slider(ax_slider, 'Tempo', dados['Tempo'].min(), dados['Tempo'].max(), 
                       valinit=dados['Tempo'].min(), valfmt='%1.2f')
        
        def update(val):
            tempo = slider.val
            idx = (dados['Tempo'] - tempo).abs().argmin()
            
            # Dados até o tempo atual
            dados_ate_agora = dados.iloc[:idx+1]
            
            # Atualizar scatter plots
            scat1.set_offsets(np.c_[dados_ate_agora['Ocupacao'], dados_ate_agora['NumeroMedioRequisicoes']])
            scat1.set_array(dados_ate_agora['Tempo'].values)
            
            scat2.set_offsets(np.c_[dados_ate_agora['Ocupacao'], dados_ate_agora['TempoMedioEspera']])
            scat2.set_array(dados_ate_agora['Tempo'].values)
            
            scat3.set_offsets(np.c_[dados_ate_agora['TamanhoFila'], dados_ate_agora['NumeroMedioRequisicoes']])
            scat3.set_array(dados_ate_agora['Tempo'].values)
            
            scat4.set_offsets(np.c_[dados_ate_agora['TamanhoFila'], dados_ate_agora['TempoMedioEspera']])
            scat4.set_array(dados_ate_agora['Tempo'].values)
            
            # Atualizar pontos atuais
            point1.set_offsets(np.c_[dados_ate_agora['Ocupacao'].iloc[-1], dados_ate_agora['NumeroMedioRequisicoes'].iloc[-1]])
            point2.set_offsets(np.c_[dados_ate_agora['Ocupacao'].iloc[-1], dados_ate_agora['TempoMedioEspera'].iloc[-1]])
            point3.set_offsets(np.c_[dados_ate_agora['TamanhoFila'].iloc[-1], dados_ate_agora['NumeroMedioRequisicoes'].iloc[-1]])
            point4.set_offsets(np.c_[dados_ate_agora['TamanhoFila'].iloc[-1], dados_ate_agora['TempoMedioEspera'].iloc[-1]])
            
            # Atualizar limites
            for ax, x_var, y_var in zip(axes.flat, 
                                       ['Ocupacao', 'Ocupacao', 'TamanhoFila', 'TamanhoFila'],
                                       ['NumeroMedioRequisicoes', 'TempoMedioEspera', 'NumeroMedioRequisicoes', 'TempoMedioEspera']):
                ax.set_xlim(dados[x_var].min() - 0.01, dados[x_var].max() + 0.01)
                ax.set_ylim(dados[y_var].min() - 0.1, dados[y_var].max() + 0.1)
            
            fig.canvas.draw_idle()
        
        slider.on_changed(update)
        
        # Inicializar
        update(dados['Tempo'].min())
        
        # Adicionar barras de cores
        plt.colorbar(scat1, ax=axes[0, 0], label='Tempo')
        plt.colorbar(scat2, ax=axes[0, 1], label='Tempo')
        plt.colorbar(scat3, ax=axes[1, 0], label='Tempo')
        plt.colorbar(scat4, ax=axes[1, 1], label='Tempo')
        
        # Botão para reset
        resetax = plt.axes([0.8, 0.05, 0.1, 0.03])
        button = Button(resetax, 'Reset', hovercolor='0.975')
        
        def reset(event):
            slider.reset()
        button.on_clicked(reset)
        
        plt.savefig(f'graficos/interativos/relacoes_interativo_{nome}.png', dpi=300, bbox_inches='tight')
        
        if self.mostrar_graficos_interativos:
            plt.show()
        else:
            plt.close(fig)
            
        return fig, slider

    # ---------- GRÁFICOS interativos ----------
    def gerarGraficosEN_EW_porCenario(self):
        for nome, dados in self.dadosPorCenario.items():
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            fig.suptitle(f'Métricas da Lei de Little - {nome}', fontweight='bold')
            sns.scatterplot(x='Tempo', y='NumeroMedioRequisicoes', data=dados, ax=axes[0], alpha=0.6)
            axes[0].set_title('E[N] - Número Médio de Requisições')
            sns.scatterplot(x='Tempo', y='TempoMedioEspera', data=dados, ax=axes[1], color='orange', alpha=0.6)
            axes[1].set_title('E[W] - Tempo Médio de Espera')
            axes[1].set_xlabel('Tempo (segundos)')
            plt.tight_layout()
            caminho = f"graficos/interativos/individuais/en_ew_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico individual salvo: {caminho}")

    def gerarGraficosComparativosEN_EW(self):
        for metric, ylabel, arquivo in [('NumeroMedioRequisicoes','E[N]','comparacao_en.png'),
                                        ('TempoMedioEspera','E[W]','comparacao_ew.png')]:
            fig, ax = plt.subplots(figsize=(14,8))
            for nome, dados in self.dadosPorCenario.items():
                sns.scatterplot(x='Tempo', y=metric, data=dados, ax=ax, label=nome, alpha=0.6)
            ax.set_title(f'Comparação de {ylabel} entre Cenários', fontweight='bold')
            ax.set_ylabel(ylabel)
            ax.set_xlabel('Tempo (segundos)')
            ax.legend()
            plt.tight_layout()
            caminho = f"graficos/interativos/comparativos/{arquivo}"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico comparativo {ylabel} salvo: {caminho}")

    def ajustarModeloTendencia(self, x, y, tipo='exponencial'):
        try:
            if tipo == 'linear':
                def modelo(x,a,b): return a*x+b
            elif tipo == 'exponencial':
                def modelo(x,a,b): return a*np.exp(b*x)
            elif tipo == 'logaritmico':
                x = x[x>0]; y = y[x>0]
                def modelo(x,a,b): return a*np.log(x)+b
            popt, _ = curve_fit(modelo, x, y, maxfev=10000)
            r2 = 1 - np.sum((y-modelo(x,*popt))**2)/np.sum((y-np.mean(y))**2)
            return popt, modelo, r2
        except: return None, None, 0

    def gerarGraficosComTendencia(self):
        for nome, dados in self.dadosPorCenario.items():
            tempo = dados['Tempo'].values
            en = dados['NumeroMedioRequisicoes'].values
            ew = dados['TempoMedioEspera'].values
            parametrosEN, modeloEN, r2EN = self.ajustarModeloTendencia(tempo,en)
            parametrosEW, modeloEW, r2EW = self.ajustarModeloTendencia(tempo,ew)
            self.expressoesAnaliticas[f"{nome}_EN"] = {'expressao': f"{parametrosEN[0]:.6f}*exp({parametrosEN[1]:.6f}*t)", 'r2': r2EN} if parametrosEN is not None else None
            self.expressoesAnaliticas[f"{nome}_EW"] = {'expressao': f"{parametrosEW[0]:.6f}*exp({parametrosEW[1]:.6f}*t)", 'r2': r2EW} if parametrosEW is not None else None
            fig, axes = plt.subplots(2, 1, figsize=(12,10))
            sns.scatterplot(x=tempo, y=en, ax=axes[0], alpha=0.6)
            if parametrosEN is not None:
                t_lin = np.linspace(min(tempo), max(tempo), 100)
                axes[0].plot(t_lin, modeloEN(t_lin,*parametrosEN), 'r', label=f'Tendência (R²={r2EN:.4f})')
            axes[0].set_title('E[N] com Tendência')
            axes[0].legend()
            sns.scatterplot(x=tempo, y=ew, ax=axes[1], color='orange', alpha=0.6)
            if parametrosEW is not None:
                axes[1].plot(t_lin, modeloEW(t_lin,*parametrosEW), 'r', label=f'Tendência (R²={r2EW:.4f})')
            axes[1].set_title('E[W] com Tendência')
            axes[1].legend()
            plt.tight_layout()
            caminho = f"graficos/interativos/tendencia/tendencia_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico com tendência salvo: {caminho}")

    def gerarGraficosFilaVsOcupacao(self):
        for nome, dados in self.dadosPorCenario.items():
            fig, ax = plt.subplots(figsize=(12,8))
            sns.scatterplot(x='Ocupacao', y='TamanhoFila', hue='Tempo', palette='viridis', data=dados, ax=ax)
            ax.set_title(f'Tamanho da Fila vs Ocupação - {nome}', fontweight='bold')
            ax.set_xlabel('Ocupação')
            ax.set_ylabel('Tamanho da Fila')
            plt.tight_layout()
            caminho = f"graficos/interativos/fila/fila_vs_ocupacao_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico Fila vs Ocupação salvo: {caminho}")

    def gerarGraficosDistribuicaoOcupacao(self):
        for nome, dados in self.dadosPorCenario.items():
            fig, axes = plt.subplots(1,2,figsize=(16,6))
            sns.histplot(dados['Ocupacao'], bins=50, kde=True, ax=axes[0], color='skyblue')
            axes[0].set_title('Histograma da Ocupação')
            sns.lineplot(x='Tempo', y='Ocupacao', data=dados, ax=axes[1])
            axes[1].set_title('Evolução da Ocupação ao Longo do Tempo')
            plt.tight_layout()
            caminho = f"graficos/interativos/ocupacao/distribuicao_ocupacao_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico de distribuição de ocupação salvo: {caminho}")

    def gerarMatrizCorrelacao(self):
        for nome, dados in self.dadosPorCenario.items():
            fig, ax = plt.subplots(figsize=(10,8))
            sns.heatmap(dados.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            ax.set_title(f'Matriz de Correlação - {nome}', fontweight='bold')
            plt.tight_layout()
            caminho = f"graficos/interativos/correlacao/matriz_correlacao_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Matriz de correlação salva: {caminho}")

    def gerarGraficosRelacoesVariaveis(self):
        for nome, dados in self.dadosPorCenario.items():
            fig, axes = plt.subplots(2,2,figsize=(16,12))
            sns.scatterplot(x='Ocupacao', y='NumeroMedioRequisicoes', hue='Tempo', palette='viridis', data=dados, ax=axes[0,0])
            axes[0,0].set_title('E[N] vs Ocupação')
            sns.scatterplot(x='Ocupacao', y='TempoMedioEspera', hue='Tempo', palette='viridis', data=dados, ax=axes[0,1])
            axes[0,1].set_title('E[W] vs Ocupação')
            sns.scatterplot(x='TamanhoFila', y='NumeroMedioRequisicoes', hue='Tempo', palette='viridis', data=dados, ax=axes[1,0])
            axes[1,0].set_title('E[N] vs Tamanho da Fila')
            sns.scatterplot(x='TamanhoFila', y='TempoMedioEspera', hue='Tempo', palette='viridis', data=dados, ax=axes[1,1])
            axes[1,1].set_title('E[W] vs Tamanho da Fila')
            plt.tight_layout()
            caminho = f"graficos/interativos/relacoes/relacoes_variaveis_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico de relações entre variáveis salvo: {caminho}")

    def gerarRelatorioExpressoesAnaliticas(self):
        caminho = "expressoes_analiticas.txt"
        with open(caminho, 'w') as f:
            f.write("EXPRESSÕES ANALÍTICAS DAS TENDÊNCIAS\n\n")
            for k,v in self.expressoesAnaliticas.items():
                if v is not None:
                    f.write(f"{k}:\n  Expressão: {v['expressao']}\n")
                    if 'r2' in v: f.write(f"  R²: {v['r2']:.6f}\n")
                    f.write("\n")
        print(f"Relatório de expressões analíticas salvo: {caminho}")

    def ajustarModeloFila(self, mu=1.0):
        def modelo_EN(rho, a):
            return a * rho / (1 - rho)
        def modelo_EW(rho, a):
            return a / (mu * (1 - rho))

        for nome, dados in self.dadosPorCenario.items():
            rho = dados['Ocupacao'].values
            EN = dados['NumeroMedioRequisicoes'].values
            EW = dados['TempoMedioEspera'].values

            try:
                popt_EN, _ = curve_fit(modelo_EN, rho, EN)
                self.expressoesAnaliticas[f"{nome}_EN_ajuste"] = {'expressao': f"{popt_EN[0]:.6f} * rho / (1 - rho)"}
            except Exception as e:
                print(f"Erro no ajuste E[N] - {nome}: {e}")
                continue

            try:
                popt_EW, _ = curve_fit(modelo_EW, rho, EW)
                self.expressoesAnaliticas[f"{nome}_EW_ajuste"] = {'expressao': f"{popt_EW[0]:.6f} / (mu * (1 - rho))"}
            except Exception as e:
                print(f"Erro no ajuste E[W] - {nome}: {e}")
                continue

            fig, axes = plt.subplots(1,2,figsize=(16,6))
            axes[0].scatter(rho, EN, label='Simulação', alpha=0.6)
            rho_lin = np.linspace(min(rho), max(rho), 100)
            axes[0].plot(rho_lin, modelo_EN(rho_lin, *popt_EN), 'r', label='Ajuste')
            axes[0].plot(rho_lin, rho_lin / (1 - rho_lin), 'g--', label='Teoria M/M/1')
            axes[0].set_title(f'E[N] vs ρ - {nome}')
            axes[0].set_xlabel('Ocupação ρ')
            axes[0].set_ylabel('E[N]')
            axes[0].legend()

            axes[1].scatter(rho, EW, label='Simulação', alpha=0.6, color='orange')
            axes[1].plot(rho_lin, modelo_EW(rho_lin, *popt_EW), 'r', label='Ajuste')
            axes[1].plot(rho_lin, 1 / (mu * (1 - rho_lin)), 'g--', label='Teoria M/M/1')
            axes[1].set_title(f'E[W] vs ρ - {nome}')
            axes[1].set_xlabel('Ocupação ρ')
            axes[1].set_ylabel('E[W]')
            axes[1].legend()

            plt.tight_layout()
            caminho = f"graficos/interativos/relacoes/EN_EW_vs_rho_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico E[N]/E[W] vs ρ salvo: {caminho}")
            print(f"{nome} - E[N] ajuste: a = {popt_EN[0]:.6f}, E[W] ajuste: a = {popt_EW[0]:.6f}")

    # ---------- ANIMAÇÕES MP4 ----------
    def criar_animacao_EN_EW(self, nome, dados, fps=30):
        """Cria animação MP4 de E[N] e E[W] ao longo do tempo"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Configurar eixo
        ax.set_xlabel('Tempo')
        ax.set_ylabel('Valor')
        ax.set_title(f'E[N] e E[W] ao longo do Tempo - {nome}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(dados['Tempo'].min(), dados['Tempo'].max())
        ax.set_ylim(min(dados['NumeroMedioRequisicoes'].min(), dados['TempoMedioEspera'].min()) - 0.1,
                   max(dados['NumeroMedioRequisicoes'].max(), dados['TempoMedioEspera'].max()) + 0.1)
        
        # Elementos do gráfico
        line_EN, = ax.plot([], [], 'b-', alpha=0.7, linewidth=2, label='E[N]')
        line_EW, = ax.plot([], [], 'r-', alpha=0.7, linewidth=2, label='E[W]')
        point_EN = ax.scatter([], [], color='blue', s=100, zorder=5)
        point_EW = ax.scatter([], [], color='red', s=100, zorder=5)
        ax.legend()
        
        def init():
            line_EN.set_data([], [])
            line_EW.set_data([], [])
            point_EN.set_offsets(np.empty((0, 2)))
            point_EW.set_offsets(np.empty((0, 2)))
            return line_EN, line_EW, point_EN, point_EW
        
        def animate(i):
            # Para não sobrecarregar a animação, usar apenas alguns pontos
            passo = max(1, len(dados) // 200)
            idx = min(i * passo, len(dados) - 1)
            
            line_EN.set_data(dados['Tempo'].iloc[:idx+1], dados['NumeroMedioRequisicoes'].iloc[:idx+1])
            line_EW.set_data(dados['Tempo'].iloc[:idx+1], dados['TempoMedioEspera'].iloc[:idx+1])
            
            point_EN.set_offsets(np.c_[dados['Tempo'].iloc[idx], dados['NumeroMedioRequisicoes'].iloc[idx]])
            point_EW.set_offsets(np.c_[dados['Tempo'].iloc[idx], dados['TempoMedioEspera'].iloc[idx]])
            
            return line_EN, line_EW, point_EN, point_EW
        
        # Criar animação
        anim = FuncAnimation(fig, animate, init_func=init,
                            frames=min(200, len(dados)), interval=50, blit=True)
        
        # Salvar como MP4
        caminho_video = f'videos/EN_EW_tempo_{nome}.mp4'
        writer = FFMpegWriter(fps=fps, metadata=dict(artist='AnaliseInterativaCompleta'), bitrate=1800)
        anim.save(caminho_video, writer=writer, dpi=100)
        plt.close(fig)
        print(f"Vídeo salvo: {caminho_video}")

    def criar_animacao_fila_ocupacao(self, nome, dados, fps=30):
        """Cria animação MP4 de Tamanho da Fila vs Ocupação"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Configurar eixo
        ax.set_xlabel('Ocupação')
        ax.set_ylabel('Tamanho da Fila')
        ax.set_title(f'Tamanho da Fila vs Ocupação - {nome}')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(dados['Ocupacao'].min() - 0.01, dados['Ocupacao'].max() + 0.01)
        ax.set_ylim(dados['TamanhoFila'].min() - 1, dados['TamanhoFila'].max() + 1)
        
        # Elementos do gráfico
        scat = ax.scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        point = ax.scatter([], [], color='red', s=100, zorder=5)
        
        # Adicionar barra de cores
        plt.colorbar(scat, ax=ax, label='Tempo')
        
        def init():
            scat.set_offsets(np.empty((0, 2)))
            scat.set_array(np.array([]))
            point.set_offsets(np.empty((0, 2)))
            return scat, point
        
        def animate(i):
            # Para não sobrecarregar a animação, usar apenas alguns pontos
            passo = max(1, len(dados) // 200)
            idx = min(i * passo, len(dados) - 1)
            
            # Dados até o frame atual
            dados_ate_agora = dados.iloc[:idx+1]
            
            # Preparar dados para scatter plot
            scat.set_offsets(np.c_[dados_ate_agora['Ocupacao'], dados_ate_agora['TamanhoFila']])
            scat.set_array(dados_ate_agora['Tempo'].values)
            
            # Atualizar ponto atual
            point.set_offsets(np.c_[dados_ate_agora['Ocupacao'].iloc[-1], dados_ate_agora['TamanhoFila'].iloc[-1]])
            
            return scat, point
        
        # Criar animação
        anim = FuncAnimation(fig, animate, init_func=init,
                            frames=min(200, len(dados)), interval=50, blit=True)
        
        # Salvar como MP4
        caminho_video = f'videos/fila_ocupacao_{nome}.mp4'
        writer = FFMpegWriter(fps=fps, metadata=dict(artist='AnaliseInterativaCompleta'), bitrate=1800)
        anim.save(caminho_video, writer=writer, dpi=100)
        plt.close(fig)
        print(f"Vídeo salvo: {caminho_video}")

    def criar_animacao_relacoes(self, nome, dados, fps=30):
        """Cria animação MP4 das relações entre variáveis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Configurar eixos
        axes[0, 0].set_xlabel('Ocupação')
        axes[0, 0].set_ylabel('E[N]')
        axes[0, 0].set_title('E[N] vs Ocupação')
        
        axes[0, 1].set_xlabel('Ocupação')
        axes[0, 1].set_ylabel('E[W]')
        axes[0, 1].set_title('E[W] vs Ocupação')
        
        axes[1, 0].set_xlabel('Tamanho da Fila')
        axes[1, 0].set_ylabel('E[N]')
        axes[1, 0].set_title('E[N] vs Tamanho da Fila')
        
        axes[1, 1].set_xlabel('Tamanho da Fila')
        axes[1, 1].set_ylabel('E[W]')
        axes[1, 1].set_title('E[W] vs Tamanho da Fila')
        
        for ax in axes.flat:
            ax.grid(True, alpha=0.3)
        
        # Elementos do gráfico
        scat1 = axes[0, 0].scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        scat2 = axes[0, 1].scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        scat3 = axes[1, 0].scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        scat4 = axes[1, 1].scatter([], [], c=[], cmap='viridis', alpha=0.6, s=20)
        
        point1 = axes[0, 0].scatter([], [], color='red', s=100, zorder=5)
        point2 = axes[0, 1].scatter([], [], color='red', s=100, zorder=5)
        point3 = axes[1, 0].scatter([], [], color='red', s=100, zorder=5)
        point4 = axes[1, 1].scatter([], [], color='red', s=100, zorder=5)
        
        # Adicionar barras de cores
        plt.colorbar(scat1, ax=axes[0, 0], label='Tempo')
        plt.colorbar(scat2, ax=axes[0, 1], label='Tempo')
        plt.colorbar(scat3, ax=axes[1, 0], label='Tempo')
        plt.colorbar(scat4, ax=axes[1, 1], label='Tempo')
        
        def init():
            scat1.set_offsets(np.empty((0, 2)))
            scat1.set_array(np.array([]))
            scat2.set_offsets(np.empty((0, 2)))
            scat2.set_array(np.array([]))
            scat3.set_offsets(np.empty((0, 2)))
            scat3.set_array(np.array([]))
            scat4.set_offsets(np.empty((0, 2)))
            scat4.set_array(np.array([]))
            
            point1.set_offsets(np.empty((0, 2)))
            point2.set_offsets(np.empty((0, 2)))
            point3.set_offsets(np.empty((0, 2)))
            point4.set_offsets(np.empty((0, 2)))
            
            return scat1, scat2, scat3, scat4, point1, point2, point3, point4
        
        def animate(i):
            # Para não sobrecarregar a animação, usar apenas alguns pontos
            passo = max(1, len(dados) // 200)
            idx = min(i * passo, len(dados) - 1)
            
            # Dados até o frame atual
            dados_ate_agora = dados.iloc[:idx+1]
            
            # Atualizar scatter plots
            scat1.set_offsets(np.c_[dados_ate_agora['Ocupacao'], dados_ate_agora['NumeroMedioRequisicoes']])
            scat1.set_array(dados_ate_agora['Tempo'].values)
            
            scat2.set_offsets(np.c_[dados_ate_agora['Ocupacao'], dados_ate_agora['TempoMedioEspera']])
            scat2.set_array(dados_ate_agora['Tempo'].values)
            
            scat3.set_offsets(np.c_[dados_ate_agora['TamanhoFila'], dados_ate_agora['NumeroMedioRequisicoes']])
            scat3.set_array(dados_ate_agora['Tempo'].values)
            
            scat4.set_offsets(np.c_[dados_ate_agora['TamanhoFila'], dados_ate_agora['TempoMedioEspera']])
            scat4.set_array(dados_ate_agora['Tempo'].values)
            
            # Atualizar pontos atuais
            point1.set_offsets(np.c_[dados_ate_agora['Ocupacao'].iloc[-1], dados_ate_agora['NumeroMedioRequisicoes'].iloc[-1]])
            point2.set_offsets(np.c_[dados_ate_agora['Ocupacao'].iloc[-1], dados_ate_agora['TempoMedioEspera'].iloc[-1]])
            point3.set_offsets(np.c_[dados_ate_agora['TamanhoFila'].iloc[-1], dados_ate_agora['NumeroMedioRequisicoes'].iloc[-1]])
            point4.set_offsets(np.c_[dados_ate_agora['TamanhoFila'].iloc[-1], dados_ate_agora['TempoMedioEspera'].iloc[-1]])
            
            return scat1, scat2, scat3, scat4, point1, point2, point3, point4
        
        # Criar animação
        anim = FuncAnimation(fig, animate, init_func=init,
                            frames=min(200, len(dados)), interval=50, blit=True)
        
        # Salvar como MP4
        caminho_video = f'videos/relacoes_{nome}.mp4'
        writer = FFMpegWriter(fps=fps, metadata=dict(artist='AnaliseInterativaCompleta'), bitrate=1800)
        anim.save(caminho_video, writer=writer, dpi=100)
        plt.close(fig)
        print(f"Vídeo salvo: {caminho_video}")

    def criar_animacao_3d(self, nome, dados, fps=30):
        """Cria animação MP4 3D de E[N], E[W] e Tempo"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Configurar eixos
        ax.set_xlabel('Tempo')
        ax.set_ylabel('E[N]')
        ax.set_zlabel('E[W]')
        ax.set_title(f'E[N], E[W] vs Tempo - {nome}')
        
        # Elementos do gráfico
        line, = ax.plot([], [], [], 'b-', alpha=0.7, linewidth=2)
        point = ax.scatter([], [], [], color='red', s=100, zorder=5)
        
        def init():
            line.set_data([], [])
            line.set_3d_properties([])
            point._offsets3d = (np.empty((0,)), np.empty((0,)), np.empty((0,)))
            return line, point
        
        def animate(i):
            # Para não sobrecarregar a animação, usar apenas alguns pontos
            passo = max(1, len(dados) // 200)
            idx = min(i * passo, len(dados) - 1)
            
            # Dados até o frame atual
            dados_ate_agora = dados.iloc[:idx+1]
            
            # Atualizar linha
            line.set_data(dados_ate_agora['Tempo'], dados_ate_agora['NumeroMedioRequisicoes'])
            line.set_3d_properties(dados_ate_agora['TempoMedioEspera'])
            
            # Atualizar ponto atual
            point._offsets3d = (
                [dados_ate_agora['Tempo'].iloc[-1]],
                [dados_ate_agora['NumeroMedioRequisicoes'].iloc[-1]],
                [dados_ate_agora['TempoMedioEspera'].iloc[-1]]
            )
            
            # Atualizar limites
            ax.set_xlim(dados['Tempo'].min(), dados['Tempo'].max())
            ax.set_ylim(dados['NumeroMedioRequisicoes'].min(), dados['NumeroMedioRequisicoes'].max())
            ax.set_zlim(dados['TempoMedioEspera'].min(), dados['TempoMedioEspera'].max())
            
            # Rotacionar a vista
            ax.view_init(elev=30, azim=i*2)
            
            return line, point
        
        # Criar animação
        anim = FuncAnimation(fig, animate, init_func=init,
                            frames=min(180, len(dados)), interval=50, blit=True)
        
        # Salvar como MP4
        caminho_video = f'videos/3d_en_ew_tempo_{nome}.mp4'
        writer = FFMpegWriter(fps=fps, metadata=dict(artist='AnaliseInterativaCompleta'), bitrate=1800)
        anim.save(caminho_video, writer=writer, dpi=100)
        plt.close(fig)
        print(f"Vídeo 3D salvo: {caminho_video}")

    # ---------- EXECUÇÃO COMPLETA ----------
    def executarAnaliseCompleta(self, caminhosArquivos, mu=1.0, janela_entropia=100):
        """Executa a análise completa dos dados de simulação"""
        print("Iniciando análise científica avançada...")
        self.carregarDados(caminhosArquivos)
        
        if not self.dadosPorCenario:
            print("Nenhum dado foi carregado.")
            return
        
        # Cálculo de entropia para todos os cenários
        for nome, dados in self.dadosPorCenario.items():
            df_entropia = self.calcular_entropia(dados, 'TamanhoFila', janela_entropia)
            self.dadosPorCenario[nome] = pd.merge_asof(
                dados.sort_values('Tempo'), 
                df_entropia.sort_values('Tempo'), 
                on='Tempo', 
                direction='nearest'
            )
        
        # Gera todas as visualizações
        print("Gerando gráficos 3D...")
        self.gerarGraficos3D()
        
        print("Gerando gráficos interativos...")
        self.gerarGraficosEN_EW_porCenario()
        self.gerarGraficosComparativosEN_EW()
        self.gerarGraficosComTendencia()
        self.gerarGraficosFilaVsOcupacao()
        self.gerarGraficosDistribuicaoOcupacao()
        self.gerarMatrizCorrelacao()
        self.gerarGraficosRelacoesVariaveis()
        self.ajustarModeloFila(mu=mu)
        self.gerarRelatorioExpressoesAnaliticas()
        
        # Executa análise estatística avançada
        print("Executando análise estatística avançada...")
        self.executar_analise_estatistica_avancada()
        
        # Para cada cenário, criar gráficos interativos e animações
        for nome, dados in self.dadosPorCenario.items():
            print(f"Processando cenário: {nome}")
            
            # Criar gráficos interativos com sliders
            print(f"Criando gráficos interativos para {nome}...")
            self.criar_grafico_EN_EW_interativo(nome, dados)
            self.criar_grafico_fila_ocupacao_interativo(nome, dados)
            self.criar_grafico_relacoes_interativo(nome, dados)
            
            # Criar animações MP4
            print(f"Criando animações MP4 para {nome}...")
            self.criar_animacao_EN_EW(nome, dados)
            self.criar_animacao_fila_ocupacao(nome, dados)
            self.criar_animacao_relacoes(nome, dados)
            self.criar_animacao_3d(nome, dados)
        
        print("Análise completa concluída. Gráficos interativos, vídeos e relatórios gerados.")


def main():
    # Configuração principal
    arquivos = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv',
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    # Cria analisador com visualizações interativas
    analisador = AnaliseInterativaCompleta(mostrar_graficos_interativos=True)
    
    # Executa análise completa
    analisador.executarAnaliseCompleta(arquivos, mu=1.0, janela_entropia=100)


if __name__ == "__main__":
    main()
