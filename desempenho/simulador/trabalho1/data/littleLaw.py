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
from pathlib import Path


class DadosSimulacao:
    """
    Classe para representar e analisar os dados de um cenário de simulação.
    Responsável por carregar, processar e analisar estatisticamente os dados.
    """
    
    def __init__(self, caminhoArquivo):
        """
        Inicializa o objeto com os dados de um cenário de simulação.
        
        Parâmetros:
            caminhoArquivo (str): Caminho para o arquivo CSV com os dados
        """
        self.caminhoArquivo = caminhoArquivo
        self.nomeCenario = self.extrairNomeCenario(caminhoArquivo)
        self.dataframe = None
        self.metricasEstatisticas = {}
        self.carregarDados()
        self.calcularMetricasEstatisticas()
    
    def extrairNomeCenario(self, caminhoArquivo):
        """
        Extrai o nome do cenário a partir do nome do arquivo.
        
        Parâmetros:
            caminhoArquivo (str): Caminho para o arquivo
            
        Retorna:
            str: Nome do cenário (ex: "ocupacao_080")
        """
        nomeArquivo = os.path.basename(caminhoArquivo)
        return nomeArquivo.replace('dados_', '').replace('.csv', '')
    
    def carregarDados(self):
        """Carrega os dados do arquivo CSV para um DataFrame."""
        try:
            self.dataframe = pd.read_csv(self.caminhoArquivo)
            print(f"Dados carregados: {self.nomeCenario} ({len(self.dataframe)} registros)")
        except Exception as erro:
            print(f"Erro ao carregar {self.caminhoArquivo}: {erro}")
            self.dataframe = pd.DataFrame()
    
    def calcularMetricasEstatisticas(self):
        """Calcula métricas estatísticas para todas as colunas numéricas."""
        if self.dataframe.empty:
            return
            
        colunasNumericas = self.dataframe.select_dtypes(include=[np.number]).columns
        
        for coluna in colunasNumericas:
            dados = self.dataframe[coluna]
            self.metricasEstatisticas[coluna] = {
                'media': np.mean(dados),
                'mediana': np.median(dados),
                'desvioPadrao': np.std(dados),
                'variancia': np.var(dados),
                'minimo': np.min(dados),
                'maximo': np.max(dados),
                'assimetria': stats.skew(dados),
                'curtose': stats.kurtosis(dados),
                'quantil_05': np.quantile(dados, 0.05),
                'quantil_25': np.quantile(dados, 0.25),
                'quantil_75': np.quantile(dados, 0.75),
                'quantil_95': np.quantile(dados, 0.95)
            }
    
    def gerarRelatorioEstatistico(self, caminhoSaida):
        """
        Gera um relatório estatístico completo e salva em arquivo.
        
        Parâmetros:
            caminhoSaida (str): Caminho para salvar o relatório
        """
        if not self.metricasEstatisticas:
            return
            
        with open(caminhoSaida, 'w') as arquivo:
            arquivo.write(f"Relatório Estatístico - {self.nomeCenario}\n")
            arquivo.write("=" * 50 + "\n\n")
            
            for coluna, metricas in self.metricasEstatisticas.items():
                arquivo.write(f"Coluna: {coluna}\n")
                arquivo.write("-" * 30 + "\n")
                
                for nomeMetrica, valor in metricas.items():
                    arquivo.write(f"{nomeMetrica}: {valor:.6f}\n")
                
                arquivo.write("\n")
            
            # Informações adicionais sobre a distribuição
            arquivo.write("Análise de Distribuição:\n")
            arquivo.write("-" * 30 + "\n")
            
            for coluna in self.dataframe.select_dtypes(include=[np.number]).columns:
                dados = self.dataframe[coluna]
                estatisticaShapiro, valorPShapiro = stats.shapiro(dados)
                
                arquivo.write(f"{coluna} - Teste de Shapiro-Wilk:\n")
                arquivo.write(f"Estatística: {estatisticaShapiro:.6f}, Valor-p: {valorPShapiro:.6f}\n")
                
                if valorPShapiro > 0.05:
                    arquivo.write("Distribuição normal (p > 0.05)\n")
                else:
                    arquivo.write("Distribuição não normal (p <= 0.05)\n")
                
                arquivo.write("\n")
        
        print(f"Relatório estatístico salvo: {caminhoSaida}")


