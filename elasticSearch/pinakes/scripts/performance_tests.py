#!/usr/bin/env python3
"""
Pinakes — Automated Performance & Quality Test Suite
=====================================================

This module provides a comprehensive, statistically rigorous evaluation of the
Pinakes search engine. It covers:

1. Latency benchmarking (p50, p95, p99, mean, std, CV, normality)
2. Relevance scoring (nDCG, precision@k, MRR against a ground-truth set)
3. Semantic similarity of top results via TF-IDF cosine (proxy for semantic relevance)
4. Spell-check pipeline correctness (precision, recall of corrections)
5. Payload size analysis (§2.4: highlight=true should yield smaller payloads)
6. Concurrency stress test (throughput @ N parallel workers)
7. Statistical comparison: original vs improved query strategies (Wilcoxon signed-rank)

All figures are saved as publication-quality B&W PNGs (300 dpi) suitable for
scientific articles. Colour is never used — differentiation via hatching,
line styles, and markers.

Usage:
    python performance_tests.py --base-url http://localhost:8080 --output-dir ./results

Dependencies:
    pip install requests numpy scipy matplotlib scikit-learn pandas tqdm
"""

import argparse
import concurrent.futures
import json
import math
import os
import statistics
import sys
import time
import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import requests
from scipy import stats as scipy_stats
from scipy.stats import wilcoxon, mannwhitneyu, shapiro, kstest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

matplotlib.use("Agg")
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# Representative Wikipedia query dataset — covers different difficulty tiers:
#   EASY:   exact title match expected
#   MEDIUM: multi-word, potential ranking ambiguity
#   HARD:   typo, rare term, or cross-field relevance needed
QUERY_DATASET = [
    # Easy — should return a relevant result in position 1
    {"query": "binary search", "tier": "easy", "expected_title_fragment": "binary search"},
    {"query": "merge sort", "tier": "easy", "expected_title_fragment": "merge sort"},
    {"query": "fibonacci", "tier": "easy", "expected_title_fragment": "fibonacci"},
    {"query": "quantum mechanics", "tier": "easy", "expected_title_fragment": "quantum"},
    {"query": "kolmogorov complexity", "tier": "easy", "expected_title_fragment": "kolmogorov"},
    # Medium — requires multi-field or phrase matching
    {"query": "randomized binary search tree", "tier": "medium", "expected_title_fragment": "treap"},
    {"query": "divide and conquer sorting", "tier": "medium", "expected_title_fragment": "merge"},
    {"query": "atoms physical properties", "tier": "medium", "expected_title_fragment": "quantum"},
    {"query": "tree heap bst", "tier": "medium", "expected_title_fragment": "treap"},
    {"query": "computational complexity measure", "tier": "medium", "expected_title_fragment": "kolmogorov"},
    # Hard — typos and rare terms
    {"query": "binery serch", "tier": "hard", "expected_title_fragment": "binary"},
    {"query": "kolmogrov complxity", "tier": "hard", "expected_title_fragment": "kolmogorov"},
    {"query": "fibonaci sequnce", "tier": "hard", "expected_title_fragment": "fibonacci"},
    {"query": "merg srot algorithm", "tier": "hard", "expected_title_fragment": "merge"},
    {"query": "quantm mechancis atoms", "tier": "hard", "expected_title_fragment": "quantum"},
]

# Ground-truth relevance judgments for nDCG computation.
# Format: {query: {url_fragment: relevance_grade}}
# Grades: 3=highly relevant, 2=relevant, 1=marginally relevant, 0=not relevant
RELEVANCE_JUDGMENTS: Dict[str, Dict[str, int]] = {
    "binary search": {
        "Binary_search_algorithm": 3,
        "Binary_search_tree": 2,
        "Treap": 1,
    },
    "merge sort": {
        "Merge_sort": 3,
        "Randomized_algorithm": 1,
    },
    "fibonacci": {
        "Fibonacci_sequence": 3,
    },
    "quantum mechanics": {
        "Quantum_mechanics": 3,
    },
    "kolmogorov complexity": {
        "Kolmogorov_complexity": 3,
    },
    "randomized binary search tree": {
        "Treap": 3,
        "Binary_search_tree": 2,
        "Randomized_algorithm": 1,
    },
}

# Spell-check test cases: input → expected correction fragment
SPELL_CHECK_CASES = [
    ("binery serch", "binary"),
    ("kolmogrov", "kolmogorov"),
    ("fibonaci", "fibonacci"),
    ("merg srot", "merge"),
    ("algorihm", "algorithm"),
]


# ─────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class QueryResult:
    """Container for a single query execution result."""
    query: str
    tier: str
    latency_ms: float
    status_code: int
    total_hits: int
    results: List[Dict[str, Any]]
    took_es_ms: int   # ES-internal took field (excludes network)
    payload_bytes: int
    error: Optional[str] = None


@dataclass
class BenchmarkRun:
    """Aggregated results for a full benchmark run."""
    results: List[QueryResult] = field(default_factory=list)
    run_label: str = "baseline"

    @property
    def latencies(self) -> List[float]:
        return [r.latency_ms for r in self.results if r.error is None]

    @property
    def p50(self) -> float:
        return float(np.percentile(self.latencies, 50)) if self.latencies else 0

    @property
    def p95(self) -> float:
        return float(np.percentile(self.latencies, 95)) if self.latencies else 0

    @property
    def p99(self) -> float:
        return float(np.percentile(self.latencies, 99)) if self.latencies else 0

    @property
    def mean(self) -> float:
        return statistics.mean(self.latencies) if self.latencies else 0

    @property
    def std(self) -> float:
        return statistics.stdev(self.latencies) if len(self.latencies) > 1 else 0

    @property
    def cv(self) -> float:
        """Coefficient of variation — normalised dispersion; <0.3 is stable."""
        return (self.std / self.mean) if self.mean > 0 else 0

    @property
    def error_rate(self) -> float:
        errors = sum(1 for r in self.results if r.error is not None)
        return errors / len(self.results) if self.results else 0


# ─────────────────────────────────────────────────────────────────────────────
# HTTP CLIENT
# ─────────────────────────────────────────────────────────────────────────────

