"""
Hybrid Recommendation Engine
=============================
Combines three orthogonal signals into a single score per candidate track:

    Score = α × ContentSimilarity
          + β × UserPreferenceSimilarity
          + γ × MoodAlignment

All sub-scores are min-max normalised to [0, 1] before combination.

Supports four operating modes:
  1. **Full hybrid** — seed track(s) + user profile + context
  2. **Mood-only**   — pure context/mood discovery
  3. **User-only**   — personalised without an explicit seed
  4. **Content-only** — falls back to basic content engine
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity as _cos_sim

from .content_model import AUDIO_FEATURES, ContentEngine
from .mood_engine import MoodEngine
from .user_model import UserModel, UserProfile
from .explainability import explain_recommendation_row


# ── Score Normalisation ──────────────────────────────────────────────────────

def _minmax(arr: np.ndarray) -> np.ndarray:
    """Min-max normalise to [0, 1] (safe for constant arrays)."""
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-12:
        return np.ones_like(arr) * 0.5
    return (arr - lo) / (hi - lo)


# ── Hybrid Recommender ───────────────────────────────────────────────────────

class HybridRecommender:
    """Multi-signal music recommendation engine.

    Parameters
    ----------
    engine : ContentEngine
        Fitted content engine with scaled feature matrix.
    mood_engine : MoodEngine
        Mood engine initialised with the same scaler.
    user_model : UserModel
        User modelling utility.
    alpha, beta, gamma : float
        Default mixing weights (content, user, mood).
    candidate_pool : int
        How many raw candidates to retrieve from NN before rescoring.
    """

    def __init__(
        self,
        engine: ContentEngine,
        mood_engine: MoodEngine,
        user_model: UserModel,
        alpha: float = 0.45,
        beta: float = 0.30,
        gamma: float = 0.25,
        candidate_pool: int = 500,
    ) -> None:
        self.engine = engine
        self.mood = mood_engine
        self.user_model = user_model
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.candidate_pool = candidate_pool

    # ── Full Hybrid Recommend ────────────────────────────────────────────

    def recommend(
        self,
        seed_ids: Optional[Sequence[str]] = None,
        user_profile: Optional[UserProfile] = None,
        context: Optional[str] = None,
        n: int = 10,
        alpha: Optional[float] = None,
        beta: Optional[float] = None,
        gamma: Optional[float] = None,
    ) -> pd.DataFrame:
        """Generate recommendations with hybrid scoring.

        Parameters
        ----------
        seed_ids : list of str, optional
            Seed track IDs for content similarity anchor.
        user_profile : UserProfile, optional
            User behavioural profile.
        context : str, optional
            Natural-language context keyword (e.g. "gym", "study").
        n : int
            Number of recommendations to return.
        alpha, beta, gamma : float, optional
            Override default weights for this call.
        """
        a = alpha if alpha is not None else self.alpha
        b = beta if beta is not None else self.beta
        g = gamma if gamma is not None else self.gamma

        # Build query vector (content anchor)
        exclude_ids = set(seed_ids or [])
        if user_profile:
            exclude_ids |= set(user_profile.all_track_ids)

        if seed_ids:
            vecs = self.engine.get_vectors_for_ids(seed_ids)
            query_vec = np.mean(vecs, axis=0)
        elif user_profile:
            query_vec = self.user_model.build_user_vector(user_profile, self.engine)
        elif context:
            query_vec = self.mood.context_to_mood_vector(context)
        else:
            # Random exploration
            query_vec = np.mean(self.engine.X, axis=0)

        # Get candidate pool
        cand_df, cand_X = self.engine.candidates_by_vector(
            query_vec, n=self.candidate_pool, exclude_ids=list(exclude_ids),
        )

        if cand_df.empty:
            return cand_df

        # ── Sub-scores ────────────────────────────────────────────────
        # Content similarity (already computed by NN)
        content_scores = cand_df["content_similarity"].values.copy()

        # User preference similarity
        if user_profile:
            user_vec = self.user_model.build_user_vector(user_profile, self.engine)
            user_scores = _cos_sim(cand_X, user_vec.reshape(1, -1)).ravel()
        else:
            user_scores = np.zeros(len(cand_df))
            b = 0.0  # disable user signal

        # Mood alignment
        if context:
            mood_vec = self.mood.context_to_mood_vector(context)
            mood_scores = self.mood.mood_similarity_batch(cand_X, mood_vec)
        else:
            mood_scores = np.zeros(len(cand_df))
            g = 0.0  # disable mood signal

        # Re-normalise weights so they sum to 1
        w_sum = a + b + g
        if w_sum < 1e-12:
            a, b, g = 1.0, 0.0, 0.0
            w_sum = 1.0
        a, b, g = a / w_sum, b / w_sum, g / w_sum

        # Normalise sub-scores
        c_norm = _minmax(content_scores)
        u_norm = _minmax(user_scores) if b > 0 else np.zeros(len(cand_df))
        m_norm = _minmax(mood_scores) if g > 0 else np.zeros(len(cand_df))

        # Hybrid score
        hybrid = a * c_norm + b * u_norm + g * m_norm

        # ── Build output ──────────────────────────────────────────────
        cand_df = cand_df.copy()
        cand_df["content_score"] = np.round(c_norm, 4)
        cand_df["user_score"] = np.round(u_norm, 4)
        cand_df["mood_score"] = np.round(m_norm, 4)
        cand_df["hybrid_score"] = np.round(hybrid, 4)
        cand_df["mood_label"] = self.mood.batch_assign_moods(cand_X)

        # Generate explanations
        explanations = []
        for i in range(len(cand_df)):
            explanations.append(
                explain_recommendation_row(
                    content_score=c_norm[i],
                    user_score=u_norm[i],
                    mood_score=m_norm[i],
                    mood_label=cand_df.iloc[i]["mood_label"],
                    track_vector=cand_X[i],
                    seed_vector=query_vec,
                    feature_names=AUDIO_FEATURES,
                    context=context,
                )
            )
        cand_df["explanation"] = explanations

        # Sort and rank
        cand_df = cand_df.sort_values("hybrid_score", ascending=False).head(n)
        cand_df = cand_df.reset_index(drop=True)
        cand_df.insert(0, "rank", range(1, len(cand_df) + 1))

        # Select output columns
        out_cols = [
            "rank", "track_name", "artist_name", "track_id",
            "hybrid_score", "content_score", "user_score", "mood_score",
            "mood_label", "explanation",
        ]
        if "popularity" in cand_df.columns:
            out_cols.insert(4, "popularity")
        return cand_df[[c for c in out_cols if c in cand_df.columns]]

    # ── Convenience Modes ────────────────────────────────────────────────

    def recommend_by_mood(
        self, context: str, n: int = 10
    ) -> pd.DataFrame:
        """Pure mood-based discovery (no seed, no user)."""
        return self.recommend(context=context, n=n, alpha=0.0, beta=0.0, gamma=1.0)

    def recommend_for_user(
        self, user_profile: UserProfile, n: int = 10, context: Optional[str] = None,
    ) -> pd.DataFrame:
        """User-profile-driven recs (no explicit seed)."""
        return self.recommend(
            user_profile=user_profile, context=context, n=n,
            alpha=0.0, beta=0.6, gamma=0.4 if context else 0.0,
        )

    def recommend_content_only(
        self, seed_ids: Sequence[str], n: int = 10
    ) -> pd.DataFrame:
        """Pure content-based (backward-compatible mode)."""
        return self.recommend(seed_ids=seed_ids, n=n, alpha=1.0, beta=0.0, gamma=0.0)

    # ── Repr ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"<HybridRecommender(α={self.alpha}, β={self.beta}, γ={self.gamma}, "
            f"pool={self.candidate_pool}, catalog={self.engine.catalog_size:,})>"
        )
