#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Análise Científica para Dados de Simulação de Filas
Análise das métricas da Lei de Little com diferentes níveis de ocupação
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import scipy.stats as stats
from scipy.optimize import curve_fit
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class AnaliseCientificaSimulacao:
    """
    Classe principal para análise científica dos dados de simulação.
    Foca em E[N] e E[W] com visualizações detalhadas e análise de tendências.
    """
    
    def __init__(self, usarEscalaLogTempo=False):
        """
        Inicializa o analisador com configurações padrão.
        
        Parâmetros:
            usarEscalaLogTempo (bool): Se True, usa escala logarítmica no eixo de tempo
        """
        self.usarEscalaLogTempo = usarEscalaLogTempo
        self.dadosPorCenario = {}
        self.expressoesAnaliticas = {}
        
        # Configurar estilo visual
        self.configurarVisualizacoes()
        
        # Criar diretórios para saída
        self.criarDiretoriosSaida()
    
    def configurarVisualizacoes(self):
        """Configura o estilo padrão para visualizações."""
        plt.style.use('default')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
    
    def criarDiretoriosSaida(self):
        """Cria os diretórios necessários para armazenar as saídas."""
        diretorios = [
            'graficos/individuais', 
            'graficos/comparativos', 
            'graficos/tendencia', 
            'graficos/fila',
            'graficos/ocupacao',
            'graficos/correlacao',
            'graficos/distribuicao',
            'graficos/relacoes'
        ]
        
        for diretorio in diretorios:
            Path(diretorio).mkdir(parents=True, exist_ok=True)
    
    def carregarDados(self, caminhosArquivos):
        """
        Carrega os dados dos arquivos CSV.
        
        Parâmetros:
            caminhosArquivos (list): Lista de caminhos para os arquivos CSV
        """
        for caminho in caminhosArquivos:
            if os.path.exists(caminho):
                try:
                    # Extrair nome do cenário do nome do arquivo
                    nomeCenario = os.path.basename(caminho).replace('dados_', '').replace('.csv', '')
                    
                    # Carregar dados
                    dados = pd.read_csv(caminho)
                    self.dadosPorCenario[nomeCenario] = dados
                    print(f"Dados carregados: {nomeCenario} ({len(dados)} registros)")
                    
                except Exception as e:
                    print(f"Erro ao carregar {caminho}: {e}")
            else:
                print(f"Arquivo não encontrado: {caminho}")
    
    def gerarGraficosEN_EW_porCenario(self):
        """Gera gráficos de E[N] e E[W] para cada cenário individualmente."""
        figuras = []
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            # Criar figura com dois subplots (E[N] e E[W])
            figura, (eixoEN, eixoEW) = plt.subplots(2, 1, figsize=(12, 10))
            figura.suptitle(f'Métricas da Lei de Little - {nomeCenario}', fontweight='bold')
            
            # Gráfico de E[N]
            tempo = dados['Tempo']
            eixoEN.scatter(tempo, dados['NumeroMedioRequisicoes'], alpha=0.6, s=10)
            eixoEN.set_title('E[N] - Número Médio de Requisições no Sistema')
            eixoEN.set_ylabel('E[N]')
            
            # Ajustar escala do eixo x se necessário
            if self.usarEscalaLogTempo:
                eixoEN.set_xscale('log')
                eixoEN.set_xlabel('Tempo (escala logarítmica)')
            else:
                eixoEN.set_xlabel('Tempo (segundos)')
            
            # Gráfico de E[W]
            eixoEW.scatter(tempo, dados['TempoMedioEspera'], alpha=0.6, s=10, color='orange')
            eixoEW.set_title('E[W] - Tempo Médio de Espera no Sistema')
            eixoEW.set_ylabel('E[W]')
            
            # Ajustar escala do eixo x se necessário
            if self.usarEscalaLogTempo:
                eixoEW.set_xscale('log')
                eixoEW.set_xlabel('Tempo (escala logarítmica)')
            else:
                eixoEW.set_xlabel('Tempo (segundos)')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar figura
            caminhoSalvar = f"graficos/individuais/en_ew_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            print(f"Gráfico individual salvo: {caminhoSalvar}")
        
        return figuras
    
    def gerarGraficosSobrepostosEN_EW(self):
        """Gera gráficos com E[N] e E[W] sobrepostos para cada cenário."""
        figuras = []
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            figura, eixo = plt.subplots(figsize=(12, 8))
            
            # Plotar E[N] e E[W] no mesmo gráfico
            tempo = dados['Tempo']
            eixo.scatter(tempo, dados['NumeroMedioRequisicoes'], alpha=0.6, s=10, 
                        label='E[N] - Número Médio de Requisições')
            eixo.scatter(tempo, dados['TempoMedioEspera'], alpha=0.6, s=10, 
                        label='E[W] - Tempo Médio de Espera', color='orange')
            
            # Configurar título e labels
            eixo.set_title(f'E[N] e E[W] - {nomeCenario}', fontweight='bold')
            eixo.set_ylabel('Valor das Métricas')
            
            # Ajustar escala do eixo x se necessário
            if self.usarEscalaLogTempo:
                eixo.set_xscale('log')
                eixo.set_xlabel('Tempo (escala logarítmica)')
            else:
                eixo.set_xlabel('Tempo (segundos)')
            
            # Adicionar legenda
            eixo.legend()
            eixo.grid(True, alpha=0.3)
            
            # Salvar figura
            caminhoSalvar = f"graficos/individuais/en_ew_sobrepostos_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            print(f"Gráfico sobreposto salvo: {caminhoSalvar}")
        
        return figuras
    
    def gerarGraficosComparativosEN(self):
        """Gera gráficos comparativos de E[N] entre todos os cenários."""
        figura, eixo = plt.subplots(figsize=(14, 8))
        
        cores = sns.color_palette("husl", len(self.dadosPorCenario))
        
        for i, (nomeCenario, dados) in enumerate(self.dadosPorCenario.items()):
            tempo = dados['Tempo']
            eixo.scatter(tempo, dados['NumeroMedioRequisicoes'], alpha=0.6, s=10, 
                        color=cores[i], label=nomeCenario)
        
        # Configurar título e labels
        eixo.set_title('Comparação de E[N] entre Cenários', fontweight='bold')
        eixo.set_ylabel('E[N] - Número Médio de Requisições')
        
        # Ajustar escala do eixo x se necessário
        if self.usarEscalaLogTempo:
            eixo.set_xscale('log')
            eixo.set_xlabel('Tempo (escala logarítmica)')
        else:
            eixo.set_xlabel('Tempo (segundos)')
        
        # Adicionar legenda
        eixo.legend()
        eixo.grid(True, alpha=0.3)
        
        # Salvar figura
        caminhoSalvar = "graficos/comparativos/comparacao_en.png"
        figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
        plt.close(figura)
        
        print(f"Gráfico comparativo E[N] salvo: {caminhoSalvar}")
        return caminhoSalvar
    
    def gerarGraficosComparativosEW(self):
        """Gera gráficos comparativos de E[W] entre todos os cenários."""
        figura, eixo = plt.subplots(figsize=(14, 8))
        
        cores = sns.color_palette("husl", len(self.dadosPorCenario))
        
        for i, (nomeCenario, dados) in enumerate(self.dadosPorCenario.items()):
            tempo = dados['Tempo']
            eixo.scatter(tempo, dados['TempoMedioEspera'], alpha=0.6, s=10, 
                        color=cores[i], label=nomeCenario)
        
        # Configurar título e labels
        eixo.set_title('Comparação de E[W] entre Cenários', fontweight='bold')
        eixo.set_ylabel('E[W] - Tempo Médio de Espera')
        
        # Ajustar escala do eixo x se necessário
        if self.usarEscalaLogTempo:
            eixo.set_xscale('log')
            eixo.set_xlabel('Tempo (escala logarítmica)')
        else:
            eixo.set_xlabel('Tempo (segundos)')
        
        # Adicionar legenda
        eixo.legend()
        eixo.grid(True, alpha=0.3)
        
        # Salvar figura
        caminhoSalvar = "graficos/comparativos/comparacao_ew.png"
        figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
        plt.close(figura)
        
        print(f"Gráfico comparativo E[W] salvo: {caminhoSalvar}")
        return caminhoSalvar
    
    def ajustarModeloTendencia(self, x, y, tipoModelo='exponencial'):
        """
        Ajusta um modelo de tendência aos dados.
        
        Parâmetros:
            x (array): Valores do eixo x
            y (array): Valores do eixo y
            tipoModelo (str): Tipo de modelo a ser ajustado ('linear', 'exponencial', 'logaritmico')
        
        Retorna:
            tuple: (parâmetros do modelo, função do modelo, R²)
        """
        try:
            if tipoModelo == 'linear':
                # Modelo linear: y = a*x + b
                def modeloLinear(x, a, b):
                    return a * x + b
                
                parametros, covariancia = curve_fit(modeloLinear, x, y)
                rQuadrado = 1 - np.sum((y - modeloLinear(x, *parametros))**2) / np.sum((y - np.mean(y))**2)
                return parametros, modeloLinear, rQuadrado
                
            elif tipoModelo == 'exponencial':
                # Modelo exponencial: y = a * exp(b*x)
                def modeloExponencial(x, a, b):
                    return a * np.exp(b * x)
                
                parametros, covariancia = curve_fit(modeloExponencial, x, y, p0=[1, 0.1])
                rQuadrado = 1 - np.sum((y - modeloExponencial(x, *parametros))**2) / np.sum((y - np.mean(y))**2)
                return parametros, modeloExponencial, rQuadrado
                
            elif tipoModelo == 'logaritmico':
                # Modelo logarítmico: y = a * ln(x) + b
                def modeloLogaritmico(x, a, b):
                    return a * np.log(x) + b
                
                # Filtrar valores onde x > 0 para evitar problemas com log(0)
                mascara = x > 0
                xFiltrado = x[mascara]
                yFiltrado = y[mascara]
                
                if len(xFiltrado) > 2:
                    parametros, covariancia = curve_fit(modeloLogaritmico, xFiltrado, yFiltrado)
                    rQuadrado = 1 - np.sum((yFiltrado - modeloLogaritmico(xFiltrado, *parametros))**2) / np.sum((yFiltrado - np.mean(yFiltrado))**2)
                    return parametros, modeloLogaritmico, rQuadrado
                
            return None, None, 0
            
        except Exception as e:
            print(f"Erro ao ajustar modelo: {e}")
            return None, None, 0
    
    def gerarGraficosComTendencia(self):
        """Gera gráficos com curvas de tendência para E[N] e E[W]."""
        figuras = []
        self.expressoesAnaliticas = {}
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            # Preparar dados
            tempo = dados['Tempo'].values
            en = dados['NumeroMedioRequisicoes'].values
            ew = dados['TempoMedioEspera'].values
            
            # Ajustar modelos de tendência
            parametrosEN, modeloEN, r2EN = self.ajustarModeloTendencia(tempo, en, 'exponencial')
            parametrosEW, modeloEW, r2EW = self.ajustarModeloTendencia(tempo, ew, 'exponencial')
            
            # Armazenar expressões analíticas
            if parametrosEN is not None:
                aEN, bEN = parametrosEN
                self.expressoesAnaliticas[f"{nomeCenario}_EN"] = {
                    'expressao': f"{aEN:.6f} * exp({bEN:.6f} * t)",
                    'rQuadrado': r2EN
                }
            
            if parametrosEW is not None:
                aEW, bEW = parametrosEW
                self.expressoesAnaliticas[f"{nomeCenario}_EW"] = {
                    'expressao': f"{aEW:.6f} * exp({bEW:.6f} * t)",
                    'rQuadrado': r2EW
                }
            
            # Criar gráficos com tendência
            figura, (eixoEN, eixoEW) = plt.subplots(2, 1, figsize=(12, 10))
            figura.suptitle(f'Análise de Tendência - {nomeCenario}', fontweight='bold')
            
            # Gráfico de E[N] com tendência
            eixoEN.scatter(tempo, en, alpha=0.6, s=10, label='Dados')
            if parametrosEN is not None:
                tempoSuave = np.linspace(min(tempo), max(tempo), 100)
                enSuave = modeloEN(tempoSuave, *parametrosEN)
                eixoEN.plot(tempoSuave, enSuave, 'r-', linewidth=2, 
                           label=f'Tendência (R² = {r2EN:.4f})')
            eixoEN.set_title('E[N] com Tendência Exponencial')
            eixoEN.set_ylabel('E[N]')
            eixoEN.legend()
            eixoEN.grid(True, alpha=0.3)
            
            # Gráfico de E[W] com tendência
            eixoEW.scatter(tempo, ew, alpha=0.6, s=10, label='Dados', color='orange')
            if parametrosEW is not None:
                ewSuave = modeloEW(tempoSuave, *parametrosEW)
                eixoEW.plot(tempoSuave, ewSuave, 'r-', linewidth=2, 
                           label=f'Tendência (R² = {r2EW:.4f})')
            eixoEW.set_title('E[W] com Tendência Exponencial')
            eixoEW.set_ylabel('E[W]')
            eixoEW.set_xlabel('Tempo (segundos)')
            eixoEW.legend()
            eixoEW.grid(True, alpha=0.3)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar figura
            caminhoSalvar = f"graficos/tendencia/tendencia_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            print(f"Gráfico com tendência salvo: {caminhoSalvar}")
        
        return figuras
    
    def gerarGraficosAnaliseFila(self):
        """Gera gráficos de análise do tamanho da fila."""
        figuras = []
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            # Criar figura com dois subplots
            figura, (eixo1, eixo2) = plt.subplots(1, 2, figsize=(16, 6))
            figura.suptitle(f'Análise do Tamanho da Fila - {nomeCenario}', fontweight='bold')
            
            # Gráfico 1: Tamanho da fila vs tempo
            tempo = dados['Tempo']
            eixo1.scatter(tempo, dados['TamanhoFila'], alpha=0.6, s=10)
            eixo1.set_title('Evolução do Tamanho da Fila')
            eixo1.set_xlabel('Tempo (segundos)')
            eixo1.set_ylabel('Tamanho da Fila')
            eixo1.grid(True, alpha=0.3)
            
            # Gráfico 2: Histograma do tamanho da fila
            eixo2.hist(dados['TamanhoFila'], bins=50, alpha=0.7, edgecolor='black')
            eixo2.set_title('Distribuição do Tamanho da Fila')
            eixo2.set_xlabel('Tamanho da Fila')
            eixo2.set_ylabel('Frequência')
            eixo2.grid(True, alpha=0.3)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar figura
            caminhoSalvar = f"graficos/fila/analise_fila_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            print(f"Gráfico de análise de fila salvo: {caminhoSalvar}")
        
        return figuras
    
    def gerarGraficosFilaVsOcupacao(self):
        """Gera gráficos de tamanho da fila vs ocupação medida."""
        figuras = []
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            figura, eixo = plt.subplots(figsize=(12, 8))
            
            # Scatter plot de TamanhoFila vs Ocupacao
            scatter = eixo.scatter(dados['Ocupacao'], dados['TamanhoFila'], 
                                 c=dados['Tempo'], cmap='viridis', alpha=0.6, s=20)
            
            # Configurar título e labels
            eixo.set_title(f'Tamanho da Fila vs Ocupação - {nomeCenario}', fontweight='bold')
            eixo.set_xlabel('Ocupação')
            eixo.set_ylabel('Tamanho da Fila')
            
            # Adicionar barra de cores para o tempo
            barraCores = plt.colorbar(scatter)
            barraCores.set_label('Tempo (segundos)')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar figura
            caminhoSalvar = f"graficos/fila/fila_vs_ocupacao_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            print(f"Gráfico Fila vs Ocupação salvo: {caminhoSalvar}")
        
        return figuras
    
    def gerarGraficosDistribuicaoOcupacao(self):
        """Gera gráficos de distribuição da ocupação."""
        figuras = []
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            figura, (eixo1, eixo2) = plt.subplots(1, 2, figsize=(16, 6))
            figura.suptitle(f'Distribuição da Ocupação - {nomeCenario}', fontweight='bold')
            
            # Gráfico 1: Histograma da ocupação
            eixo1.hist(dados['Ocupacao'], bins=50, alpha=0.7, edgecolor='black')
            eixo1.set_title('Distribuição da Ocupação')
            eixo1.set_xlabel('Ocupação')
            eixo1.set_ylabel('Frequência')
            eixo1.grid(True, alpha=0.3)
            
            # Gráfico 2: Evolução da ocupação ao longo do tempo
            eixo2.scatter(dados['Tempo'], dados['Ocupacao'], alpha=0.6, s=10)
            eixo2.set_title('Evolução da Ocupação ao Longo do Tempo')
            eixo2.set_xlabel('Tempo (segundos)')
            eixo2.set_ylabel('Ocupação')
            eixo2.grid(True, alpha=0.3)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar figura
            caminhoSalvar = f"graficos/ocupacao/distribuicao_ocupacao_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            print(f"Gráfico de distribuição de ocupação salvo: {caminhoSalvar}")
        
        return figuras
    
    def gerarMatrizesCorrelacao(self):
        """Gera matrizes de correlação para cada cenário."""
        figuras = []
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            # Calcular matriz de correlação
            matrizCorrelacao = dados.corr()
            
            # Criar heatmap
            figura, eixo = plt.subplots(figsize=(10, 8))
            sns.heatmap(matrizCorrelacao, annot=True, cmap='coolwarm', center=0, 
                       square=True, ax=eixo, fmt='.3f')
            eixo.set_title(f'Matriz de Correlação - {nomeCenario}', fontweight='bold')
            
            # Ajustar layout
            plt.tight_layout()
            
            # Salvar figura
            caminhoSalvar = f"graficos/correlacao/matriz_correlacao_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            print(f"Matriz de correlação salva: {caminhoSalvar}")
        
        return figuras
    
    def gerarGraficosDistribuicaoConjunta(self):
        """Gera gráficos de distribuição conjunta para pares de variáveis."""
        figuras = []
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            # Selecionar apenas as colunas numéricas
            dadosNumericos = dados.select_dtypes(include=[np.number])
            
            # Criar pairplot (amostrar para não sobrecarregar)
            if len(dadosNumericos) > 1000:
                dadosAmostra = dadosNumericos.sample(1000)
            else:
                dadosAmostra = dadosNumericos
            
            figura = sns.pairplot(dadosAmostra, diag_kind='kde', plot_kws={'alpha': 0.6, 's': 10})
            figura.fig.suptitle(f'Distribuição Conjunta das Variáveis - {nomeCenario}', 
                              y=1.02, fontweight='bold')
            
            # Salvar figura
            caminhoSalvar = f"graficos/distribuicao/distribuicao_conjunta_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura.fig)
            figuras.append(caminhoSalvar)
            
            print(f"Gráfico de distribuição conjunta salvo: {caminhoSalvar}")
        
        return figuras
    
    def gerarGraficosRelesVariaveis(self):
        """Gera gráficos das relações entre variáveis."""
        figuras = []
        
        for nomeCenario, dados in self.dadosPorCenario.items():
            # Criar figura com múltiplos subplots
            figura, eixos = plt.subplots(2, 2, figsize=(16, 12))
            figura.suptitle(f'Relações entre Variáveis - {nomeCenario}', fontweight='bold')
            
            # Gráfico 1: E[N] vs Ocupação
            eixos[0, 0].scatter(dados['Ocupacao'], dados['NumeroMedioRequisicoes'], 
                              alpha=0.6, s=10, c=dados['Tempo'], cmap='viridis')
            eixos[0, 0].set_title('E[N] vs Ocupação')
            eixos[0, 0].set_xlabel('Ocupação')
            eixos[0, 0].set_ylabel('E[N]')
            
            # Gráfico 2: E[W] vs Ocupação
            eixos[0, 1].scatter(dados['Ocupacao'], dados['TempoMedioEspera'], 
                              alpha=0.6, s=10, c=dados['Tempo'], cmap='viridis')
            eixos[0, 1].set_title('E[W] vs Ocupação')
            eixos[0, 1].set_xlabel('Ocupação')
            eixos[0, 1].set_ylabel('E[W]')
            
            # Gráfico 3: E[N] vs Tamanho da Fila
            eixos[1, 0].scatter(dados['TamanhoFila'], dados['NumeroMedioRequisicoes'], 
                              alpha=0.6, s=10, c=dados['Tempo'], cmap='viridis')
            eixos[1, 0].set_title('E[N] vs Tamanho da Fila')
            eixos[1, 0].set_xlabel('Tamanho da Fila')
            eixos[1, 0].set_ylabel('E[N]')
            
            # Gráfico 4: E[W] vs Tamanho da Fila
            eixos[1, 1].scatter(dados['TamanhoFila'], dados['TempoMedioEspera'], 
                              alpha=0.6, s=10, c=dados['Tempo'], cmap='viridis')
            eixos[1, 1].set_title('E[W] vs Tamanho da Fila')
            eixos[1, 1].set_xlabel('Tamanho da Fila')
            eixos[1, 1].set_ylabel('E[W]')
            
            # Adicionar barra de cores para o tempo
            figura.subplots_adjust(right=0.85)
            cbar_ax = figura.add_axes([0.88, 0.15, 0.02, 0.7])
            scatter = eixos[0, 0].collections[0]
            figura.colorbar(scatter, cax=cbar_ax).set_label('Tempo (segundos)')
            
            # Ajustar layout
            plt.tight_layout(rect=[0, 0, 0.85, 1])
            
            # Salvar figura
            caminhoSalvar = f"graficos/relacoes/relacoes_variaveis_{nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            print(f"Gráfico de relações entre variáveis salvo: {caminhoSalvar}")
        
        return figuras
    
    def gerarRelatorioExpressoesAnaliticas(self):
        """Gera um relatório com as expressões analíticas das tendências."""
        if not self.expressoesAnaliticas:
            print("Nenhuma expressão analítica disponível para relatório.")
            return None
        
        caminhoRelatorio = "expressoes_analiticas.txt"
        
        with open(caminhoRelatorio, 'w') as arquivo:
            arquivo.write("EXPRESSÕES ANALÍTICAS DAS TENDÊNCIAS\n")
            arquivo.write("====================================\n\n")
            
            for chave, valor in self.expressoesAnaliticas.items():
                arquivo.write(f"{chave}:\n")
                arquivo.write(f"  Expressão: {valor['expressao']}\n")
                arquivo.write(f"  R²: {valor['rQuadrado']:.6f}\n\n")
        
        print(f"Relatório de expressões analíticas salvo: {caminhoRelatorio}")
        return caminhoRelatorio
    
    def executarAnaliseCompleta(self, caminhosArquivos):
        """
        Executa toda a análise dos dados de simulação.
        
        Parámetros:
            caminhosArquivos (list): Lista de caminhos para os arquivos CSV
        """
        print("Iniciando análise científica completa...")
        print(f"Usando escala logarítmica no tempo: {self.usarEscalaLogTempo}")
        
        # Carregar dados
        self.carregarDados(caminhosArquivos)
        
        if not self.dadosPorCenario:
            print("Nenhum dado foi carregado. Verifique os caminhos dos arquivos.")
            return
        
        # Gerar gráficos
        print("\nGerando gráficos individuais...")
        self.gerarGraficosEN_EW_porCenario()
        
        print("\nGerando gráficos sobrepostos...")
        self.gerarGraficosSobrepostosEN_EW()
        
        print("\nGerando gráficos comparativos...")
        self.gerarGraficosComparativosEN()
        self.gerarGraficosComparativosEW()
        
        print("\nGerando gráficos com tendência...")
        self.gerarGraficosComTendencia()
        
        print("\nGerando análise de fila...")
        self.gerarGraficosAnaliseFila()
        
        print("\nGerando gráficos de fila vs ocupação...")
        self.gerarGraficosFilaVsOcupacao()
        
        print("\nGerando gráficos de distribuição de ocupação...")
        self.gerarGraficosDistribuicaoOcupacao()
        
        print("\nGerando matrizes de correlação...")
        self.gerarMatrizesCorrelacao()
        
        print("\nGerando gráficos de distribuição conjunta...")
        self.gerarGraficosDistribuicaoConjunta()
        
        print("\nGerando gráficos de relações entre variáveis...")
        self.gerarGraficosRelesVariaveis()
        
        print("\nGerando relatório de expressões analíticas...")
        self.gerarRelatorioExpressoesAnaliticas()
        
        print("\nAnálise concluída! Verifique os diretórios:")
        print("- graficos/individuais/ para gráficos por cenário")
        print("- graficos/comparativos/ para gráficos comparativos")
        print("- graficos/tendencia/ para gráficos com tendência")
        print("- graficos/fila/ para análise do tamanho da fila")
        print("- graficos/ocupacao/ para análise da ocupação")
        print("- graficos/correlacao/ para matrizes de correlação")
        print("- graficos/distribuicao/ para distribuições conjuntas")
        print("- graficos/relacoes/ para relações entre variáveis")


def main():
    """Função principal do script."""
    # Lista de arquivos de dados
    arquivosDados = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv', 
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    # Criar analisador (altere para True para usar escala logarítmica no tempo)
    analisador = AnaliseCientificaSimulacao(usarEscalaLogTempo=False)
    
    # Executar análise completa
    analisador.executarAnaliseCompleta(arquivosDados)


if __name__ == "__main__":
    main()
