import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from typing import Optional, Dict, Any, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configurações globais
RANDOM_STATE = 42
DPI = 300  # Resolução para salvar imagens
plt.style.use('default')  # Estilo padrão para os gráficos

class ProblemFramer:
    """
    Classe para enquadrar o problema e entender o panorama geral do projeto.
    
    Responsável por coletar e validar o enunciado do problema e metadados do dataset,
    guiando o usuário no enquadramento orientado a negócios necessário antes da modelagem.
    
    @param dataset_dataframe: pandas.DataFrame opcional contendo o dataset para análise
    @param target_column_name: nome opcional da coluna target se já conhecido
    @param id_column_name: nome opcional da coluna ID se presente (usada para verificar unicidade)
    """
    
    def __init__(self, dataset_dataframe: Optional[pd.DataFrame] = None,
                 target_column_name: Optional[str] = None,
                 id_column_name: Optional[str] = None):
        self.dataset_dataframe = dataset_dataframe
        self.target_column_name = target_column_name
        self.id_column_name = id_column_name
        
        # Funções auxiliares
        self._is_categorical = lambda series: (series.dtype == object) or (series.nunique() <= 30)
        self._safe_div = lambda a, b: a / b if b != 0 else np.nan
        
    def ingest_dataset(self, dataframe: pd.DataFrame, 
                      target_column_name: Optional[str] = None, 
                      id_column_name: Optional[str] = None) -> None:
        """
        Ingere o dataset no framer.
        
        @param dataframe: pandas.DataFrame com os dados
        @param target_column_name: string opcional nomeando a coluna target
        @param id_column_name: string opcional nomeando a coluna ID
        @return: None
        """
        self.dataset_dataframe = dataframe.copy()
        if target_column_name:
            self.target_column_name = target_column_name
        if id_column_name:
            self.id_column_name = id_column_name
            
    def summarize_dataset_metadata(self) -> Dict[str, Any]:
        """
        Retorna um dicionário com metadados principais do dataset úteis para enquadramento.
        
        @return: dict com chaves: numRows, numColumns, missingValuesByColumn, 
                 sampleOfRows, idColumnIsUnique
        """
        if self.dataset_dataframe is None:
            raise ValueError("Nenhum dataset carregado. Chame ingest_dataset() primeiro.")
            
        num_rows = len(self.dataset_dataframe)
        num_columns = len(self.dataset_dataframe.columns)
        missing_values = self.dataset_dataframe.isnull().sum().to_dict()
        sample_of_rows = self.dataset_dataframe.head(5)
        
        id_column_is_unique = None
        if self.id_column_name and self.id_column_name in self.dataset_dataframe.columns:
            id_column_is_unique = self.dataset_dataframe[self.id_column_name].is_unique
            
        return {
            "numRows": num_rows,
            "numColumns": num_columns,
            "missingValuesByColumn": missing_values,
            "sampleOfRows": sample_of_rows,
            "idColumnIsUnique": id_column_is_unique
        }
    
    def infer_task_type(self) -> Dict[str, Any]:
        """
        Infere se a tarefa é classificação, regressão, clustering ou multilabel
        baseado na coluna target se disponível.
        
        @return: dict com chaves: inferredTask, isTargetCategorical, 
                 classDistribution (se classificação)
        """
        if self.dataset_dataframe is None or self.target_column_name is None:
            return {"inferredTask": "unknown", "isTargetCategorical": None, "classDistribution": None}
            
        if self.target_column_name not in self.dataset_dataframe.columns:
            raise KeyError(f"Coluna target '{self.target_column_name}' não encontrada no dataset")
            
        target_series = self.dataset_dataframe[self.target_column_name]
        is_categorical_flag = bool(self._is_categorical(target_series))
        inferred_task = "classification" if is_categorical_flag else "regression"
        result = {"inferredTask": inferred_task, "isTargetCategorical": is_categorical_flag}
        
        if is_categorical_flag:
            distribution = target_series.value_counts(dropna=False).to_dict()
            class_counts = distribution
            total_count = len(target_series)
            class_proportions = {k: (v, round(self._safe_div(v, total_count), 4)) 
                                for k, v in class_counts.items()}
            result["classDistribution"] = class_proportions
            
        return result
        
    def propose_performance_metrics(self) -> Dict[str, str]:
        """
        Propõe métricas de performance apropriadas dada a tarefa inferida.
        
        @return: dict com chaves: recommendedPrimaryMetric, recommendedSecondaryMetric, rationale
        """
        inferred = self.infer_task_type().get("inferredTask", "unknown")
        
        if inferred == "classification":
            primary_metric = "roc_auc"
            secondary_metric = "f1_score"
            rationale_text = "Use ROC AUC para separabilidade geral e F1 para balanceamento de classes e trade-offs operacionais."
        elif inferred == "regression":
            primary_metric = "root_mean_squared_error"
            secondary_metric = "mean_absolute_error"
            rationale_text = "Use RMSE para penalizar grandes erros e MAE para erro médio interpretável."
        elif inferred == "unknown":
            primary_metric = "tbd"
            secondary_metric = "tbd"
            rationale_text = "Incapaz de inferir tarefa: forneça coluna target ou especifique tipo de tarefa."
        else:
            primary_metric = "tbd"
            secondary_metric = "tbd"
            rationale_text = "Para clustering considere silhouette_score e adjusted_mutual_info_score se existir ground truth."
            
        return {
            "recommendedPrimaryMetric": primary_metric,
            "recommendedSecondaryMetric": secondary_metric,
            "rationale": rationale_text
        }
        
    def suggest_minimum_acceptable_performance(self, 
                                              baseline_performance_value: Optional[float] = None) -> Dict[str, Any]:
        """
        Sugere um limite mínimo de performance baseado no dataset e em uma baseline fornecida.
        
        @param baseline_performance_value: valor numérico opcional da baseline (ex: modelo existente ou heurística)
        @return: dict com suggestedMinimum e explanation
        """
        inferred = self.infer_task_type().get("inferredTask", "unknown")
        
        if baseline_performance_value is None:
            suggestion = None
            explanation = "Nenhuma baseline fornecida; por favor forneça performance existente ou target de negócio para sugerir mínimo."
        else:
            if inferred == "classification":
                suggested_minimum = round(min(0.99, baseline_performance_value * 1.02), 4)  # pequena melhoria
                suggestion = suggested_minimum
                explanation = "Sugiro melhorar a baseline atual em ~2% relativo quando viável."
            elif inferred == "regression":
                suggested_minimum = round(max(0.0, baseline_performance_value * 0.98), 4)  # RMSE menor é melhor
                suggestion = suggested_minimum
                explanation = "Sugiro diminuir RMSE em ~2% relativo quando viável."
            else:
                suggestion = None
                explanation = "Tarefa desconhecida; não posso propor mínimo numérico automaticamente."
                
        return {"suggestedMinimum": suggestion, "explanation": explanation}
        
    def list_checklist_items_not_applicable(self, custom_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna justificativas para itens do checklist que podem ser intencionalmente pulados.
        
        @param custom_notes: texto opcional explicando por que itens são pulados
        @return: dict com uma única chave 'justifications' contendo a nota
        """
        note_text = custom_notes if custom_notes else "Nenhuma exceção registrada."
        return {"justifications": note_text}


class DataManager:
    """
    Gerencia a aquisição e preparação inicial dos dados.
    
    Responsabilidade: listar necessidades, encontrar fontes, verificar armazenamento,
    baixar via kagglehub (preferido), normalizar para CSV, anonimizar colunas protegidas,
    inspecionar tamanho & tipo, e criar um conjunto de teste hold-out armazenado em memória.
    
    @param workspace_directory_path: diretório onde downloads e arquivos processados serão mantidos
    @param preferred_kaggle_dataset_slug: slug do dataset Kaggle para tentar download via kagglehub
    @param desired_test_ratio: fração dos dados a serem reservados para o conjunto de teste final
    @param random_state: semente inteira para splits reprodutíveis
    """
    
    def __init__(self, workspace_directory_path: str = "wdbc_workspace",
                 preferred_kaggle_dataset_slug: str = "uciml/breast-cancer-wisconsin-data",
                 desired_test_ratio: float = 0.2,
                 random_state: int = RANDOM_STATE):
        self.workspace_directory_path = Path(workspace_directory_path)
        self.raw_data_directory_path = self.workspace_directory_path / "raw"
        self.processed_data_directory_path = self.workspace_directory_path / "processed"
        self.preferred_kaggle_dataset_slug = preferred_kaggle_dataset_slug
        self.desired_test_ratio = desired_test_ratio
        self.random_state = random_state
        
        # Outputs a serem preenchidos
        self.dataFrame: Optional[pd.DataFrame] = None
        self.target_variable: Optional[str] = None
        self.X_train: Optional[pd.DataFrame] = None
        self.X_test: Optional[pd.DataFrame] = None
        self.y_train: Optional[pd.Series] = None
        self.y_test: Optional[pd.Series] = None
        
        # Funções auxiliares
        self._is_csv = lambda filename: str(filename).lower().endswith(".csv")
        self._make_path = lambda p: Path(p)
        self._ensure_dir = lambda p: Path(p).mkdir(parents=True, exist_ok=True)
        
    def _ensure_workspace(self) -> None:
        """Cria diretórios do workspace se faltantes."""
        for directory in (self.workspace_directory_path, self.raw_data_directory_path, self.processed_data_directory_path):
            self._ensure_dir(directory)
            
    def _fallback_load_from_sklearn(self) -> pd.DataFrame:
        """
        Carregador fallback usando o dataset breast cancer embutido no sklearn.
        
        @return: pandas.DataFrame com dados e uma coluna 'target'
        """
        payload = load_breast_cancer()
        df = pd.DataFrame(payload.data, columns=[c.replace(" ", "_") for c in payload.feature_names])
        df["target"] = payload.target
        return df
        
    def _identify_and_set_target(self, dataframe: pd.DataFrame, 
                                potential_targets: Optional[List[str]] = None) -> str:
        """
        Identifica coluna target de nomes comuns ou fallback para última coluna.
        
        @param dataframe: pandas.DataFrame para inspecionar
        @param potential_targets: lista opcional de nomes candidatos
        @return: nome da coluna target escolhida
        """
        potential_targets = potential_targets or ['target', 'diagnosis', 'class', 'outcome']
        for candidate in potential_targets:
            if candidate in dataframe.columns:
                return candidate
        fallback = dataframe.columns[-1]
        return fallback
        
    def _encode_target_if_needed(self, y_series: pd.Series) -> pd.Series:
        """
        Codifica labels string para numérico (ex: 'M'/'B' -> 1/0). Retorna série transformada.
        
        @param y_series: pandas.Series com valores target
        @return: pandas.Series codificada (int/float)
        """
        if y_series.dtype == object or y_series.dtype.name == "category":
            unique_vals = y_series.unique()
            mapping = {v: i for i, v in enumerate(sorted(unique_vals))}
            return y_series.map(lambda v: mapping[v]).astype(int)
        return y_series
        
    def get_data(self) -> None:
        """
        Adquire e prepara o dataset de acordo com o checklist.
        
        Passos executados de acordo com o checklist de projeto.
        Preenche self.dataFrame, self.targetVariable, e splits de treino/teste.
        """
        print("1. Listando os dados que você precisa e quanto você precisa.")
        print("   Necessário: Dados de diagnóstico de câncer de mama com 30 características numéricas computadas de imagens FNA. Necessário pelo menos várias centenas de amostras para validação cruzada robusta.")
        
        print("\n2. Encontrando e documentando onde você pode obter esses dados.")
        print(f"   Fonte preferida: Dataset Kaggle slug: {self.preferred_kaggle_dataset_slug}")
        
        print("\n3. Verificando quanto espaço vai ocupar.")
        print("   Tamanho esperado: muito pequeno (dezenas a centenas de KB). Sobrecarga de armazenamento negligenciável.")
        
        print("\n4. Verificando obrigações legais e obtendo autorização se necessário.")
        print("   Dataset tipicamente sob CC BY 4.0 (cópias UCI/Kaggle). Reveja licença se redistribuindo ou comercializando.")
        
        print("\n5. Obtendo autorizações de acesso.")
        print("   Método de acesso: kagglehub (não precisa de kaggle.json). Se usando API oficial Kaggle, garanta kaggle.json presente ou env vars configuradas.")
        
        print("\n6. Criando workspace (com espaço de armazenamento suficiente).")
        self._ensure_workspace()
        
        print("\n7. Obtendo os dados.")
        try:
            # Tentativa de download via kagglehub
            # Se falhar, carrega do sklearn
            self.dataFrame = self._fallback_load_from_sklearn()
            print("   Dataset carregado do sklearn (load_breast_cancer)...")
        except Exception as e:
            print(f"   Erro no download: {e}")
            print("   Carregando dataset de fallback do sklearn...")
            self.dataFrame = self._fallback_load_from_sklearn()
            
        print("\n8. Convertendo os dados para um formato que você pode manipular facilmente (sem mudar os dados em si).")
        print("   Usando pandas DataFrame como representação canônica em memória.")
        
        print("\n9. Garantindo que informações sensíveis sejam deletadas ou protegidas (ex: anonimizadas).")
        # placeholder: WDBC não tem PII, mas demonstra API
        # self.dataFrame = self._anonymize_columns_if_needed(self.dataFrame, columnsToMask=[])  # adaptar conforme necessário
        
        print("\n10. Verificando o tamanho e tipo dos dados (série temporal, amostra, geográfica, etc.).")
        rows_count, cols_count = self.dataFrame.shape
        print(f"   Tipo de dados: Tabular. Amostras: {rows_count}, Características (incluindo target se presente): {cols_count}")
        
        print("\n11. Amostrando um conjunto de teste, colocando de lado e nunca olhando (sem data snooping!).")
        # identificar target
        self.target_variable = self._identify_and_set_target(self.dataFrame)
        # separar X/y
        X = self.dataFrame.drop(columns=[self.target_variable])
        y = self.dataFrame[self.target_variable]
        
        # codificar target se strings categóricas
        y_encoded = self._encode_target_if_needed(y)
        
        # estratificar se classificação (poucos valores únicos)
        is_classification = True if y_encoded.nunique() <= 20 and y_encoded.dtype in [np.int64, np.int32, np.int16, np.int8] else False
        stratify_arg = y_encoded if is_classification else None
        
        # realizar split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y_encoded, test_size=self.desired_test_ratio, 
            random_state=self.random_state, stratify=stratify_arg)
            
        print(f"   Conjunto de teste criado com {len(self.y_test)} amostras ({int(self.desired_test_ratio*100)}% do total).")


class ExploratoryAnalyzer:
    """
    Realiza análise exploratória completa em um pandas DataFrame e produz
    diagnósticos, visualizações e um dicionário de descobertas conciso.
    
    @param dataset_dataframe: pandas.DataFrame contendo o dataset para explorar
    @param target_column_name: nome opcional da coluna target (se None será inferido)
    @param sample_max_rows: máximo de linhas para manter para visualizações interativas
    @param random_state: semente inteira para reprodutibilidade de amostragem
    """
    
    def __init__(self, dataset_dataframe: pd.DataFrame,
                 target_column_name: Optional[str] = None,
                 sample_max_rows: int = 1000,
                 random_state: int = RANDOM_STATE):
        self.dataset_dataframe = dataset_dataframe
        self.target_column_name = target_column_name
        self.sample_max_rows = sample_max_rows
        self.random_state = random_state
        self.findings_summary: Dict[str, Any] = {}
        
        # Funções auxiliares
        self._is_categorical = lambda series: (series.dtype == object) or (series.nunique() <= 30)
        self._safe_div = lambda a, b: a / b if b != 0 else np.nan
        self._sample_df = lambda df: df.sample(n=min(len(df), self.sample_max_rows), 
                                              random_state=self.random_state)
                                              
    def create_exploration_copy(self) -> pd.DataFrame:
        """
        Cria uma cópia do dataframe para exploração e opcionalmente reduz amostra.
        
        @return: pandas.DataFrame cópia para exploração
        """
        df_copy = self.dataset_dataframe.copy()
        if len(df_copy) > self.sample_max_rows:
            print(f"   Dataset grande ({len(df_copy)} linhas), amostrando até {self.sample_max_rows} linhas para EDA interativa")
            df_copy = self._sample_df(df_copy)
        else:
            print("   Dataset em tamanho manejável; usando cópia completa para exploração")
        print(f"   Cópia criada com shape: {df_copy.shape}")
        return df_copy
        
    def summarize_schema_and_missing(self, df_explore: pd.DataFrame) -> pd.DataFrame:
        """
        Produz resumo de schema com tipos e estatísticas de valores ausentes.
        
        @param df_explore: pandas.DataFrame usado para exploração
        @return: pandas.DataFrame com colunas: name, dtype, missing_count, missing_pct, unique_count
        """
        print("3. Estudando cada atributo: nome, tipo, % missing, ruído estimado, utilidade preliminar")
        col_names = []
        col_types = []
        missing_counts = []
        missing_pcts = []
        unique_counts = []
        
        for col in df_explore.columns:
            col_names.append(col)
            col_types.append(str(df_explore[col].dtype))
            missing_count = int(df_explore[col].isnull().sum())
            missing_counts.append(missing_count)
            missing_pcts.append(round(self._safe_div(missing_count, len(df_explore)) * 100, 3))
            unique_counts.append(int(df_explore[col].nunique(dropna=True)))
            
        schema_df = pd.DataFrame({
            "name": col_names,
            "dtype": col_types,
            "missing_count": missing_counts,
            "missing_pct": missing_pcts,
            "unique_count": unique_counts
        }).sort_values(by="missing_pct", ascending=False).reset_index(drop=True)
        
        return schema_df
        
    def describe_numeric_and_categorical(self, df_explore: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Mostra estatísticas descritivas separadamente para atributos numéricos e categóricos.
        
        @param df_explore: pandas.DataFrame usado para exploração
        @return: tupla(numeric_description_df, categorical_description_df)
        """
        print("   Estatísticas descritivas para atributos numéricos e categóricos")
        numeric_df = df_explore.select_dtypes(include=[np.number])
        categorical_df = df_explore.select_dtypes(exclude=[np.number])
        
        num_desc = numeric_df.describe().T
        cat_desc = categorical_df.describe().T if not categorical_df.empty else pd.DataFrame()
        
        return num_desc, cat_desc
        
    def identify_target_and_distribution(self, df_explore: pd.DataFrame) -> Dict[str, Any]:
        """
        Identifica coluna target e retorna suas estatísticas de distribuição básicas.
        
        @param df_explore: pandas.DataFrame usado para exploração
        @return: dict com targetColumn, isCategorical, valueCounts (se categórico) ou summary stats
        """
        print("4. Identificando o(s) atributo(s) alvo para tarefas supervisionadas")
        if self.target_column_name and self.target_column_name in df_explore.columns:
            chosen_target = self.target_column_name
            print(f"   Target informado: {chosen_target}")
        else:
            candidates = ['target', 'diagnosis', 'class', 'outcome']
            chosen_target = next((c for c in candidates if c in df_explore.columns), df_explore.columns[-1])
            print(f"   Target inferido: {chosen_target}")
            
        target_series = df_explore[chosen_target]
        is_categorical_flag = self._is_categorical(target_series)
        distribution_info = None
        
        if is_categorical_flag:
            value_counts = target_series.value_counts(dropna=False)
            distribution_info = value_counts.to_dict()
            print(f"   Target categórico detectado com distribuição: {distribution_info}")
        else:
            distribution_info = target_series.describe().to_dict()
            print(f"   Target numérico detectado com estatísticas: {distribution_info}")
            
        self.findings_summary["targetColumn"] = chosen_target
        self.findings_summary["targetIsCategorical"] = is_categorical_flag
        self.findings_summary["targetDistributionSample"] = distribution_info
        
        # Visualização
        print("   Visualizando distribuição do target")
        plt.figure(figsize=(6, 4))
        if is_categorical_flag:
            sns.countplot(x=chosen_target, data=df_explore)
            plt.title("Distribuição da Variável Target")
        else:
            sns.histplot(target_series, kde=True)
            plt.title("Distribuição da Variável Target (numérica)")
        plt.tight_layout()
        
        # Salvar figura
        plt.savefig("target_distribution.png", dpi=DPI, bbox_inches='tight')
        plt.show()
        
        return {
            "targetColumn": chosen_target, 
            "isCategorical": is_categorical_flag, 
            "distribution": distribution_info
        }
        
    def plot_numeric_feature_distributions(self, df_explore: pd.DataFrame, 
                                          exclude_columns: Optional[List[str]] = None) -> None:
        """
        Plota histogramas com KDE para características numéricas, pulando colunas excluídas.
        
        @param df_explore: pandas.DataFrame usado para exploração
        @param exclude_columns: lista opcional de colunas para excluir do plot
        """
        print("5. Visualizando atributos numéricos (histogramas + KDE)")
        exclude = set(exclude_columns or [])
        numeric_cols = [c for c in df_explore.select_dtypes(include=[np.number]).columns 
                       if c not in exclude]
                       
        if not numeric_cols:
            print("   Sem atributos numéricos para plotar")
            return
            
        cols_per_row = 3
        rows = (len(numeric_cols) + cols_per_row - 1) // cols_per_row
        fig, axes = plt.subplots(rows, cols_per_row, figsize=(5*cols_per_row, 4*rows))
        axes = axes.flatten()
        
        for i, feature in enumerate(numeric_cols):
            sns.histplot(df_explore[feature].dropna(), kde=True, ax=axes[i])
            axes[i].set_title(f"Distribuição de {feature}")
            
        for j in range(i+1, len(axes)):
            axes[j].set_visible(False)
            
        plt.tight_layout()
        
        # Salvar figura
        plt.savefig("numeric_features_distributions.png", dpi=DPI, bbox_inches='tight')
        plt.show()
        
    def compute_and_plot_correlations(self, df_explore: pd.DataFrame, 
                                    annotate_top_k: int = 10) -> pd.DataFrame:
        """
        Calcula matriz de correlação para atributos numéricos, plota heatmap e mostra
        correlações top com target.
        
        @param df_explore: pandas.DataFrame usado para exploração
        @param annotate_top_k: número de características top para listar correlacionadas com target
        @return: DataFrame da matriz de correlação
        """
        print("6. Estudando correlações entre atributos")
        df_numeric = df_explore.select_dtypes(include=[np.number]).copy()
        target = self.findings_summary.get("targetColumn", None)
        
        if target and target not in df_numeric.columns and target in df_explore.columns:
            # Codificar target para numérico para correlação se categórico
            print("   Target não numérico presente: codificando temporariamente para correlação")
            encoded = LabelEncoder().fit_transform(df_explore[target].astype(str))
            df_numeric[target] = encoded
            
        corr_matrix = df_numeric.corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, vmax=1.0, vmin=-1.0, cmap="vlag", 
                   square=True, linewidths=.5, cbar_kws={"shrink": .6})
        plt.title("Matriz de Correlação de Características")
        plt.tight_layout()
        
        # Salvar figura
        plt.savefig("correlation_matrix.png", dpi=DPI, bbox_inches='tight')
        plt.show()
        
        if target and target in corr_matrix.columns:
            abs_sorted = corr_matrix[target].abs().sort_values(ascending=False)
            top_correlated = abs_sorted.drop(labels=[target]).head(annotate_top_k)
            print("   Top características correlacionadas com target (correlação absoluta):")
            self.findings_summary["topCorrelatedWithTarget"] = top_correlated.to_dict()
            
        return corr_matrix
        
    def manual_problem_solving_notes(self) -> str:
        """
        Registra notas breves sobre como um especialista abordaria o problema manualmente.
        
        @return: string com esboço compacto de solução manual
        """
        print("7. Estudando como resolver manualmente com expertise de domínio")
        note = ("Inspeção especializada de padrões de raio, textura, perímetro e concavidade do núcleo "
                "para sinalizar malignidade; combinar thresholds em múltiplas características para decisões baseadas em regras simples.")
        print("   Esboço de solução manual registrado")
        self.findings_summary["manualSolutionSketch"] = note
        return note
        
    def propose_transformations_and_actions(self) -> Dict[str, Any]:
        """
        Sugere transformações promissoras e ações de pré-processamento.
        
        @return: dict com sugestões de transformações e racional
        """
        print("8. Identificando transformações promissoras")
        suggestions = {
            "standardization": "StandardScaler para características numéricas",
            "log_transform": "Considerar transformação log para características enviesadas (área, perímetro)",
            "pca": "PCA para redução de dimensionalidade ou visualização se muitas características correlacionadas",
            "encoding": "LabelEncoder para target e OneHot se novas características categóricas aparecerem",
            "classImbalanceHandling": "SMOTE ou perdas ponderadas por classe se desbalanceamento detectado"
        }
        print("   Transformações sugeridas")
        self.findings_summary["transformations"] = suggestions
        return suggestions
        
    def suggest_additional_data(self) -> List[str]:
        """
        Lista dados externos que melhorariam a modelagem.
        
        @return: lista de fontes de dados extras sugeridas
        """
        print("9. Identificando dados extras úteis")
        extras = ["demográficos_paciente", "histórico_familiar", "marcadores_genéticos", 
                 "metadados de imagem multi-modal"]
        print(f"   Dados adicionais sugeridos: {extras}")
        self.findings_summary["additionalDataSuggestions"] = extras
        return extras
        
    def document_findings(self) -> Dict[str, Any]:
        """
        Finaliza e retorna o dicionário de resumo de descobertas.
        
        @return: findings_summary dict
        """
        print("10. Documentando o que foi aprendido durante a EDA")
        # Entradas de resumo compactas
        self.findings_summary.setdefault("notes", "EDA completada; consulte chaves de descobertas para detalhes")
        return self.findings_summary
        
    def explore_data(self) -> Dict[str, Any]:
        """
        Orchestrador de alto nível executando o pipeline EDA usando os métodos atômicos acima.
        
        @return: findings_summary dict
        """
        df_for_exploration = self.create_exploration_copy()
        schema_summary = self.summarize_schema_and_missing(df_for_exploration)
        numeric_desc, categorical_desc = self.describe_numeric_and_categorical(df_for_exploration)
        target_info = self.identify_target_and_distribution(df_for_exploration)
        
        # Excluir colunas tipo id de plots e correlação
        exclude_columns = [c for c in df_for_exploration.columns if c.lower() == "id"]
        self.plot_numeric_feature_distributions(df_for_exploration, 
                                              exclude_columns=exclude_columns + [target_info["targetColumn"]])
                                              
        corr_matrix = self.compute_and_plot_correlations(df_for_exploration)
        self.manual_problem_solving_notes()
        self.propose_transformations_and_actions()
        self.suggest_additional_data()
        findings = self.document_findings()
        
        print("[DEBUG] Pipeline EDA completo")
        return findings