class AnalisadorExploratorio:
    """
    Classe para realizar análise exploratória dos dados de simulação.
    Gera visualizações e relatórios para compreensão dos dados.
    """
    
    def __init__(self, dadosSimulacao):
        """
        Inicializa o analisador com os dados de simulação.
        
        Parâmetros:
            dadosSimulacao (list): Lista de objetos DadosSimulacao
        """
        self.dadosSimulacao = dadosSimulacao
        self.configurarVisualizacoes()
        
        # Criar diretórios para saída
        self.criarDiretoriosSaida()
    
    def configurarVisualizacoes(self):
        """Configura o estilo padrão para visualizações."""
        plt.style.use('default')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    def criarDiretoriosSaida(self):
        """Cria os diretórios necessários para armazenar as saídas."""
        diretorios = ['eda', 'graficos/individuais', 'graficos/comparativos', 'graficos/matriz']
        
        for diretorio in diretorios:
            Path(diretorio).mkdir(parents=True, exist_ok=True)
    
    def gerarBoxplotsPorCenario(self):
        """Gera boxplots para cada variável numérica por cenário."""
        figuras = []
        
        for dados in self.dadosSimulacao:
            if dados.dataframe.empty:
                continue
                
            colunasNumericas = dados.dataframe.select_dtypes(include=[np.number]).columns
            
            for coluna in colunasNumericas:
                figura, eixo = plt.subplots(figsize=(10, 6))
                sns.boxplot(y=dados.dataframe[coluna], ax=eixo)
                eixo.set_title(f'Boxplot - {coluna} - {dados.nomeCenario}')
                eixo.set_ylabel(coluna)
                
                caminhoSalvar = f"graficos/individuais/boxplot_{coluna}_{dados.nomeCenario}.png"
                figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
                plt.close(figura)
                figuras.append(caminhoSalvar)
        
        return figuras
    
    def gerarHistogramasPorCenario(self):
        """Gera histogramas para cada variável numérica por cenário."""
        figuras = []
        
        for dados in self.dadosSimulacao:
            if dados.dataframe.empty:
                continue
                
            colunasNumericas = dados.dataframe.select_dtypes(include=[np.number]).columns
            
            for coluna in colunasNumericas:
                figura, eixos = plt.subplots(1, 2, figsize=(15, 6))
                
                # Histograma com curva de densidade
                sns.histplot(dados.dataframe[coluna], kde=True, ax=eixos[0])
                eixos[0].set_title(f'Histograma - {coluna} - {dados.nomeCenario}')
                eixos[0].set_xlabel(coluna)
                eixos[0].set_ylabel('Frequência')
                
                # Gráfico Q-Q para verificar normalidade
                stats.probplot(dados.dataframe[coluna], plot=eixos[1])
                eixos[1].set_title(f'Q-Q Plot - {coluna} - {dados.nomeCenario}')
                
                caminhoSalvar = f"graficos/individuais/histograma_{coluna}_{dados.nomeCenario}.png"
                figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
                plt.close(figura)
                figuras.append(caminhoSalvar)
        
        return figuras
    
    def gerarGraficosEvolucaoTemporal(self):
        """Gera gráficos de evolução temporal para as métricas principais."""
        figuras = []
        
        for dados in self.dadosSimulacao:
            if dados.dataframe.empty:
                continue
                
            metricas = ['NumeroMedioRequisicoes', 'TempoMedioEspera', 'Ocupacao']
            
            for metrica in metricas:
                if metrica not in dados.dataframe.columns:
                    continue
                    
                figura, eixo = plt.subplots(figsize=(12, 6))
                eixo.plot(dados.dataframe['Tempo'], dados.dataframe[metrica], linewidth=2)
                eixo.set_title(f'Evolução Temporal - {metrica} - {dados.nomeCenario}')
                eixo.set_xlabel('Tempo (segundos)')
                eixo.set_ylabel(metrica)
                eixo.grid(True, alpha=0.3)
                
                # Adicionar escala logarítmica se necessário
                if dados.dataframe[metrica].max() / dados.dataframe[metrica].min() > 100:
                    eixo.set_yscale('log')
                    eixo.set_title(f'Evolução Temporal (Escala Log) - {metrica} - {dados.nomeCenario}')
                
                caminhoSalvar = f"graficos/individuais/evolucao_{metrica}_{dados.nomeCenario}.png"
                figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
                plt.close(figura)
                figuras.append(caminhoSalvar)
        
        return figuras
    
    def gerarGraficosComparativos(self):
        """Gera gráficos comparativos entre os diferentes cenários."""
        figuras = []
        
        # Preparar dados combinados
        dadosCombinados = []
        for dados in self.dadosSimulacao:
            if not dados.dataframe.empty:
                dfTemp = dados.dataframe.copy()
                dfTemp['Cenario'] = dados.nomeCenario
                dadosCombinados.append(dfTemp)
        
        if not dadosCombinados:
            return figuras
            
        dfCombinado = pd.concat(dadosCombinados, ignore_index=True)
        
        # Gráficos comparativos para cada métrica
        metricas = ['NumeroMedioRequisicoes', 'TempoMedioEspera', 'Ocupacao']
        
        for metrica in metricas:
            if metrica not in dfCombinado.columns:
                continue
                
            # Boxplot comparativo
            figura, eixo = plt.subplots(figsize=(12, 8))
            sns.boxplot(x='Cenario', y=metrica, data=dfCombinado, ax=eixo)
            eixo.set_title(f'Distribuição de {metrica} por Cenário')
            eixo.tick_params(axis='x', rotation=45)
            
            caminhoSalvar = f"graficos/comparativos/boxplot_comparativo_{metrica}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
            
            # Violin plot comparativo
            figura, eixo = plt.subplots(figsize=(12, 8))
            sns.violinplot(x='Cenario', y=metrica, data=dfCombinado, ax=eixo)
            eixo.set_title(f'Distribuição de {metrica} por Cenário (Violin Plot)')
            eixo.tick_params(axis='x', rotation=45)
            
            caminhoSalvar = f"graficos/comparativos/violin_comparativo_{metrica}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
        
        return figuras
    
    def gerarMatrizCorrelacao(self):
        """Gera matrizes de correlação para cada cenário."""
        figuras = []
        
        for dados in self.dadosSimulacao:
            if dados.dataframe.empty:
                continue
                
            colunasNumericas = dados.dataframe.select_dtypes(include=[np.number]).columns
            
            if len(colunasNumericas) < 2:
                continue
                
            # Calcular matriz de correlação
            matrizCorrelacao = dados.dataframe[colunasNumericas].corr()
            
            # Gerar heatmap
            figura, eixo = plt.subplots(figsize=(10, 8))
            sns.heatmap(matrizCorrelacao, annot=True, cmap='coolwarm', center=0, 
                       square=True, ax=eixo)
            eixo.set_title(f'Matriz de Correlação - {dados.nomeCenario}')
            
            caminhoSalvar = f"graficos/matriz/correlacao_{dados.nomeCenario}.png"
            figura.savefig(caminhoSalvar, dpi=300, bbox_inches='tight')
            plt.close(figura)
            figuras.append(caminhoSalvar)
        
        return figuras
    
    def gerarRelatorioComparativo(self):
        """Gera um relatório comparativo entre todos os cenários."""
        caminhoRelatorio = "eda/relatorio_comparativo.md"
        
        with open(caminhoRelatorio, 'w') as arquivo:
            arquivo.write("# Relatório Comparativo - Métricas de Simulação\n\n")
            
            # Tabela comparativa de métricas
            arquivo.write("## Métricas Estatísticas por Cenário\n\n")
            
            for dados in self.dadosSimulacao:
                if dados.dataframe.empty:
                    continue
                    
                arquivo.write(f"### {dados.nomeCenario}\n\n")
                
                for coluna, metricas in dados.metricasEstatisticas.items():
                    arquivo.write(f"#### {coluna}\n")
                    
                    # Criar tabela Markdown
                    arquivo.write("| Métrica | Valor |\n")
                    arquivo.write("|---------|-------|\n")
                    
                    for nomeMetrica, valor in metricas.items():
                        arquivo.write(f"| {nomeMetrica} | {valor:.6f} |\n")
                    
                    arquivo.write("\n")
            
            # Análise comparativa
            arquivo.write("## Análise Comparativa\n\n")
            
            metricasPrincipais = ['NumeroMedioRequisicoes', 'TempoMedioEspera', 'Ocupacao']
            
            for metrica in metricasPrincipais:
                valores = []
                cenarios = []
                
                for dados in self.dadosSimulacao:
                    if not dados.dataframe.empty and metrica in dados.metricasEstatisticas:
                        valores.append(dados.metricasEstatisticas[metrica]['media'])
                        cenarios.append(dados.nomeCenario)
                
                if valores:
                    arquivo.write(f"### {metrica}\n")
                    arquivo.write(f"- Média entre cenários: {np.mean(valores):.6f}\n")
                    arquivo.write(f"- Desvio padrão entre cenários: {np.std(valores):.6f}\n")
                    arquivo.write(f"- Variação entre máximo e mínimo: {((max(valores) - min(valores)) / min(valores)) * 100:.2f}%\n\n")
        
        print(f"Relatório comparativo salvo: {caminhoRelatorio}")
        return caminhoRelatorio
    
    def executarAnaliseCompleta(self):
        """Executa toda a análise exploratória e gera todos os relatórios."""
        print("Iniciando análise exploratória completa...")
        
        # Gerar relatórios estatísticos individuais
        for dados in self.dadosSimulacao:
            if not dados.dataframe.empty:
                caminhoRelatorio = f"eda/relatorio_estatistico_{dados.nomeCenario}.txt"
                dados.gerarRelatorioEstatistico(caminhoRelatorio)
        
        # Gerar visualizações
        print("Gerando visualizações...")
        self.gerarBoxplotsPorCenario()
        self.gerarHistogramasPorCenario()
        self.gerarGraficosEvolucaoTemporal()
        self.gerarGraficosComparativos()
        self.gerarMatrizCorrelacao()
        
        # Gerar relatório comparativo
        self.gerarRelatorioComparativo()
        
        print("Análise exploratória concluída!")


def main():
    """Função principal do script."""
    # Lista de arquivos de dados
    arquivosDados = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv', 
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    # Verificar quais arquivos existem
    arquivosExistentes = [arquivo for arquivo in arquivosDados if os.path.exists(arquivo)]
    
    if not arquivosExistentes:
        print("Nenhum arquivo de dados encontrado. Execute primeiro o simulador em C.")
        return
    
    print(f"Arquivos encontrados: {len(arquivosExistentes)}")
    
    # Carregar dados de todos os cenários
    dadosSimulacao = [DadosSimulacao(arquivo) for arquivo in arquivosExistentes]
    
    # Executar análise exploratória
    analisador = AnalisadorExploratorio(dadosSimulacao)
    analisador.executarAnaliseCompleta()
    
    print("\nAnálise concluída! Verifique os diretórios:")
    print("- eda/ para relatórios estatísticos")
    print("- graficos/individuais/ para gráficos por cenário")
    print("- graficos/comparativos/ para gráficos comparativos")
    print("- graficos/matriz/ para matrizes de correlação")


if __name__ == "__main__":
    main()