import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.cluster import KMeans
import glob
import os

sns.set(style="whitegrid", palette="muted", font_scale=1.2)
data_path = "./results"
output_path = "./plots"
os.makedirs(output_path, exist_ok=True)

csv_files = sorted(glob.glob(os.path.join(data_path, "run_rho*.csv")))

def save_scatter(df, x_col, y_col, hue_col='timestamp', title=None, filename=None):
    plt.figure(figsize=(8,6))
    scatter = plt.scatter(df[x_col], df[y_col], c=df[hue_col], cmap='viridis', alpha=0.7)
    plt.colorbar(scatter, label=hue_col)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    if title:
        plt.title(title)
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def save_hist(df, col, title=None, filename=None):
    plt.figure(figsize=(8,6))
    sns.histplot(df[col], kde=True, bins=30)
    plt.xlabel(col)
    plt.ylabel("Frequency")
    if title:
        plt.title(title)
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def save_box(df, col, title=None, filename=None):
    plt.figure(figsize=(6,6))
    sns.boxplot(y=df[col])
    plt.title(title if title else col)
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def save_pairplot(df, cols, filename):
    g = sns.pairplot(df[cols], diag_kind="kde", corner=True)
    g.fig.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def save_heatmap(df, cols, filename):
    corr = df[cols].corr()
    plt.figure(figsize=(8,6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm')
    plt.title("Correlation Heatmap")
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def error_analysis(df, cols):
    stats = {}
    for col in cols:
        mean = df[col].mean()
        std = df[col].std()
        rel_error = std / mean if mean != 0 else np.nan
        stats[col] = {'mean': mean, 'std': std, 'rel_error': rel_error}
    return pd.DataFrame(stats)

def propagate_error(df, col1, col2):
    std1 = df[col1].std()
    std2 = df[col2].std()
    mean1 = df[col1].mean()
    mean2 = df[col2].mean()
    rel_err1 = std1 / mean1 if mean1 != 0 else 0
    rel_err2 = std2 / mean2 if mean2 != 0 else 0
    return np.sqrt(rel_err1**2 + rel_err2**2)

for file in csv_files:
    df = pd.read_csv(file)
    base_name = os.path.splitext(os.path.basename(file))[0]

    # Scatter plots
    save_scatter(df, 'timestamp', 'EN', title=f'{base_name} - EN vs Time', filename=f'{output_path}/{base_name}_EN_vs_time.png')
    save_scatter(df, 'timestamp', 'EW', title=f'{base_name} - EW vs Time', filename=f'{output_path}/{base_name}_EW_vs_time.png')
    for queue in ['queue0','queue1','queue2']:
        save_scatter(df, 'timestamp', queue, title=f'{base_name} - {queue} vs Time', filename=f'{output_path}/{base_name}_{queue}_vs_time.png')
        save_scatter(df, queue, 'EN', title=f'{base_name} - EN vs {queue}', filename=f'{output_path}/{base_name}_EN_vs_{queue}.png')
        save_scatter(df, queue, 'EW', title=f'{base_name} - EW vs {queue}', filename=f'{output_path}/{base_name}_EW_vs_{queue}.png')
    save_scatter(df, 'lambda', 'EN', title=f'{base_name} - EN vs lambda', filename=f'{output_path}/{base_name}_EN_vs_lambda.png')
    save_scatter(df, 'lambda', 'EW', title=f'{base_name} - EW vs lambda', filename=f'{output_path}/{base_name}_EW_vs_lambda.png')

    # Histograms
    for col in ['EN','EW','queue0','queue1','queue2','lambda']:
        save_hist(df, col, title=f'{base_name} - {col} histogram', filename=f'{output_path}/{base_name}_{col}_hist.png')

    # Boxplots
    for col in ['EN','EW','queue0','queue1','queue2','lambda']:
        save_box(df, col, title=f'{base_name} - {col} boxplot', filename=f'{output_path}/{base_name}_{col}_box.png')

    # Pairplots
    save_pairplot(df, ['EN','EW','queue0','queue1','queue2','lambda'], filename=f'{output_path}/{base_name}_pairplot.png')

    # Heatmap
    save_heatmap(df, ['EN','EW','queue0','queue1','queue2','lambda'], filename=f'{output_path}/{base_name}_heatmap.png')

    # Error analysis
    err_stats = error_analysis(df, ['EN','EW'])
    err_stats.to_csv(f'{output_path}/{base_name}_error_stats.csv')
    combined_rel_err = propagate_error(df, 'EN','EW')
    with open(f'{output_path}/{base_name}_propagated_error.txt','w') as f:
        f.write(f'Propagated relative error (EN + EW): {combined_rel_err}\n')

    # KMeans clustering
    features = df[['EN','EW','queue0','queue1','queue2']].values
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['cluster'] = kmeans.fit_predict(features)
    plt.figure(figsize=(8,6))
    sns.scatterplot(x='EN', y='EW', hue='cluster', palette='Set2', data=df)
    plt.title(f'{base_name} - EN vs EW clusters')
    plt.savefig(f'{output_path}/{base_name}_EN_EW_clusters.png', dpi=300, bbox_inches='tight')
    plt.close()

