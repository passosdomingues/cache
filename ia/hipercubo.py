import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider
from itertools import product

# Configuração do estilo
plt.style.use('dark_background')

# Gera os vértices do tesseract (cubo 4D)
def generate_tesseract():
    vertices = list(product([0, 1], repeat=4))
    return np.array(vertices)

# Projeção 4D -> 3D com perspectiva
def project_4d_to_3d(vertices, w_perspective=0.5):
    scale = 1 / (1 + w_perspective * vertices[:, 3])
    return vertices[:, :3] * scale[:, np.newaxis]

# Conexões do tesseract (arestas)
def get_tesseract_edges():
    edges = []
    vertices = generate_tesseract()
    for i, v1 in enumerate(vertices):
        for j, v2 in enumerate(vertices):
            if np.sum(np.abs(v1 - v2)) == 1:
                edges.append((v1, v2))
    return edges

# Configuração da figura
fig = plt.figure(figsize=(14, 8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.2)

# Slider para perspectiva 4D
slider_ax = plt.axes([0.25, 0.1, 0.5, 0.03])
w_slider = Slider(
    ax=slider_ax,
    label='Perspectiva 4D',
    valmin=0,
    valmax=1,
    valinit=0.5,
    valstep=0.01,
    color='#FF5722'
)

# Plot inicial
def update(val):
    w = w_slider.val
    ax.clear()
    
    # Projeta vértices
    vertices = generate_tesseract()
    vertices_3d = project_4d_to_3d(vertices, w)
    
    # Divide em cubo interno (w=0) e externo (w=1)
    inner_cube = vertices_3d[vertices[:, 3] == 0]
    outer_cube = vertices_3d[vertices[:, 3] == 1]
    
    # Desenha cubos
    for cube, size, color in [(inner_cube, 8, 'cyan'), (outer_cube, 6, 'magenta')]:
        if len(cube) > 0:
            ax.scatter(cube[:, 0], cube[:, 1], cube[:, 2], s=size**2, c=color, depthshade=False)
    
    # Desenha arestas
    edges = get_tesseract_edges()
    for edge in edges:
        start, end = project_4d_to_3d(np.array(edge), w)
        ax.plot(*zip(start, end), color='white', alpha=0.4, lw=1.5)
    
    # Liga cubos (arestas da 4ª dimensão)
    for v_inner in inner_cube:
        for v_outer in outer_cube:
            if np.sum(np.abs(v_inner - v_outer[:3])) == 0:
                ax.plot(*zip(v_inner, v_outer), '--', color='yellow', alpha=0.3)
    
    ax.set_title('Tesseract (Hipercubo 4D)', fontsize=16, pad=20)
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_zlim(-0.5, 1.5)
    ax.grid(False)

w_slider.on_changed(update)
update(0.5)  # Inicializa
plt.show()