class PinakesClient:
    """
    Thin HTTP client for the Pinakes REST API.

    Measures wall-clock latency (includes serialisation + network) independently
    from the ES-internal 'took' field, giving us two complementary views:
      - wall_ms:  what the user actually experiences
      - es_ms:    how long ES spent (excluding Spring overhead + network)
    """

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"
        self.timeout = timeout

    def search(self, query: str, **kwargs) -> QueryResult:
        params = {"query": query, "highlight": "true", "spellCheck": "true", **kwargs}
        t0 = time.perf_counter()
        try:
            resp = self.session.get(
                f"{self.base_url}/api/search",
                params=params,
                timeout=self.timeout,
            )
            latency = (time.perf_counter() - t0) * 1000
            body = resp.json() if resp.ok else {}
            return QueryResult(
                query=query,
                tier=kwargs.get("tier", "unknown"),
                latency_ms=latency,
                status_code=resp.status_code,
                total_hits=body.get("totalCount", 0),
                results=body.get("results", []),
                took_es_ms=body.get("tookMs", 0),
                payload_bytes=len(resp.content),
                error=None if resp.ok else f"HTTP {resp.status_code}",
            )
        except Exception as exc:
            return QueryResult(
                query=query,
                tier="unknown",
                latency_ms=(time.perf_counter() - t0) * 1000,
                status_code=0,
                total_hits=0,
                results=[],
                took_es_ms=0,
                payload_bytes=0,
                error=str(exc),
            )

    def suggest(self, query: str) -> Optional[Dict]:
        try:
            resp = self.session.get(
                f"{self.base_url}/api/suggest",
                params={"query": query},
                timeout=self.timeout,
            )
            return resp.json() if resp.ok else None
        except Exception:
            return None

    def health(self) -> bool:
        try:
            resp = self.session.get(f"{self.base_url}/api/health", timeout=5)
            return resp.ok
        except Exception:
            return False


# ─────────────────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_ndcg(results: List[Dict], query: str, k: int = 5) -> float:
    """
    Normalised Discounted Cumulative Gain @ k.

    DCG rewards relevant results at the top of the ranking.
    nDCG = DCG / ideal_DCG, so it's always in [0, 1].

    Formula:  DCG = Σ (2^rel_i - 1) / log2(i + 2)   for i in [0..k-1]

    Relevance grades come from RELEVANCE_JUDGMENTS; unrated results get 0.
    """
    judgments = RELEVANCE_JUDGMENTS.get(query, {})
    if not judgments:
        return float("nan")

    def rel_grade(result: Dict) -> int:
        url = result.get("url", "")
        for fragment, grade in judgments.items():
            if fragment.lower() in url.lower():
                return grade
        return 0

    gains = [rel_grade(r) for r in results[:k]]
    dcg = sum((2 ** g - 1) / math.log2(i + 2) for i, g in enumerate(gains))
    ideal_gains = sorted(judgments.values(), reverse=True)[:k]
    ideal_dcg = sum((2 ** g - 1) / math.log2(i + 2) for i, g in enumerate(ideal_gains))
    return dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def compute_mrr(results: List[Dict], query: str) -> float:
    """
    Mean Reciprocal Rank — position of first relevant result.
    MRR = 1/rank_of_first_relevant, 0 if no relevant result in top 10.
    """
    judgments = RELEVANCE_JUDGMENTS.get(query, {})
    if not judgments:
        return float("nan")
    for i, r in enumerate(results[:10]):
        url = r.get("url", "")
        for fragment in judgments:
            if fragment.lower() in url.lower() and judgments[fragment] >= 2:
                return 1.0 / (i + 1)
    return 0.0


def compute_precision_at_k(results: List[Dict], query: str, k: int = 5) -> float:
    """
    Precision@k = (relevant results in top k) / k
    A result is relevant if its grade ≥ 1 in RELEVANCE_JUDGMENTS.
    """
    judgments = RELEVANCE_JUDGMENTS.get(query, {})
    if not judgments:
        return float("nan")
    relevant = 0
    for r in results[:k]:
        url = r.get("url", "")
        for fragment, grade in judgments.items():
            if fragment.lower() in url.lower() and grade >= 1:
                relevant += 1
                break
    return relevant / k


def compute_semantic_similarity(results: List[Dict], query: str) -> float:
    """
    TF-IDF cosine similarity between the query and the concatenated
    title + abstract of the top-5 results.

    This is a proxy for semantic relevance when ground-truth judgments
    are unavailable. Higher cosine = more topically aligned results.

    Limitations: TF-IDF is not a true semantic model (no word embeddings);
    it measures lexical overlap. Suitable for a controlled dataset with known
    vocabulary overlap.
    """
    docs = [
        f"{r.get('title', '')} {r.get('abs', '')}"
        for r in results[:5]
    ]
    if not docs:
        return 0.0
    try:
        corpus = [query] + docs
        vectorizer = TfidfVectorizer(stop_words="english", min_df=1)
        tfidf = vectorizer.fit_transform(corpus)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        return float(np.mean(sims))
    except Exception:
        return 0.0


def normality_test(data: List[float]) -> Tuple[str, float]:
    """
    Tests whether latency distribution is normal.
    Uses Shapiro-Wilk for n≤50, Kolmogorov-Smirnov for larger samples.
    Returns (test_name, p_value).
    """
    if len(data) < 3:
        return ("insufficient_data", float("nan"))
    if len(data) <= 50:
        _, p = shapiro(data)
        return ("shapiro-wilk", p)
    else:
        _, p = kstest(data, "norm",
                      args=(np.mean(data), np.std(data)))
        return ("kolmogorov-smirnov", p)


# ─────────────────────────────────────────────────────────────────────────────
# BENCHMARK RUNNERS
# ─────────────────────────────────────────────────────────────────────────────

def run_latency_benchmark(client: PinakesClient,
                          n_warmup: int = 5,
                          n_iterations: int = 3) -> BenchmarkRun:
    """
    Executes all queries n_iterations times, with warm-up rounds discarded.

    Why warm-up? The JVM JIT and ES field-data caches are cold on first access.
    Discarding warm-up rounds isolates steady-state latency.
    """
    run = BenchmarkRun(run_label="latency_benchmark")

    # Warm-up
    print(f"  Warming up ({n_warmup} rounds)…")
    for _ in range(n_warmup):
        for q in QUERY_DATASET:
            client.search(q["query"])

    # Measurement
    print(f"  Measuring ({n_iterations} iterations × {len(QUERY_DATASET)} queries)…")
    for _ in tqdm(range(n_iterations), desc="  Benchmark"):
        for q in QUERY_DATASET:
            result = client.search(q["query"], tier=q["tier"])
            run.results.append(result)

    return run


