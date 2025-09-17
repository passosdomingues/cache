#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Análise Científica para Dados de Simulação de Filas
Visualização e análise de E[N], E[W], tamanho da fila e ocupação usando Seaborn
Inclui ajuste analítico de E[N] e E[W] em função de ρ e μ
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
    def __init__(self, usarEscalaLogTempo=False):
        self.usarEscalaLogTempo = usarEscalaLogTempo
        self.dadosPorCenario = {}
        self.expressoesAnaliticas = {}
        self.configurarVisualizacoes()
        self.criarDiretoriosSaida()

    def configurarVisualizacoes(self):
        sns.set(style="whitegrid", palette="husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['axes.labelsize'] = 14

    def criarDiretoriosSaida(self):
        diretorios = [
            'graficos/rafaPlots/individuais', 
            'graficos/rafaPlots/comparativos', 
            'graficos/rafaPlots/tendencia', 
            'graficos/rafaPlots/fila',
            'graficos/rafaPlots/ocupacao',
            'graficos/rafaPlots/correlacao',
            'graficos/rafaPlots/distribuicao',
            'graficos/rafaPlots/relacoes'
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

    # ---------- GRÁFICOS ----------
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
            caminho = f"graficos/rafaPlots/individuais/en_ew_{nome}.png"
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
            caminho = f"graficos/rafaPlots/comparativos/{arquivo}"
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
            caminho = f"graficos/rafaPlots/tendencia/tendencia_{nome}.png"
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
            caminho = f"graficos/rafaPlots/fila/fila_vs_ocupacao_{nome}.png"
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
            caminho = f"graficos/rafaPlots/ocupacao/distribuicao_ocupacao_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico de distribuição de ocupação salvo: {caminho}")

    def gerarMatrizCorrelacao(self):
        for nome, dados in self.dadosPorCenario.items():
            fig, ax = plt.subplots(figsize=(10,8))
            sns.heatmap(dados.corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
            ax.set_title(f'Matriz de Correlação - {nome}', fontweight='bold')
            plt.tight_layout()
            caminho = f"graficos/rafaPlots/correlacao/matriz_correlacao_{nome}.png"
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
            caminho = f"graficos/rafaPlots/relacoes/relacoes_variaveis_{nome}.png"
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

    # ---------- AJUSTE ANALÍTICO E[N], E[W] ----------
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
            caminho = f"graficos/rafaPlots/relacoes/EN_EW_vs_rho_{nome}.png"
            fig.savefig(caminho, dpi=300, bbox_inches='tight')
            plt.close(fig)
            print(f"Gráfico E[N]/E[W] vs ρ salvo: {caminho}")
            print(f"{nome} - E[N] ajuste: a = {popt_EN[0]:.6f}, E[W] ajuste: a = {popt_EW[0]:.6f}")

    # ---------- EXECUÇÃO COMPLETA ----------
    def executarAnaliseCompleta(self, caminhosArquivos, mu=1.0):
        print("Iniciando análise científica completa...")
        self.carregarDados(caminhosArquivos)
        if not self.dadosPorCenario:
            print("Nenhum dado foi carregado.")
            return
        self.gerarGraficosEN_EW_porCenario()
        self.gerarGraficosComparativosEN_EW()
        self.gerarGraficosComTendencia()
        self.gerarGraficosFilaVsOcupacao()
        self.gerarGraficosDistribuicaoOcupacao()
        self.gerarMatrizCorrelacao()
        self.gerarGraficosRelacoesVariaveis()
        self.ajustarModeloFila(mu=mu)
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
    analisador.executarAnaliseCompleta(arquivos, mu=1.0)


if __name__ == "__main__":
    main()

