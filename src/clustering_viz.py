"""
Clustering & Visualization
===========================
Unsupervised clustering of the music catalog and 2-D visualisation of
the "music space" using PCA and t-SNE.

Features
--------
* KMeans and DBSCAN clustering with silhouette-score evaluation
* PCA / t-SNE dimensionality reduction
* Scatter-plot visualisation coloured by mood or cluster label
* Overlay of user vectors and recommendations in the 2-D space
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

try:
    from sklearn.manifold import TSNE
    _TSNE_AVAILABLE = True
except ImportError:
    _TSNE_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    _PLOTTING_AVAILABLE = True
except ImportError:
    _PLOTTING_AVAILABLE = False


# ── Colour Palette ───────────────────────────────────────────────────────────

MOOD_COLOURS: Dict[str, str] = {
    "Chill":       "#6EC6FF",
    "Energetic":   "#FF6B6B",
    "Romantic":    "#FFB4D4",
    "Melancholic": "#9B8EC2",
    "Focus":       "#7ED6A4",
}

CLUSTER_CMAP = plt.cm.get_cmap("Set2") if _PLOTTING_AVAILABLE else None


# ── Clustering ───────────────────────────────────────────────────────────────

def cluster_tracks_kmeans(
    X: np.ndarray,
    n_clusters: int = 5,
    random_state: int = 42,
) -> Tuple[np.ndarray, float, "KMeans"]:
    """KMeans clustering with silhouette evaluation.

    Returns
    -------
    labels : (N,) integer cluster assignments
    sil_score : silhouette score (-1 to 1, higher is better)
    model : fitted KMeans object
    """
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = model.fit_predict(X)
    sil = silhouette_score(X, labels, sample_size=min(10_000, len(X)))
    return labels, sil, model


def cluster_tracks_dbscan(
    X: np.ndarray,
    eps: float = 0.5,
    min_samples: int = 10,
) -> Tuple[np.ndarray, float, "DBSCAN"]:
    """DBSCAN clustering with silhouette evaluation.

    Returns labels (-1 = noise), silhouette score, model.
    """
    model = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean")
    labels = model.fit_predict(X)
    n_clusters = len(set(labels) - {-1})
    if n_clusters < 2:
        sil = -1.0
    else:
        mask = labels != -1
        sil = silhouette_score(X[mask], labels[mask], sample_size=min(10_000, mask.sum()))
    return labels, sil, model


def find_optimal_k(
    X: np.ndarray,
    k_range: Sequence[int] = range(3, 12),
    random_state: int = 42,
) -> Tuple[int, Dict[int, float]]:
    """Test multiple k values and return the best by silhouette score."""
    scores: Dict[int, float] = {}
    for k in k_range:
        _, sil, _ = cluster_tracks_kmeans(X, n_clusters=k, random_state=random_state)
        scores[k] = sil
    best_k = max(scores, key=scores.get)
    return best_k, scores


# ── Dimensionality Reduction ─────────────────────────────────────────────────

def reduce_pca(
    X: np.ndarray,
    n_components: int = 2,
) -> Tuple[np.ndarray, "PCA"]:
    """PCA reduction → (N, n_components), PCA model."""
    model = PCA(n_components=n_components, random_state=42)
    X_2d = model.fit_transform(X)
    return X_2d, model


def reduce_tsne(
    X: np.ndarray,
    n_components: int = 2,
    perplexity: float = 30.0,
    sample_size: Optional[int] = 15_000,
    random_state: int = 42,
) -> Tuple[np.ndarray, Optional[np.ndarray]]:
    """t-SNE reduction.

    If sample_size is set and X is larger, a random subset is used.
    Returns (X_2d, sample_indices_or_None).
    """
    if not _TSNE_AVAILABLE:
        raise ImportError("scikit-learn TSNE not available.")

    indices = None
    X_in = X
    if sample_size and len(X) > sample_size:
        rng = np.random.RandomState(random_state)
        indices = rng.choice(len(X), size=sample_size, replace=False)
        X_in = X[indices]

    tsne = TSNE(
        n_components=n_components,
        perplexity=perplexity,
        random_state=random_state,
        init="pca",
        learning_rate="auto",
    )
    X_2d = tsne.fit_transform(X_in)
    return X_2d, indices


# ── Visualisation ────────────────────────────────────────────────────────────

def plot_music_space(
    X_2d: np.ndarray,
    labels: np.ndarray,
    label_type: str = "mood",
    title: str = "Music Space",
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (14, 10),
    alpha: float = 0.35,
    point_size: float = 3.0,
) -> plt.Figure:
    """2-D scatter plot of the music space coloured by mood or cluster.

    Parameters
    ----------
    X_2d : (N, 2) array of 2-D coordinates
    labels : (N,) array of string mood labels or integer cluster IDs
    label_type : 'mood' or 'cluster'
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor="#0D1117")
    ax.set_facecolor("#0D1117")

    unique_labels = sorted(set(labels))

    for i, lab in enumerate(unique_labels):
        mask = labels == lab
        if label_type == "mood" and lab in MOOD_COLOURS:
            color = MOOD_COLOURS[lab]
        else:
            color = CLUSTER_CMAP(i / max(len(unique_labels) - 1, 1))

        ax.scatter(
            X_2d[mask, 0], X_2d[mask, 1],
            c=color, label=str(lab),
            s=point_size, alpha=alpha, edgecolors="none",
        )

    ax.legend(
        loc="upper right", fontsize=9, framealpha=0.7,
        facecolor="#161B22", edgecolor="#30363D", labelcolor="white",
        markerscale=4,
    )
    ax.set_title(title, fontsize=16, color="white", pad=15, fontweight="bold")
    ax.tick_params(colors="#8B949E", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#30363D")
    ax.set_xlabel("Dimension 1", color="#8B949E", fontsize=10)
    ax.set_ylabel("Dimension 2", color="#8B949E", fontsize=10)

    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
        print(f"Saved → {save_path}")

    return fig


def plot_user_in_space(
    X_2d: np.ndarray,
    labels: np.ndarray,
    user_point_2d: np.ndarray,
    rec_points_2d: Optional[np.ndarray] = None,
    title: str = "User in Music Space",
    save_path: Optional[str] = None,
    figsize: Tuple[int, int] = (14, 10),
) -> plt.Figure:
    """Overlay user vector and recommended tracks on the music space."""
    fig = plot_music_space(
        X_2d, labels, title=title, figsize=figsize, alpha=0.15,
    )
    ax = fig.axes[0]

    # User vector
    ax.scatter(
        user_point_2d[0], user_point_2d[1],
        c="#FFD700", s=200, marker="*", zorder=10,
        edgecolors="white", linewidths=1.2, label="You",
    )

    # Recommendations
    if rec_points_2d is not None and len(rec_points_2d) > 0:
        ax.scatter(
            rec_points_2d[:, 0], rec_points_2d[:, 1],
            c="#00FF88", s=60, marker="D", zorder=9,
            edgecolors="white", linewidths=0.8, alpha=0.9,
            label="Recommendations",
        )

    ax.legend(
        loc="upper right", fontsize=9, framealpha=0.7,
        facecolor="#161B22", edgecolor="#30363D", labelcolor="white",
        markerscale=1.5,
    )

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
        print(f"Saved → {save_path}")

    return fig


def plot_silhouette_scores(
    k_scores: Dict[int, float],
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Bar chart of silhouette scores for different k values."""
    fig, ax = plt.subplots(figsize=(8, 5), facecolor="#0D1117")
    ax.set_facecolor("#0D1117")

    ks = sorted(k_scores.keys())
    scores = [k_scores[k] for k in ks]
    best_k = max(k_scores, key=k_scores.get)

    colors = ["#00FF88" if k == best_k else "#6EC6FF" for k in ks]
    ax.bar(ks, scores, color=colors, edgecolor="#30363D")
    ax.set_xlabel("Number of Clusters (k)", color="#8B949E")
    ax.set_ylabel("Silhouette Score", color="#8B949E")
    ax.set_title("Optimal k Selection", color="white", fontweight="bold")
    ax.tick_params(colors="#8B949E")
    for spine in ax.spines.values():
        spine.set_color("#30363D")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="#0D1117")
    return fig
