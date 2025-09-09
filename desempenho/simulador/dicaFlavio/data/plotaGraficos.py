import matplotlib.pyplot as plt
import numpy as np
import os

# Configuração dos arquivos
arquivos = ['ocupacao_80.0.dat', 'ocupacao_90.0.dat', 'ocupacao_95.0.dat', 'ocupacao_99.9.dat']
nomes_ocupacao = ['80%', '90%', '95%', '99.9%']

# Processar cada arquivo e criar gráfico individual
for i, (arquivo, ocupacao) in enumerate(zip(arquivos, nomes_ocupacao)):
    if not os.path.exists(arquivo):
        print(f"Arquivo {arquivo} não encontrado. Pulando...")
        continue
    
    # Ler dados do arquivo
    dados = np.loadtxt(arquivo)
    
    if dados.size == 0:
        print(f"Arquivo {arquivo} está vazio. Pulando...")
        continue
    
    # Extrair colunas
    tempo = dados[:, 0]
    E_N = dados[:, 1]
    E_W = dados[:, 2]
    
    # Criar figura para este cenário de ocupação
    plt.figure(figsize=(10, 6))
    
    # Plotar E[N] - Número médio de requisições
    plt.plot(tempo, E_N, color='blue', label='E[N] - Nº médio de requisições', linewidth=1.5)
    
    # Plotar E[W] - Tempo médio entre requisições
    plt.plot(tempo, E_W, color='red', label='E[W] - Tempo médio (segundos)', linewidth=1.5)
    
    # Configurar o gráfico
    plt.xlabel('Tempo (segundos)')
    plt.ylabel('Valor')
    plt.title(f'Evolução das Métricas - Ocupação {ocupacao}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Salvar gráfico individual
    nome_arquivo_imagem = f'ocupacao_{ocupacao.replace("%", "")}.png'
    plt.savefig(nome_arquivo_imagem, dpi=300)
    plt.close()
    
    print(f"Gráfico salvo como {nome_arquivo_imagem}")

# Análise estatística dos dados
print("\n=== ANÁLISE ESTATÍSTICA DOS DADOS ===")
for i, (arquivo, ocupacao) in enumerate(zip(arquivos, nomes_ocupacao)):
    if not os.path.exists(arquivo):
        continue
    
    dados = np.loadtxt(arquivo)
    if dados.size == 0:
        continue
    
    # Estatísticas do E[N]
    en_media = np.mean(dados[:, 1])
    en_std = np.std(dados[:, 1])
    en_max = np.max(dados[:, 1])
    en_min = np.min(dados[:, 1])
    
    # Estatísticas do E[W]
    ew_media = np.mean(dados[:, 2])
    ew_std = np.std(dados[:, 2])
    ew_max = np.max(dados[:, 2])
    ew_min = np.min(dados[:, 2])
    
    print(f"\n--- Ocupação {ocupacao} ---")
    print(f"E[N] - Média: {en_media:.4f}, Desvio padrão: {en_std:.4f}, Mínimo: {en_min:.4f}, Máximo: {en_max:.4f}")
    print(f"E[W] - Média: {ew_media:.4f}, Desvio padrão: {ew_std:.4f}, Mínimo: {ew_min:.4f}, Máximo: {ew_max:.4f}")

# Verificar a Lei de Little (E[N] = λ * E[W])
print("\n=== VERIFICAÇÃO DA LEI DE LITTLE ===")
for i, (arquivo, ocupacao) in enumerate(zip(arquivos, nomes_ocupacao)):
    if not os.path.exists(arquivo):
        continue
    
    dados = np.loadtxt(arquivo)
    if dados.size == 0:
        continue
    
    # Calcular lambda (taxa de chegada) a partir da ocupação
    ocupacao_valor = float(ocupacao.replace('%', '')) / 100
    # Assumindo tempo médio de serviço = 1 segundo (como definido na simulação)
    lambda_valor = ocupacao_valor / 1.0
    
    # Valores médios de E[N] e E[W]
    en_media = np.mean(dados[:, 1])
    ew_media = np.mean(dados[:, 2])
    
    # Verificar a lei de Little
    diferenca = en_media - (lambda_valor * ew_media)
    erro_percentual = (diferenca / en_media) * 100 if en_media != 0 else 0
    
    print(f"\n--- Ocupação {ocupacao} ---")
    print(f"λ (taxa de chegada): {lambda_valor:.4f}")
    print(f"E[N] médio: {en_media:.4f}")
    print(f"E[W] médio: {ew_media:.4f}")
    print(f"λ * E[W]: {lambda_valor * ew_media:.4f}")
    print(f"Diferença (E[N] - λ*E[W]): {diferenca:.4f}")
    print(f"Erro percentual: {erro_percentual:.2f}%")

print("\nAnálise concluída. Gráficos individuais gerados para cada cenário de ocupação.")