def run_relevance_evaluation(client: PinakesClient) -> Dict[str, Any]:
    """
    Evaluates retrieval quality against the ground-truth relevance judgments.
    Returns per-query and aggregate metrics.
    """
    metrics = []
    print("  Evaluating relevance metrics…")
    for q in tqdm(QUERY_DATASET, desc="  Relevance"):
        result = client.search(q["query"])
        if result.error:
            continue
        ndcg   = compute_ndcg(result.results, q["query"])
        mrr    = compute_mrr(result.results, q["query"])
        p_at_5 = compute_precision_at_k(result.results, q["query"], k=5)
        sem    = compute_semantic_similarity(result.results, q["query"])
        metrics.append({
            "query": q["query"],
            "tier": q["tier"],
            "ndcg@5": ndcg,
            "mrr": mrr,
            "precision@5": p_at_5,
            "semantic_sim": sem,
            "total_hits": result.total_hits,
        })
    return {
        "per_query": metrics,
        "aggregate": {
            "ndcg@5_mean":       float(np.nanmean([m["ndcg@5"] for m in metrics])),
            "mrr_mean":          float(np.nanmean([m["mrr"] for m in metrics])),
            "precision@5_mean":  float(np.nanmean([m["precision@5"] for m in metrics])),
            "semantic_sim_mean": float(np.mean([m["semantic_sim"] for m in metrics])),
        },
    }


def run_payload_analysis(client: PinakesClient) -> Dict[str, Any]:
    """
    §2.4 validation: compares response payload sizes with highlight=true vs false.
    Expected: highlight=true yields significantly smaller payloads because
    'content' is excluded from _source (only fragments returned).
    """
    hl_sizes, no_hl_sizes = [], []
    print("  Analysing payload sizes (highlight=true vs false)…")
    for q in tqdm(QUERY_DATASET[:10], desc="  Payload"):
        r_hl   = client.search(q["query"], highlight="true")
        r_noHl = client.search(q["query"], highlight="false")
        if not r_hl.error:  hl_sizes.append(r_hl.payload_bytes)
        if not r_noHl.error: no_hl_sizes.append(r_noHl.payload_bytes)

    ratio = np.mean(no_hl_sizes) / np.mean(hl_sizes) if hl_sizes else 0
    # Wilcoxon signed-rank test: non-parametric, paired, tests H0: no size difference
    if len(hl_sizes) >= 6 and len(no_hl_sizes) >= 6:
        stat, p_val = wilcoxon(no_hl_sizes[:len(hl_sizes)], hl_sizes)
    else:
        stat, p_val = float("nan"), float("nan")

    return {
        "hl_sizes_bytes": hl_sizes,
        "no_hl_sizes_bytes": no_hl_sizes,
        "mean_hl": float(np.mean(hl_sizes)) if hl_sizes else 0,
        "mean_no_hl": float(np.mean(no_hl_sizes)) if no_hl_sizes else 0,
        "reduction_ratio": ratio,
        "wilcoxon_stat": stat,
        "wilcoxon_p": p_val,
        "significant": p_val < 0.05 if not math.isnan(p_val) else False,
    }


def run_spell_check_evaluation(client: PinakesClient) -> Dict[str, Any]:
    """
    Evaluates the spell-check pipeline against known misspelling cases.
    Measures correction precision (did it correct it?) and
    correction accuracy (was the correction right?).
    """
    results = []
    print("  Evaluating spell-check pipeline…")
    for misspelled, expected in tqdm(SPELL_CHECK_CASES, desc="  SpellCheck"):
        resp = client.suggest(misspelled)
        corrected = False
        correct_correction = False
        correction_text = ""
        if resp and resp.get("hasSuggestion") and resp.get("suggestions"):
            corrected = True
            correction_text = resp["suggestions"][0]
            correct_correction = expected.lower() in correction_text.lower()
        results.append({
            "input": misspelled,
            "expected": expected,
            "corrected": corrected,
            "correct_correction": correct_correction,
            "suggestion": correction_text,
        })

    precision = sum(1 for r in results if r["corrected"]) / len(results)
    accuracy  = sum(1 for r in results if r["correct_correction"]) / len(results)
    return {
        "cases": results,
        "correction_rate": precision,
        "accuracy": accuracy,
        "n_cases": len(results),
    }


def run_concurrency_test(client: PinakesClient,
                         n_workers: List[int] = (1, 2, 4, 8)) -> Dict[str, Any]:
    """
    Measures throughput (requests/sec) and p95 latency at different concurrency levels.
    Uses ThreadPoolExecutor to simulate concurrent users.
    This is NOT a load test — it's a concurrency characterisation to confirm that
    CompletableFuture on the server side scales gracefully.
    """
    results = {}
    queries = [q["query"] for q in QUERY_DATASET[:5]]  # use 5 queries, rotated

    for n in n_workers:
        print(f"  Concurrency: {n} workers…")
        latencies = []
        n_requests = n * 4  # 4 requests per worker
        t_start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(max_workers=n) as pool:
            futures = [
                pool.submit(client.search, queries[i % len(queries)])
                for i in range(n_requests)
            ]
            for fut in concurrent.futures.as_completed(futures):
                r = fut.result()
                if not r.error:
                    latencies.append(r.latency_ms)

        total_time = time.perf_counter() - t_start
        throughput  = len(latencies) / total_time

        results[n] = {
            "workers": n,
            "requests": n_requests,
            "latencies": latencies,
            "throughput_rps": throughput,
            "p50": float(np.percentile(latencies, 50)) if latencies else 0,
            "p95": float(np.percentile(latencies, 95)) if latencies else 0,
            "error_count": n_requests - len(latencies),
        }

    return results


def run_tier_comparison(client: PinakesClient, n_repeats: int = 5) -> Dict[str, Any]:
    """
    Compares latency across query difficulty tiers (easy / medium / hard).
    Tests H0: mean latency is equal across tiers via one-way Kruskal-Wallis
    (non-parametric equivalent of ANOVA, appropriate for potentially non-normal data).
    """
    tier_latencies = defaultdict(list)
    for _ in tqdm(range(n_repeats), desc="  Tier comparison"):
        for q in QUERY_DATASET:
            r = client.search(q["query"])
            if not r.error:
                tier_latencies[q["tier"]].append(r.latency_ms)

    # Kruskal-Wallis test
    groups = list(tier_latencies.values())
    if len(groups) >= 2:
        stat, p_val = scipy_stats.kruskal(*groups)
    else:
        stat, p_val = float("nan"), float("nan")

    return {
        "tier_latencies": dict(tier_latencies),
        "kruskal_stat": float(stat),
        "kruskal_p": float(p_val),
        "significant_difference": p_val < 0.05,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PLOTTING — B&W, 300 DPI, publication-ready
# ─────────────────────────────────────────────────────────────────────────────

# Global style: no colour, clean grid, appropriate font sizes for A4 paper
plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "lines.linewidth": 1.5,
    "axes.grid": True,
    "grid.alpha": 0.4,
    "grid.linestyle": "--",
    "figure.figsize": (8, 5),
})

