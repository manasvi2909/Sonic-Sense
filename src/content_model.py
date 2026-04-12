"""
Content Engine
==============
Refactored, importable content-based recommendation engine.
Wraps data loading, feature scaling, NearestNeighbors fitting, and
vector-space recommendation into a clean API consumed by all other modules.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

# ── Feature Specification ────────────────────────────────────────────────────

AUDIO_FEATURES: List[str] = [
    "danceability",
    "energy",
    "acousticness",
    "instrumentalness",
    "liveness",
    "speechiness",
    "valence",
    "tempo",
    "loudness",
]

REQUIRED_COLS: List[str] = ["track_id", "track_name", "artist_name"] + AUDIO_FEATURES
OPTIONAL_COLS: List[str] = ["popularity", "duration_ms", "key", "mode", "time_signature"]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _resolve_data_paths(
    csv_paths: Optional[Sequence[str]] = None,
    data_dir: str = "data",
) -> List[str]:
    """Return list of CSV paths, auto-discovering from *data_dir* if needed."""
    if csv_paths:
        return list(csv_paths)
    data_dir = Path(data_dir)
    if data_dir.is_dir():
        found = sorted(data_dir.glob("*.csv"))
        if found:
            return [str(p) for p in found]
    raise FileNotFoundError(
        f"No CSV paths provided and no CSVs found in '{data_dir}/'."
    )


def _normalize_search_text(value: object) -> str:
    """Normalize track and artist text for forgiving search."""
    text = "" if value is None else str(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# ── Content Engine ───────────────────────────────────────────────────────────

class ContentEngine:
    """Content-based music recommendation engine.

    Loads Spotify audio-feature CSVs, scales features, fits a
    NearestNeighbors model, and exposes vector-space search for
    arbitrary query points (tracks, centroids, mood vectors, etc.).
    """

    def __init__(
        self,
        n_neighbors: int = 200,
        metric: str = "cosine",
    ) -> None:
        self.n_neighbors = n_neighbors
        self.metric = metric

        # Populated after fit
        self.df: Optional[pd.DataFrame] = None
        self.scaler: Optional[StandardScaler] = None
        self.X: Optional[np.ndarray] = None  # scaled feature matrix (N × d)
        self.nn: Optional[NearestNeighbors] = None
        self._id_to_idx: Dict[str, int] = {}

    # ── Fitting ──────────────────────────────────────────────────────────

    def fit_from_csvs(
        self,
        csv_paths: Optional[Sequence[str]] = None,
        data_dir: str = "data",
        subset: Optional[int] = None,
    ) -> "ContentEngine":
        """Load one or more CSVs, merge, deduplicate, scale, and fit NN."""
        paths = _resolve_data_paths(csv_paths, data_dir)
        frames = []
        for p in paths:
            raw = pd.read_csv(p)
            missing = [c for c in REQUIRED_COLS if c not in raw.columns]
            if missing:
                raise ValueError(f"{p} missing required columns: {missing}")
            keep = [c for c in REQUIRED_COLS + OPTIONAL_COLS if c in raw.columns]
            frames.append(raw[keep])

        df = pd.concat(frames, ignore_index=True)
        df = df.dropna(subset=AUDIO_FEATURES).drop_duplicates(subset=["track_id"])

        if subset is not None and subset < len(df):
            df = df.sample(n=subset, random_state=42)

        self.df = df.reset_index(drop=True)
        self._prepare_search_index()
        self._id_to_idx = {
            tid: idx for idx, tid in enumerate(self.df["track_id"])
        }

        # Scale
        self.scaler = StandardScaler()
        self.X = self.scaler.fit_transform(self.df[AUDIO_FEATURES].values)

        # Fit NN
        k = min(self.n_neighbors, len(self.df))
        self.nn = NearestNeighbors(n_neighbors=k, metric=self.metric)
        self.nn.fit(self.X)

        return self

    def fit(self, df: pd.DataFrame) -> "ContentEngine":
        """Fit from an already-loaded DataFrame."""
        self.df = df.reset_index(drop=True)
        self._prepare_search_index()
        self._id_to_idx = {
            tid: idx for idx, tid in enumerate(self.df["track_id"])
        }
        self.scaler = StandardScaler()
        self.X = self.scaler.fit_transform(self.df[AUDIO_FEATURES].values)
        k = min(self.n_neighbors, len(self.df))
        self.nn = NearestNeighbors(n_neighbors=k, metric=self.metric)
        self.nn.fit(self.X)
        return self

    # ── Accessors ────────────────────────────────────────────────────────

    def _ensure_fitted(self) -> None:
        if self.X is None:
            raise RuntimeError("ContentEngine not fitted. Call fit_from_csvs() first.")

    def idx_for_track_id(self, track_id: str) -> int:
        """Integer index for a track_id (raises KeyError if missing)."""
        try:
            return self._id_to_idx[track_id]
        except KeyError:
            raise KeyError(f"track_id not found in catalog: {track_id}")

    def get_track_vector(self, track_id: str) -> np.ndarray:
        """Return the *scaled* feature vector for a single track (1-D)."""
        self._ensure_fitted()
        return self.X[self.idx_for_track_id(track_id)]

    def get_vectors_for_ids(self, track_ids: Sequence[str]) -> np.ndarray:
        """Return scaled feature matrix for multiple track_ids (N × d)."""
        self._ensure_fitted()
        idxs = [self.idx_for_track_id(tid) for tid in track_ids]
        return self.X[idxs]

    def get_raw_features(self, track_id: str) -> Dict[str, float]:
        """Return the *unscaled* audio features for a track as a dict."""
        self._ensure_fitted()
        idx = self.idx_for_track_id(track_id)
        row = self.df.iloc[idx]
        return {f: float(row[f]) for f in AUDIO_FEATURES}

    @property
    def catalog_size(self) -> int:
        return 0 if self.df is None else len(self.df)

    @property
    def feature_dim(self) -> int:
        return len(AUDIO_FEATURES)

    # ── Recommendation ───────────────────────────────────────────────────

    def recommend_by_id(
        self,
        track_id: str,
        n: int = 10,
        include_seed: bool = False,
    ) -> pd.DataFrame:
        """Top-n recommendations for a single seed track."""
        self._ensure_fitted()
        idx = self.idx_for_track_id(track_id)
        return self._recommend_from_vector(
            self.X[idx], n=n, exclude_idxs=(set() if include_seed else {idx})
        )

    def recommend_from_multiple(
        self,
        track_ids: Sequence[str],
        n: int = 10,
    ) -> pd.DataFrame:
        """Top-n recommendations using the centroid of multiple seeds."""
        self._ensure_fitted()
        idxs = [self.idx_for_track_id(tid) for tid in track_ids]
        centroid = np.mean(self.X[idxs], axis=0)
        return self._recommend_from_vector(centroid, n=n, exclude_idxs=set(idxs))

    def recommend_by_vector(
        self,
        vector: np.ndarray,
        n: int = 10,
        exclude_ids: Optional[Sequence[str]] = None,
    ) -> pd.DataFrame:
        """Top-n recommendations from an arbitrary point in feature space."""
        self._ensure_fitted()
        exclude_idxs = set()
        if exclude_ids:
            for tid in exclude_ids:
                if tid in self._id_to_idx:
                    exclude_idxs.add(self._id_to_idx[tid])
        return self._recommend_from_vector(vector, n=n, exclude_idxs=exclude_idxs)

    def candidates_by_vector(
        self,
        vector: np.ndarray,
        n: int = 500,
        exclude_ids: Optional[Sequence[str]] = None,
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """Return a wide candidate pool (DataFrame + their scaled vectors).

        Used by HybridRecommender to get raw candidates before rescoring.
        """
        self._ensure_fitted()
        query = vector.reshape(1, -1)
        k = min(n, len(self.df))
        distances, indices = self.nn.kneighbors(query, n_neighbors=k)
        distances, indices = distances[0], indices[0]

        exclude_idxs = set()
        if exclude_ids:
            for tid in exclude_ids:
                if tid in self._id_to_idx:
                    exclude_idxs.add(self._id_to_idx[tid])

        valid_mask = np.array([i not in exclude_idxs for i in indices])
        indices = indices[valid_mask]
        distances = distances[valid_mask]

        df_out = self.df.iloc[indices].copy()
        df_out["content_distance"] = distances
        df_out["content_similarity"] = 1.0 - distances
        vectors_out = self.X[indices]
        return df_out.reset_index(drop=True), vectors_out

    # ── Search ───────────────────────────────────────────────────────────

    def _prepare_search_index(self) -> None:
        """Build normalized text columns used for product search."""
        if self.df is None:
            return

        self.df["_track_search"] = self.df["track_name"].map(_normalize_search_text)
        self.df["_artist_search"] = self.df["artist_name"].map(_normalize_search_text)
        self.df["_combo_search"] = (
            self.df["_track_search"] + " " + self.df["_artist_search"]
        ).str.strip()

    def search_tracks(
        self,
        query: str,
        limit: int = 10,
    ) -> pd.DataFrame:
        """Ranked search by track name or artist name."""
        self._ensure_fitted()
        q = _normalize_search_text(query)
        base_cols = ["track_name", "artist_name", "track_id"]
        extra_cols = [col for col in ["popularity", "duration_ms"] if col in self.df.columns]
        out_cols = base_cols + extra_cols

        if not q:
            return pd.DataFrame(columns=out_cols)

        q_tokens = [token for token in q.split() if token]
        track_text = self.df["_track_search"]
        artist_text = self.df["_artist_search"]
        combo_text = self.df["_combo_search"]

        exact_track = track_text == q
        exact_artist = artist_text == q
        exact_combo = combo_text == q
        prefix_track = track_text.str.startswith(q, na=False)
        prefix_artist = artist_text.str.startswith(q, na=False)
        contains_track = track_text.str.contains(re.escape(q), regex=True, na=False)
        contains_artist = artist_text.str.contains(re.escape(q), regex=True, na=False)
        contains_combo = combo_text.str.contains(re.escape(q), regex=True, na=False)

        combo_token_hits = pd.Series(0, index=self.df.index, dtype=float)
        track_token_hits = pd.Series(0, index=self.df.index, dtype=float)
        artist_token_hits = pd.Series(0, index=self.df.index, dtype=float)
        for token in q_tokens:
            token_re = rf"\b{re.escape(token)}\b"
            combo_token_hits += combo_text.str.contains(token_re, regex=True, na=False).astype(float)
            track_token_hits += track_text.str.contains(token_re, regex=True, na=False).astype(float)
            artist_token_hits += artist_text.str.contains(token_re, regex=True, na=False).astype(float)

        track_all_tokens = track_token_hits == len(q_tokens)
        artist_all_tokens = artist_token_hits == len(q_tokens)
        combo_all_tokens = combo_token_hits == len(q_tokens)
        min_token_hits = 1 if len(q_tokens) == 1 else min(2, len(q_tokens))

        mask = contains_combo | combo_all_tokens | (combo_token_hits >= min_token_hits)
        if not mask.any():
            return pd.DataFrame(columns=out_cols)

        popularity = (
            self.df["popularity"].fillna(0).astype(float)
            if "popularity" in self.df.columns
            else pd.Series(0.0, index=self.df.index)
        )

        score = (
            exact_combo.astype(float) * 200
            + exact_track.astype(float) * 160
            + exact_artist.astype(float) * 140
            + combo_all_tokens.astype(float) * 110
            + artist_all_tokens.astype(float) * 95
            + track_all_tokens.astype(float) * 90
            + prefix_track.astype(float) * 90
            + prefix_artist.astype(float) * 80
            + contains_track.astype(float) * 55
            + contains_artist.astype(float) * 45
            + contains_combo.astype(float) * 35
            + combo_token_hits * 12
            + artist_token_hits * 10
            + track_token_hits * 8
            + (popularity / 100.0) * 8
        )

        sort_cols = ["search_score", "track_name"]
        ascending = [False, True]
        if "popularity" in out_cols:
            sort_cols.insert(1, "popularity")
            ascending.insert(1, False)

        hits = (
            self.df.loc[mask, out_cols]
            .assign(search_score=score[mask].values)
            .sort_values(sort_cols, ascending=ascending)
            .head(limit)
            .reset_index(drop=True)
        )
        return hits

    # ── Private ──────────────────────────────────────────────────────────

    def _recommend_from_vector(
        self,
        vector: np.ndarray,
        n: int = 10,
        exclude_idxs: Optional[set] = None,
    ) -> pd.DataFrame:
        """Core NN search → ranked DataFrame."""
        query = vector.reshape(1, -1)
        k = min(self.n_neighbors, len(self.df))
        distances, indices = self.nn.kneighbors(query, n_neighbors=k)
        distances, indices = distances[0], indices[0]
        exclude = exclude_idxs or set()

        rows = []
        for i, d in zip(indices, distances):
            if i in exclude:
                continue
            row = self.df.iloc[i].to_dict()
            sim = 1.0 - float(d)
            row.update({"rank": len(rows) + 1, "distance": float(d), "similarity": sim})
            rows.append(row)
            if len(rows) >= n:
                break

        cols = ["rank", "track_name", "artist_name", "track_id", "similarity", "distance"]
        if "popularity" in self.df.columns:
            cols.insert(4, "popularity")
        return pd.DataFrame(rows)[cols] if rows else pd.DataFrame(columns=cols)

    # ── Repr ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        status = "fitted" if self.X is not None else "unfitted"
        n = self.catalog_size
        return f"<ContentEngine({status}, {n:,} tracks, {self.feature_dim}d)>"
