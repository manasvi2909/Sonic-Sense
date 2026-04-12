"""
Spotify API Integration (Scaffold)
====================================
Interface for Spotify Web API via ``spotipy``.

⚠  This module is a **scaffold** — it defines the full interface but requires
valid Spotify API credentials (``client_id``, ``client_secret``, and for
user-specific endpoints a ``redirect_uri`` + OAuth flow).

When credentials are available, the same API surface will be used by the
Streamlit frontend and the session-based recommender.

Environment Variables
---------------------
  SPOTIPY_CLIENT_ID       — Spotify app client ID
  SPOTIPY_CLIENT_SECRET   — Spotify app client secret
  SPOTIPY_REDIRECT_URI    — OAuth redirect URI (e.g. http://localhost:8888/callback)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
    _SPOTIPY_AVAILABLE = True
except ImportError:
    _SPOTIPY_AVAILABLE = False


@dataclass
class SpotifyTrack:
    """Lightweight track representation from the Spotify API."""
    track_id: str
    track_name: str
    artist_name: str
    album_name: str
    popularity: int
    preview_url: Optional[str]
    album_art_url: Optional[str]
    audio_features: Optional[Dict[str, float]] = None


class SpotifyClient:
    """Wrapper around ``spotipy`` for the Music Intelligence System.

    Supports two modes:
      1. **Client Credentials** — for search, audio features (no user data).
      2. **User OAuth** — for user history, playlists, saved tracks.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scope: str = "user-read-recently-played user-top-read playlist-modify-public",
    ) -> None:
        if not _SPOTIPY_AVAILABLE:
            raise ImportError(
                "spotipy is required for Spotify API integration. "
                "Install with: pip install spotipy"
            )

        self.client_id = client_id or os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIPY_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv(
            "SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback"
        )
        self.scope = scope
        self._sp: Optional["spotipy.Spotify"] = None
        self._sp_user: Optional["spotipy.Spotify"] = None

    @property
    def is_configured(self) -> bool:
        """Whether API credentials are set."""
        return bool(self.client_id and self.client_secret)

    # ── Connection ───────────────────────────────────────────────────────

    def connect_client_credentials(self) -> "SpotifyClient":
        """Connect with client credentials (no user scope)."""
        if not self.is_configured:
            raise RuntimeError(
                "Spotify credentials not configured. Set SPOTIPY_CLIENT_ID "
                "and SPOTIPY_CLIENT_SECRET environment variables."
            )
        auth = SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        self._sp = spotipy.Spotify(auth_manager=auth)
        return self

    def connect_user_oauth(self) -> "SpotifyClient":
        """Connect with user OAuth (for personal data)."""
        if not self.is_configured:
            raise RuntimeError("Spotify credentials not configured.")
        auth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )
        self._sp_user = spotipy.Spotify(auth_manager=auth)
        return self

    def _client(self, user: bool = False) -> "spotipy.Spotify":
        sp = self._sp_user if user else self._sp
        if sp is None:
            raise RuntimeError(
                "Not connected. Call connect_client_credentials() or connect_user_oauth()."
            )
        return sp

    # ── Search ───────────────────────────────────────────────────────────

    def search_track(
        self, query: str, limit: int = 5
    ) -> List[SpotifyTrack]:
        """Search for tracks by name/artist."""
        sp = self._client()
        results = sp.search(q=query, type="track", limit=limit)
        tracks = []
        for item in results["tracks"]["items"]:
            tracks.append(SpotifyTrack(
                track_id=item["id"],
                track_name=item["name"],
                artist_name=", ".join(a["name"] for a in item["artists"]),
                album_name=item["album"]["name"],
                popularity=item["popularity"],
                preview_url=item.get("preview_url"),
                album_art_url=item["album"]["images"][0]["url"] if item["album"]["images"] else None,
            ))
        return tracks

    # ── Audio Features ───────────────────────────────────────────────────

    def get_audio_features(
        self, track_ids: List[str]
    ) -> List[Dict[str, float]]:
        """Get audio features for a batch of track IDs."""
        sp = self._client()
        # Spotify API allows max 100 IDs per request
        all_features = []
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            results = sp.audio_features(batch)
            for feat in results:
                if feat:
                    all_features.append(feat)
        return all_features

    # ── User Data ────────────────────────────────────────────────────────

    def get_user_recent_tracks(
        self, limit: int = 50
    ) -> List[SpotifyTrack]:
        """Get the current user's recently played tracks."""
        sp = self._client(user=True)
        results = sp.current_user_recently_played(limit=limit)
        tracks = []
        for item in results["items"]:
            t = item["track"]
            tracks.append(SpotifyTrack(
                track_id=t["id"],
                track_name=t["name"],
                artist_name=", ".join(a["name"] for a in t["artists"]),
                album_name=t["album"]["name"],
                popularity=t["popularity"],
                preview_url=t.get("preview_url"),
                album_art_url=t["album"]["images"][0]["url"] if t["album"]["images"] else None,
            ))
        return tracks

    def get_user_top_tracks(
        self,
        time_range: str = "medium_term",
        limit: int = 50,
    ) -> List[SpotifyTrack]:
        """Get the current user's top tracks.

        time_range: 'short_term' (~4 weeks), 'medium_term' (~6 months), 'long_term' (years)
        """
        sp = self._client(user=True)
        results = sp.current_user_top_tracks(time_range=time_range, limit=limit)
        tracks = []
        for item in results["items"]:
            tracks.append(SpotifyTrack(
                track_id=item["id"],
                track_name=item["name"],
                artist_name=", ".join(a["name"] for a in item["artists"]),
                album_name=item["album"]["name"],
                popularity=item["popularity"],
                preview_url=item.get("preview_url"),
                album_art_url=item["album"]["images"][0]["url"] if item["album"]["images"] else None,
            ))
        return tracks

    def get_user_saved_tracks(
        self, limit: int = 50
    ) -> List[SpotifyTrack]:
        """Get the current user's saved/liked tracks."""
        sp = self._client(user=True)
        results = sp.current_user_saved_tracks(limit=limit)
        tracks = []
        for item in results["items"]:
            t = item["track"]
            tracks.append(SpotifyTrack(
                track_id=t["id"],
                track_name=t["name"],
                artist_name=", ".join(a["name"] for a in t["artists"]),
                album_name=t["album"]["name"],
                popularity=t["popularity"],
                preview_url=t.get("preview_url"),
                album_art_url=t["album"]["images"][0]["url"] if t["album"]["images"] else None,
            ))
        return tracks

    # ── Playlist Creation ────────────────────────────────────────────────

    def create_playlist(
        self,
        name: str,
        track_ids: List[str],
        description: str = "Created by Music Intelligence System",
        public: bool = True,
    ) -> str:
        """Create a new playlist and add tracks. Returns playlist URL."""
        sp = self._client(user=True)
        user_info = sp.current_user()
        user_id = user_info["id"]

        playlist = sp.user_playlist_create(
            user=user_id, name=name,
            public=public, description=description,
        )
        playlist_id = playlist["id"]

        # Add tracks in batches of 100
        uris = [f"spotify:track:{tid}" for tid in track_ids]
        for i in range(0, len(uris), 100):
            sp.playlist_add_items(playlist_id, uris[i:i+100])

        return playlist["external_urls"]["spotify"]

    # ── Repr ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        configured = "configured" if self.is_configured else "not configured"
        connected = "connected" if self._sp else "disconnected"
        return f"<SpotifyClient({configured}, {connected})>"