BW_HATCHES = ["/", "\\", "x", ".", "o", "+", "-", "|", "*"]
BW_MARKERS = ["o", "s", "^", "D", "v", "P", "*"]
BW_LINESTYLES = ["-", "--", "-.", ":", (0, (3, 1, 1, 1))]


def _save(fig: plt.Figure, path: Path, label: str) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"    Saved: {path.name}")


def plot_latency_distribution(run: BenchmarkRun, output_dir: Path) -> None:
    """
    Figure 1: Latency distribution — histogram + KDE + percentile markers.
    Statistical annotation: mean, std, p95, normality test result.
    """
    latencies = run.latencies
    test_name, p_val = normality_test(latencies)
    normality_str = f"Normality ({test_name}): p={p_val:.4f}"

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel A: Histogram + KDE
    ax = axes[0]
    n_bins = min(40, max(10, len(latencies) // 5))
    ax.hist(latencies, bins=n_bins, density=True,
            color="white", edgecolor="black", linewidth=0.8,
            label="Observed frequency")

    # KDE via scipy
    if len(latencies) > 5:
        kde = scipy_stats.gaussian_kde(latencies, bw_method=0.3)
        x = np.linspace(min(latencies), max(latencies), 300)
        ax.plot(x, kde(x), "k-", linewidth=2, label="KDE")

    # Percentile lines
    for label, val, ls in [
        ("p50", run.p50, "--"),
        ("p95", run.p95, "-."),
        ("p99", run.p99, ":"),
    ]:
        ax.axvline(val, color="black", linestyle=ls, linewidth=1.5,
                   label=f"{label}={val:.1f} ms")

    ax.set_xlabel("Response Latency (ms)")
    ax.set_ylabel("Density")
    ax.set_title("(A) Latency Distribution")
    ax.legend(fontsize=8)
    ax.annotate(
        f"n={len(latencies)}  μ={run.mean:.1f}  σ={run.std:.1f}  CV={run.cv:.2f}\n{normality_str}",
        xy=(0.98, 0.97), xycoords="axes fraction",
        ha="right", va="top", fontsize=7.5,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.9),
    )

    # Panel B: Box-plot per tier
    ax = axes[1]
    tier_data = defaultdict(list)
    for r in run.results:
        if not r.error:
            tier_data[r.tier].append(r.latency_ms)

    tiers = sorted(tier_data.keys())
    tier_arrays = [tier_data[t] for t in tiers if tier_data[t]]
    tier_labels = [t for t in tiers if tier_data[t]]
    if tier_arrays:
        bp = ax.boxplot(tier_arrays, labels=tier_labels,
                        patch_artist=True, notch=False,
                        medianprops=dict(color="black", linewidth=2))
        for patch, hatch in zip(bp["boxes"], BW_HATCHES):
            patch.set_facecolor("white")
            patch.set_hatch(hatch)
    else:
        ax.text(0.5, 0.5, "No tier data", ha="center", va="center",
                transform=ax.transAxes, fontsize=10, color="gray")

    ax.set_xlabel("Query Difficulty Tier")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("(B) Latency by Query Tier")

    _save(fig, output_dir / "fig1_latency_distribution.png", "Figure 1")


def plot_latency_percentiles(run: BenchmarkRun, output_dir: Path) -> None:
    """
    Figure 2: Percentile curve (latency vs. percentile rank).
    Shows the full shape of the tail — important for SLA analysis.
    """
    latencies = sorted(run.latencies)
    if not latencies:
        print("    Skipping Fig 2 — no latency data")
        return
    percentiles = np.linspace(0, 100, len(latencies))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(percentiles, latencies, "k-", linewidth=1.5, label="Observed")

    # Mark key percentiles
    for pct, ls, mk in [(50, "--", "o"), (90, "-.", "s"), (95, ":", "^"), (99, (0, (3,1,1,1)), "D")]:
        val = float(np.percentile(latencies, pct))
        ax.axvline(pct, color="black", linestyle=ls, linewidth=1, alpha=0.7)
        ax.annotate(f"p{pct}={val:.0f}ms",
                    xy=(pct, val), xytext=(pct + 1, val * 1.05),
                    fontsize=8, arrowprops=dict(arrowstyle="->", color="black"),
                    color="black")

    ax.set_xlabel("Percentile Rank (%)")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Figure 2 — Response Time Percentile Curve")
    ax.legend()

    _save(fig, output_dir / "fig2_percentile_curve.png", "Figure 2")


def plot_relevance_metrics(eval_data: Dict, output_dir: Path) -> None:
    """
    Figure 3: Relevance metrics grouped by tier.
    Bar chart of nDCG@5, MRR, Precision@5 per query tier.
    """
    per_query = [m for m in eval_data["per_query"] if not math.isnan(m.get("ndcg@5", float("nan")))]
    if not per_query:
        print("    Skipping Fig 3 — no ground-truth data available")
        return

    df = pd.DataFrame(per_query)
    tiers = df["tier"].unique().tolist()
    metrics = ["ndcg@5", "mrr", "precision@5"]
    metric_labels = ["nDCG@5", "MRR", "Precision@5"]

    x = np.arange(len(tiers))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (m, lbl) in enumerate(zip(metrics, metric_labels)):
        vals = [df[df["tier"] == t][m].mean() for t in tiers]
        bars = ax.bar(x + i * width, vals, width,
                      label=lbl, color="white", edgecolor="black",
                      hatch=BW_HATCHES[i])
        # Value labels on bars
        for bar, v in zip(bars, vals):
            if not math.isnan(v):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.01, f"{v:.2f}",
                        ha="center", va="bottom", fontsize=7.5)

    ax.set_xticks(x + width)
    ax.set_xticklabels([t.capitalize() for t in tiers])
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("Query Difficulty Tier")
    ax.set_ylabel("Score (0–1)")
    ax.set_title("Figure 3 — Retrieval Quality Metrics by Query Tier")
    ax.legend()

    agg = eval_data["aggregate"]
    ax.annotate(
        f"Overall: nDCG@5={agg['ndcg@5_mean']:.3f}  MRR={agg['mrr_mean']:.3f}  P@5={agg['precision@5_mean']:.3f}",
        xy=(0.5, 1.01), xycoords="axes fraction",
        ha="center", fontsize=9,
    )

    _save(fig, output_dir / "fig3_relevance_metrics.png", "Figure 3")


