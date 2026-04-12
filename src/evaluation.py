"""
Evaluation Module
=================
Comprehensive evaluation metrics that go far beyond Hit-Rate@K.

Metrics
-------
1. **Intra-List Diversity (ILD)** — are recommendations too similar to each other?
2. **Novelty** — are we recommending non-obvious (low-popularity) songs?
3. **Personalization** — how different are results across users?
4. **Coverage** — what fraction of the catalog is utilised?
5. **Hit-Rate@K** — baseline relevance (same-artist retrieval)
6. **NDCG@K** — ranking quality with graded relevance
"""

from __future__ import annotations

import sys
from collections import Counter
from itertools import combinations
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity as _cos_sim

from .content_model import ContentEngine
from .hybrid_recommender import HybridRecommender
from .user_model import UserModel, UserProfile


# ── Individual Metrics ───────────────────────────────────────────────────────

def intra_list_diversity(rec_vectors: np.ndarray) -> float:
    """Average pairwise cosine *distance* within a recommendation list.

    ILD = mean(1 - cos_sim(r_i, r_j))  for all pairs  i < j

    Range: [0, 2]  (in practice [0, ~1]).  Higher → more diverse.
    """
    n = len(rec_vectors)
    if n < 2:
        return 0.0
    sim_matrix = _cos_sim(rec_vectors)
    # Upper triangle (excluding diagonal)
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += 1.0 - sim_matrix[i, j]
            count += 1
    return total / count


def novelty(
    rec_df: pd.DataFrame,
    popularity_col: str = "popularity",
    max_popularity: float = 100.0,
) -> float:
    """Self-information novelty: mean(-log₂(pop_i / max_pop)).

    Tracks with low popularity → high novelty score.
    Returns 0.0 if popularity data is unavailable.
    """
    if popularity_col not in rec_df.columns:
        return 0.0
    pops = rec_df[popularity_col].fillna(0).values.astype(float)
    # Clamp to [1, max] to avoid log(0)
    pops = np.clip(pops, 1.0, max_popularity)
    probs = pops / max_popularity
    return float(np.mean(-np.log2(probs + 1e-12)))


def personalization(
    user_rec_lists: List[List[str]],
) -> float:
    """Average pairwise Jaccard *distance* across users' recommendation lists.

    Personalization = 1 - mean(|L_u ∩ L_v| / |L_u ∪ L_v|)

    Range: [0, 1].  Higher → more personalised (less overlap).
    """
    n = len(user_rec_lists)
    if n < 2:
        return 0.0

    sets = [set(lst) for lst in user_rec_lists]
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            inter = len(sets[i] & sets[j])
            union = len(sets[i] | sets[j])
            jaccard = inter / union if union > 0 else 0.0
            total += 1.0 - jaccard
            count += 1
    return total / count


def coverage(
    all_rec_ids: Sequence[str],
    catalog_size: int,
) -> float:
    """Fraction of unique catalog tracks that appear in *any* recommendation.

    Range: [0, 1].  Higher → more of the catalog is surfaced.
    """
    if catalog_size == 0:
        return 0.0
    return len(set(all_rec_ids)) / catalog_size


def hit_rate_at_k(
    engine: ContentEngine,
    k: int = 10,
    n_trials: int = 200,
    seed: int = 42,
) -> float:
    """Original Hit-Rate@K metric (kept for backward compatibility).

    For artists with ≥2 songs: use one song as seed, hide another,
    measure if the hidden song appears in the top-K.
    """
    rng = np.random.RandomState(seed)
    df = engine.df

    # Find artists with ≥2 tracks
    artist_counts = df["artist_name"].value_counts()
    eligible_artists = artist_counts[artist_counts >= 2].index.tolist()
    if not eligible_artists:
        return 0.0

    hits = 0
    trials = 0
    sampled_artists = rng.choice(
        eligible_artists, size=min(n_trials, len(eligible_artists)), replace=False
    )

    for artist in sampled_artists:
        artist_tracks = df[df["artist_name"] == artist]["track_id"].tolist()
        if len(artist_tracks) < 2:
            continue
        idx_pair = rng.choice(len(artist_tracks), size=2, replace=False)
        seed_id = artist_tracks[idx_pair[0]]
        target_id = artist_tracks[idx_pair[1]]

        try:
            recs = engine.recommend_by_id(seed_id, n=k)
            if target_id in recs["track_id"].values:
                hits += 1
        except KeyError:
            continue
        trials += 1

    return hits / trials if trials > 0 else 0.0


