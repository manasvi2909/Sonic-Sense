"""
User Model
==========
Behavioral user-profile modeling for personalized recommendations.

A user is represented as a *weighted centroid* of their interaction history
in the same scaled feature space used by ContentEngine.  Weights account for:
  • Recency   — exponential decay so recent plays dominate
  • Frequency — repeated listens amplify
  • Likes     — explicit favorites get a boost

Because we lack real Spotify user data (no API credentials yet), this module
also provides **synthetic user generation** that samples coherent profiles
from different mood clusters for evaluation purposes.
"""

from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from .content_model import AUDIO_FEATURES, ContentEngine
from .mood_engine import MoodEngine, MOOD_NAMES


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass
class UserProfile:
    """Lightweight representation of a user's listening behaviour."""

    user_id: str
    liked_track_ids: List[str] = field(default_factory=list)
    recent_track_ids: List[str] = field(default_factory=list)   # ordered oldest → newest
    play_counts: Dict[str, int] = field(default_factory=dict)   # track_id → count
    timestamps: Optional[List[datetime]] = None                  # parallel to recent_track_ids
    preferred_mood: Optional[str] = None                         # override / ground-truth

    @property
    def all_track_ids(self) -> List[str]:
        """Deduplicated union of liked + recent tracks (preserving order)."""
        seen = set()
        out = []
        for tid in self.liked_track_ids + self.recent_track_ids:
            if tid not in seen:
                seen.add(tid)
                out.append(tid)
        return out


# ── Time-of-Day Buckets ─────────────────────────────────────────────────────

_TIME_BUCKETS = {
    "morning":    (6, 11),    # 06:00–11:59
    "afternoon":  (12, 16),   # 12:00–16:59
    "evening":    (17, 21),   # 17:00–21:59
    "late_night": (22, 5),    # 22:00–05:59  (wraps around midnight)
}

# Default mood hint per time bucket
_TIME_TO_MOOD_HINT: Dict[str, str] = {
    "morning":    "Focus",
    "afternoon":  "Energetic",
    "evening":    "Romantic",
    "late_night": "Chill",
}


def _hour_to_bucket(hour: int) -> str:
    for bucket, (lo, hi) in _TIME_BUCKETS.items():
        if lo <= hi:
            if lo <= hour <= hi:
                return bucket
        else:  # wraps midnight
            if hour >= lo or hour <= hi:
                return bucket
    return "evening"  # fallback


# ── User Model ───────────────────────────────────────────────────────────────

class UserModel:
    """Builds user vectors from profiles and content/mood engines.

    Parameters
    ----------
    recency_halflife : int
        Number of tracks (from most recent) for exponential weight to halve.
    like_boost : float
        Multiplicative boost for explicitly liked tracks.
    """

    def __init__(
        self,
        recency_halflife: int = 10,
        like_boost: float = 2.0,
    ) -> None:
        self.recency_halflife = recency_halflife
        self.like_boost = like_boost

    # ── User Vector Construction ─────────────────────────────────────────

    def build_user_vector(
        self,
        profile: UserProfile,
        engine: ContentEngine,
    ) -> np.ndarray:
        """Weighted centroid of a user's track history in scaled feature space.

        Weight for track *i* (0 = oldest, N-1 = newest):
            w_i = recency_weight × frequency_weight × like_weight
        """
        all_ids = profile.all_track_ids
        if not all_ids:
            # Cold-start: return the catalog centroid
            return np.mean(engine.X, axis=0)

        # Resolve track vectors (skip unknown IDs gracefully)
        valid_ids = [tid for tid in all_ids if tid in engine._id_to_idx]
        if not valid_ids:
            return np.mean(engine.X, axis=0)

        vectors = engine.get_vectors_for_ids(valid_ids)
        n = len(valid_ids)

        # Recency weights (exponential decay — newest = index n-1)
        decay = math.log(2) / max(self.recency_halflife, 1)
        recency_w = np.array([math.exp(decay * (i - (n - 1))) for i in range(n)])

        # Frequency weights
        freq_w = np.array([
            profile.play_counts.get(tid, 1) for tid in valid_ids
        ], dtype=float)

        # Like boost
        like_set = set(profile.liked_track_ids)
        like_w = np.array([
            self.like_boost if tid in like_set else 1.0 for tid in valid_ids
        ])

        weights = recency_w * freq_w * like_w
        weights /= weights.sum()  # normalize

        user_vec = np.average(vectors, axis=0, weights=weights)
        return user_vec

    # ── Temporal Context ─────────────────────────────────────────────────

    def infer_time_context(
        self, timestamps: Sequence[datetime]
    ) -> Tuple[str, str]:
        """Return (dominant_bucket, mood_hint) from listening timestamps."""
        if not timestamps:
            return "evening", "Romantic"
        buckets = [_hour_to_bucket(ts.hour) for ts in timestamps]
        counter = Counter(buckets)
        dominant = counter.most_common(1)[0][0]
        return dominant, _TIME_TO_MOOD_HINT[dominant]

    # ── Preferred Mood ───────────────────────────────────────────────────

    def get_preferred_mood(
        self,
        profile: UserProfile,
        engine: ContentEngine,
        mood_engine: MoodEngine,
    ) -> str:
        """Majority-vote mood across a user's track history."""
        if profile.preferred_mood:
            return profile.preferred_mood
        valid_ids = [tid for tid in profile.all_track_ids if tid in engine._id_to_idx]
        if not valid_ids:
            return "Chill"
        vectors = engine.get_vectors_for_ids(valid_ids)
        moods = mood_engine.batch_assign_moods(vectors)
        counter = Counter(moods)
        return counter.most_common(1)[0][0]

    # ── User Similarity ──────────────────────────────────────────────────

    @staticmethod
    def user_similarity(
        user_vec: np.ndarray, track_vec: np.ndarray
    ) -> float:
        """Cosine similarity between user vector and a track vector."""
        from sklearn.metrics.pairwise import cosine_similarity as _cs
        return float(_cs(user_vec.reshape(1, -1), track_vec.reshape(1, -1))[0, 0])

    @staticmethod
    def user_similarity_batch(
        user_vec: np.ndarray, X: np.ndarray
    ) -> np.ndarray:
        """Cosine similarities of user vector vs. many tracks."""
        from sklearn.metrics.pairwise import cosine_similarity as _cs
        return _cs(user_vec.reshape(1, -1), X).ravel()