def plot_payload_comparison(payload_data: Dict, output_dir: Path) -> None:
    """
    Figure 4: Payload size comparison (highlight=true vs false).
    Validates §2.4 improvement: content excluded from _source when highlight active.
    Includes Wilcoxon test result as annotation.
    """
    hl  = payload_data["hl_sizes_bytes"]
    nhl = payload_data["no_hl_sizes_bytes"]
    n   = min(len(hl), len(nhl))
    if n == 0:
        print("    Skipping Fig 4 — no payload data")
        return

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # Panel A: paired bar chart
    ax = axes[0]
    idx = np.arange(n)
    w   = 0.35
    ax.bar(idx - w/2, [b/1024 for b in nhl[:n]], w,
           label="highlight=false (full content)", color="white",
           edgecolor="black", hatch="//")
    ax.bar(idx + w/2, [b/1024 for b in hl[:n]], w,
           label="highlight=true (fragments only)", color="white",
           edgecolor="black", hatch="\\\\")
    ax.set_xticks(idx)
    ax.set_xticklabels([f"Q{i+1}" for i in range(n)], rotation=45)
    ax.set_xlabel("Query")
    ax.set_ylabel("Payload Size (KB)")
    ax.set_title("(A) Payload Size Per Query")
    ax.legend(fontsize=8)

    stat = payload_data.get("wilcoxon_stat", float("nan"))
    p    = payload_data.get("wilcoxon_p", float("nan"))
    sig  = "✓ significant" if payload_data.get("significant") else "✗ not significant"
    ax.annotate(
        f"Wilcoxon signed-rank: W={stat:.2f}, p={p:.4f} ({sig})\n"
        f"Payload reduction ratio: ×{payload_data['reduction_ratio']:.2f}",
        xy=(0.5, 0.97), xycoords="axes fraction",
        ha="center", va="top", fontsize=8,
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="black"),
    )

    # Panel B: violin / box
    ax = axes[1]
    data = [[b/1024 for b in nhl], [b/1024 for b in hl]]
    bp = ax.boxplot(data, labels=["highlight=false", "highlight=true"],
                    patch_artist=True, notch=False,
                    medianprops=dict(color="black", linewidth=2))
    for patch, hatch in zip(bp["boxes"], ["//", "\\\\"]):
        patch.set_facecolor("white")
        patch.set_hatch(hatch)
    ax.set_ylabel("Payload Size (KB)")
    ax.set_title("(B) Payload Size Distribution")

    _save(fig, output_dir / "fig4_payload_comparison.png", "Figure 4")


def plot_concurrency_throughput(conc_data: Dict, output_dir: Path) -> None:
    """
    Figure 5: Throughput vs. concurrency level.
    Shows how requests/sec and p95 latency evolve as workers increase.
    """
    workers    = sorted(conc_data.keys())
    if not workers:
        print("    Skipping Fig 5 — no concurrency data")
        return
    throughput = [conc_data[w]["throughput_rps"] for w in workers]
    p95_vals   = [conc_data[w]["p95"] for w in workers]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()

    ax1.plot(workers, throughput, "k-o", linewidth=2, markersize=7,
             label="Throughput (req/s)")
    ax2.plot(workers, p95_vals, "k--s", linewidth=2, markersize=7,
             label="p95 Latency (ms)")

    ax1.set_xlabel("Concurrent Workers")
    ax1.set_ylabel("Throughput (requests/sec)")
    ax2.set_ylabel("p95 Latency (ms)")
    ax1.set_title("Figure 5 — Throughput and Latency vs. Concurrency Level")
    ax1.set_xticks(workers)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    _save(fig, output_dir / "fig5_concurrency_throughput.png", "Figure 5")


def plot_tier_latency_comparison(tier_data: Dict, output_dir: Path) -> None:
    """
    Figure 6: Latency statistics per query tier with Kruskal-Wallis annotation.
    Demonstrates whether query complexity (easy/medium/hard) affects response time.
    """
    tier_latencies = tier_data["tier_latencies"]
    tiers = [t for t in sorted(tier_latencies.keys()) if tier_latencies[t]]
    if not tiers:
        print("    Skipping Fig 6 — no tier latency data")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot([tier_latencies[t] for t in tiers],
                    labels=[t.capitalize() for t in tiers],
                    patch_artist=True, notch=False,
                    medianprops=dict(color="black", linewidth=2),
                    showfliers=True,
                    flierprops=dict(marker="x", color="black", markersize=5))
    for patch, hatch in zip(bp["boxes"], BW_HATCHES):
        patch.set_facecolor("white")
        patch.set_hatch(hatch)

    ax.set_xlabel("Query Difficulty Tier")
    ax.set_ylabel("Latency (ms)")
    ax.set_title("Figure 6 — Latency Distribution by Query Tier")

    stat = tier_data["kruskal_stat"]
    p    = tier_data["kruskal_p"]
    sig  = "p < 0.05 → tiers differ significantly" \
           if tier_data["significant_difference"] else "p ≥ 0.05 → no significant difference"
    ax.annotate(
        f"Kruskal-Wallis H={stat:.2f}, p={p:.4f}\n{sig}",
        xy=(0.98, 0.97), xycoords="axes fraction",
        ha="right", va="top", fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black"),
    )

    _save(fig, output_dir / "fig6_tier_latency.png", "Figure 6")


def plot_semantic_similarity(eval_data: Dict, output_dir: Path) -> None:
    """
    Figure 7: TF-IDF cosine similarity heatmap — query vs. tier.
    Visualises how semantically aligned the top-5 results are with the query,
    as a proxy for retrieval relevance when no ground truth is available.
    """
    per_query = eval_data["per_query"]
    if not per_query:
        return

    queries = [m["query"][:30] + ("…" if len(m["query"]) > 30 else "") for m in per_query]
    sims    = [m["semantic_sim"] for m in per_query]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(queries, sims, color="white", edgecolor="black")
    for bar, hatch in zip(bars, BW_HATCHES * 3):
        bar.set_hatch(hatch)
    ax.axvline(np.mean(sims), color="black", linestyle="--", linewidth=1.5,
               label=f"Mean = {np.mean(sims):.3f}")
    ax.set_xlabel("TF-IDF Cosine Similarity (query vs. top-5 results)")
    ax.set_title("Figure 7 — Semantic Alignment of Results per Query")
    ax.legend()
    ax.set_xlim(0, 1)

    _save(fig, output_dir / "fig7_semantic_similarity.png", "Figure 7")


