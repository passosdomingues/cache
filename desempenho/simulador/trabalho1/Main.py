#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Análise Científica Avançada para Dados de Simulação de Filas
Ajuste analítico de E[N] e E[W] por cenário de ocupação, gráficos comparativos e insights diretos
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')


class AnaliseCientificaSimulacao:
    def __init__(self, taxa_servico=1.0):
        self.taxa_servico = taxa_servico
        self.dadosPorCenario = {}
        self.expressoesAnaliticas = {}
        self.configurarVisualizacoes()
        self.criarDiretoriosSaida()

    def configurarVisualizacoes(self):
        sns.set(style="whitegrid", palette="tab10")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['axes.labelsize'] = 14

    def criarDiretoriosSaida(self):
        diretorios = [
            'graficos/Main/individuais', 
            'graficos/Main/comparativos', 
            'graficos/Main/tendencia', 
            'graficos/Main/fila',
            'graficos/Main/ocupacao',
            'graficos/Main/correlacao',
            'graficos/Main/relacoes'
        ]
        for d in diretorios:
            Path(d).mkdir(parents=True, exist_ok=True)

    def carregarDados(self, caminhosArquivos):
        for caminho in caminhosArquivos:
            if Path(caminho).exists():
                nome = Path(caminho).stem.replace('dados_', '')
                self.dadosPorCenario[nome] = pd.read_csv(caminho)
                print(f"Dados carregados: {nome} ({len(self.dadosPorCenario[nome])} registros)")
            else:
                print(f"Arquivo não encontrado: {caminho}")

    # ---------- GRÁFICOS INDIVIDUAIS ----------
    def gerarGraficosEN_EW_porCenario(self):
        for nome, dados in self.dadosPorCenario.items():
            fig, axes = plt.subplots(2, 1, figsize=(12, 10))
            fig.suptitle(f'Métricas da Lei de Little - {nome}', fontweight='bold')
            sns.scatterplot(x='Tempo', y='NumeroMedioRequisicoes', data=dados, ax=axes[0], alpha=0.6, color='dodgerblue')
            axes[0].set_title('E[N] - Número Médio de Requisições')
            sns.scatterplot(x='Tempo', y='TempoMedioEspera', data=dados, ax=axes[1], color='orange', alpha=0.6)
            axes[1].set_title('E[W] - Tempo Médio de Espera')
            axes[1].set_xlabel('Tempo (segundos)')
            plt.tight_layout()
            caminho = f"graficos/Main/individuais/en_ew_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)

    # ---------- GRÁFICOS COMPARATIVOS ----------
    def gerarGraficosComparativosEN_EW(self):
        for metric, ylabel, arquivo in [('NumeroMedioRequisicoes','E[N]','comparacao_en.png'),
                                        ('TempoMedioEspera','E[W]','comparacao_ew.png')]:
            fig, ax = plt.subplots(figsize=(14,8))
            cores = sns.color_palette("tab10", n_colors=len(self.dadosPorCenario))
            for (nome, dados), cor in zip(self.dadosPorCenario.items(), cores):
                x = dados['Tempo'].values
                y = dados[metric].values
                if nome.endswith('0999'):
                    # Escala log para cenário extremo
                    y = np.log10(y + 1e-6)
                    ax.set_ylabel(f'{ylabel} (log10)')
                sns.scatterplot(x=x, y=y, ax=ax, label=nome, color=cor, alpha=0.6)
            ax.set_title(f'Comparação de {ylabel} entre Cenários', fontweight='bold')
            ax.set_xlabel('Tempo (segundos)')
            ax.legend()
            plt.tight_layout()
            caminho = f"graficos/Main/comparativos/{arquivo}"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)

    # ---------- AJUSTE ANALÍTICO POR CENÁRIO ----------
    def gerarEN_EW_vs_rho(self):
        def modelo_EN(rho, a): return a*rho/(1-rho)
        def modelo_EW(rho, a): return a/(self.taxa_servico*(1-rho))

        for nome, dados in self.dadosPorCenario.items():
            medias = dados.groupby('Ocupacao').agg({'NumeroMedioRequisicoes':'mean',
                                                    'TempoMedioEspera':'mean'}).reset_index()
            rho = medias['Ocupacao'].values
            en = medias['NumeroMedioRequisicoes'].values
            ew = medias['TempoMedioEspera'].values

            popt_EN, _ = curve_fit(modelo_EN, rho, en)
            popt_EW, _ = curve_fit(modelo_EW, rho, ew)

            self.expressoesAnaliticas[f"{nome}_EN_rho"] = {'expressao': f"{popt_EN[0]:.6f}*rho/(1-rho)"}
            self.expressoesAnaliticas[f"{nome}_EW_rho"] = {'expressao': f"{popt_EW[0]:.6f}/(mu*(1-rho))"}

            rho_lin = np.linspace(min(rho), max(rho), 100)
            fig, ax = plt.subplots(figsize=(10,6))
            ax.scatter(rho, en, alpha=0.7, color='dodgerblue', label='E[N] simulados médios')
            ax.plot(rho_lin, modelo_EN(rho_lin, *popt_EN), 'r', label=f'Ajuste E[N] (a={popt_EN[0]:.3f})')
            ax.plot(rho_lin, rho_lin/(1-rho_lin), 'k--', label='Teórico E[N]')
            ax.set_xlabel('Ocupação ρ')
            ax.set_ylabel('E[N]')
            ax.set_title(f'E[N] vs ρ - {nome}')
            ax.legend()
            caminho = f"graficos/Main/relacoes/EN_vs_rho_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)

            fig, ax = plt.subplots(figsize=(10,6))
            if nome.endswith('0999'):
                ew_plot = np.log10(ew + 1e-6)
                ylabel_plot = 'E[W] (log10)'
            else:
                ew_plot = ew
                ylabel_plot = 'E[W]'
            ax.scatter(rho, ew_plot, alpha=0.7, color='orange', label='E[W] simulados médios')
            ax.plot(rho_lin, modelo_EW(rho_lin, *popt_EW), 'r', label=f'Ajuste E[W] (a={popt_EW[0]:.3f})')
            ax.plot(rho_lin, 1.0/(self.taxa_servico*(1-rho_lin)), 'k--', label='Teórico E[W]')
            ax.set_xlabel('Ocupação ρ')
            ax.set_ylabel(ylabel_plot)
            ax.set_title(f'E[W] vs ρ - {nome}')
            ax.legend()
            caminho = f"graficos/Main/relacoes/EW_vs_rho_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)

            print(f"{nome} - E[N] ajuste: a = {popt_EN[0]:.6f}, E[W] ajuste: a = {popt_EW[0]:.6f}")

    # ---------- RELATÓRIO EXPRESSÕES ANALÍTICAS ----------
    def gerarRelatorioExpressoesAnaliticas(self):
        caminho = "expressoes_analiticas.txt"
        with open(caminho, 'w') as f:
            f.write("EXPRESSÕES ANALÍTICAS AJUSTADAS POR CENÁRIO\n\n")
            for k,v in self.expressoesAnaliticas.items():
                f.write(f"{k}:\n  Expressão: {v['expressao']}\n\n")
        print(f"Relatório de expressões analíticas salvo: {caminho}")

    # ---------- EXECUÇÃO COMPLETA ----------
    def executarAnaliseCompleta(self, caminhosArquivos):
        print("Iniciando análise científica completa...")
        self.carregarDados(caminhosArquivos)
        if not self.dadosPorCenario:
            print("Nenhum dado foi carregado.")
            return
        self.gerarGraficosEN_EW_porCenario()
        self.gerarGraficosComparativosEN_EW()
        self.gerarEN_EW_vs_rho()
        self.gerarRelatorioExpressoesAnaliticas()
        print("Análise completa concluída.")


def main():
    arquivos = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv',
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    analisador = AnaliseCientificaSimulacao()
    analisador.executarAnaliseCompleta(arquivos)


if __name__ == "__main__":
    main()

