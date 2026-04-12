"""
Mood & Context Engine
=====================
Maps Spotify audio features → inferred mood clusters, and resolves
natural-language context queries (e.g. "gym", "study", "breakup") into
mood vectors for context-aware recommendation.

Mood Taxonomy (5 canonical moods)
---------------------------------
* **Chill**       — low energy, moderate valence, high acousticness
* **Energetic**   — high energy/tempo/danceability, low acousticness
* **Romantic**    — mid energy, warm valence, moderate acousticness
* **Melancholic** — low valence, mid energy, mid-high acousticness
* **Focus**       — low energy, neutral valence, moderate tempo
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity as _cos_sim
from sklearn.preprocessing import StandardScaler

from .content_model import AUDIO_FEATURES

# ── Mood Definitions ─────────────────────────────────────────────────────────
# Each mood is defined as a *raw-feature* prototype vector (before scaling).
# Order matches AUDIO_FEATURES:
#   danceability, energy, acousticness, instrumentalness,
#   liveness, speechiness, valence, tempo, loudness

MOOD_PROTOTYPES_RAW: Dict[str, Dict[str, float]] = {
    "Chill": {
        "danceability": 0.45, "energy": 0.25, "acousticness": 0.75,
        "instrumentalness": 0.30, "liveness": 0.10, "speechiness": 0.04,
        "valence": 0.40, "tempo": 95.0, "loudness": -12.0,
    },
    "Energetic": {
        "danceability": 0.78, "energy": 0.88, "acousticness": 0.05,
        "instrumentalness": 0.02, "liveness": 0.20, "speechiness": 0.08,
        "valence": 0.72, "tempo": 135.0, "loudness": -4.5,
    },
    "Romantic": {
        "danceability": 0.55, "energy": 0.40, "acousticness": 0.55,
        "instrumentalness": 0.05, "liveness": 0.10, "speechiness": 0.04,
        "valence": 0.55, "tempo": 105.0, "loudness": -8.0,
    },
    "Melancholic": {
        "danceability": 0.35, "energy": 0.30, "acousticness": 0.65,
        "instrumentalness": 0.15, "liveness": 0.10, "speechiness": 0.04,
        "valence": 0.18, "tempo": 88.0, "loudness": -11.0,
    },
    "Focus": {
        "danceability": 0.40, "energy": 0.35, "acousticness": 0.50,
        "instrumentalness": 0.60, "liveness": 0.08, "speechiness": 0.03,
        "valence": 0.35, "tempo": 110.0, "loudness": -10.0,
    },
}

MOOD_NAMES: List[str] = list(MOOD_PROTOTYPES_RAW.keys())

# ── Context → Mood Mapping ───────────────────────────────────────────────────
# Natural-language keywords → mood label.  Multiple keywords may map to the
# same mood; compound contexts (e.g. "late night study") are resolved by
# majority vote.

CONTEXT_MAP: Dict[str, str] = {
    # Focus
    "study": "Focus", "work": "Focus", "coding": "Focus",
    "reading": "Focus", "concentrate": "Focus", "homework": "Focus",
    "writing": "Focus", "exam": "Focus", "focus": "Focus",
    "morning": "Focus", "productivity": "Focus",
    # Energetic
    "gym": "Energetic", "workout": "Energetic", "running": "Energetic",
    "exercise": "Energetic", "party": "Energetic", "club": "Energetic",
    "hype": "Energetic", "drive": "Energetic", "road trip": "Energetic",
    "dancing": "Energetic", "pregame": "Energetic", "pump up": "Energetic",
    # Chill
    "chill": "Chill", "relax": "Chill", "sleep": "Chill",
    "calm": "Chill", "unwind": "Chill", "meditation": "Chill",
    "spa": "Chill", "yoga": "Chill", "ambient": "Chill",
    "late night": "Chill", "lazy": "Chill", "lofi": "Chill",
    # Melancholic
    "sad": "Melancholic", "breakup": "Melancholic", "rain": "Melancholic",
    "cry": "Melancholic", "lonely": "Melancholic", "nostalgia": "Melancholic",
    "heartbreak": "Melancholic", "missing": "Melancholic", "grief": "Melancholic",
    "melancholy": "Melancholic", "blue": "Melancholic",
    # Romantic
    "love": "Romantic", "date": "Romantic", "dinner": "Romantic",
    "romance": "Romantic", "couple": "Romantic", "wedding": "Romantic",
    "valentine": "Romantic", "slow dance": "Romantic", "candle": "Romantic",
    "intimate": "Romantic",
}

# Alias handling for multi-word context
_CONTEXT_ALIASES: Dict[str, str] = {
    "late night": "Chill",
    "road trip": "Energetic",
    "pump up": "Energetic",
    "slow dance": "Romantic",
}


# ── Mood Engine ──────────────────────────────────────────────────────────────

class MoodEngine:
    """Maps tracks → moods and context keywords → mood vectors.

    Parameters
    ----------
    scaler : StandardScaler
        The *fitted* scaler from ContentEngine, so that mood prototypes
        live in the same scaled space as all track vectors.
    """

    def __init__(self, scaler: StandardScaler) -> None:
        self.scaler = scaler
        self._mood_centroids: Dict[str, np.ndarray] = {}
        self._build_mood_centroids()

    # ── Initialization ───────────────────────────────────────────────────

    def _build_mood_centroids(self) -> None:
        """Convert raw mood prototypes → scaled vectors."""
        for mood, feat_dict in MOOD_PROTOTYPES_RAW.items():
            raw_vec = np.array([feat_dict[f] for f in AUDIO_FEATURES]).reshape(1, -1)
            scaled = self.scaler.transform(raw_vec)[0]
            self._mood_centroids[mood] = scaled

    @property
    def mood_centroids(self) -> Dict[str, np.ndarray]:
        return dict(self._mood_centroids)

    # ── Single-Track Mood Assignment ─────────────────────────────────────

    def assign_mood(self, track_vector: np.ndarray) -> str:
        """Assign the closest mood label to a scaled track vector."""
        best_mood, best_sim = "", -1.0
        tv = track_vector.reshape(1, -1)
        for mood, centroid in self._mood_centroids.items():
            sim = float(_cos_sim(tv, centroid.reshape(1, -1))[0, 0])
            if sim > best_sim:
                best_mood, best_sim = mood, sim
        return best_mood

    def assign_mood_with_scores(
        self, track_vector: np.ndarray
    ) -> Tuple[str, Dict[str, float]]:
        """Return (best_mood, {mood: similarity_score})."""
        tv = track_vector.reshape(1, -1)
        scores = {}
        for mood, centroid in self._mood_centroids.items():
            scores[mood] = float(_cos_sim(tv, centroid.reshape(1, -1))[0, 0])
        best = max(scores, key=scores.get)
        return best, scores

    # ── Batch Mood Assignment ────────────────────────────────────────────

    def batch_assign_moods(self, X: np.ndarray) -> np.ndarray:
        """Assign mood labels to every row in a scaled feature matrix.

        Returns an array of mood strings with shape (N,).
        """
        centroid_matrix = np.vstack(
            [self._mood_centroids[m] for m in MOOD_NAMES]
        )  # (5, d)
        sim_matrix = _cos_sim(X, centroid_matrix)  # (N, 5)
        best_idxs = np.argmax(sim_matrix, axis=1)
        return np.array([MOOD_NAMES[i] for i in best_idxs])

    def batch_assign_moods_df(self, df: pd.DataFrame, X: np.ndarray) -> pd.DataFrame:
        """Add a 'mood' column to a DataFrame."""
        df = df.copy()
        df["mood"] = self.batch_assign_moods(X)
        return df

    # ── Context → Mood Resolution ────────────────────────────────────────

    def context_to_mood(self, context_str: str) -> str:
        """Resolve a natural-language context string to a mood label.

        Strategy: tokenize → look up each token in CONTEXT_MAP →
        majority vote.  Falls back to "Chill" if nothing matches.
        """
        context = context_str.strip().lower()

        # Try exact multi-word match first
        if context in _CONTEXT_ALIASES:
            return _CONTEXT_ALIASES[context]
        if context in CONTEXT_MAP:
            return CONTEXT_MAP[context]

        # Token-level majority vote
        tokens = context.split()
        votes: Dict[str, int] = {}
        for tok in tokens:
            if tok in CONTEXT_MAP:
                mood = CONTEXT_MAP[tok]
                votes[mood] = votes.get(mood, 0) + 1

        # Also try bi-grams
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i+1]}"
            if bigram in _CONTEXT_ALIASES:
                mood = _CONTEXT_ALIASES[bigram]
                votes[mood] = votes.get(mood, 0) + 2  # bigrams get extra weight

        if votes:
            return max(votes, key=votes.get)
        return "Chill"  # safe default

    def context_to_mood_vector(self, context_str: str) -> np.ndarray:
        """Return the scaled mood centroid for a context keyword."""
        mood = self.context_to_mood(context_str)
        return self._mood_centroids[mood]

    # ── Similarity ───────────────────────────────────────────────────────

    def mood_similarity(
        self, track_vector: np.ndarray, mood_vector: np.ndarray
    ) -> float:
        """Cosine similarity between a track and a mood centroid (both scaled)."""
        return float(
            _cos_sim(
                track_vector.reshape(1, -1),
                mood_vector.reshape(1, -1),
            )[0, 0]
        )

    def mood_similarity_batch(
        self, X: np.ndarray, mood_vector: np.ndarray
    ) -> np.ndarray:
        """Cosine similarities of many tracks against a single mood vector."""
        return _cos_sim(X, mood_vector.reshape(1, -1)).ravel()

    # ── Mood Distribution of a Set of Tracks ─────────────────────────────

    def mood_distribution(self, X: np.ndarray) -> Dict[str, float]:
        """Return the fraction of tracks in each mood cluster."""
        moods = self.batch_assign_moods(X)
        total = len(moods)
        return {m: float(np.sum(moods == m)) / total for m in MOOD_NAMES}

    # ── Repr ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<MoodEngine(moods={MOOD_NAMES})>"