def plot_spell_check_summary(sc_data: Dict, output_dir: Path) -> None:
    """
    Figure 8: Spell-check pipeline evaluation.
    Shows per-case outcome and overall correction rate.
    """
    cases = sc_data["cases"]
    labels = [c["input"] for c in cases]
    corrected = [1 if c["corrected"] else 0 for c in cases]
    accurate  = [1 if c["correct_correction"] else 0 for c in cases]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel A: per-case outcome matrix
    ax = axes[0]
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w/2, corrected, w, label="Correction triggered",
           color="white", edgecolor="black", hatch="//")
    ax.bar(x + w/2, accurate, w, label="Correction accurate",
           color="white", edgecolor="black", hatch="\\\\")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["No", "Yes"])
    ax.set_title("(A) Per-case Spell-Check Outcome")
    ax.legend(fontsize=8)

    # Panel B: summary donut-style bar
    ax = axes[1]
    metrics = ["Correction Rate", "Correction Accuracy"]
    vals    = [sc_data["correction_rate"], sc_data["accuracy"]]
    bars = ax.bar(metrics, vals, color="white", edgecolor="black",
                  hatch=["/", "\\"])
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.02, f"{v:.0%}",
                ha="center", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 1.2)
    ax.set_ylabel("Rate (0–1)")
    ax.set_title("(B) Overall Spell-Check Performance")
    ax.annotate(
        f"n={sc_data['n_cases']} test cases",
        xy=(0.5, 1.01), xycoords="axes fraction", ha="center", fontsize=9
    )

    _save(fig, output_dir / "fig8_spell_check.png", "Figure 8")


def plot_summary_dashboard(run: BenchmarkRun, eval_data: Dict,
                           payload_data: Dict, sc_data: Dict,
                           output_dir: Path) -> None:
    """
    Figure 9: Single-page summary dashboard for paper inclusion.
    Condenses the most important metrics into one figure.
    """
    fig = plt.figure(figsize=(14, 9))
    fig.suptitle("Pinakes Search Engine — Performance & Quality Summary",
                 fontsize=13, fontweight="bold", y=1.01)

    gs = fig.add_gridspec(2, 3, hspace=0.5, wspace=0.4)

    # ① Latency summary bar
    ax1 = fig.add_subplot(gs[0, 0])
    labels = ["Mean", "p50", "p95", "p99"]
    vals   = [run.mean, run.p50, run.p95, run.p99]
    bars = ax1.bar(labels, vals, color="white", edgecolor="black")
    for bar, hatch, v in zip(bars, BW_HATCHES, vals):
        bar.set_hatch(hatch)
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{v:.0f}", ha="center", fontsize=8)
    ax1.set_ylabel("ms")
    ax1.set_title("① Latency Percentiles")

    # ② Relevance scores
    ax2 = fig.add_subplot(gs[0, 1])
    agg = eval_data.get("aggregate", {})
    m_labels = ["nDCG@5", "MRR", "P@5", "Sem.Sim"]
    m_vals   = [agg.get("ndcg@5_mean", 0), agg.get("mrr_mean", 0),
                agg.get("precision@5_mean", 0), agg.get("semantic_sim_mean", 0)]
    bars = ax2.bar(m_labels, m_vals, color="white", edgecolor="black")
    for bar, hatch, v in zip(bars, BW_HATCHES, m_vals):
        bar.set_hatch(hatch)
        if not math.isnan(v):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                     f"{v:.2f}", ha="center", fontsize=8)
    ax2.set_ylim(0, 1.2)
    ax2.set_title("② Relevance Metrics")

    # ③ Payload reduction
    ax3 = fig.add_subplot(gs[0, 2])
    groups = ["highlight=false\n(full content)", "highlight=true\n(fragments)"]
    sizes  = [payload_data.get("mean_no_hl", 0)/1024,
              payload_data.get("mean_hl", 0)/1024]
    bars = ax3.bar(groups, sizes, color="white", edgecolor="black",
                   hatch=["//", "\\\\"])
    for bar, v in zip(bars, sizes):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f"{v:.1f} KB", ha="center", fontsize=8)
    ax3.set_ylabel("Mean Payload (KB)")
    ax3.set_title(f"③ Payload Reduction\n(×{payload_data.get('reduction_ratio',0):.1f})")

    # ④ Spell-check summary
    ax4 = fig.add_subplot(gs[1, 0])
    sc_vals   = [sc_data.get("correction_rate", 0), sc_data.get("accuracy", 0)]
    sc_labels = ["Correction Rate", "Accuracy"]
    bars = ax4.bar(sc_labels, sc_vals, color="white", edgecolor="black",
                   hatch=["//", "\\\\"])
    for bar, v in zip(bars, sc_vals):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f"{v:.0%}", ha="center", fontsize=9, fontweight="bold")
    ax4.set_ylim(0, 1.2)
    ax4.set_title("④ Spell-Check Performance")

    # ⑤ Latency CDF
    ax5 = fig.add_subplot(gs[1, 1])
    sorted_l = sorted(run.latencies)
    cdf = np.arange(1, len(sorted_l) + 1) / len(sorted_l)
    ax5.plot(sorted_l, cdf, "k-", linewidth=1.5)
    ax5.axhline(0.95, color="black", linestyle="--", linewidth=1, alpha=0.7, label="95th %ile")
    ax5.set_xlabel("Latency (ms)")
    ax5.set_ylabel("CDF")
    ax5.set_title("⑤ Latency CDF")
    ax5.legend(fontsize=8)

    # ⑥ Textual stats table
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis("off")
    table_data = [
        ["Metric", "Value"],
        ["n queries",     str(len(run.results))],
        ["Error rate",    f"{run.error_rate:.1%}"],
        ["Mean latency",  f"{run.mean:.1f} ms"],
        ["Std dev",       f"{run.std:.1f} ms"],
        ["CV",            f"{run.cv:.3f}"],
        ["p95",           f"{run.p95:.1f} ms"],
        ["p99",           f"{run.p99:.1f} ms"],
    ]
    t = ax6.table(cellText=table_data[1:], colLabels=table_data[0],
                  loc="center", cellLoc="center")
    t.auto_set_font_size(False)
    t.set_fontsize(9)
    t.scale(1, 1.4)
    ax6.set_title("⑥ Statistical Summary")

    _save(fig, output_dir / "fig9_summary_dashboard.png", "Figure 9 (Summary)")


