# end_to_end_pipeline.py
# Full, self-contained pipeline implementing the 8-step checklist.
# All comments and docstrings in English; prints/logging in English.
# Each plot is saved as PNG with dpi=300. Use in Colab (install missing libs if needed).

import os
import json
import time
import logging
import joblib
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union, Callable

# sklearn imports
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV, HalvingRandomSearchCV
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (confusion_matrix, classification_report, roc_curve, auc,
                             accuracy_score, precision_score, recall_score, f1_score, roc_auc_score)

from scipy.stats import randint, uniform

# Logging config
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("e2e_ml_pipeline")

# Global reproducibility
GLOBAL_RANDOM_SEED = 42
np.random.seed(GLOBAL_RANDOM_SEED)
os.environ["PYTHONHASHSEED"] = str(GLOBAL_RANDOM_SEED)

# ---------- Helpers ----------
def ensure_dir(path_like: Union[str, Path]) -> Path:
    p = Path(path_like)
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_figure(fig_object: plt.Figure, destination_path: Union[str, Path], dpi: int = 300) -> None:
    """
    Save matplotlib figure object with specified dpi.
    """
    destination = Path(destination_path)
    ensure_dir(destination.parent)
    fig_object.savefig(destination, dpi=dpi, bbox_inches="tight")
    plt.close(fig_object)

# ---------- 1. Problem Framer ----------
class ProblemFramer:
    """
    Frame the problem and capture business context.

    @param problem_title: short title of the problem
    @param business_objective_description: business objective (what metric matters and why)
    """

    def __init__(self, problem_title: str, business_objective_description: str):
        self.problemTitle = problem_title
        self.businessObjectiveDescription = business_objective_description

    def summarizeProblem(self) -> Dict[str, str]:
        """
        Return a small dictionary summarizing the framing.

        @return: dict with title and objective
        """
        summary = {"title": self.problemTitle, "business_objective": self.businessObjectiveDescription}
        logger.info("Problem framed: %s", summary)
        return summary

# ---------- 2. Data Manager ----------
class DataManager:
    """
    Obtain and provide dataset. Tries to load via Kaggle-like helper or falls back to sklearn dataset.

    @param workspace_directory_path: local folder to store downloads and artifacts
    @param kaggle_dataset_slug: optional kaggle dataset slug to try (e.g., "yasserh/breast-cancer-dataset")
    """

    def __init__(self, workspace_directory_path: str = "data_workspace", kaggle_dataset_slug: Optional[str] = None):
        self.workspaceDir = ensure_dir(workspace_directory_path)
        self.kaggleDatasetSlug = kaggle_dataset_slug
        self.dataFrame: Optional[pd.DataFrame] = None
        self.targetColumnName: Optional[str] = None
        self.rawDownloadPath: Optional[Path] = None

    def _load_from_sklearn(self) -> pd.DataFrame:
        ds = load_breast_cancer()
        df = pd.DataFrame(ds.data, columns=[c.replace(" ", "_") for c in ds.feature_names])
        df["target"] = ds.target
        return df

    def acquireData(self) -> pd.DataFrame:
        """
        Acquire dataset. Attempts kagglehub if slug provided, otherwise loads sklearn dataset.

        @return: pandas DataFrame with loaded data
        """
        logger.info("Acquiring data...")
        if self.kaggleDatasetSlug:
            try:
                import kagglehub
                path = kagglehub.dataset_download(self.kaggleDatasetSlug)
                self.rawDownloadPath = Path(path)
                # look for CSV in folder
                csv_candidates = list(self.rawDownloadPath.rglob("*.csv"))
                if csv_candidates:
                    df = pd.read_csv(csv_candidates[0])
                    self.dataFrame = df
                    logger.info("Dataset loaded from kagglehub: %s", csv_candidates[0])
                    # try to infer target column
                    if "diagnosis" in df.columns:
                        self.targetColumnName = "diagnosis"
                    elif "target" in df.columns:
                        self.targetColumnName = "target"
                    return df
            except Exception as exc:
                logger.warning("Kagglehub download failed: %s — falling back to sklearn dataset", exc)

        # fallback
        self.dataFrame = self._load_from_sklearn()
        self.targetColumnName = "target"
        logger.info("Dataset loaded from sklearn; shape: %s", self.dataFrame.shape)
        return self.dataFrame

