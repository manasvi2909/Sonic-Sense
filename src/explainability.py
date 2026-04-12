"""
Explainability Module
=====================
Generates natural-language explanations for each recommendation,
answering **"why was this song recommended?"**

Two levels of explainability:
  1. **Score-level** — which signals (content / user / mood) drove the score.
  2. **Feature-level** — which audio features are most similar between
     the seed and the recommendation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np


# ── Feature-Level Contribution ───────────────────────────────────────────────

def feature_contribution_breakdown(
    seed_vec: np.ndarray,
    rec_vec: np.ndarray,
    feature_names: Sequence[str],
) -> Dict[str, float]:
    """Per-feature contribution to cosine similarity.

    Returns a dict {feature_name: contribution} where contributions
    sum (approximately) to the total cosine similarity.
    """
    dot = seed_vec * rec_vec
    norm_s = np.linalg.norm(seed_vec) + 1e-12
    norm_r = np.linalg.norm(rec_vec) + 1e-12
    contributions = dot / (norm_s * norm_r)
    return {f: float(contributions[i]) for i, f in enumerate(feature_names)}


def _top_contributing_features(
    seed_vec: np.ndarray,
    rec_vec: np.ndarray,
    feature_names: Sequence[str],
    top_k: int = 3,
) -> List[str]:
    """Return the top-K feature names driving similarity."""
    contribs = feature_contribution_breakdown(seed_vec, rec_vec, feature_names)
    ranked = sorted(contribs, key=contribs.get, reverse=True)
    return ranked[:top_k]


# ── Score-Level Explanation ──────────────────────────────────────────────────

def explain_recommendation_row(
    content_score: float,
    user_score: float,
    mood_score: float,
    mood_label: str,
    track_vector: np.ndarray,
    seed_vector: np.ndarray,
    feature_names: Sequence[str],
    context: Optional[str] = None,
    top_k_features: int = 3,
) -> str:
    """One-line natural-language explanation for a single recommendation.

    Example output:
        "Similar energy & tempo · 'Energetic' mood match · fits 'gym' context"
    """
    parts: List[str] = []

    # Top contributing features
    top_feats = _top_contributing_features(
        seed_vector, track_vector, feature_names, top_k=top_k_features
    )
    feat_str = " & ".join(top_feats)
    parts.append(f"similar {feat_str}")

    # Mood cluster
    parts.append(f"'{mood_label}' mood")

    # Context match
    if context and mood_score > 0.3:
        parts.append(f"fits '{context}' context")

    # Signal strengths
    signals = []
    if content_score >= 0.7:
        signals.append("strong content match")
    if user_score >= 0.6:
        signals.append("matches your taste")
    if signals:
        parts.append(" · ".join(signals))

    return " · ".join(parts)


# ── Batch Explanation ────────────────────────────────────────────────────────

def explain_batch(
    seed_vector: np.ndarray,
    rec_vectors: np.ndarray,
    rec_df: "pd.DataFrame",
    feature_names: Sequence[str],
    mood_labels: Sequence[str],
    content_scores: np.ndarray,
    user_scores: np.ndarray,
    mood_scores: np.ndarray,
    context: Optional[str] = None,
) -> List[str]:
    """Generate explanations for an entire recommendation list."""
    explanations = []
    for i in range(len(rec_df)):
        explanations.append(
            explain_recommendation_row(
                content_score=float(content_scores[i]),
                user_score=float(user_scores[i]),
                mood_score=float(mood_scores[i]),
                mood_label=mood_labels[i],
                track_vector=rec_vectors[i],
                seed_vector=seed_vector,
                feature_names=feature_names,
                context=context,
            )
        )
    return explanations


# ── Detailed Explanation ─────────────────────────────────────────────────────

def explain_recommendation_detailed(
    seed_track_id: str,
    rec_track_id: str,
    engine: "ContentEngine",
    mood_engine: "MoodEngine",
) -> Dict:
    """Rich, structured explanation comparing two tracks.

    Returns a dict with:
      - feature_deltas: per-feature absolute differences (raw space)
      - top_features: top contributing features
      - seed_mood / rec_mood: mood labels
      - mood_match: bool
      - feature_comparison: side-by-side raw feature values
    """
    from .content_model import AUDIO_FEATURES

    seed_raw = engine.get_raw_features(seed_track_id)
    rec_raw = engine.get_raw_features(rec_track_id)
    seed_vec = engine.get_track_vector(seed_track_id)
    rec_vec = engine.get_track_vector(rec_track_id)

    deltas = {f: abs(seed_raw[f] - rec_raw[f]) for f in AUDIO_FEATURES}
    contribs = feature_contribution_breakdown(seed_vec, rec_vec, AUDIO_FEATURES)
    top_feats = sorted(contribs, key=contribs.get, reverse=True)[:3]

    seed_mood = mood_engine.assign_mood(seed_vec)
    rec_mood = mood_engine.assign_mood(rec_vec)

    comparison = {}
    for f in AUDIO_FEATURES:
        comparison[f] = {
            "seed": round(seed_raw[f], 4),
            "recommended": round(rec_raw[f], 4),
            "delta": round(deltas[f], 4),
            "contribution": round(contribs[f], 4),
        }

    return {
        "seed_track_id": seed_track_id,
        "rec_track_id": rec_track_id,
        "top_features": top_feats,
        "seed_mood": seed_mood,
        "rec_mood": rec_mood,
        "mood_match": seed_mood == rec_mood,
        "feature_comparison": comparison,
    }