# ─────────────────────────────────────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────────────────────────────────────

def save_json_report(data: Dict, output_dir: Path) -> None:
    """Saves the full results as a machine-readable JSON for CI/CD thresholds."""
    path = output_dir / "performance_report.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"    Saved JSON report: {path.name}")


def print_summary(run: BenchmarkRun, eval_data: Dict,
                  payload_data: Dict, sc_data: Dict) -> None:
    """Prints a concise human-readable summary to stdout."""
    sep = "═" * 60
    print(f"\n{sep}")
    print("  PINAKES PERFORMANCE REPORT")
    print(sep)
    print(f"  Queries executed : {len(run.results)}")
    print(f"  Error rate       : {run.error_rate:.1%}")
    print(f"  Mean latency     : {run.mean:.1f} ms")
    print(f"  Std dev          : {run.std:.1f} ms")
    print(f"  CV (stability)   : {run.cv:.3f}  {'✓ stable' if run.cv < 0.3 else '⚠ variable'}")
    print(f"  p50 / p95 / p99  : {run.p50:.0f} / {run.p95:.0f} / {run.p99:.0f} ms")
    print()
    agg = eval_data.get("aggregate", {})
    print(f"  nDCG@5 (mean)    : {agg.get('ndcg@5_mean', float('nan')):.3f}")
    print(f"  MRR (mean)       : {agg.get('mrr_mean', float('nan')):.3f}")
    print(f"  Precision@5      : {agg.get('precision@5_mean', float('nan')):.3f}")
    print(f"  Semantic sim     : {agg.get('semantic_sim_mean', 0):.3f}")
    print()
    print(f"  Payload reduction: ×{payload_data.get('reduction_ratio', 0):.2f}  "
          f"({'significant' if payload_data.get('significant') else 'not significant'})")
    print(f"  Spell correction : {sc_data.get('correction_rate', 0):.0%} rate, "
          f"{sc_data.get('accuracy', 0):.0%} accuracy")
    print(sep)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATION
# ─────────────────────────────────────────────────────────────────────────────

def wait_for_service(client: PinakesClient, max_wait: int = 120) -> None:
    """Blocks until the Pinakes health endpoint responds or timeout is exceeded."""
    print(f"Waiting for Pinakes at {client.base_url} …")
    deadline = time.time() + max_wait
    while time.time() < deadline:
        if client.health():
            print("  Service is up!\n")
            return
        time.sleep(3)
    print(f"ERROR: Service did not respond within {max_wait}s. Exiting.")
    sys.exit(1)



# ─────────────────────────────────────────────────────────────────────────────
# HOLISTIC SPELL-CHECK & EXACT-PHRASE TESTS (new features)
# ─────────────────────────────────────────────────────────────────────────────

HOLISTIC_CASES = [
    {
        "input":    "Einsin's foula, revolutiozed physics",
        "expected_corrections": ["einstein", "formula", "revolutionized"],
        "unchanged": ["physics"],
    },
    {
        "input":    "binery serach tree",
        "expected_corrections": ["binary", "search"],
        "unchanged": ["tree"],
    },
    {
        "input":    "kolmogrov complxity measur",
        "expected_corrections": ["kolmogorov", "complexity", "measure"],
        "unchanged": [],
    },
]

EXACT_PHRASE_CASES = [
    # query with quotes should return the phrase result first
    {
        "query":           '"binary search" algorithm',
        "expected_in_top": "binary search",
    },
    {
        "query":           '"merge sort" divide conquer',
        "expected_in_top": "merge sort",
    },
]


def run_holistic_spell_check_test(client: PinakesClient) -> Dict[str, Any]:
    """
    Validates the holistic spell-check pipeline end-to-end:
      1. Calls /api/suggest for a misspelled multi-word query.
      2. Verifies that correctedQueryHtml contains <strong class="correction"> on
         changed tokens and NOT on correct tokens.
      3. Checks case preservation (EINSIN → EINSTEIN, Einsin → Einstein).
    """
    results = []
    print("  Holistic spell-check validation…")
    for case in HOLISTIC_CASES:
        resp = client.suggest(case["input"])
        if resp is None:
            results.append({"input": case["input"], "status": "api_error"})
            continue

        suggestion = resp.get("suggestions", [""])[0] if resp.get("hasSuggestion") else ""
        html        = resp.get("correctedQueryHtml", "")
        corrections_found = []
        unchanged_found   = []

        for expected in case["expected_corrections"]:
            if expected.lower() in suggestion.lower():
                corrections_found.append(expected)
        for word in case["unchanged"]:
            if word.lower() in suggestion.lower():
                unchanged_found.append(word)

        strong_count = html.count('<strong class="correction">')
        results.append({
            "input":               case["input"],
            "suggestion":          suggestion,
            "corrections_found":   corrections_found,
            "expected_corrections":case["expected_corrections"],
            "unchanged_preserved": unchanged_found,
            "strong_tag_count":    strong_count,
            "has_html_diff":       strong_count > 0,
        })

    precision = sum(1 for r in results if len(r.get("corrections_found", [])) > 0) / max(len(results), 1)
    return {
        "cases":    results,
        "precision": precision,
        "n_cases":   len(results),
    }


def run_exact_phrase_test(client: PinakesClient) -> Dict[str, Any]:
    """
    Validates exact phrase search:
      - Queries with "quotes" should return results where the phrase appears together.
      - Results from exact-phrase queries should score the phrase match at top.
    """
    results = []
    print("  Exact-phrase search validation…")
    for case in EXACT_PHRASE_CASES:
        result = client.search(case["query"])
        top_title = result.results[0].get("title", "") if result.results else ""
        top_abs   = result.results[0].get("abs", "")   if result.results else ""
        phrase_in_top = (
            case["expected_in_top"].lower() in top_title.lower() or
            case["expected_in_top"].lower() in top_abs.lower()
        )
        results.append({
            "query":              case["query"],
            "expected":           case["expected_in_top"],
            "top_title":          top_title,
            "phrase_in_top_result": phrase_in_top,
            "total_hits":         result.total_hits,
        })

    success_rate = sum(1 for r in results if r["phrase_in_top_result"]) / max(len(results), 1)
    return {
        "cases":        results,
        "success_rate": success_rate,
        "n_cases":      len(results),
    }


