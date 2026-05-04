#!/usr/bin/env python3
import subprocess
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

def main():
    sizes = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    num_runs = 5
    
    dijkstra_means, dijkstra_stds = [], []
    duan_means, duan_stds = [], []
    outro_means, outro_stds = [], []

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    base_exec = os.path.join("codigo base", "base")
    if not os.path.exists(base_exec):
        subprocess.run(['make', '-C', 'codigo base'], check=True)

    venv_python = os.path.join("venv", "bin", "python3")
    generator_script = os.path.join("gerador de instancias", "generator.py")

    output_dir = "relatorio_tp03"
    os.makedirs(output_dir, exist_ok=True)
    tex_path = os.path.join(output_dir, 'tabela_estatistica.tex')
    
    with open(tex_path, 'w') as f_tex:
        f_tex.write("\\begin{table}[htbp]\n")
        f_tex.write("\\centering\n")
        f_tex.write("\\caption{Tempo de Execução (média $\\pm$ desvio padrão em segundos) para 5 execuções independentes.}\n")
        f_tex.write("\\label{tab:estatistica}\n")
        f_tex.write("\\resizebox{\\textwidth}{!}{\n")
        f_tex.write("\\begin{tabular}{rccc}\n")
        f_tex.write("\\toprule\n")
        f_tex.write("\\textbf{Vértices ($N$)} & \\textbf{Dijkstra} & \\textbf{BMSSP (Duan)} & \\textbf{Bellman-Ford (Outro)} \\\\\n")
        f_tex.write("\\midrule\n")

        for n in sizes:
            d_times, u_times, o_times = [], [], []
            print(f"Executando N={n} ({num_runs} repetições)...")
            
            for _ in range(num_runs):
                with open('temp.dat', 'wb') as f:
                    subprocess.run([venv_python, generator_script, 'erdos', str(n), '0.5'], stdout=f, check=True)
                
                result = subprocess.run([base_exec, 'temp.dat'], capture_output=True, text=True, check=True)
                
                for line in result.stdout.splitlines():
                    parts = line.split()
                    if len(parts) >= 3:
                        if line.startswith('Dijkstra:'): d_times.append(float(parts[2]))
                        elif line.startswith('Duan:'): u_times.append(float(parts[2]))
                        elif line.startswith('Outro:'): o_times.append(float(parts[2]))
            
            d_mean, d_std = np.mean(d_times), np.std(d_times)
            u_mean, u_std = np.mean(u_times), np.std(u_times)
            o_mean, o_std = np.mean(o_times), np.std(o_times)
            
            dijkstra_means.append(d_mean); dijkstra_stds.append(d_std)
            duan_means.append(u_mean); duan_stds.append(u_std)
            outro_means.append(o_mean); outro_stds.append(o_std)

            f_tex.write(f"{n} & {d_mean:.4f} $\\pm$ {d_std:.4f} & {u_mean:.4f} $\\pm$ {u_std:.4f} & {o_mean:.4f} $\\pm$ {o_std:.4f} \\\\\n")

        f_tex.write("\\bottomrule\n")
        f_tex.write("\\end{tabular}\n")
        f_tex.write("}\n")
        f_tex.write("\\end{table}\n")

    print("Gerando gráfico...")
    plt.figure(figsize=(10, 6))
    plt.errorbar(sizes, dijkstra_means, yerr=dijkstra_stds, label='Dijkstra', fmt='-o', color='black', capsize=4)
    plt.errorbar(sizes, duan_means, yerr=duan_stds, label='Duan (BMSSP)', fmt='--s', color='black', capsize=4)
    plt.errorbar(sizes, outro_means, yerr=outro_stds, label='Bellman-Ford', fmt=':^', color='black', capsize=4)

    plt.xlabel('Número de Vértices (N)')
    plt.ylabel('Tempo de Execução Médio (s)')
    plt.title('Desempenho dos Algoritmos SSSP (5 execuções)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)

    output_path = os.path.join(output_dir, 'desempenho_algoritmos_pb.png')
    plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo com sucesso em: {output_path}")
    
    if os.path.exists('temp.dat'):
        os.remove('temp.dat')

if __name__ == "__main__":
    main()
