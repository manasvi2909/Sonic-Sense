"""
SonicSense - premium product shell
==================================
Run with:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="SonicSense",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.pages import (
    page_deep_scan,
    page_diagnostics,
    page_mainframe,
    page_mood_matrix,
    page_music_space,
    page_track_scan,
    page_user_terminal,
)
from app.retro_theme import RETRO_CSS, equalizer_html
from src.content_model import ContentEngine
from src.hybrid_recommender import HybridRecommender
from src.mood_engine import MoodEngine
from src.user_model import UserModel, generate_synthetic_users

st.markdown(RETRO_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_system():
    """Load and cache the recommendation stack."""
    engine = ContentEngine(n_neighbors=200, metric="cosine")
    engine.fit_from_csvs(data_dir="data")

    mood_engine = MoodEngine(engine.scaler)
    user_model = UserModel(recency_halflife=10, like_boost=2.0)
    hybrid = HybridRecommender(
        engine,
        mood_engine,
        user_model,
        alpha=0.45,
        beta=0.30,
        gamma=0.25,
    )
    users = generate_synthetic_users(engine, mood_engine, n_users=50, tracks_per_user=30)
    return engine, mood_engine, user_model, hybrid, users


boot_placeholder = st.empty()
if "booted" not in st.session_state:
    with boot_placeholder.container():
        st.markdown(
            """
            <div class="boot-screen">
                <div class="boot-screen__panel">
                    <div class="boot-screen__title">SonicSense</div>
                    <div class="boot-screen__sub">Discover music with taste, mood, and momentum<span class="cursor-blink">_</span></div>
                    <div class="boot-screen__meta">Loading catalog intelligence, vibe matching, personal profiles, and creative listening tools.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

engine, mood_engine, user_model, hybrid, users = load_system()
st.session_state["engine"] = engine
st.session_state["mood_engine"] = mood_engine
st.session_state["user_model"] = user_model
st.session_state["hybrid"] = hybrid
st.session_state["users"] = users
st.session_state["booted"] = True
boot_placeholder.empty()

st.markdown(
    f"""
    <section class="shell-frame">
        <div class="shell-frame__top">
            <div>
                <div class="shell-frame__eyebrow">Curated discovery platform</div>
                <div class="shell-frame__brand">SonicSense</div>
            </div>
            <div class="shell-frame__meta">
                <span class="shell-frame__chip"><span class="status-dot"></span>live catalog</span>
                <span class="shell-frame__chip">{engine.catalog_size:,} tracks</span>
                <span class="shell-frame__chip">{engine.feature_dim} audio signals</span>
                <span class="shell-frame__chip">{len(users)} listener profiles</span>
            </div>
        </div>
        <div class="shell-frame__marquee">Search the song you know. Start from the mood you feel. Build a mix that feels personal.</div>
        <div class="shell-frame__grid">
            <div class="hud-card hud-card--warm">
                <div class="hud-card__title">A richer way to discover music</div>
                <div class="hud-card__copy">
                    SonicSense blends direct song search, mood-led browsing, and personalized recommendation logic into one polished listening experience. It is built to feel more like a product than a prototype.
                </div>
                <div style="margin-top:16px">
                    {equalizer_html(26, "small")}
                </div>
                <div class="hud-card__routes">
                    <span>search songs</span>
                    <span>browse vibes</span>
                    <span>personal mixes</span>
                    <span>sound map</span>
                    <span>engine studio</span>
                    <span>compare tracks</span>
                </div>
            </div>
            <div class="hud-card">
                <div class="hud-card__title">System status</div>
                <div class="hud-meter-grid">
                    <div class="hud-meter">
                        <div class="hud-meter__top"><span>Catalog readiness</span><span>100%</span></div>
                        <div class="hud-meter__track"><div class="hud-meter__fill" style="width:100%"></div></div>
                    </div>
                    <div class="hud-meter">
                        <div class="hud-meter__top"><span>Vibe matching</span><span>92%</span></div>
                        <div class="hud-meter__track"><div class="hud-meter__fill" style="width:92%"></div></div>
                    </div>
                    <div class="hud-meter">
                        <div class="hud-meter__top"><span>Personalization</span><span>88%</span></div>
                        <div class="hud-meter__track"><div class="hud-meter__fill" style="width:88%"></div></div>
                    </div>
                    <div class="hud-meter">
                        <div class="hud-meter__top"><span>Insight tools</span><span>81%</span></div>
                        <div class="hud-meter__track"><div class="hud-meter__fill" style="width:81%"></div></div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

page = st.radio(
    "Navigation",
    [
        "Home",
        "Search",
        "Vibes",
        "For You",
        "Map",
        "Studio",
        "Compare",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

ROUTES = {
    "Home": page_mainframe,
    "Search": page_track_scan,
    "Vibes": page_mood_matrix,
    "For You": page_user_terminal,
    "Map": page_music_space,
    "Studio": page_diagnostics,
    "Compare": page_deep_scan,
}

ROUTES[page]()

st.markdown(
    """
    <div class="footer-note">
        SonicSense / premium music discovery / search songs, browse moods, build personal mixes, and explore your catalog with confidence
    </div>
    """,
    unsafe_allow_html=True,
)