def ndcg_at_k(
    engine: ContentEngine,
    k: int = 10,
    n_trials: int = 200,
    seed: int = 42,
) -> float:
    """NDCG@K using same-artist tracks as graded relevance.

    Relevance grades:
      - Same artist, same track: not used (excluded as seed)
      - Same artist: relevance = 1
      - Different artist: relevance = 0
    """
    rng = np.random.RandomState(seed)
    df = engine.df

    artist_counts = df["artist_name"].value_counts()
    eligible_artists = artist_counts[artist_counts >= 3].index.tolist()
    if not eligible_artists:
        return 0.0

    ndcg_scores = []
    sampled = rng.choice(
        eligible_artists, size=min(n_trials, len(eligible_artists)), replace=False
    )

    for artist in sampled:
        artist_tracks = df[df["artist_name"] == artist]["track_id"].tolist()
        seed_id = rng.choice(artist_tracks)

        try:
            recs = engine.recommend_by_id(seed_id, n=k)
        except KeyError:
            continue

        # Build relevance vector
        rels = np.array([
            1.0 if aid == artist else 0.0
            for aid in recs["artist_name"].values
        ])

        # DCG
        discounts = np.log2(np.arange(2, len(rels) + 2))
        dcg = np.sum(rels / discounts)

        # Ideal DCG
        ideal_rels = np.sort(rels)[::-1]
        idcg = np.sum(ideal_rels / discounts)

        if idcg > 0:
            ndcg_scores.append(dcg / idcg)

    return float(np.mean(ndcg_scores)) if ndcg_scores else 0.0


# ── Aggregate Evaluator ──────────────────────────────────────────────────────

class Evaluator:
    """Run all evaluation metrics and produce a summary report.

    Parameters
    ----------
    engine : ContentEngine
        Fitted content engine.
    """

    def __init__(self, engine: ContentEngine) -> None:
        self.engine = engine

    def evaluate_single_list(
        self,
        rec_df: pd.DataFrame,
    ) -> Dict[str, float]:
        """Evaluate a single recommendation list (ILD + novelty)."""
        # Get vectors for recommended tracks
        valid_ids = [
            tid for tid in rec_df["track_id"]
            if tid in self.engine._id_to_idx
        ]
        results: Dict[str, float] = {}

        if valid_ids:
            rec_vecs = self.engine.get_vectors_for_ids(valid_ids)
            results["intra_list_diversity"] = round(intra_list_diversity(rec_vecs), 4)
        else:
            results["intra_list_diversity"] = 0.0

        results["novelty"] = round(novelty(rec_df), 4)
        return results

    def full_evaluation(
        self,
        recommender: HybridRecommender,
        users: List[UserProfile],
        k: int = 10,
        context: Optional[str] = None,
        verbose: bool = True,
    ) -> Dict[str, float]:
        """Run all metrics across a set of users.

        Returns a dict of metric_name → value.
        """
        all_rec_ids: List[str] = []
        user_rec_lists: List[List[str]] = []
        ild_scores: List[float] = []
        novelty_scores: List[float] = []

        if verbose:
            print(f"Evaluating {len(users)} users with k={k}...")

        for i, user in enumerate(users):
            try:
                recs = recommender.recommend(
                    user_profile=user, context=context, n=k,
                )
            except Exception as e:
                if verbose:
                    print(f"  ⚠ Skipping user {user.user_id}: {e}", file=sys.stderr)
                continue

            rec_ids = recs["track_id"].tolist()
            all_rec_ids.extend(rec_ids)
            user_rec_lists.append(rec_ids)

            # Per-list metrics
            single = self.evaluate_single_list(recs)
            ild_scores.append(single["intra_list_diversity"])
            novelty_scores.append(single["novelty"])

            if verbose and (i + 1) % 10 == 0:
                print(f"  Evaluated {i + 1}/{len(users)} users")

        results: Dict[str, float] = {}

        # Means
        results["intra_list_diversity"] = round(float(np.mean(ild_scores)), 4) if ild_scores else 0.0
        results["novelty"] = round(float(np.mean(novelty_scores)), 4) if novelty_scores else 0.0
        results["personalization"] = round(personalization(user_rec_lists), 4)
        results["coverage"] = round(coverage(all_rec_ids, self.engine.catalog_size), 4)

        # Classic metrics
        if verbose:
            print("Computing Hit-Rate@K and NDCG@K...")
        results["hit_rate_at_k"] = round(hit_rate_at_k(self.engine, k=k), 4)
        results["ndcg_at_k"] = round(ndcg_at_k(self.engine, k=k), 4)

        return results

    def print_evaluation_report(self, results: Dict[str, float]) -> None:
        """Pretty-print an evaluation report to stdout."""
        print("\n" + "=" * 60)
        print("  📊 EVALUATION REPORT")
        print("=" * 60)

        labels = {
            "intra_list_diversity": "Intra-List Diversity (ILD) ↑",
            "novelty":             "Novelty ↑",
            "personalization":     "Personalization ↑",
            "coverage":            "Catalog Coverage ↑",
            "hit_rate_at_k":       "Hit-Rate@K ↑",
            "ndcg_at_k":           "NDCG@K ↑",
        }

        for key, label in labels.items():
            val = results.get(key, "N/A")
            if isinstance(val, float):
                print(f"  {label:40s} {val:.4f}")
            else:
                print(f"  {label:40s} {val}")

        print("=" * 60 + "\n")