# ---------- 3. Exploratory Analyzer ----------
class ExploratoryAnalyzer:
    """
    Exploratory Data Analysis utilities: descriptive stats, missing values, histograms, correlation heatmap.
    Each plot is saved as PNG at 300 dpi.

    @param dataset_dataframe: DataFrame to analyze
    @param target_column_name: name of target column
    @param output_figures_directory: folder to save figures
    """

    def __init__(self, dataset_dataframe: pd.DataFrame, target_column_name: str, output_figures_directory: str = "figures"):
        self.df = dataset_dataframe.copy()
        self.targetName = target_column_name
        self.figuresDir = ensure_dir(output_figures_directory)
        # helper lambdas
        self._percent_missing = lambda col: round(100 * col.isnull().sum() / len(col), 3)
        self._savefig = lambda fig, name: save_figure(fig, self.figuresDir / f"{name}.png", dpi=300)

    def basicInfo(self) -> Dict[str, Any]:
        """
        Return basic dataset info and missing value report.

        @return: dict with shape, dtypes and missing-summary
        """
        info = {"shape": self.df.shape, "dtypes": self.df.dtypes.to_dict()}
        missing_series = self.df.apply(self._percent_missing)
        info["missing_percentages"] = missing_series.to_dict()
        logger.info("EDA basic info: shape=%s", info["shape"])
        return info

    def plotHistograms(self, numerical_bins: int = 50) -> None:
        """
        Plot histograms of numeric features and save PNG.

        @param numerical_bins: number of histogram bins
        """
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_columns:
            logger.info("No numeric columns to plot histograms")
            return
        fig, axes = plt.subplots(nrows=(len(numeric_columns)+3)//4, ncols=4, figsize=(16, 4*((len(numeric_columns)+3)//4)))
        axes = axes.flatten()
        for i, col in enumerate(numeric_columns):
            sns.histplot(self.df[col].dropna(), kde=True, ax=axes[i])
            axes[i].set_title(col)
        for j in range(i+1, len(axes)):
            axes[j].set_visible(False)
        plt.tight_layout()
        self._savefig(fig, "histograms")
        logger.info("Saved histogram grid to figures/histograms.png")

    def plotCorrelationMatrix(self) -> None:
        """
        Compute and save correlation heatmap as PNG.
        """
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            logger.info("Not enough numeric columns for correlation matrix")
            return
        corr = numeric_df.corr()
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr, cmap="coolwarm", ax=ax, square=True, cbar_kws={"shrink": .5})
        ax.set_title("Feature Correlation Matrix")
        plt.tight_layout()
        self._savefig(fig, "correlation_matrix")
        logger.info("Saved correlation matrix to figures/correlation_matrix.png")

    def plotTargetDistribution(self) -> None:
        """
        Plot and save target distribution bar plot.
        """
        if self.targetName not in self.df.columns:
            logger.info("Target not found in DataFrame")
            return
        fig, ax = plt.subplots(figsize=(6,4))
        sns.countplot(x=self.targetName, data=self.df, ax=ax)
        ax.set_title("Target Distribution")
        plt.tight_layout()
        self._savefig(fig, "target_distribution")
        logger.info("Saved target distribution to figures/target_distribution.png")

    def scatterPairWithTarget(self, feature_x: str, feature_y: str) -> None:
        """
        Scatter plot of two features colored by target label and save PNG.

        @param feature_x: feature name for x axis
        @param feature_y: feature name for y axis
        """
        if feature_x not in self.df.columns or feature_y not in self.df.columns:
            logger.info("Requested scatter features not present")
            return
        fig, ax = plt.subplots(figsize=(7,6))
        sns.scatterplot(x=self.df[feature_x], y=self.df[feature_y], hue=self.df[self.targetName], ax=ax, alpha=0.7)
        ax.set_title(f"{feature_x} vs {feature_y} colored by {self.targetName}")
        plt.tight_layout()
        self._savefig(fig, f"scatter_{feature_x}_vs_{feature_y}")
        logger.info("Saved scatter to figures/scatter_%s_vs_%s.png", feature_x, feature_y)