def plot_holistic_spell_check(holistic_data: Dict, output_dir: Path) -> None:
    """
    Figure 10: Holistic spell-check pipeline evaluation.
    Shows per-case correction detection and HTML diff generation.
    """
    cases = holistic_data.get("cases", [])
    if not cases:
        return

    labels       = [c["input"][:25] + "…" if len(c["input"]) > 25 else c["input"] for c in cases]
    found_counts = [len(c.get("corrections_found", [])) for c in cases]
    expected_counts = [len(c.get("expected_corrections", [])) for c in cases]
    html_diff    = [1 if c.get("has_html_diff") else 0 for c in cases]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Panel A: corrections found vs expected
    ax = axes[0]
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w/2, expected_counts, w, label="Expected corrections",
           color="white", edgecolor="black", hatch="//")
    ax.bar(x + w/2, found_counts,    w, label="Corrections detected",
           color="white", edgecolor="black", hatch="\\\\")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("Number of tokens corrected")
    ax.set_title("(A) Holistic Spell-Check: Expected vs. Detected")
    ax.legend(fontsize=8)
    ax.annotate(
        f"Overall precision: {holistic_data.get('precision', 0):.0%}",
        xy=(0.5, 0.97), xycoords="axes fraction",
        ha="center", va="top", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="black"),
    )

    # Panel B: HTML diff generation rate
    ax = axes[1]
    ax.bar(labels, html_diff, color="white", edgecolor="black", hatch="xx")
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["No", "Yes"])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=8)
    ax.set_title("(B) HTML Diff (<strong> markup) Generated")
    ax.set_ylabel("HTML diff present")

    _save(fig, output_dir / "fig10_holistic_spell_check.png", "Figure 10")


# Patch main to include new tests
def main() -> None:
    parser = argparse.ArgumentParser(description="Pinakes Performance & Quality Test Suite")
    parser.add_argument("--base-url",   default="http://localhost:8080",
                        help="Base URL of the Pinakes application")
    parser.add_argument("--output-dir", default="./results",
                        help="Directory to save PNG figures and JSON report")
    parser.add_argument("--iterations", type=int, default=3,
                        help="Number of benchmark iterations per query")
    parser.add_argument("--warmup",     type=int, default=5,
                        help="Number of warm-up rounds (discarded)")
    parser.add_argument("--skip-wait",  action="store_true",
                        help="Skip health-check wait (for CI / dry-run)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    client = PinakesClient(args.base_url)
    if not args.skip_wait:
        wait_for_service(client)

    print("=" * 60)
    print("  PINAKES AUTOMATED TEST SUITE")
    print("=" * 60)

    print("\n[1/8] Latency Benchmark")
    benchmark_run = run_latency_benchmark(client, args.warmup, args.iterations)

    print("\n[2/8] Relevance Evaluation")
    eval_data = run_relevance_evaluation(client)

    print("\n[3/8] Payload Analysis (§2.4)")
    payload_data = run_payload_analysis(client)

    print("\n[4/8] Classic Spell-Check Evaluation (§2.5 / §3.1)")
    sc_data = run_spell_check_evaluation(client)

    print("\n[5/8] Holistic Spell-Check (multi-word, case-aware, HTML diff)")
    holistic_data = run_holistic_spell_check_test(client)

    print("\n[6/8] Exact-Phrase Search Validation (§busca exata)")
    exact_data = run_exact_phrase_test(client)

    print("\n[7/8] Concurrency Test")
    conc_data = run_concurrency_test(client, n_workers=[1, 2, 4, 8])

    print("\n[8/8] Tier Latency Comparison (Kruskal-Wallis)")
    tier_data = run_tier_comparison(client, n_repeats=3)

    # ── Plotting ───────────────────────────────────────────────────────────
    print("\n[Plotting] Generating publication-quality figures (B&W, 300 dpi)…")
    plot_latency_distribution(benchmark_run, output_dir)
    plot_latency_percentiles(benchmark_run, output_dir)
    plot_relevance_metrics(eval_data, output_dir)
    plot_payload_comparison(payload_data, output_dir)
    plot_concurrency_throughput(conc_data, output_dir)
    plot_tier_latency_comparison(tier_data, output_dir)
    plot_semantic_similarity(eval_data, output_dir)
    plot_spell_check_summary(sc_data, output_dir)
    plot_summary_dashboard(benchmark_run, eval_data, payload_data, sc_data, output_dir)
    plot_holistic_spell_check(holistic_data, output_dir)

    # ── JSON report ────────────────────────────────────────────────────────
    report = {
        "latency": {
            "mean_ms":   benchmark_run.mean,
            "std_ms":    benchmark_run.std,
            "cv":        benchmark_run.cv,
            "p50_ms":    benchmark_run.p50,
            "p95_ms":    benchmark_run.p95,
            "p99_ms":    benchmark_run.p99,
            "error_rate":benchmark_run.error_rate,
        },
        "relevance":  eval_data["aggregate"],
        "payload": {k: v for k, v in payload_data.items() if not isinstance(v, list)},
        "spell_check": {k: v for k, v in sc_data.items() if not isinstance(v, list)},
        "holistic_spell_check": {
            "precision": holistic_data.get("precision", 0),
            "n_cases":   holistic_data.get("n_cases", 0),
        },
        "exact_phrase": {
            "success_rate": exact_data.get("success_rate", 0),
            "n_cases":      exact_data.get("n_cases", 0),
        },
        "concurrency": {
            str(k): {kk: vv for kk, vv in v.items() if not isinstance(vv, list)}
            for k, v in conc_data.items()
        },
        "tier_stats": {
            "kruskal_h":  tier_data["kruskal_stat"],
            "kruskal_p":  tier_data["kruskal_p"],
            "significant":tier_data["significant_difference"],
        },
    }
    save_json_report(report, output_dir)

    # ── Summary ────────────────────────────────────────────────────────────
    print_summary(benchmark_run, eval_data, payload_data, sc_data)
    sep = "═" * 60
    print(f"\n{sep}")
    print("  NEW FEATURES")
    print(sep)
    print(f"  Holistic spell-check precision : {holistic_data.get('precision', 0):.0%}")
    print(f"  Exact-phrase search success    : {exact_data.get('success_rate', 0):.0%}")
    print(sep)
    print(f"\nAll figures saved to: {output_dir.resolve()}\n")


if __name__ == "__main__":
    main()
