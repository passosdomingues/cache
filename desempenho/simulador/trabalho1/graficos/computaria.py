#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Análise Científica Avançada para Dados de Simulação de Filas
Análise visual e estatística completa com visualizações 3D interativas,
cálculo de entropia, transformações de dados e testes estatísticos robustos
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
from scipy.special import boxcox, inv_boxcox
from statsmodels.graphics.gofplots import qqplot
import warnings
warnings.filterwarnings('ignore')


class AnaliseCientificaAvancada:
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
            'graficos/computaria/individuais', 
            'graficos/computaria/comparativos', 
            'graficos/computaria/tendencia', 
            'graficos/computaria/fila',
            'graficos/computaria/ocupacao',
            'graficos/computaria/correlacao',
            'graficos/computaria/distribuicao',
            'graficos/computaria/relacoes',
            'graficos/computaria/3d',
            'graficos/computaria/entropia',
            'graficos/computaria/estatistica',
            'graficos/computaria/transformacoes'
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
            """Executa a análise estatística completa"""
            if self.remover_transiente:
                self.remover_transiente_inicial()
            else:
                self.dados_estacionarios = self.dados_originais
            
            # Estatísticas descritivas para dados originais
            self.resultados['estatisticas_originais'] = self.calcular_estatisticas_descritivas(
                self.dados_estacionarios['TamanhoFila'], 'Original'
            )
            
            # Aplica transformações
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
            analise.gerar_graficos_estatisticos("graficos/computaria/estatistica")
            print(f"Gráficos estatísticos salvos para {nome}")

    # ---------- GRÁFICOS 3D INTERATIVOS ----------
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
            caminho = f"graficos/computaria/3d/visualizacao_3d_completa_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            print(f"Gráficos 3D salvos: {caminho}")
            
            # Mostra gráficos interativos se solicitado
            if self.mostrar_graficos_interativos:
                plt.show()
            else:
                plt.close(fig)

    # ---------- MÉTODOS DE ANÁLISE COMPLEMENTARES ----------
    def gerarGraficosEntropia(self):
        """Gera gráficos de entropia em relação a outras variáveis"""
        for nome, dados in self.dadosPorCenario.items():
            if 'Entropia' not in dados.columns:
                df_entropia = self.calcular_entropia(dados, 'TamanhoFila', 100)
                dados = pd.merge_asof(
                    dados.sort_values('Tempo'), 
                    df_entropia.sort_values('Tempo'), 
                    on='Tempo', 
                    direction='nearest'
                )
            
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle(f'Análise de Entropia - {nome}', fontsize=16, fontweight='bold')
            
            # Entropia vs Tamanho da Fila
            sc1 = axes[0, 0].scatter(dados['TamanhoFila'], dados['Entropia'], 
                                    c=dados['Ocupacao'], cmap='viridis', alpha=0.6)
            axes[0, 0].set_xlabel('Tamanho da Fila')
            axes[0, 0].set_ylabel('Entropia')
            axes[0, 0].set_title('Entropia vs Tamanho da Fila (Ocupação)')
            plt.colorbar(sc1, ax=axes[0, 0], label='Ocupação')
            
            # Entropia vs Tempo
            axes[0, 1].plot(dados['Tempo'], dados['Entropia'], 'b-', alpha=0.7)
            axes[0, 1].set_xlabel('Tempo')
            axes[0, 1].set_ylabel('Entropia')
            axes[0, 1].set_title('Evolução da Entropia no Tempo')
            axes[0, 1].grid(True, alpha=0.3)
            
            # Entropia vs E[N]
            sc2 = axes[1, 0].scatter(dados['NumeroMedioRequisicoes'], dados['Entropia'],
                                    c=dados['TempoMedioEspera'], cmap='plasma', alpha=0.6)
            axes[1, 0].set_xlabel('E[N]')
            axes[1, 0].set_ylabel('Entropia')
            axes[1, 0].set_title('Entropia vs E[N] (E[W])')
            plt.colorbar(sc2, ax=axes[1, 0], label='E[W]')
            
            # Entropia vs E[W]
            sc3 = axes[1, 1].scatter(dados['TempoMedioEspera'], dados['Entropia'],
                                    c=dados['TamanhoFila'], cmap='inferno', alpha=0.6)
            axes[1, 1].set_xlabel('E[W]')
            axes[1, 1].set_ylabel('Entropia')
            axes[1, 1].set_title('Entropia vs E[W] (Tamanho Fila)')
            plt.colorbar(sc3, ax=axes[1, 1], label='Tamanho da Fila')
            
            plt.tight_layout()
            caminho = f"graficos/computaria/entropia/analise_entropia_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráficos de entropia salvos: {caminho}")

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
        self.gerarGraficos3D()
        self.gerarGraficosEntropia()
        
        # Executa análise estatística avançada
        self.executar_analise_estatistica_avancada()
        
        print("Análise completa concluída.")


def main():
    # Configuração principal
    arquivos = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv',
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    # Cria analisador com visualizações interativas
    analisador = AnaliseCientificaAvancada(mostrar_graficos_interativos=True)
    
    # Executa análise completa
    analisador.executarAnaliseCompleta(arquivos, mu=1.0, janela_entropia=100)


if __name__ == "__main__":
    main()