# ── Synthetic User Generation ────────────────────────────────────────────────

def generate_synthetic_users(
    engine: ContentEngine,
    mood_engine: MoodEngine,
    n_users: int = 50,
    tracks_per_user: int = 30,
    seed: int = 42,
) -> List[UserProfile]:
    """Create diverse synthetic users by sampling tracks from mood clusters.

    Each user is assigned a *dominant mood* and draws ~60 % of their tracks
    from that mood, with the remainder scattered across other moods.
    This produces users with distinct preference profiles suitable for
    evaluating personalization and diversity metrics.
    """
    rng = random.Random(seed)
    np_rng = np.random.RandomState(seed)

    # Assign moods to all catalog tracks
    all_moods = mood_engine.batch_assign_moods(engine.X)
    mood_to_ids: Dict[str, List[str]] = {m: [] for m in MOOD_NAMES}
    for mood_label, tid in zip(all_moods, engine.df["track_id"]):
        mood_to_ids[mood_label].append(tid)

    PERSONA_NAMES = [
        "Neural Architect", "Ambient Analyst", "Vaporwave Visionary", "Acoustic Voyager",
        "Rhythm Specialist", "Sentiment Engineer", "BPM Balancer", "Spectral Explorer",
        "Frequency Curator", "Lofi Logician", "Sonic Strategist", "Melody Miner",
        "Vector Virtuoso", "Latent Listener", "Dissonance Director", "Harmony Handler",
        "Pulse Programmer", "Echo Enthusiast", "Timbre Technician", "Synth Scientist"
    ]

    users: List[UserProfile] = []
    for i in range(n_users):
        dominant_mood = MOOD_NAMES[i % len(MOOD_NAMES)]
        persona = PERSONA_NAMES[i % len(PERSONA_NAMES)]
        
        # Create a more readable user ID with persona + index
        user_id = f"{persona} {i+1:02d}"

        # 60 % from dominant mood, 40 % from others
        n_dominant = int(tracks_per_user * 0.6)
        n_other = tracks_per_user - n_dominant

        dominant_pool = mood_to_ids[dominant_mood]
        other_pools = [
            tid for m, ids in mood_to_ids.items()
            if m != dominant_mood for tid in ids
        ]

        selected_dominant = rng.sample(
            dominant_pool, min(n_dominant, len(dominant_pool))
        )
        selected_other = rng.sample(
            other_pools, min(n_other, len(other_pools))
        )

        all_selected = selected_dominant + selected_other
        rng.shuffle(all_selected)

        # Simulate play counts (zipf-like)
        play_counts = {}
        for tid in all_selected:
            play_counts[tid] = max(1, int(np_rng.zipf(1.5)))

        # ~30 % of tracks are "liked"
        n_liked = max(1, int(len(all_selected) * 0.3))
        liked = rng.sample(all_selected, n_liked)

        # Simulate timestamps (spread over the last 7 days)
        now = datetime.now()
        timestamps = [
            now - timedelta(hours=rng.uniform(0, 168))
            for _ in all_selected
        ]
        timestamps.sort()  # oldest first

        users.append(UserProfile(
            user_id=user_id,
            liked_track_ids=liked,
            recent_track_ids=all_selected,
            play_counts=play_counts,
            timestamps=timestamps,
            preferred_mood=dominant_mood,
        ))

    return users
