import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider
from itertools import product, combinations
import os

# Configuração anti-travamento
os.environ['MPLBACKEND'] = 'TkAgg'  # Ou 'Qt5Agg' se preferir

# Hipercubo mágico (projeção inteligente)
def plot_hypercube(n, ax):
    ax.clear()
    
    # Gerar vértices do hipercubo nD
    vertices = np.array(list(product([0, 1], repeat=n)))
    
    # Projeção 3D inteligente (preserva estrutura)
    if n > 3:
        # Técnica: Força as primeiras 3 dimensões a serem as principais
        projection = np.zeros((n, 3))
        projection[:3, :3] = np.eye(3)
        vertices_3d = vertices @ projection
    else:
        vertices_3d = np.pad(vertices, ((0, 0), (0, 3 - n)))[:, :3]
    
    # Plotar arestas
    for edge in combinations(vertices, 2):
        if np.sum(np.abs(edge[0] - edge[1])) == 1:  # Apenas arestas unitárias
            start, end = vertices_3d[vertices.tolist().index(list(edge[0]))], vertices_3d[vertices.tolist().index(list(edge[1]))]
            ax.plot(*zip(start, end), color='dodgerblue', linewidth=2, alpha=0.8)
    
    # Configuração estética
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_zlim(-0.5, 1.5)
    ax.set_title(f'Hipercubo {n}D', fontsize=14, pad=20)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

# Configuração da figura
fig = plt.figure(figsize=(14, 7))
ax_3d = fig.add_subplot(121, projection='3d')
ax_plot = fig.add_subplot(122)
plt.subplots_adjust(bottom=0.2)

# Slider profissional
slider_ax = plt.axes([0.25, 0.1, 0.5, 0.03])
dim_slider = Slider(
    ax=slider_ax,
    label='Dimensões',
    valmin=1,
    valmax=20,
    valinit=3,
    valstep=1,
    color='#FF5722'
)

# Gráfico do volume (melhorado)
def update_volume_plot(n):
    ax_plot.clear()
    dims = np.arange(1, 21)
    epsilon = 0.1
    v_int = (1 - 2*epsilon) ** dims
    v_bord = 1 - v_int
    
    ax_plot.semilogy(dims, v_int, 'r-', lw=2, label='Volume Interno')
    ax_plot.semilogy(dims, v_bord, 'b-', lw=2, label='Volume Borda')
    ax_plot.axvline(n, color='k', linestyle='--', alpha=0.5)
    ax_plot.plot(n, v_int[n-1], 'ro', markersize=8)
    ax_plot.plot(n, v_bord[n-1], 'bo', markersize=8)
    
    ax_plot.set_title('Maldição da Dimensionalidade', pad=20)
    ax_plot.set_xlabel('Dimensões')
    ax_plot.set_ylabel('Volume (log)')
    ax_plot.legend()
    ax_plot.grid(True, which="both", ls="-", alpha=0.3)
    ax_plot.set_ylim(1e-10, 1)

# Atualização conjunta
def update(val):
    n = int(dim_slider.val)
    plot_hypercube(n, ax_3d)
    update_volume_plot(n)
    fig.canvas.draw_idle()

dim_slider.on_changed(update)

# Inicialização
update(3)
plt.show()