# ---------- 4. Data Preparer ----------
class DataPreparer:
    """
    Prepare data for modeling: cleaning, imputing, feature engineering, pipeline construction.

    @param raw_dataframe: original DataFrame
    @param target_column_name: name of target column in raw_dataframe
    @param test_size: fraction for test split if splitting is needed
    @param random_state: random seed
    """

    def __init__(self, raw_dataframe: pd.DataFrame, target_column_name: str, test_size: float = 0.2, random_state: int = GLOBAL_RANDOM_SEED):
        self.rawDf = raw_dataframe.copy()
        self.targetName = target_column_name
        self.testSize = test_size
        self.randomState = random_state

        # placeholders
        self.trainDf: Optional[pd.DataFrame] = None
        self.testDf: Optional[pd.DataFrame] = None
        self.pipeline_: Optional[Pipeline] = None
        self.featureNamesAfterProcessing: Optional[List[str]] = None
        self.X_train_raw: Optional[pd.DataFrame] = None
        self.X_test_raw: Optional[pd.DataFrame] = None
        self.y_train_raw: Optional[pd.Series] = None
        self.y_test_raw: Optional[pd.Series] = None
        ensure_dir("figures")  # ensure directory for EDA artifacts

    def splitTrainTest(self, stratify_on_target: bool = True) -> None:
        """
        Create train/test split and store DataFrames.

        @param stratify_on_target: whether to stratify split on target variable (recommended for classification)
        """
        X = self.rawDf.drop(columns=[self.targetName])
        y = self.rawDf[self.targetName]
        stratify_obj = y if stratify_on_target else None
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.testSize,
                                                            random_state=self.randomState, stratify=stratify_obj)
        self.trainDf = pd.concat([X_train, y_train.reset_index(drop=True)], axis=1)
        self.testDf = pd.concat([X_test, y_test.reset_index(drop=True)], axis=1)
        self.X_train_raw = X_train.reset_index(drop=True)
        self.X_test_raw = X_test.reset_index(drop=True)
        self.y_train_raw = y_train.reset_index(drop=True)
        self.y_test_raw = y_test.reset_index(drop=True)
        logger.info("Train/test split created: train=%s, test=%s", self.trainDf.shape, self.testDf.shape)

    def buildPreprocessingPipeline(self,
                                   numerical_imputer_strategy: str = "median",
                                   use_pca: bool = True,
                                   pca_variance_threshold: float = 0.95) -> Pipeline:
        """
        Build and store preprocessing pipeline using ColumnTransformer.

        @param numerical_imputer_strategy: 'median' or 'mean'
        @param use_pca: whether to append PCA to numeric pipeline
        @param pca_variance_threshold: variance fraction to keep in PCA (if used)
        @return: sklearn Pipeline stored in self.pipeline_
        """
        # numeric and categorical selectors
        numeric_selector = make_column_selector(dtype_include=np.number)
        categorical_selector = make_column_selector(dtype_include=object)

        numeric_pipeline = make_pipeline(SimpleImputer(strategy=numerical_imputer_strategy), StandardScaler())
        if use_pca:
            numeric_pipeline = make_pipeline(SimpleImputer(strategy=numerical_imputer_strategy), StandardScaler(), PCA(n_components=pca_variance_threshold, random_state=self.randomState))

        categorical_pipeline = make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore", sparse_output=False))

        preprocessor = ColumnTransformer([
            ("num", numeric_pipeline, numeric_selector),
            ("cat", categorical_pipeline, categorical_selector),
        ], remainder="drop")

        self.pipeline_ = preprocessor
        logger.info("Preprocessing pipeline built (PCA=%s)", use_pca)
        return Pipeline([("preprocessing", preprocessor)])  # convenience wrapper

    def fitTransformTrainAndTransformTest(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit preprocessing on train and transform both train and test. Also record post-processing feature names when possible.

        @return: (X_train_prepared, X_test_prepared)
        """
        if self.pipeline_ is None:
            raise RuntimeError("Call buildPreprocessingPipeline before fitTransformTrainAndTransformTest")

        # fit on train data Frame (pipeline expects DataFrame so column selectors work)
        preproc = self.pipeline_
        # If pipeline is a wrapper Pipeline with single 'preprocessing', unwrap for ColumnTransformer methods
        if isinstance(preproc, Pipeline) and "preprocessing" in preproc.named_steps:
            ct = preproc.named_steps["preprocessing"]
        else:
            ct = preproc

        X_train_df = self.X_train_raw.copy()
        X_test_df = self.X_test_raw.copy()

        # Fit/transform
        X_train_prepared = ct.fit_transform(X_train_df)
        X_test_prepared = ct.transform(X_test_df)

        # Try to obtain feature names (works with scikit-learn >=1.0 for transformers with get_feature_names_out)
        try:
            feature_names_out = ct.get_feature_names_out()
            self.featureNamesAfterProcessing = list(feature_names_out)
        except Exception:
            self.featureNamesAfterProcessing = [f"feat_{i}" for i in range(X_train_prepared.shape[1])]

        logger.info("Data prepared: train shape=%s, test shape=%s", X_train_prepared.shape, X_test_prepared.shape)
        return X_train_prepared, X_test_prepared

# ---------- 5. Model Shortlister ----------
class ModelShortlister:
    """
    Train quick-and-dirty models and shortlist promising ones.

    @param X_train_array: training features (after preprocessing or raw depending on pipeline design)
    @param X_test_array: test features
    @param y_train_array: training labels
    @param y_test_array: test labels
    @param random_state: seed
    """

    def __init__(self, X_train_array: np.ndarray, X_test_array: np.ndarray, y_train_array: np.ndarray, y_test_array: np.ndarray, random_state: int = GLOBAL_RANDOM_SEED):
        self.X_train = X_train_array
        self.X_test = X_test_array
        self.y_train = np.asarray(y_train_array)
        self.y_test = np.asarray(y_test_array)
        self.randomState = random_state
        self.modelsCatalog: Dict[str, Any] = {}
        self.resultsDataFrame: Optional[pd.DataFrame] = None
        self.topModelNames: Optional[List[str]] = None

    def defineCandidateModels(self) -> Dict[str, Any]:
        """
        Define a small diverse catalog of candidate models.

        @return: dict name->unfitted estimator
        """
        catalog = {
            "LogisticRegression": LogisticRegression(max_iter=2000, random_state=self.randomState),
            "SVC": SVC(probability=True, random_state=self.randomState),
            "RandomForest": RandomForestClassifier(random_state=self.randomState),
            "MLP": MLPClassifier(max_iter=1000, random_state=self.randomState)
        }
        self.modelsCatalog = catalog
        return catalog

    def trainQuickAndEvaluate(self, cv_folds: int = 5) -> pd.DataFrame:
        """
        Fit each candidate with default params (fast) and evaluate via cross-validation.

        @param cv_folds: number of CV folds
        @return: DataFrame with evaluation summary sorted by mean CV accuracy
        """
        if not self.modelsCatalog:
            self.defineCandidateModels()

        records = []
        for name, estimator in self.modelsCatalog.items():
            try:
                logger.info("Training quick model: %s", name)
                estimator.fit(self.X_train, self.y_train)
                cv_scores = cross_val_score(estimator, self.X_train, self.y_train, cv=cv_folds, scoring="accuracy", n_jobs=1)
                y_pred = estimator.predict(self.X_test)
                rec = {
                    "Model": name,
                    "CV_Mean_Accuracy": float(np.mean(cv_scores)),
                    "CV_Std_Accuracy": float(np.std(cv_scores)),
                    "Test_Accuracy": float(accuracy_score(self.y_test, y_pred)),
                    "Test_Precision": float(precision_score(self.y_test, y_pred, zero_division=0)),
                    "Test_Recall": float(recall_score(self.y_test, y_pred, zero_division=0)),
                    "Test_F1": float(f1_score(self.y_test, y_pred, zero_division=0))
                }
                records.append(rec)
            except Exception as exc:
                logger.warning("Candidate model %s failed quick training: %s", name, exc)
                records.append({"Model": name, "CV_Mean_Accuracy": np.nan, "CV_Std_Accuracy": np.nan, "Test_Accuracy": np.nan, "Test_Precision": np.nan, "Test_Recall": np.nan, "Test_F1": np.nan})

        df = pd.DataFrame(records).sort_values(by="CV_Mean_Accuracy", ascending=False).reset_index(drop=True)
        self.resultsDataFrame = df
        self.topModelNames = df.head(3)["Model"].tolist()
        logger.info("Top models shortlisted: %s", self.topModelNames)
        return df

# ---------- 6. Fine Tuner (with array->DataFrame conversion when feature names provided) ----------
class FineTuner:
    """
    Fine-tune hyperparameters, try ensembles and evaluate final models.

    @param preprocessing_pipeline: optional preprocessing pipeline applied before estimator (if present, tuning occurs on Pipeline(preprocessing, estimator))
    @param candidate_models_dict: dict name->unfitted estimator
    @param X_train_source: features used for search; if arrays are provided and feature_names is given, they will be converted to DataFrame
    @param X_test_source: test features used for evaluation
    @param y_train_source: training labels
    @param y_test_source: test labels
    @param feature_names: optional list of column names to convert arrays into DataFrame (required if ColumnTransformer uses strings)
    @param random_state: seed
    @param n_jobs: parallel jobs for search
    """

    def __init__(self,
                 preprocessing_pipeline: Optional[Union[Pipeline, ColumnTransformer]],
                 candidate_models_dict: Dict[str, Any],
                 X_train_source: Union[np.ndarray, pd.DataFrame],
                 X_test_source: Union[np.ndarray, pd.DataFrame],
                 y_train_source: Union[np.ndarray, pd.Series],
                 y_test_source: Union[np.ndarray, pd.Series],
                 feature_names: Optional[List[str]] = None,
                 random_state: int = GLOBAL_RANDOM_SEED,
                 n_jobs: int = -1):
        self.preprocessingPipeline = preprocessing_pipeline
        self.candidateModelsDict = candidate_models_dict.copy()
        self.X_train_source = X_train_source
        self.X_test_source = X_test_source
        self.y_train = np.asarray(y_train_source)
        self.y_test = np.asarray(y_test_source)
        self.featureNames = feature_names
        self.randomState = random_state
        self.nJobs = n_jobs

        # internal prepared views for search/fitting; conversion done below
        self.X_train_for_search = self._maybe_convert_array_to_df(self.X_train_source, self.featureNames, "X_train")
        self.X_test_for_search = self._maybe_convert_array_to_df(self.X_test_source, self.featureNames, "X_test")

        self.tunedModels: Dict[str, Any] = {}
        self.tuningReports: Dict[str, Any] = {}
        self.finalResults: Optional[pd.DataFrame] = None

    def _maybe_convert_array_to_df(self, X_maybe_array: Union[np.ndarray, pd.DataFrame], feature_names: Optional[List[str]], marker_name: str):
        """
        Convert numpy array to DataFrame when feature_names provided. Returns DataFrame or original input.

        @param X_maybe_array: array or DataFrame
        @param feature_names: column names
        @param marker_name: textual marker for logs
        """
        if feature_names is not None and isinstance(X_maybe_array, np.ndarray):
            try:
                df = pd.DataFrame(X_maybe_array, columns=feature_names)
                logger.info("Converted %s ndarray -> DataFrame using provided feature names", marker_name)
                return df
            except Exception as exc:
                logger.warning("Conversion of %s failed: %s; will keep ndarray", marker_name, exc)
                return X_maybe_array
        return X_maybe_array

    def _wrap_estimator_in_pipeline(self, estimator):
        """
        If preprocessingPipeline provided, return Pipeline([('preprocessing', preprocessing), ('estimator', estimator)]).
        Otherwise return estimator itself.
        """
        if self.preprocessingPipeline is not None:
            return Pipeline([("preprocessing", self.preprocessingPipeline), ("estimator", estimator)])
        return estimator

    def _filter_params_against_estimator(self, estimator_pipeline, param_distributions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Keep only param keys that exist in estimator_pipeline.get_params().keys() to avoid invalid keys.
        """
        valid_keys = set(estimator_pipeline.get_params().keys())
        filtered = {k: v for k, v in (param_distributions or {}).items() if k in valid_keys}
        dropped = [k for k in (param_distributions or {}).keys() if k not in filtered]
        if dropped:
            logger.debug("Dropped invalid hyperparameter keys: %s", dropped)
        return filtered

    def defineDefaultSearchSpaces(self) -> Dict[str, Dict[str, Any]]:
        """
        Return default hyperparameter distributions for common models.
        Keys are pipeline-prefixed (if pipeline used, 'estimator__param' will match pipeline.get_params()).
        """
        base_spaces = {
            "LogisticRegression": {"estimator__C": uniform(0.01, 10), "estimator__solver": ["lbfgs", "liblinear"]},
            "RandomForest": {"estimator__n_estimators": randint(50, 300), "estimator__max_depth": [None, 5, 10, 20]},
            "SVC": {"estimator__C": uniform(0.1, 10), "estimator__gamma": ["scale", "auto"]},
            "MLP": {"estimator__hidden_layer_sizes": [(50,), (100,), (100,50)], "estimator__alpha": uniform(1e-6, 1e-2)}
        }
        return base_spaces

    def tuneModel(self,
                  model_name: str,
                  estimator,
                  param_distributions: Optional[Dict[str, Any]] = None,
                  n_iter: int = 30,
                  cv_folds: int = 3,
                  scoring: str = "accuracy",
                  use_halving: bool = False) -> Tuple[Any, Dict[str, Any]]:
        """
        Tune a single model using RandomizedSearchCV or HalvingRandomSearchCV.

        @param model_name: textual name
        @param estimator: unfitted estimator
        @param param_distributions: candidate parameter distributions (pipeline-prefixed)
        @param n_iter: number of random search iterations
        @param cv_folds: CV folds
        @param scoring: scoring metric name
        @param use_halving: whether to use iterative halving search
        """
        logger.info("Tuning model: %s", model_name)
        pipe_or_est = self._wrap_estimator_in_pipeline(estimator)
        filtered_space = self._filter_params_against_estimator(pipe_or_est, param_distributions or {})
        if not filtered_space:
            # no valid hyperparams -> fit baseline pipeline/estimator
            logger.info("No valid hyperparameters found for %s; training baseline", model_name)
            pipe_or_est.fit(self.X_train_for_search, self.y_train)
            self.tunedModels[model_name] = pipe_or_est
            self.tuningReports[model_name] = {"note": "baseline trained; no valid hyperparameters"}
            return pipe_or_est, self.tuningReports[model_name]

        searcher = HalvingRandomSearchCV(pipe_or_est, filtered_space, cv=cv_folds, scoring=scoring, random_state=self.randomState, n_jobs=self.nJobs) if use_halving else RandomizedSearchCV(pipe_or_est, filtered_space, n_iter=n_iter, cv=cv_folds, scoring=scoring, random_state=self.randomState, n_jobs=self.nJobs, return_train_score=False)

        try:
            searcher.fit(self.X_train_for_search, self.y_train)
            best_estimator = searcher.best_estimator_
            report = {"best_params": searcher.best_params_, "best_score": float(searcher.best_score_)}
            self.tunedModels[model_name] = best_estimator
            self.tuningReports[model_name] = report
            logger.info("Tuning complete for %s: best_score=%.4f", model_name, report["best_score"])
            return best_estimator, report
        except Exception as exc:
            logger.warning("Hyperparameter search failed for %s: %s; falling back to baseline fit", model_name, exc)
            try:
                pipe_or_est.fit(self.X_train_for_search, self.y_train)
                self.tunedModels[model_name] = pipe_or_est
                self.tuningReports[model_name] = {"note": f"fallback trained due to search failure: {exc}"}
                return pipe_or_est, self.tuningReports[model_name]
            except Exception as exc2:
                logger.error("Fallback baseline also failed for %s: %s", model_name, exc2)
                raise

    def tuneAll(self,
                param_distribution_overrides: Optional[Dict[str, Dict[str, Any]]] = None,
                n_iter: int = 30,
                cv_folds: int = 3,
                scoring: str = "accuracy",
                use_halving: bool = False) -> Dict[str, Any]:
        """
        Tune all candidate models provided in candidateModelsDict.

        @param param_distribution_overrides: optional dict model_name->param_dist
        """
        default_spaces = self.defineDefaultSearchSpaces()
        for model_name, estimator in self.candidateModelsDict.items():
            space = (param_distribution_overrides.get(model_name) if param_distribution_overrides and model_name in param_distribution_overrides else default_spaces.get(model_name, {}))
            try:
                self.tuneModel(model_name, estimator, param_distributions=space, n_iter=n_iter, cv_folds=cv_folds, scoring=scoring, use_halving=use_halving)
            except Exception as exc:
                logger.error("Tuning failed for %s: %s", model_name, exc)
        return self.tuningReports

    def buildEnsemble(self, ensemble_type: str = "voting", voting: str = "soft", final_estimator: Optional[Any] = None) -> Any:
        """
        Build ensemble (voting or stacking). If preprocessing pipeline present, the ensemble is wrapped into a Pipeline(preprocessing, ensemble).

        @param ensemble_type: 'voting' or 'stacking'
        @param voting: 'soft' or 'hard' (for VotingClassifier)
        @param final_estimator: optional final stacking estimator
        """
        if len(self.tunedModels) < 2:
            raise ValueError("At least two tuned models are required to build an ensemble")
        estimators_for_ensemble = []
        for name, mdl in self.tunedModels.items():
            # extract estimator from pipeline if wrapped
            if isinstance(mdl, Pipeline) and "estimator" in mdl.named_steps:
                base_est = mdl.named_steps["estimator"]
            else:
                base_est = mdl
            estimators_for_ensemble.append((name, base_est))

        if ensemble_type == "voting":
            ensemble_body = VotingClassifier(estimators=estimators_for_ensemble, voting=voting, n_jobs=self.nJobs)
        else:
            final_est = final_estimator or estimators_for_ensemble[-1][1]
            ensemble_body = StackingClassifier(estimators=estimators_for_ensemble, final_estimator=final_est, n_jobs=self.nJobs, passthrough=False)

        if self.preprocessingPipeline is not None:
            ensemble_pipeline = Pipeline([("preprocessing", self.preprocessingPipeline), ("ensemble", ensemble_body)])
            ensemble_pipeline.fit(self.X_train_for_search, self.y_train)
            self.tunedModels["Ensemble"] = ensemble_pipeline
            logger.info("Ensemble pipeline built and trained (with preprocessing)")
            return ensemble_pipeline
        else:
            ensemble_body.fit(self.X_train_for_search, self.y_train)
            self.tunedModels["Ensemble"] = ensemble_body
            logger.info("Ensemble built and trained (no preprocessing)")
            return ensemble_body

    def evaluateAll(self) -> pd.DataFrame:
        """
        Evaluate tuned models (and Ensemble if present) on test set and return DataFrame sorted by Accuracy.
        """
        records = []
        for name, mdl in self.tunedModels.items():
            try:
                preds = mdl.predict(self.X_test_for_search)
                rec = {
                    "Model": name,
                    "Accuracy": float(accuracy_score(self.y_test, preds)),
                    "Precision": float(precision_score(self.y_test, preds, zero_division=0)),
                    "Recall": float(recall_score(self.y_test, preds, zero_division=0)),
                    "F1": float(f1_score(self.y_test, preds, zero_division=0)),
                    "ROC_AUC": float(roc_auc_score(self.y_test, mdl.predict_proba(self.X_test_for_search)[:,1]) if hasattr(mdl, "predict_proba") else np.nan)
                }
                records.append(rec)
                logger.info("Evaluated %s: Accuracy=%.4f", name, rec["Accuracy"])
            except Exception as exc:
                logger.warning("Evaluation failed for %s: %s", name, exc)
                records.append({"Model": name, "Accuracy": np.nan, "Precision": np.nan, "Recall": np.nan, "F1": np.nan, "ROC_AUC": np.nan})

        df = pd.DataFrame(records).sort_values(by="Accuracy", ascending=False).reset_index(drop=True)
        self.finalResults = df
        return df

# ---------- 7. Presenter ----------
class Presenter:
    """
    Present final results: confusion matrix, classification report, ROC curve and feature importance when available.

    @param model_object: fitted model or pipeline
    @param X_test_for_evaluation: features used for final evaluation
    @param y_test_for_evaluation: labels used for final evaluation
    @param output_directory: folder to save presentation figures and JSON report
    @param problem_summary: short text summarizing the business problem
    """

    def __init__(self,
                 model_object: Any,
                 X_test_for_evaluation: Union[np.ndarray, pd.DataFrame],
                 y_test_for_evaluation: Union[np.ndarray, pd.Series],
                 output_directory: str = "presentation_workspace",
                 problem_summary: str = ""):
        self.modelObject = model_object
        self.X_test = X_test_for_evaluation
        self.y_test = np.asarray(y_test_for_evaluation)
        self.outputDir = ensure_dir(output_directory)
        self.problemSummary = problem_summary
        ensure_dir(self.outputDir / "figures")

    def _save_fig_and_log(self, fig, base_name: str):
        dest = self.outputDir / "figures" / f"{base_name}.png"
        save_figure(fig, dest, dpi=300)
        logger.info("Saved figure: %s", dest)

    def generateConfusionMatrix(self) -> np.ndarray:
        """
        Create confusion matrix plot and save PNG.

        @return: confusion matrix numpy array
        """
        preds = self.modelObject.predict(self.X_test)
        cm = confusion_matrix(self.y_test, preds)
        fig, ax = plt.subplots(figsize=(6,5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title("Confusion Matrix")
        plt.tight_layout()
        self._save_fig_and_log(fig, "confusion_matrix")
        return cm

    def generateClassificationReport(self) -> Dict[str, Any]:
        """
        Compute classification report and save as JSON.

        @return: classification report dict
        """
        preds = self.modelObject.predict(self.X_test)
        report = classification_report(self.y_test, preds, output_dict=True, zero_division=0)
        report_path = self.outputDir / "classification_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info("Saved classification report to %s", report_path)
        return report

    def generateRocCurve(self) -> Optional[Tuple[np.ndarray, np.ndarray, float]]:
        """
        If probabilities or decision function exists, plot ROC and save PNG.

        @return: (fpr, tpr, roc_auc) or None
        """
        proba = None
        try:
            if hasattr(self.modelObject, "predict_proba"):
                proba = self.modelObject.predict_proba(self.X_test)[:,1]
            elif hasattr(self.modelObject, "decision_function"):
                proba = self.modelObject.decision_function(self.X_test)
        except Exception as exc:
            logger.warning("ROC curve probabilities extraction failed: %s", exc)
            proba = None

        if proba is None:
            logger.info("ROC not available (no proba/decision_function).")
            return None

        fpr, tpr, _ = roc_curve(self.y_test, proba)
        roc_auc_value = auc(fpr, tpr)
        fig, ax = plt.subplots(figsize=(7,6))
        ax.plot(fpr, tpr, label=f"AUC = {roc_auc_value:.3f}")
        ax.plot([0,1],[0,1], linestyle="--", color="gray")
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("ROC Curve")
        ax.legend()
        plt.tight_layout()
        self._save_fig_and_log(fig, "roc_curve")
        return fpr, tpr, roc_auc_value

    def generateFeatureImportance(self, feature_names: Optional[List[str]] = None, top_k: int = 20) -> Optional[np.ndarray]:
        """
        If model or pipeline contains a tree-based estimator with feature_importances_ or linear coef_, plot and save.

        @param feature_names: optional list of feature names for x-axis
        """
        # try to extract estimator if pipeline
        est = self.modelObject
        if isinstance(self.modelObject, Pipeline) and "estimator" in self.modelObject.named_steps:
            est = self.modelObject.named_steps["estimator"]

        importances = None
        labels = feature_names or []
        if hasattr(est, "feature_importances_"):
            importances = np.array(est.feature_importances_)
            if not labels:
                labels = [f"feat_{i}" for i in range(len(importances))]
        elif hasattr(est, "coef_"):
            coeffs = np.array(est.coef_)
            if coeffs.ndim > 1:
                coeffs = np.mean(coeffs, axis=0)
            importances = np.abs(coeffs).ravel()
            if not labels:
                labels = [f"feat_{i}" for i in range(len(importances))]
        else:
            logger.info("No feature importance or coefficients available for this model.")
            return None

        indices = np.argsort(importances)[::-1][:top_k]
        top_importances = importances[indices]
        top_labels = [labels[i] for i in indices]

        fig, ax = plt.subplots(figsize=(8, max(4, 0.3*len(top_labels))))
        sns.barplot(x=top_importances, y=top_labels, ax=ax)
        ax.set_title("Top Feature Importances")
        plt.tight_layout()
        self._save_fig_and_log(fig, "feature_importances")
        return top_importances

    def saveSummaryJson(self, additional_notes: Optional[Dict[str, Any]] = None) -> Path:
        """
        Save a short JSON summary of evaluation artifacts and notes.

        @param additional_notes: optional dict to include
        """
        summary = {"problem": self.problemSummary, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        summary.update(additional_notes or {})
        out_path = self.outputDir / "presentation_summary.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        logger.info("Saved presentation summary to %s", out_path)
        return out_path

# ---------- 8. Launcher (Deployment + Monitoring Helpers) ----------
class Launcher:
    """
    Save artifact, create a mini prediction endpoint factory, and simple monitoring helpers (PSI, snapshots).

    @param artifact_directory: where to save models
    @param monitoring_directory: where to store monitoring snapshots/logs
    """

    def __init__(self, artifact_directory: str = "production_models", monitoring_directory: str = "monitoring_workspace"):
        self.artifactDir = ensure_dir(artifact_directory)
        self.monitoringDir = ensure_dir(monitoring_directory)
        self.registryPath = self.artifactDir / "registry.json"

    def persistModel(self, fitted_pipeline_or_model: Any, model_name: str, metadata: Optional[Dict[str, Any]] = None) -> Path:
        """
        Persist model with fingerprint and registry entry.

        @return: path to saved artifact
        """
        bytes_obj = joblib.dumps(fitted_pipeline_or_model)
        fingerprint = hashlib.sha1(bytes_obj).hexdigest()
        timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        filename = f"{model_name}_{timestamp}_{fingerprint[:8]}.joblib"
        path = self.artifactDir / filename
        joblib.dump(fitted_pipeline_or_model, path)
        # update registry
        registry = {}
        if self.registryPath.exists():
            try:
                registry = json.loads(self.registryPath.read_text(encoding="utf-8"))
            except Exception:
                registry = {}
        registry_entry = {"model_name": model_name, "artifact": str(path), "fingerprint": fingerprint, "saved_at": timestamp, "metadata": metadata or {}}
        registry.setdefault(model_name, []).append(registry_entry)
        self.registryPath.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        logger.info("Persisted model to %s", path)
        return path

    def snapshotInputs(self, production_inputs_dataframe: pd.DataFrame, snapshot_name: Optional[str] = None) -> Path:
        """
        Save a CSV snapshot of recent production inputs for offline drift checks.

        @param production_inputs_dataframe: DataFrame
        """
        name = snapshot_name or f"snapshot_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
        path = self.monitoringDir / f"{name}.csv"
        production_inputs_dataframe.to_csv(path, index=False)
        logger.info("Saved inputs snapshot to %s", path)
        return path

    def computePSI(self, reference_array: np.ndarray, production_array: np.ndarray, buckets: int = 10) -> float:
        """
        Compute Population Stability Index (PSI) for one-dimensional numeric arrays.

        @param reference_array: historical array
        @param production_array: latest array
        """
        eps = 1e-8
        quantiles = np.linspace(0, 1, buckets+1)
        breaks = np.quantile(reference_array, quantiles)
        # ensure uniqueness
        breaks = np.unique(breaks)
        ref_counts, _ = np.histogram(reference_array, bins=breaks)
        prod_counts, _ = np.histogram(production_array, bins=breaks)
        ref_pct = (ref_counts + eps) / (len(reference_array) + eps*buckets)
        prod_pct = (prod_counts + eps) / (len(production_array) + eps*buckets)
        psi_val = np.sum((ref_pct - prod_pct) * np.log(ref_pct / prod_pct))
        logger.info("PSI computed: %.6f", psi_val)
        return float(psi_val)

# ---------- Main Orchestrator ----------
class MainOrchestrator:
    """
    Orchestrate the full pipeline end-to-end, calling each class in order.

    @param kaggle_dataset_slug: optional slug for DataManager
    """

    def __init__(self, kaggle_dataset_slug: Optional[str] = None):
        self.problemFramer = ProblemFramer("Breast Cancer Diagnostic Classification", "High recall to minimize false negatives")
        self.dataManager = DataManager(workspace_directory_path="data_workspace", kaggle_dataset_slug=kaggle_dataset_slug)
        self.explorer: Optional[ExploratoryAnalyzer] = None
        self.preparer: Optional[DataPreparer] = None
        self.shortlister: Optional[ModelShortlister] = None
        self.tuner: Optional[FineTuner] = None
        self.presenter: Optional[Presenter] = None
        self.launcher = Launcher()
        ensure_dir("artifacts")

    def run(self) -> None:
        """
        Execute pipeline sequentially. All outputs, plots and artifacts are saved under workspace folders.
        """
        logger.info("=== PIPELINE START ===")
        # 1 Frame problem
        framing = self.problemFramer.summarizeProblem()

        # 2 Get Data
        df = self.dataManager.acquireData()

        # 3 Explore
        self.explorer = ExploratoryAnalyzer(dataset_dataframe=df, target_column_name=self.dataManager.targetColumnName, output_figures_directory="figures")
        self.explorer.basicInfo()
        self.explorer.plotHistograms()
        self.explorer.plotCorrelationMatrix()
        self.explorer.plotTargetDistribution()
        # scatter two representative features if available
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            self.explorer.scatterPairWithTarget(numeric_cols[0], numeric_cols[1])

        # 4 Prepare data
        self.preparer = DataPreparer(raw_dataframe=df, target_column_name=self.dataManager.targetColumnName)
        self.preparer.splitTrainTest(stratify_on_target=True)
        self.preparer.buildPreprocessingPipeline(numerical_imputer_strategy="median", use_pca=True, pca_variance_threshold=0.95)
        X_train_prepared, X_test_prepared = self.preparer.fitTransformTrainAndTransformTest()

        # 5 Shortlist models (use prepared features from preprocessing)
        self.shortlister = ModelShortlister(X_train_prepared, X_test_prepared, self.preparer.y_train_raw, self.preparer.y_test_raw)
        shortlist_df = self.shortlister.trainQuickAndEvaluate(cv_folds=5)
        shortlist_path = Path("artifacts") / "shortlist_summary.json"
        shortlist_path.write_text(shortlist_df.to_json(orient="records"), encoding="utf-8")
        logger.info("Saved shortlist summary to %s", shortlist_path)

        # 6 Fine tune
        # Build candidate models dict using shortlister.catalog
        candidate_models = self.shortlister.modelsCatalog
        # instantiate FineTuner with feature names so ColumnTransformer with string selectors works
        feature_names_for_tuner = list(self.preparer.X_train_raw.columns)
        self.tuner = FineTuner(preprocessing_pipeline=self.preparer.pipeline_, candidate_models_dict=candidate_models,
                               X_train_source=self.preparer.X_train_raw, X_test_source=self.preparer.X_test_raw,
                               y_train_source=self.preparer.y_train_raw, y_test_source=self.preparer.y_test_raw,
                               feature_names=feature_names_for_tuner, random_state=GLOBAL_RANDOM_SEED, n_jobs=2)
        self.tuner.tuneAll(n_iter=20, cv_folds=3, scoring="accuracy", use_halving=False)
        # Ensemble
        if len(self.tuner.tunedModels) >= 2:
            self.tuner.buildEnsemble(ensemble_type="voting", voting="soft")
        eval_df = self.tuner.evaluateAll()
        eval_df.to_csv("artifacts/final_evaluation.csv", index=False)
        logger.info("Final evaluation saved to artifacts/final_evaluation.csv")

        # 7 Present results
        # choose best model
        best_model_obj = None
        if self.tuner.finalResults is not None and not self.tuner.finalResults.empty:
            best_name = self.tuner.finalResults.iloc[0]["Model"]
            best_model_obj = self.tuner.tunedModels.get(best_name)
            logger.info("Best model chosen: %s", best_name)
        elif "Ensemble" in self.tuner.tunedModels:
            best_model_obj = self.tuner.tunedModels["Ensemble"]
            logger.info("Using Ensemble as best model")
        else:
            # fallback: first tuned model
            best_model_obj = next(iter(self.tuner.tunedModels.values())) if self.tuner.tunedModels else None
            logger.info("Fallback best model selected")

        if best_model_obj is not None:
            self.presenter = Presenter(model_object=best_model_obj, X_test_for_evaluation=self.preparer.X_test_raw, y_test_for_evaluation=self.preparer.y_test_raw, output_directory="presentation_workspace", problem_summary=framing["business_objective"])
            self.presenter.generateConfusionMatrix()
            self.presenter.generateClassificationReport()
            self.presenter.generateRocCurve()
            self.presenter.generateFeatureImportance(feature_names=self.preparer.featureNamesAfterProcessing, top_k=10)
            self.presenter.saveSummaryJson({"selected_model": getattr(best_model_obj, "__class__", str(type(best_model_obj))).__name__})

        # 8 Launch
        if best_model_obj is not None:
            art_path = self.launcher.persistModel(best_model_obj, "final_best_model", metadata={"selected_on": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            # snapshot inputs for monitoring
            self.launcher.snapshotInputs(self.preparer.X_test_raw, snapshot_name="post_deploy_snapshot")
            # compute PSI for numeric columns between train and test first numeric column as example
            numeric_cols_train = self.preparer.X_train_raw.select_dtypes(include=[np.number]).columns
            if len(numeric_cols_train) > 0:
                col = numeric_cols_train[0]
                psi_val = self.launcher.computePSI(self.preparer.X_train_raw[col].values, self.preparer.X_test_raw[col].values, buckets=10)
                logger.info("PSI for column %s = %.6f", col, psi_val)

        logger.info("=== PIPELINE END ===")

# ---------- Run (example) ----------
if __name__ == "__main__":
    orchestrator = MainOrchestrator(kaggle_dataset_slug=None)  # or provide slug "yasserh/breast-cancer-dataset"
    orchestrator.run()

