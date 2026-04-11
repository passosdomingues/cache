import os
import csv
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import defaultdict

class BenchmarkAnalyzer:
    """
    @brief Classe responsável por processar dados de benchmark e gerar tabelas/gráficos.
    @details Lê os dados de tempo e score biológico do arquivo CSV e gera artefatos de saída.
    """
    def __init__(self, arquivo_csv):
        """
        @brief Construtor da classe.
        @param arquivo_csv Caminho para o arquivo CSV de entrada.
        """
        self.arquivo_csv = arquivo_csv
        self.dados_tempo_dp = defaultdict(list)
        self.dados_tempo_guloso = defaultdict(list)
        self.dados_score_dp = defaultdict(list)
        self.dados_score_guloso = defaultdict(list)
        self.tamanhos = []

    def carregar_dados(self):
        """
        @brief Lê o arquivo CSV contendo os benchmarks.
        @details Espera o formato: Tamanho, Tempo_DP, Tempo_Guloso, Score_DP, Score_Guloso
        """
        try:
            with open(self.arquivo_csv, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Salta o cabeçalho
                for row in reader:
                    # Verifica se temos todas as colunas necessárias
                    if len(row) < 5:
                        print("Erro: O CSV deve ter 5 colunas: Tamanho, Tempo_DP, Tempo_Guloso, Score_DP, Score_Guloso")
                        exit(1)
                    
                    tamanho = int(row[0])
                    self.dados_tempo_dp[tamanho].append(float(row[1]))
                    self.dados_tempo_guloso[tamanho].append(float(row[2]))
                    self.dados_score_dp[tamanho].append(float(row[3]))
                    self.dados_score_guloso[tamanho].append(float(row[4]))
            
            self.tamanhos = np.array(sorted(self.dados_tempo_dp.keys()))
        except FileNotFoundError:
            print(f"Erro: O arquivo {self.arquivo_csv} não foi encontrado. Rode o testador primeiro.")
            exit(1)

    def gerar_tabela_scores(self, caminho_saida):
        """
        @brief Gera um arquivo CSV/TXT com as pontuações para fácil importação no LaTeX.
        @param caminho_saida Diretório/arquivo onde a tabela será salva.
        """
        with open(caminho_saida, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Tamanho", "Score_DP (Otimo)", "Score_Guloso", "Diferenca"])
            
            for t in self.tamanhos:
                # Pega a média dos scores para aquele tamanho de instância
                score_dp_avg = np.mean(self.dados_score_dp[t])
                score_guloso_avg = np.mean(self.dados_score_guloso[t])
                dif = score_dp_avg - score_guloso_avg
                writer.writerow([t, int(score_dp_avg), int(score_guloso_avg), int(dif)])
                
        print(f"[OK] Tabela de Scores extraída para LaTeX: {caminho_saida}")

    def plotar_graficos(self, pasta_saida):
        """
        @brief Gera os gráficos de desempenho acadêmicos em tons de cinza.
        @param pasta_saida Diretório onde os gráficos serão salvos.
        """
        tempo_dp_avg = np.array([np.mean(self.dados_tempo_dp[t]) for t in self.tamanhos])
        tempo_guloso_avg = np.array([np.mean(self.dados_tempo_guloso[t]) for t in self.tamanhos])
        memoria_dp = (self.tamanhos ** 2) * 8 / 1024 
        memoria_guloso = np.array([1] * len(self.tamanhos))

        sns.set_theme(style="ticks", rc={"axes.grid": True, "grid.linestyle": ":", "grid.color": "#cccccc"})
        sns.set_context("paper", font_scale=1.2)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        estilo_dp = {'color': 'black', 'linestyle': '-', 'marker': 'o', 'markersize': 6, 'linewidth': 1.5}
        estilo_guloso = {'color': '#555555', 'linestyle': '--', 'marker': 's', 'markersize': 6, 'linewidth': 1.5}

        # Gráfico 1: Tempo
        axes[0].plot(self.tamanhos, tempo_dp_avg, label='Prog. Dinâmica', **estilo_dp)
        axes[0].plot(self.tamanhos, tempo_guloso_avg, label='Algoritmo Guloso', **estilo_guloso)
        axes[0].set_title('Tempo de Execução vs. Tamanho da Entrada', fontweight='bold')
        axes[0].set_xlabel('Tamanho da Entrada (N)')
        axes[0].set_ylabel('Tempo (Segundos)')
        axes[0].legend(frameon=True, edgecolor='black')

        # Gráfico 2: Memória
        axes[1].plot(self.tamanhos, memoria_dp, label='Prog. Dinâmica', **estilo_dp)
        axes[1].plot(self.tamanhos, memoria_guloso, label='Algoritmo Guloso', **estilo_guloso)
        axes[1].set_title('Consumo de Memória vs. Tamanho', fontweight='bold')
        axes[1].set_xlabel('Tamanho da Entrada (N)')
        axes[1].set_ylabel('Memória (KB)')
        axes[1].set_yscale('log')
        axes[1].legend(frameon=True, edgecolor='black')

        sns.despine()
        plt.tight_layout()
        
        caminho_arquivo = os.path.join(pasta_saida, "desempenho_algoritmos_pb.png")
        plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight')
        print(f"[OK] Gráficos de alta qualidade salvos em: {caminho_arquivo}")


class AlgoritmoAnimator:
    """
    @brief Classe para gerar a animação didática (MP4) das decisões do Algoritmo Guloso.
    @details Anima um pareamento simples (match, mismatch, gap) passo a passo.
    """
    def __init__(self, s1="ATCGT", s2="AT-GT"):
        """
        @brief Construtor da animação.
        @param s1 Sequência de DNA primária.
        @param s2 Sequência de DNA secundária (alinhada).
        """
        self.s1 = s1
        self.s2 = s2
        self.n = len(s1)

    def gerar_video(self, caminho_saida):
        """
        @brief Renderiza o arquivo MP4 mostrando a dinâmica de decisão frame a frame.
        @param caminho_saida Caminho do arquivo de vídeo gerado.
        """
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.set_xlim(-1, self.n)
        ax.set_ylim(-1, 2)
        ax.axis('off')
        
        ax.text(self.n/2 - 0.5, 1.5, 'Dinâmica do Algoritmo Guloso', fontsize=16, ha='center', fontweight='bold')

        # Desenha as strings estáticas na tela
        textos_s1 = [ax.text(i, 0.8, self.s1[i], fontsize=20, ha='center', va='center') for i in range(self.n)]
        textos_s2 = [ax.text(i, 0.2, self.s2[i], fontsize=20, ha='center', va='center') for i in range(self.n)]
        
        status_texto = ax.text(self.n/2 - 0.5, -0.5, '', fontsize=14, ha='center', color='black')
        cursor = ax.add_patch(plt.Rectangle((-0.5, 0.0), 1, 1, fill=False, edgecolor='blue', lw=2, alpha=0))

        def animar(frame):
            if frame < self.n:
                # Atualiza a posição do cursor e torna visível
                cursor.set_xy((frame - 0.4, 0.0))
                cursor.set_alpha(1)
                
                char_a = self.s1[frame]
                char_b = self.s2[frame]
                
                # Regras de Negócio (Score)
                if char_a == char_b and char_a != '-':
                    cor = 'green'
                    msg = f"Match perfeito (+2)"
                elif char_a == '-' or char_b == '-':
                    cor = 'orange'
                    msg = f"Gap inserido (-2)"
                else:
                    cor = 'red'
                    msg = f"Mismatch aceito (-1)"

                # Aplica as cores biológicas (taxonomia visual do professor)
                textos_s1[frame].set_color(cor)
                textos_s2[frame].set_color(cor)
                status_texto.set_text(msg)
                status_texto.set_color(cor)
            else:
                # Fim da animação
                cursor.set_alpha(0)
                status_texto.set_text("Alinhamento Concluído")
                status_texto.set_color('black')
                
            return textos_s1 + textos_s2 + [status_texto, cursor]

        # FuncAnimation gera os frames
        ani = animation.FuncAnimation(fig, animar, frames=self.n + 2, interval=1000, blit=True)
        
        # Salva o arquivo em MP4 usando o pacote FFMpeg
        try:
            ani.save(caminho_saida, writer='ffmpeg', fps=1)
            print(f"[OK] Animação em vídeo exportada com sucesso: {caminho_saida}")
        except Exception as e:
            print(f"[ALERTA] Não foi possível salvar o MP4. Verifique se o ffmpeg está instalado no sistema OS. Erro: {e}")


if __name__ == "__main__":
    print("Iniciando Operação Dupla Hélice - Módulo de Análise e Visão...\n")
    
    pasta_saida = "graficos"
    os.makedirs(pasta_saida, exist_ok=True)
    
    # 1. Pipeline de Benchmarking e Tabela LaTeX
    analyzer = BenchmarkAnalyzer('benchmarks.csv')
    analyzer.carregar_dados()
    analyzer.gerar_tabela_scores(os.path.join(pasta_saida, "tabela_scores.csv"))
    analyzer.plotar_graficos(pasta_saida)
    
    # 2. Pipeline de Animação (Vídeo)
    animator = AlgoritmoAnimator()
    animator.gerar_video(os.path.join(pasta_saida, "animacao_guloso.mp4"))
    
    print("\n[SISTEMA] Processamento tático concluído com êxito.")