class DataPreparer:
    """
    Prepara os dados para melhor expor padrões subjacentes aos algoritmos de ML.
    
    Responsável por limpeza, engenharia de características, seleção e escalonamento.
    
    @param X_train: DataFrame com características de treino
    @param X_test: DataFrame com características de teste  
    @param y_train: Series com target de treino
    @param y_test: Series com target de teste
    @param target_variable: nome da coluna target
    """
    
    def __init__(self, X_train: pd.DataFrame, X_test: pd.DataFrame,
                 y_train: pd.Series, y_test: pd.Series,
                 target_variable: str):
        self.X_train = X_train.copy()
        self.X_test = X_test.copy()
        self.y_train = y_train.copy()
        self.y_test = y_test.copy()
        self.target_variable = target_variable
        
    def handle_missing_values(self, strategy: str = "median") -> None:
        """
        Preenche valores ausentes usando estratégia especificada.
        
        @param strategy: estratégia para preencher valores ausentes ("median", "mean", "mode", "drop")
        @return: None
        """
        print("Lidando com valores ausentes...")
        
        if strategy == "drop":
            # Remover linhas com valores ausentes
            self.X_train.dropna(inplace=True)
            self.X_test.dropna(inplace=True)
            # Ajustar y correspondente
            self.y_train = self.y_train.loc[self.X_train.index]
            self.y_test = self.y_test.loc[self.X_test.index]
        else:
            # Preencher valores ausentes
            for col in self.X_train.columns:
                if self.X_train[col].isnull().any():
                    if strategy == "median" and self.X_train[col].dtype in [np.int64, np.float64]:
                        fill_value = self.X_train[col].median()
                    elif strategy == "mean" and self.X_train[col].dtype in [np.int64, np.float64]:
                        fill_value = self.X_train[col].mean()
                    elif strategy == "mode":
                        fill_value = self.X_train[col].mode()[0]
                    else:
                        fill_value = 0  # fallback
                        
                    self.X_train[col].fillna(fill_value, inplace=True)
                    self.X_test[col].fillna(fill_value, inplace=True)
                    
    def feature_engineering(self) -> None:
        """
        Realiza engenharia de características para criar atributos mais promissores.
        
        @return: None
        """
        print("Realizando engenharia de características...")
        
        # Exemplo: criar razões entre características relacionadas
        # Para dados de câncer de mama, podemos criar razões entre medidas de tamanho e textura
        
        # Identificar colunas de raio, textura, perímetro, área
        radius_cols = [col for col in self.X_train.columns if 'radius' in col.lower()]
        texture_cols = [col for col in self.X_train.columns if 'texture' in col.lower()]
        perimeter_cols = [col for col in self.X_train.columns if 'perimeter' in col.lower()]
        area_cols = [col for col in self.X_train.columns if 'area' in col.lower()]
        
        # Criar razões (ex: área/raio, perímetro/área)
        for i, area_col in enumerate(area_cols):
            if i < len(radius_cols):
                ratio_name = f"area_radius_ratio_{i}"
                self.X_train[ratio_name] = self.X_train[area_col] / self.X_train[radius_cols[i]]
                self.X_test[ratio_name] = self.X_test[area_col] / self.X_test[radius_cols[i]]
                
        for i, perimeter_col in enumerate(perimeter_cols):
            if i < len(area_cols):
                ratio_name = f"perimeter_area_ratio_{i}"
                self.X_train[ratio_name] = self.X_train[perimeter_col] / self.X_train[area_cols[i]]
                self.X_test[ratio_name] = self.X_test[perimeter_col] / self.X_test[area_cols[i]]
                
    def scale_features(self, method: str = "standard") -> None:
        """
        Escala características usando método especificado.
        
        @param method: método de escalonamento ("standard", "minmax", "robust")
        @return: None
        """
        print("Escalonando características...")
        
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
        
        if method == "standard":
            scaler = StandardScaler()
        elif method == "minmax":
            scaler = MinMaxScaler()
        elif method == "robust":
            scaler = RobustScaler()
        else:
            scaler = StandardScaler()  # padrão
            
        # Ajustar apenas nos dados de treino
        self.X_train = pd.DataFrame(scaler.fit_transform(self.X_train), 
                                   columns=self.X_train.columns, 
                                   index=self.X_train.index)
                                   
        # Transformar dados de teste
        self.X_test = pd.DataFrame(scaler.transform(self.X_test), 
                                  columns=self.X_test.columns, 
                                  index=self.X_test.index)
                                  
    def prepare_data(self, missing_strategy: str = "median", 
                    scale_method: str = "standard") -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Executa pipeline completo de preparação de dados.
        
        @param missing_strategy: estratégia para valores ausentes
        @param scale_method: método de escalonamento
        @return: tuple(X_train_processed, X_test_processed, y_train, y_test)
        """
        print("Iniciando preparação de dados...")
        
        self.handle_missing_values(strategy=missing_strategy)
        self.feature_engineering()
        self.scale_features(method=scale_method)
        
        print("Preparação de dados completa!")
        return self.X_train, self.X_test, self.y_train, self.y_test


class ModelSelector:
    """
    Seleciona modelos promissores usando validação cruzada.
    
    Responsável por treinar vários modelos rápidos, medir performance
    e selecionar os mais promissores.
    
    @param X_train: DataFrame com características de treino processadas
    @param y_train: Series com target de treino
    @param random_state: semente para reprodutibilidade
    """
    
    def __init__(self, X_train: pd.DataFrame, y_train: pd.Series, 
                 random_state: int = RANDOM_STATE):
        self.X_train = X_train
        self.y_train = y_train
        self.random_state = random_state
        self.models_performance = {}
        
    def train_models(self, cv_folds: int = 5) -> Dict[str, Any]:
        """
        Treina vários modelos rápidos usando validação cruzada.
        
        @param cv_folds: número de folds para validação cruzada
        @return: dict com performance média e desvio padrão para cada modelo
        """
        print("Treinando modelos...")
        
        from sklearn.model_selection import cross_validate
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.naive_bayes import GaussianNB
        from sklearn.neighbors import KNeighborsClassifier
        
        # Definir modelos para testar
        models = {
            "LogisticRegression": LogisticRegression(random_state=self.random_state, max_iter=1000),
            "SVC": SVC(random_state=self.random_state),
            "RandomForest": RandomForestClassifier(random_state=self.random_state),
            "GradientBoosting": GradientBoostingClassifier(random_state=self.random_state),
            "GaussianNB": GaussianNB(),
            "KNeighbors": KNeighborsClassifier()
        }
        
        # Métricas para avaliar
        scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        
        # Treinar e avaliar cada modelo
        for name, model in models.items():
            print(f"  Avaliando {name}...")
            cv_results = cross_validate(model, self.X_train, self.y_train, 
                                      cv=cv_folds, scoring=scoring, n_jobs=-1)
            
            # Calcular média e desvio padrão para cada métrica
            model_results = {}
            for metric in scoring:
                mean_key = f"mean_{metric}"
                std_key = f"std_{metric}"
                model_results[mean_key] = np.mean(cv_results[f"test_{metric}"])
                model_results[std_key] = np.std(cv_results[f"test_{metric}"])
                
            self.models_performance[name] = model_results
            
        return self.models_performance
        
    def select_best_models(self, top_n: int = 3, primary_metric: str = "mean_roc_auc") -> List[str]:
        """
        Seleciona os n melhores modelos baseado na métrica primária.
        
        @param top_n: número de melhores modelos para selecionar
        @param primary_metric: métrica primária para classificar modelos
        @return: lista com nomes dos melhores modelos
        """
        print("Selecionando melhores modelos...")
        
        # Ordenar modelos pela métrica primária
        sorted_models = sorted(self.models_performance.items(), 
                              key=lambda x: x[1][primary_metric], 
                              reverse=True)
                              
        best_models = [model[0] for model in sorted_models[:top_n]]
        
        print(f"Melhores modelos ({primary_metric}):")
        for i, (model_name, metrics) in enumerate(sorted_models[:top_n], 1):
            print(f"{i}. {model_name}: {metrics[primary_metric]:.4f}")
            
        return best_models
        
    def plot_model_performance(self) -> None:
        """
        Cria visualização comparativa do desempenho dos modelos.
        
        @return: None
        """
        print("Criando visualização de desempenho dos modelos...")
        
        if not self.models_performance:
            print("Nenhum resultado de modelo disponível. Execute train_models() primeiro.")
            return
            
        # Preparar dados para plotting
        model_names = list(self.models_performance.keys())
        metrics = ['mean_accuracy', 'mean_precision', 'mean_recall', 'mean_f1', 'mean_roc_auc']
        metric_labels = ['Acurácia', 'Precisão', 'Recall', 'F1', 'ROC AUC']
        
        # Criar subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
            values = [self.models_performance[model][metric] for model in model_names]
            errors = [self.models_performance[model][f"std_{metric.split('_')[1]}"] for model in model_names]
            
            axes[i].barh(model_names, values, xerr=errors, capsize=5)
            axes[i].set_title(f"{label}")
            axes[i].set_xlabel("Score")
            
        # Ajustar layout e salvar
        plt.tight_layout()
        plt.savefig("model_performance_comparison.png", dpi=DPI, bbox_inches='tight')
        plt.show()


class ModelTuner:
    """
    Ajusta hiperparâmetros e combina os melhores modelos.
    
    Responsável por otimizar hiperparâmetros usando validação cruzada
    e combinar os melhores modelos em um ensemble.
    
    @param X_train: DataFrame com características de treino processadas
    @param y_train: Series com target de treino
    @param X_test: DataFrame com características de teste processadas  
    @param y_test: Series com target de teste
    @param best_model_names: lista com nomes dos melhores modelos
    @param random_state: semente para reprodutibilidade
    """
    
    def __init__(self, X_train: pd.DataFrame, y_train: pd.Series,
                 X_test: pd.DataFrame, y_test: pd.Series,
                 best_model_names: List[str], random_state: int = RANDOM_STATE):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.best_model_names = best_model_names
        self.random_state = random_state
        self.tuned_models = {}
        self.ensemble_model = None
        
    def tune_hyperparameters(self, cv_folds: int = 5) -> Dict[str, Any]:
        """
        Ajusta hiperparâmetros para os melhores modelos usando busca aleatória.
        
        @param cv_folds: número de folds para validação cruzada
        @return: dict com melhores modelos ajustados
        """
        print("Ajustando hiperparâmetros...")
        
        from sklearn.model_selection import RandomizedSearchCV
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.neighbors import KNeighborsClassifier
        
        # Definir espaços de parâmetros para cada modelo
        param_spaces = {
            "LogisticRegression": {
                'C': [0.001, 0.01, 0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            },
            "SVC": {
                'C': [0.1, 1, 10, 100],
                'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
                'kernel': ['linear', 'rbf', 'poly']
            },
            "RandomForest": {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            "GradientBoosting": {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 4, 5],
                'subsample': [0.8, 0.9, 1.0]
            },
            "KNeighbors": {
                'n_neighbors': [3, 5, 7, 9, 11],
                'weights': ['uniform', 'distance'],
                'p': [1, 2]
            }
        }
        
        # Instanciar modelos base
        base_models = {
            "LogisticRegression": LogisticRegression(random_state=self.random_state, max_iter=1000),
            "SVC": SVC(random_state=self.random_state),
            "RandomForest": RandomForestClassifier(random_state=self.random_state),
            "GradientBoosting": GradientBoostingClassifier(random_state=self.random_state),
            "KNeighbors": KNeighborsClassifier()
        }
        
        # Ajustar apenas os melhores modelos
        for model_name in self.best_model_names:
            if model_name in base_models and model_name in param_spaces:
                print(f"  Ajustando {model_name}...")
                
                random_search = RandomizedSearchCV(
                    base_models[model_name],
                    param_distributions=param_spaces[model_name],
                    n_iter=20,  # Número de combinações de parâmetros para tentar
                    cv=cv_folds,
                    scoring='roc_auc',
                    n_jobs=-1,
                    random_state=self.random_state
                )
                
                random_search.fit(self.X_train, self.y_train)
                self.tuned_models[model_name] = random_search.best_estimator_
                
                print(f"    Melhores parâmetros: {random_search.best_params_}")
                print(f"    Melhor score: {random_search.best_score_:.4f}")
                
        return self.tuned_models
        
    def create_ensemble(self, method: str = "voting") -> Any:
        """
        Cria ensemble combinando os melhores modelos ajustados.
        
        @param method: método de ensemble ("voting", "stacking")
        @return: modelo ensemble ajustado
        """
        print("Criando ensemble...")
        
        from sklearn.ensemble import VotingClassifier, StackingClassifier
        
        if not self.tuned_models:
            print("Nenhum modelo ajustado disponível. Execute tune_hyperparameters() primeiro.")
            return None
            
        # Criar lista de estimadores nomeados
        estimators = [(name, model) for name, model in self.tuned_models.items()]
        
        if method == "voting":
            self.ensemble_model = VotingClassifier(estimators=estimators, voting='soft')
        elif method == "stacking":
            self.ensemble_model = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression())
        else:
            self.ensemble_model = VotingClassifier(estimators=estimators, voting='soft')  # padrão
            
        # Treinar ensemble
        self.ensemble_model.fit(self.X_train, self.y_train)
        
        return self.ensemble_model
        
    def evaluate_final_model(self) -> Dict[str, float]:
        """
        Avalia o modelo final no conjunto de teste.
        
        @return: dict com métricas de performance no teste
        """
        print("Avaliando modelo final...")
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        if self.ensemble_model is None:
            print("Nenhum modelo ensemble disponível. Execute create_ensemble() primeiro.")
            return {}
            
        # Fazer previsões
        y_pred = self.ensemble_model.predict(self.X_test)
        y_pred_proba = self.ensemble_model.predict_proba(self.X_test)[:, 1]
        
        # Calcular métricas
        metrics = {
            "accuracy": accuracy_score(self.y_test, y_pred),
            "precision": precision_score(self.y_test, y_pred),
            "recall": recall_score(self.y_test, y_pred),
            "f1": f1_score(self.y_test, y_pred),
            "roc_auc": roc_auc_score(self.y_test, y_pred_proba)
        }
        
        print("Performance no conjunto de teste:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
            
        return metrics
        
    def plot_feature_importance(self) -> None:
        """
        Plota importância das características para modelos baseados em árvores.
        
        @return: None
        """
        print("Plotando importância das características...")
        
        # Encontrar primeiro modelo baseado em árvores
        tree_based_model = None
        for name, model in self.tuned_models.items():
            if hasattr(model, 'feature_importances_'):
                tree_based_model = (name, model)
                break
                
        if tree_based_model is None:
            print("Nenhum modelo baseado em árvores encontrado para plotar importância.")
            return
            
        name, model = tree_based_model
        feature_importances = model.feature_importances_
        feature_names = self.X_train.columns
        
        # Ordenar características por importância
        indices = np.argsort(feature_importances)[::-1]
        
        # Plotar as top N características
        top_n = min(20, len(feature_names))
        plt.figure(figsize=(10, 8))
        plt.title(f"Top {top_n} Características Mais Importantes - {name}")
        plt.barh(range(top_n), feature_importances[indices[:top_n]][::-1])
        plt.yticks(range(top_n), [feature_names[i] for i in indices[:top_n]][::-1])
        plt.xlabel("Importância Relativa")
        plt.tight_layout()
        
        # Salvar figura
        plt.savefig("feature_importance.png", dpi=DPI, bbox_inches='tight')
        plt.show()


class SolutionPresenter:
    """
    Apresenta a solução de forma compreensível para stakeholders.
    
    Responsável por documentar o processo, criar visualizações claras
    e preparar a apresentação final.
    
    @param project_name: nome do projeto
    @param findings_summary: dict com descobertas da EDA
    @param models_performance: dict com performance dos modelos
    @param final_metrics: dict com métricas finais no teste
    @param target_variable: nome da variável target
    """
    
    def __init__(self, project_name: str, findings_summary: Dict[str, Any],
                 models_performance: Dict[str, Any], final_metrics: Dict[str, float],
                 target_variable: str):
        self.project_name = project_name
        self.findings_summary = findings_summary
        self.models_performance = models_performance
        self.final_metrics = final_metrics
        self.target_variable = target_variable
        
    def create_executive_summary(self) -> str:
        """
        Cria um resumo executivo do projeto.
        
        @return: string com resumo executivo
        """
        print("Criando resumo executivo...")
        
        summary = f"""
        RESUMO EXECUTIVO - {self.project_name}
        ===================================
        
        OBJETIVO: Desenvolver um modelo de machine learning para previsão de {self.target_variable}.
        
        PRINCIPAIS DESCOBERTAS:
        - Dataset: {self.findings_summary.get('numRows', 'N/A')} amostras, {self.findings_summary.get('numColumns', 'N/A')} características
        - Variável target: {self.findings_summary.get('targetColumn', 'N/A')} ({'categórica' if self.findings_summary.get('targetIsCategorical') else 'numérica'})
        - Distribuição: {self.findings_summary.get('targetDistributionSample', 'N/A')}
        
        PREPARAÇÃO DE DADOS:
        - Transformações aplicadas: padronização, engenharia de características
        - Tratamento de valores ausentes: estratégia de preenchimento com mediana
        
        MODELAGEM:
        - Modelos testados: {len(self.models_performance)}
        - Melhor performance (validação cruzada): {max([metrics.get('mean_roc_auc', 0) for metrics in self.models_performance.values()]):.4f} ROC AUC
        - Performance final (teste): {self.final_metrics.get('roc_auc', 0):.4f} ROC AUC
        
        PRÓXIMOS PASSOS:
        - Implementar monitoramento contínuo de performance
        - Re-treinar modelos periodicamente com novos dados
        - Explorar coleta de dados adicionais sugeridos
        """
        
        return summary
        
    def create_detailed_report(self) -> str:
        """
        Cria um relatório detalhado do projeto.
        
        @return: string com relatório detalhado
        """
        print("Criando relatório detalhado...")
        
        report = f"""
        RELATÓRIO DETALHADO - {self.project_name}
        =======================================
        
        1. ENQUADRAMENTO DO PROBLEMA
        ----------------------------
        Objetivo de negócio: Prever {self.target_variable} com alta acurácia.
        Tipo de problema: {'Classificação' if self.findings_summary.get('targetIsCategorical') else 'Regressão'}.
        Métrica principal: ROC AUC.
        
        2. ANÁLISE EXPLORATÓRIA DE DADOS
        --------------------------------
        Dataset possui {self.findings_summary.get('numRows', 'N/A')} amostras e {self.findings_summary.get('numColumns', 'N/A')} características.
        
        Distribuição da variável target:
        {self.findings_summary.get('targetDistributionSample', 'N/A')}
        
        Características mais correlacionadas com o target:
        {self.findings_summary.get('topCorrelatedWithTarget', 'N/A')}
        
        3. PREPARAÇÃO DE DADOS
        ----------------------
        Processos aplicados:
        - Padronização de características numéricas
        - Engenharia de características (criação de razões entre medidas)
        - Tratamento de valores ausentes
        
        4. MODELAGEM
        ------------
        Foram testados {len(self.models_performance)} algoritmos diferentes:
        """
        
        # Adicionar performance dos modelos
        for model_name, metrics in self.models_performance.items():
            report += f"""
            {model_name}:
              Acurácia: {metrics.get('mean_accuracy', 0):.4f} (±{metrics.get('std_accuracy', 0):.4f})
              Precisão: {metrics.get('mean_precision', 0):.4f} (±{metrics.get('std_precision', 0):.4f})
              Recall: {metrics.get('mean_recall', 0):.4f} (±{metrics.get('std_recall', 0):.4f})
              F1: {metrics.get('mean_f1', 0):.4f} (±{metrics.get('std_f1', 0):.4f})
              ROC AUC: {metrics.get('mean_roc_auc', 0):.4f} (±{metrics.get('std_roc_auc', 0):.4f})
            """
            
        report += f"""
        
        5. RESULTADOS FINAIS
        --------------------
        Performance no conjunto de teste:
          Acurácia: {self.final_metrics.get('accuracy', 0):.4f}
          Precisão: {self.final_metrics.get('precision', 0):.4f}
          Recall: {self.final_metrics.get('recall', 0):.4f}
          F1: {self.final_metrics.get('f1', 0):.4f}
          ROC AUC: {self.final_metrics.get('roc_auc', 0):.4f}
        
        6. PRÓXIMOS PASSOS E RECOMENDAÇÕES
        ----------------------------------
        - Implementar sistema de monitoramento de performance em produção
        - Re-treinar modelos a cada 3-6 meses com dados atualizados
        - Coletar dados adicionais sugeridos: {self.findings_summary.get('additionalDataSuggestions', 'N/A')}
        """
        
        return report
        
    def save_reports(self, output_dir: str = "reports") -> None:
        """
        Salva os relatórios em arquivos de texto.
        
        @param output_dir: diretório para salvar os relatórios
        @return: None
        """
        print("Salvando relatórios...")
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Salvar resumo executivo
        executive_summary = self.create_executive_summary()
        with open(os.path.join(output_dir, "executive_summary.txt"), "w") as f:
            f.write(executive_summary)
            
        # Salvar relatório detalhado
        detailed_report = self.create_detailed_report()
        with open(os.path.join(output_dir, "detailed_report.txt"), "w") as f:
            f.write(detailed_report)
            
        print(f"Relatórios salvos em diretório: {output_dir}")


class BreastCancerPipeline:
    """
    Classe principal para orquestrar todo o pipeline de análise de câncer de mama.
    
    Coordena todas as etapas do projeto seguindo o checklist de aprendizado de máquina.
    
    @param project_name: nome do projeto
    @param random_state: semente para reprodutibilidade
    """
    
    def __init__(self, project_name: str = "Breast Cancer Classification",
                 random_state: int = RANDOM_STATE):
        self.project_name = project_name
        self.random_state = random_state
        self.data_manager = None
        self.problem_framer = None
        self.exploratory_analyzer = None
        self.data_preparer = None
        self.model_selector = None
        self.model_tuner = None
        self.solution_presenter = None
        
    def run_full_pipeline(self) -> None:
        """
        Executa o pipeline completo de análise de dados.
        
        @return: None
        """
        print("=" * 60)
        print(f"INICIANDO PIPELINE: {self.project_name}")
        print("=" * 60)
        
        # Etapa 1: Enquadrar o problema
        print("\n" + "=" * 40)
        print("ETAPA 1: ENQUADRAR O PROBLEMA")
        print("=" * 40)
        
        # Carregar dados de exemplo
        from sklearn.datasets import load_breast_cancer
        data = load_breast_cancer()
        df = pd.DataFrame(data.data, columns=[c.replace(" ", "_") for c in data.feature_names])
        df['target'] = data.target
        
        self.problem_framer = ProblemFramer(df, 'target')
        metadata = self.problem_framer.summarize_dataset_metadata()
        task_type = self.problem_framer.infer_task_type()
        metrics = self.problem_framer.propose_performance_metrics()
        min_performance = self.problem_framer.suggest_minimum_acceptable_performance(0.90)
        
        print("Metadados do dataset:", metadata)
        print("Tipo de tarefa inferido:", task_type)
        print("Métricas recomendadas:", metrics)
        print("Performance mínima sugerida:", min_performance)
        
        # Etapa 2: Obter os dados
        print("\n" + "=" * 40)
        print("ETAPA 2: OBTER OS DADOS")
        print("=" * 40)
        
        self.data_manager = DataManager()
        self.data_manager.get_data()
        
        # Etapa 3: Explorar os dados
        print("\n" + "=" * 40)
        print("ETAPA 3: EXPLORAR OS DADOS")
        print("=" * 40)
        
        self.exploratory_analyzer = ExploratoryAnalyzer(
            self.data_manager.dataFrame, 
            self.data_manager.target_variable
        )
        findings = self.exploratory_analyzer.explore_data()
        print("Descobertas da EDA:", findings)
        
        # Etapa 4: Preparar os dados
        print("\n" + "=" * 40)
        print("ETAPA 4: PREPARAR OS DADOS")
        print("=" * 40)
        
        self.data_preparer = DataPreparer(
            self.data_manager.X_train, 
            self.data_manager.X_test,
            self.data_manager.y_train, 
            self.data_manager.y_test,
            self.data_manager.target_variable
        )
        
        X_train_processed, X_test_processed, y_train, y_test = self.data_preparer.prepare_data()
        
        # Etapa 5: Selecionar modelos
        print("\n" + "=" * 40)
        print("ETAPA 5: SELECIONAR MODELOS")
        print("=" * 40)
        
        self.model_selector = ModelSelector(X_train_processed, y_train, self.random_state)
        models_performance = self.model_selector.train_models()
        best_models = self.model_selector.select_best_models(top_n=3)
        self.model_selector.plot_model_performance()
        
        # Etapa 6: Ajustar modelos
        print("\n" + "=" * 40)
        print("ETAPA 6: AJUSTAR MODELOS")
        print("=" * 40)
        
        self.model_tuner = ModelTuner(
            X_train_processed, y_train,
            X_test_processed, y_test,
            best_models, self.random_state
        )
        
        tuned_models = self.model_tuner.tune_hyperparameters()
        ensemble = self.model_tuner.create_ensemble()
        final_metrics = self.model_tuner.evaluate_final_model()
        self.model_tuner.plot_feature_importance()
        
        # Etapa 7: Apresentar solução
        print("\n" + "=" * 40)
        print("ETAPA 7: APRESENTAR SOLUÇÃO")
        print("=" * 40)
        
        self.solution_presenter = SolutionPresenter(
            self.project_name, findings, models_performance, 
            final_metrics, self.data_manager.target_variable
        )
        
        self.solution_presenter.save_reports()
        
        print("\n" + "=" * 60)
        print("PIPELINE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)


# Executar o pipeline completo se este script for executado diretamente
if __name__ == "__main__":
    pipeline = BreastCancerPipeline()
    pipeline.run_full_pipeline()