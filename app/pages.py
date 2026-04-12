"""
SonicSense page renderers
=========================
Product-style pixel pages for the Streamlit app.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retro_theme import (
    MOOD_DESCS,
    MOOD_HEX,
    MOOD_ICONS,
    PLOTLY_LAYOUT,
    crt_monitor,
    desktop_intro,
    desktop_shell,
    equalizer_html,
    gauge_bar,
    paper_note,
    retro_table_html,
    route_hud,
    section_banner,
    stat_box,
    terminal_window,
)
from src.content_model import AUDIO_FEATURES
from src.mood_engine import CONTEXT_MAP, MOOD_NAMES


def _get_system():
    return (
        st.session_state["engine"],
        st.session_state["mood_engine"],
        st.session_state["user_model"],
        st.session_state["hybrid"],
        st.session_state["users"],
    )


def _section_header(icon: str, title: str, subtitle: str, eyebrow: str):
    st.markdown(
        section_banner(icon=icon, title=title, subtitle=subtitle, eyebrow=eyebrow),
        unsafe_allow_html=True,
    )


def _bullet_html(lines: list[str]) -> str:
    return '<div class="bullet-stack">' + "".join(
        f'<div class="bullet-line">{line}</div>' for line in lines
    ) + "</div>"


def _plotly_radar(features, values, title=""):
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=features + [features[0]],
            fill="toself",
            fillcolor="rgba(241, 104, 77, 0.14)",
            line=dict(color="#f1684d", width=3),
            marker=dict(size=6, color="#4de3bb", line=dict(color="#19263d", width=1)),
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                color="#50607c",
                gridcolor="rgba(25, 38, 61, 0.14)",
                linecolor="rgba(25, 38, 61, 0.18)",
            ),
            angularaxis=dict(
                color="#50607c",
                gridcolor="rgba(25, 38, 61, 0.14)",
                linecolor="rgba(25, 38, 61, 0.18)",
            ),
        ),
        showlegend=False,
        title=dict(
            text=title,
            font=dict(family="IBM Plex Mono, monospace", size=13, color="#19263d"),
            x=0.5,
            xanchor="center",
        ),
        height=380,
    )
    return fig


def page_mainframe():
    engine, mood_engine, _, _, users = _get_system()

    st.markdown(
        desktop_shell(
            desktop_intro(
                "FIND YOUR NEXT TRACK FAST",
                "Search by song or artist, jump into a vibe, or generate picks around a listener profile. SonicSense now feels like a real music product first and a power tool second.",
                badges=[
                    f"{engine.catalog_size:,} tracks",
                    f"{engine.feature_dim} signals",
                    f"{len(users)} profiles",
                    "retro product ui",
                ],
            ),
            crt_monitor(
                "LIVE ROUTES",
                "SEARCH\\nVIBES\\nFOR YOU",
                [
                    ("song lookup", "ready"),
                    ("vibe picks", "ready"),
                    ("personal mixes", "ready"),
                    ("compare", "ready"),
                ],
            ),
        ),
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_box("Tracks", f"{engine.catalog_size:,}", "#f1684d"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_box("Signals", str(engine.feature_dim), "#4de3bb"), unsafe_allow_html=True)
    with c3:
        st.markdown(stat_box("Vibes", str(len(MOOD_NAMES)), "#ffb347"), unsafe_allow_html=True)
    with c4:
        st.markdown(stat_box("Profiles", str(len(users)), "#c7f36b"), unsafe_allow_html=True)

    st.markdown(
        """
        <div class="ticker-bar"><div class="ticker-content">
        search any song or artist  .  start with a vibe  .  generate personal mixes  .  compare tracks side by side  .  explore the full sound map
        </div></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        paper_note(
            "START LISTENING",
            "Head to <strong>Search</strong> when you know the song, <strong>Vibes</strong> when you know the feeling, and <strong>For You</strong> when you want the app to lean into a listener profile.",
        ),
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95])
    with left:
        st.markdown(
            terminal_window(
                "WHAT YOU CAN DO",
                _bullet_html(
                    [
                        "<strong>Search</strong> turns any track or artist lookup into an instant recommendation source.",
                        "<strong>Vibes</strong> builds a list from prompts like focus, gym, late night, or rain.",
                        "<strong>For You</strong> shapes mixes around profile taste and session context.",
                        "<strong>Compare</strong> shows exactly why two songs feel close or far apart.",
                    ]
                ),
                tone="paper",
            ),
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            terminal_window(
                "RIGHT NOW",
                _bullet_html(
                    [
                        "<strong>Fast lookup</strong> for song and artist search.",
                        "<strong>Ranked results</strong> instead of raw unsorted substring hits.",
                        "<strong>Multiple entry points</strong> for songs, vibes, and profiles.",
                        "<strong>Studio tools</strong> still available when you want to tune the engine.",
                    ]
                ),
                tone="navy",
            ),
            unsafe_allow_html=True,
        )

    mood_labels = mood_engine.batch_assign_moods(engine.X)
    dist = {mood: int(np.sum(mood_labels == mood)) for mood in MOOD_NAMES}
    mood_rows = ['<div class="mood-split-grid">']
    for mood in MOOD_NAMES:
        pct = dist[mood] / engine.catalog_size * 100
        color = MOOD_HEX[mood]
        mood_rows.append(
            f"""
            <div class="mood-split-row">
                <div class="mood-split-row__meta">
                    <div class="mood-split-row__title" style="color:{color} !important">{MOOD_ICONS[mood]} {mood}</div>
                    <div class="mood-split-row__desc">{MOOD_DESCS[mood]}</div>
                </div>
                <div class="gauge-track"><div class="gauge-fill" style="width:{pct:.1f}%;background:{color}"></div></div>
                <div class="mood-split-row__value">{dist[mood]:,}</div>
            </div>
            """
        )
    mood_rows.append("</div>")

    modules = [
        ("song search", "online", "good"),
        ("vibe matcher", "online", "good"),
        ("personal mixes", "active", "good"),
        ("hybrid ranker", "online", "good"),
        ("compare view", "ready", "good"),
        ("sound map", "loaded", "good"),
        ("spotify api", "scaffold", "warn"),
        ("studio tools", "ready", "warn"),
    ]
    module_html = ['<div class="status-grid">']
    for name, status, tone in modules:
        pill = "status-pill--good" if tone == "good" else "status-pill--warn"
        module_html.append(
            f'<div class="status-line"><span>{name}</span><span class="status-pill {pill}">{status}</span></div>'
        )
    module_html.append("</div>")

    m1, m2 = st.columns([1, 1])
    with m1:
        st.markdown(
            terminal_window("VIBE MIX", "".join(mood_rows), tone="crt"),
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            terminal_window("PRODUCT STATUS", "".join(module_html), tone="navy"),
            unsafe_allow_html=True,
        )


def page_track_scan():
    engine, _, _, hybrid, users = _get_system()

    _section_header(
        "01",
        "SEARCH",
        "Look up a song or artist, lock onto the best match, and turn it into a clean recommendation list.",
        eyebrow="SONG SEARCH",
    )
    st.markdown(equalizer_html(18, "small"), unsafe_allow_html=True)
    st.markdown(
        route_hud(
            "SEARCH AND PLAY",
            "LOOKUP FLOW",
            "Type a song, an artist, or both. Results are ranked so the most useful matches rise first instead of getting buried in raw dataset order.",
            chips=["song search", "ranked results", "3 mix modes"],
            cells=[
                ("SEARCH", "Find the closest match by title, artist, or both."),
                ("SET", "Choose mode, vibe, profile, and output size."),
                ("PLAY", "Generate a list that feels ready to listen to."),
            ],
        ),
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns([1.1, 0.9])
    with top_left:
        st.markdown(
            paper_note(
                "SEARCH TIPS",
                "Try a <strong>track name</strong>, an <strong>artist name</strong>, or a combined query like <strong>Midnight City M83</strong>. The matching engine now ranks results instead of just slicing raw hits.",
            ),
            unsafe_allow_html=True,
        )
    with top_right:
        st.markdown(
            terminal_window(
                "MIX MODES",
                _bullet_html(
                    [
                        "<strong>Hybrid</strong> blends similarity, vibe, and listener context.",
                        "<strong>Content Only</strong> stays closest to the source track.",
                        "<strong>Mood Enhanced</strong> bends the result toward a typed vibe.",
                    ]
                ),
                tone="navy",
            ),
            unsafe_allow_html=True,
        )

    query = st.text_input(
        "Search track or artist",
        placeholder="Search for a song or artist",
        label_visibility="collapsed",
    )

    if not query:
        return

    results = engine.search_tracks(query, limit=15)
    if results.empty:
        st.warning("No matching songs or artists were found in the local catalog.")
        return

    result_cols = [
        col for col in ["track_name", "artist_name", "popularity", "duration_ms"] if col in results.columns
    ]
    st.markdown(
        terminal_window(
            f"TOP MATCHES / {len(results)}",
            retro_table_html(results[result_cols]),
            tone="paper",
        ),
        unsafe_allow_html=True,
    )

    options = [f"{row['track_name']} - {row['artist_name']}" for _, row in results.iterrows()]
    selected = st.selectbox("Pick a song", options, index=0)
    seed_idx = options.index(selected)
    seed_id = results.iloc[seed_idx]["track_id"]
    seed_row = results.iloc[seed_idx]
    duration_min = float(seed_row["duration_ms"]) / 60000 if "duration_ms" in seed_row else None

    left, right = st.columns([1.05, 0.95])
    with left:
        raw = engine.get_raw_features(seed_id)
        radar_features = [
            "danceability",
            "energy",
            "acousticness",
            "valence",
            "speechiness",
            "liveness",
            "instrumentalness",
        ]
        radar_values = [raw[feature] for feature in radar_features]
        st.plotly_chart(
            _plotly_radar(radar_features, radar_values, "SONG FINGERPRINT"),
            use_container_width=True,
        )
    with right:
        seed_details = [
            f"Track: <strong>{seed_row['track_name']}</strong>",
            f"Artist: <strong>{seed_row['artist_name']}</strong>",
            f"Popularity: <strong>{int(seed_row['popularity'])}</strong>" if "popularity" in seed_row else "Popularity: <strong>n/a</strong>",
            f"Duration: <strong>{duration_min:.2f} min</strong>" if duration_min is not None else "Duration: <strong>n/a</strong>",
        ]
        st.markdown(
            terminal_window("NOW PLAYING SOURCE", _bullet_html(seed_details), tone="paper"),
            unsafe_allow_html=True,
        )

    st.markdown(
        paper_note(
            "BUILD YOUR MIX",
            "Pick how tightly the list should stick to the source track, how many songs you want back, and whether a listener profile or vibe should steer the final ranking.",
        ),
        unsafe_allow_html=True,
    )

    mode = st.radio("Mode", ["Hybrid", "Content Only", "Mood Enhanced"], horizontal=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        n_recs = st.slider("Songs", 5, 30, 10)
    with c2:
        user_idx = st.selectbox("Profile", range(len(users)), format_func=lambda i: users[i].user_id)
    with c3:
        ctx = st.text_input("Vibe", placeholder="gym / focus / chill / late night")

    if st.button("Play Recommendations"):
        with st.spinner("Building your mix..."):
            if mode == "Hybrid":
                recs = hybrid.recommend(
                    seed_ids=[seed_id],
                    user_profile=users[user_idx],
                    context=ctx or None,
                    n=n_recs,
                )
            elif mode == "Content Only":
                recs = hybrid.recommend_content_only([seed_id], n=n_recs)
            else:
                recs = hybrid.recommend(
                    seed_ids=[seed_id],
                    context=ctx or "chill",
                    n=n_recs,
                    alpha=0.4,
                    beta=0.0,
                    gamma=0.6,
                )
            st.session_state["track_scan_recs"] = recs

    if "track_scan_recs" not in st.session_state:
        return

    recs = st.session_state["track_scan_recs"]
    display_cols = [
        col
        for col in ["rank", "track_name", "artist_name", "hybrid_score", "mood_label"]
        if col in recs.columns
    ]
    st.markdown(
        terminal_window(
            f"YOUR MIX / TOP {len(recs)}",
            retro_table_html(recs[display_cols]),
            tone="paper",
        ),
        unsafe_allow_html=True,
    )

    if "explanation" in recs.columns:
        with st.expander("Why these songs showed up"):
            for _, row in recs.iterrows():
                st.markdown(
                    f'<div class="expl-chip">#{int(row["rank"])} <strong>{row["track_name"]}</strong> -> {row["explanation"]}</div>',
                    unsafe_allow_html=True,
                )


def page_mood_matrix():
    _, mood_engine, _, hybrid, _ = _get_system()

    _section_header(
        "02",
        "VIBES",
        "Start from the feeling, not the title, and get a list shaped around the moment you are in.",
        eyebrow="VIBE MATCH",
    )

    st.markdown(
        paper_note(
            "TYPE THE MOMENT",
            "Try prompts like <strong>night drive</strong>, <strong>focus session</strong>, <strong>rainy evening</strong>, <strong>after party</strong>, or <strong>morning chill</strong>.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        route_hud(
            "SET THE MOOD",
            "VIBE TO MIX",
            "This route is for moments when you know the energy immediately but the song name is nowhere in your head.",
            chips=["vibe search", "mood cards", "instant picks"],
            cells=[
                ("DESCRIBE", "Write the scene, feeling, or activity."),
                ("MATCH", "Resolve it into a listening lane."),
                ("LISTEN", "Get songs shaped around that lane."),
            ],
        ),
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    for idx, mood in enumerate(MOOD_NAMES):
        with cols[idx]:
            color = MOOD_HEX[mood]
            st.markdown(
                f"""
                <div class="mood-card" style="border-color:{color}">
                    <div class="mood-card__icon" style="color:{color} !important">{MOOD_ICONS[mood]}</div>
                    <div class="mood-card__name" style="color:{color} !important">{mood}</div>
                    <div class="mood-card__desc">{MOOD_DESCS[mood]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(equalizer_html(14, "small"), unsafe_allow_html=True)
    c1, c2 = st.columns([1.15, 0.85])
    with c1:
        ctx_input = st.text_input(
            "Enter context or mood",
            placeholder="night drive, focus, breakup, gym, calm...",
        )
    with c2:
        n = st.slider("Songs", 5, 25, 10)

    if ctx_input:
        resolved = mood_engine.context_to_mood(ctx_input)
        color = MOOD_HEX.get(resolved, "#f1684d")
        st.markdown(
            terminal_window(
                "MATCHED VIBE",
                _bullet_html(
                    [
                        f"Input: <strong>{ctx_input}</strong>",
                        f"Lane: <strong style='color:{color} !important'>{MOOD_ICONS.get(resolved, '')} {resolved}</strong>",
                        "Your next list will lean into that lane before the final ranking is returned.",
                    ]
                ),
                tone="crt",
            ),
            unsafe_allow_html=True,
        )

        if st.button("Get Vibe Picks"):
            with st.spinner("Finding songs for that mood..."):
                st.session_state["mood_recs"] = hybrid.recommend_by_mood(ctx_input, n=n)

    if "mood_recs" in st.session_state:
        recs = st.session_state["mood_recs"]
        display_cols = [
            col
            for col in ["rank", "track_name", "artist_name", "hybrid_score", "mood_label"]
            if col in recs.columns
        ]
        st.markdown(
            terminal_window(
                "VIBE PICKS",
                retro_table_html(recs[display_cols]),
                tone="paper",
            ),
            unsafe_allow_html=True,
        )

    grouped_keywords = {mood: [] for mood in MOOD_NAMES}
    for keyword, mood in sorted(CONTEXT_MAP.items()):
        grouped_keywords.setdefault(mood, []).append(keyword)

    groups_html = ['<div class="keyword-board">']
    for mood in MOOD_NAMES:
        color = MOOD_HEX.get(mood, "#f1684d")
        chips = "".join(
            f'<span class="context-chip" style="color:{color} !important;border-color:{color}55">{keyword}</span>'
            for keyword in grouped_keywords.get(mood, [])
        )
        groups_html.append(
            f"""
            <div class="keyword-board__group">
                <div class="keyword-board__title" style="color:{color} !important">{mood}</div>
                <div class="keyword-board__chips">{chips}</div>
            </div>
            """
        )
    groups_html.append("</div>")
    st.markdown(
        terminal_window("VIBE SHORTCUTS", "".join(groups_html), tone="paper"),
        unsafe_allow_html=True,
    )


def page_user_terminal():
    engine, _, user_model, hybrid, users = _get_system()

    _section_header(
        "03",
        "FOR YOU",
        "Generate picks shaped by listener taste, listening history, and time-of-day context.",
        eyebrow="PERSONAL MIX",
    )

    st.markdown(
        paper_note(
            "PERSONALIZATION",
            "Choose a listener profile, inspect its taste shape, then build a mix around that behavior.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        route_hud(
            "PERSONAL LISTENER VIEW",
            "PROFILE TO MIX",
            "This route turns a listener profile into a playlist-style output instead of burying the personalization behind technical details.",
            chips=["taste vector", "session context", "personal picks"],
            cells=[
                ("SELECT", "Choose a profile with a dominant mood and history."),
                ("READ", "See the taste vector and inferred listening window."),
                ("MIX", "Generate a list with optional vibe override."),
            ],
        ),
        unsafe_allow_html=True,
    )

    u_idx = st.selectbox(
        "Select user",
        range(len(users)),
        format_func=lambda i: f"{users[i].user_id} / {users[i].preferred_mood}",
    )
    user = users[u_idx]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(stat_box("Tracks Seen", str(len(user.all_track_ids)), "#4de3bb"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_box("Liked", str(len(user.liked_track_ids)), "#ffb347"), unsafe_allow_html=True)
    with c3:
        st.markdown(
            stat_box("Core Mood", user.preferred_mood, MOOD_HEX.get(user.preferred_mood, "#f1684d")),
            unsafe_allow_html=True,
        )

    user_vec = user_model.build_user_vector(user, engine)
    raw_vec = engine.scaler.inverse_transform(user_vec.reshape(1, -1))[0]
    radar_features = [
        "danceability",
        "energy",
        "acousticness",
        "valence",
        "speechiness",
        "liveness",
        "instrumentalness",
    ]
    feat_idx = [AUDIO_FEATURES.index(feature) for feature in radar_features]
    radar_values = [float(np.clip(raw_vec[idx], 0, 1)) for idx in feat_idx]

    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(
            _plotly_radar(radar_features, radar_values, "TASTE VECTOR"),
            use_container_width=True,
        )
    with right:
        profile_lines = [
            f"Listener ID: <strong>{user.user_id}</strong>",
            f"Preferred mood: <strong style='color:{MOOD_HEX.get(user.preferred_mood, '#f1684d')} !important'>{user.preferred_mood}</strong>",
            f"History size: <strong>{len(user.all_track_ids)}</strong> tracks",
        ]
        if user.timestamps:
            bucket, hint = user_model.infer_time_context(user.timestamps)
            profile_lines.extend(
                [
                    f"Peak session: <strong>{bucket.title()}</strong>",
                    f"Context hint: <strong>{hint}</strong>",
                    f"Tracked sessions: <strong>{len(user.timestamps)}</strong>",
                ]
            )
        st.markdown(
            terminal_window("LISTENER SNAPSHOT", _bullet_html(profile_lines), tone="navy"),
            unsafe_allow_html=True,
        )

    ctx = st.text_input("Vibe override", placeholder="Optional: gym / focus / commute / late night")
    if st.button("Create Personal Mix"):
        with st.spinner("Building your personalized mix..."):
            st.session_state["user_recs"] = hybrid.recommend_for_user(user, n=10, context=ctx or None)

    if "user_recs" in st.session_state:
        recs = st.session_state["user_recs"]
        display_cols = [
            col
            for col in ["rank", "track_name", "artist_name", "hybrid_score", "mood_label"]
            if col in recs.columns
        ]
        st.markdown(
            terminal_window(
                f"PERSONAL PICKS / {user.user_id}",
                retro_table_html(recs[display_cols]),
                tone="paper",
            ),
            unsafe_allow_html=True,
        )


@st.cache_data
def _compute_pca_data():
    engine = st.session_state["engine"]
    mood_engine = st.session_state["mood_engine"]
    from src.clustering_viz import reduce_pca

    sample_size = 12000
    rng = np.random.RandomState(42)
    idxs = rng.choice(len(engine.X), size=min(sample_size, len(engine.X)), replace=False)
    x_sample = engine.X[idxs]
    x_2d, _ = reduce_pca(x_sample, n_components=2)
    moods = mood_engine.batch_assign_moods(x_sample)
    names = engine.df.iloc[idxs]["track_name"].values
    artists = engine.df.iloc[idxs]["artist_name"].values
    return x_2d, moods, names, artists


def page_music_space():
    _section_header(
        "04",
        "MAP",
        "Explore the catalog as a sound map and see where moods and sonic neighborhoods cluster together.",
        eyebrow="SOUND MAP",
    )

    st.markdown(
        paper_note(
            "GLOBAL VIEW",
            "Use this page when you want the big picture of the catalog instead of starting from one song or one vibe.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        route_hud(
            "CATALOG MAP",
            "GLOBAL EXPLORATION",
            "Zoom out and see where songs gather, where moods overlap, and where sonic styles sit far apart.",
            chips=["map view", "mood colors", "cluster zones"],
            cells=[
                ("PROJECT", "Shrink the feature space into a readable map."),
                ("SCAN", "Spot clusters, outliers, and overlap across moods."),
                ("EXPLORE", "Use the chart as a visual guide to the catalog."),
            ],
        ),
        unsafe_allow_html=True,
    )

    st.markdown(equalizer_html(12, "small"), unsafe_allow_html=True)
    with st.spinner("Projecting catalog coordinates..."):
        x_2d, moods, names, artists = _compute_pca_data()

    fig = go.Figure()
    for mood in MOOD_NAMES:
        mask = moods == mood
        fig.add_trace(
            go.Scattergl(
                x=x_2d[mask, 0],
                y=x_2d[mask, 1],
                mode="markers",
                name=mood,
                marker=dict(size=4, color=MOOD_HEX[mood], opacity=0.66),
                text=[f"{name} - {artist}" for name, artist in zip(names[mask], artists[mask])],
                hovertemplate="<b>%{text}</b><extra></extra>",
            )
        )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="CATALOG SOUND MAP",
            font=dict(family="IBM Plex Mono, monospace", size=13, color="#19263d"),
            x=0.5,
            xanchor="center",
        ),
        height=640,
        legend=dict(
            font=dict(family="IBM Plex Mono, monospace", size=11, color="#19263d"),
            bgcolor="rgba(255, 247, 218, 0.88)",
            bordercolor="rgba(25, 38, 61, 0.16)",
            borderwidth=2,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        terminal_window(
            "MAP NOTES",
            _bullet_html(
                [
                    f"Showing a <strong>{len(x_2d):,}-track</strong> sample for responsiveness.",
                    "Each point is colored by its inferred vibe lane.",
                    "Dense pockets usually mean similar energy, valence, tempo, and texture.",
                ]
            ),
            tone="paper",
        ),
        unsafe_allow_html=True,
    )


def page_diagnostics():
    engine, _, _, hybrid, users = _get_system()

    _section_header(
        "05",
        "STUDIO",
        "Tune and inspect the recommendation engine without leaving the product experience.",
        eyebrow="ENGINE TOOLS",
    )

    st.markdown(
        paper_note(
            "QUALITY TOOLS",
            "Run a full engine check when you want to see whether recommendations stay varied, personalized, and high quality across the catalog.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        route_hud(
            "ENGINE HEALTH",
            "QUALITY VIEW",
            "This is where you verify that the recommendation engine stays strong across more than a single good-looking example.",
            chips=["engine check", "scoreboard", "ranking quality"],
            cells=[
                ("SET", "Choose the test group size and recommendation cutoff."),
                ("RUN", "Score the hybrid model across core metrics."),
                ("REVIEW", "Spot weak ranking behavior early."),
            ],
        ),
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        n_users = st.slider("Test users", 5, 50, 15)
    with c2:
        k = st.slider("K value", 5, 30, 10)

    if st.button("Run Studio Check"):
        from src.evaluation import Evaluator

        evaluator = Evaluator(engine)
        with st.spinner("Running engine checks..."):
            st.session_state["eval_results"] = evaluator.full_evaluation(
                hybrid, users[:n_users], k=k, verbose=False
            )

    if "eval_results" not in st.session_state:
        return

    results = st.session_state["eval_results"]
    labels_map = {
        "intra_list_diversity": ("Intra-list Diversity", 0.5),
        "novelty": ("Novelty", 6.0),
        "personalization": ("Personalization", 1.0),
        "coverage": ("Catalog Coverage", 0.05),
        "hit_rate_at_k": ("Hit Rate @ K", 1.0),
        "ndcg_at_k": ("NDCG @ K", 1.0),
    }

    gauges_html = "".join(
        gauge_bar(label, results.get(metric, 0), max_value)
        for metric, (label, max_value) in labels_map.items()
    )
    st.markdown(
        terminal_window("STUDIO SCOREBOARD", gauges_html, tone="crt"),
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    metric_names = list(labels_map.keys())
    vals = [results.get(name, 0) for name in metric_names]
    fig.add_trace(
        go.Bar(
            x=[labels_map[name][0] for name in metric_names],
            y=vals,
            marker=dict(
                color=["#f1684d", "#4de3bb", "#ffb347", "#c7f36b", "#7fcfff", "#ff8a8a"],
                line=dict(width=0),
            ),
            text=[f"{value:.4f}" for value in vals],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono, monospace", size=11, color="#19263d"),
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=420,
        title=dict(
            text="ENGINE SNAPSHOT",
            font=dict(family="IBM Plex Mono, monospace", size=13, color="#19263d"),
            x=0.5,
            xanchor="center",
        ),
        bargap=0.34,
    )
    st.plotly_chart(fig, use_container_width=True)


def page_deep_scan():
    engine, mood_engine, _, _, _ = _get_system()

    _section_header(
        "06",
        "COMPARE",
        "Put two tracks side by side and see how close they really are under the hood.",
        eyebrow="SIDE BY SIDE",
    )

    st.markdown(
        paper_note(
            "COMPARE ANY TWO SONGS",
            "Use this when you want to understand why one follow-up feels right, or why two songs that seem similar still land differently.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        route_hud(
            "TRACK MATCHUP",
            "A TO B",
            "Compare songs directly, inspect the overlap, and see the biggest feature gaps without leaving the app.",
            chips=["mood check", "radar overlay", "feature gaps"],
            cells=[
                ("PICK", "Search and lock in two songs."),
                ("OVERLAY", "Compare both audio fingerprints on one radar."),
                ("UNDERSTAND", "Read the deltas driving the match or mismatch."),
            ],
        ),
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        q1 = st.text_input("Track A", placeholder="Search track A")
    with c2:
        q2 = st.text_input("Track B", placeholder="Search track B")

    if not (q1 and q2):
        return

    r1 = engine.search_tracks(q1, limit=5)
    r2 = engine.search_tracks(q2, limit=5)

    if r1.empty or r2.empty:
        st.warning("One or both songs could not be found in the local catalog.")
        return

    c1, c2 = st.columns(2)
    with c1:
        opts1 = [f"{row['track_name']} - {row['artist_name']}" for _, row in r1.iterrows()]
        sel1 = st.selectbox("Select A", opts1, key="compare_a")
        tid1 = r1.iloc[opts1.index(sel1)]["track_id"]
    with c2:
        opts2 = [f"{row['track_name']} - {row['artist_name']}" for _, row in r2.iterrows()]
        sel2 = st.selectbox("Select B", opts2, key="compare_b")
        tid2 = r2.iloc[opts2.index(sel2)]["track_id"]

    if not st.button("Compare Tracks"):
        return

    from src.explainability import explain_recommendation_detailed

    detail = explain_recommendation_detailed(tid1, tid2, engine, mood_engine)
    match_ok = detail["mood_match"]
    match_text = "MATCH" if match_ok else "MISMATCH"
    match_color = "#c7f36b" if match_ok else "#f1684d"

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(
            stat_box("Track A Mood", detail["seed_mood"], MOOD_HEX.get(detail["seed_mood"], "#4de3bb")),
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(stat_box("Match", match_text, match_color), unsafe_allow_html=True)
    with s3:
        st.markdown(
            stat_box("Track B Mood", detail["rec_mood"], MOOD_HEX.get(detail["rec_mood"], "#ffb347")),
            unsafe_allow_html=True,
        )

    raw_a = engine.get_raw_features(tid1)
    raw_b = engine.get_raw_features(tid2)
    radar_features = [
        "danceability",
        "energy",
        "acousticness",
        "valence",
        "speechiness",
        "liveness",
        "instrumentalness",
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=[raw_a[f] for f in radar_features] + [raw_a[radar_features[0]]],
            theta=radar_features + [radar_features[0]],
            fill="toself",
            name="Track A",
            fillcolor="rgba(241, 104, 77, 0.14)",
            line=dict(color="#f1684d", width=3),
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=[raw_b[f] for f in radar_features] + [raw_b[radar_features[0]]],
            theta=radar_features + [radar_features[0]],
            fill="toself",
            name="Track B",
            fillcolor="rgba(77, 227, 187, 0.14)",
            line=dict(color="#4de3bb", width=3),
        )
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, color="#50607c", gridcolor="rgba(25, 38, 61, 0.14)"),
            angularaxis=dict(color="#50607c", gridcolor="rgba(25, 38, 61, 0.14)"),
        ),
        height=420,
        title=dict(
            text="TRACK OVERLAY",
            font=dict(family="IBM Plex Mono, monospace", size=13, color="#19263d"),
            x=0.5,
            xanchor="center",
        ),
        legend=dict(
            font=dict(family="IBM Plex Mono, monospace", size=11, color="#19263d"),
            bgcolor="rgba(255, 247, 218, 0.88)",
            bordercolor="rgba(25, 38, 61, 0.16)",
            borderwidth=2,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    comp = detail["feature_comparison"]
    bars_html = ""
    for feature in AUDIO_FEATURES:
        item = comp[feature]
        if feature == "loudness":
            bars_html += (
                f'<div class="feat-row"><div class="feat-name">{feature}</div>'
                f'<div>{item["seed"]:.1f} dB vs {item["recommended"]:.1f} dB</div>'
                f'<div class="feat-val">{item["delta"]:.3f}</div></div>'
            )
            continue
        max_v = max(abs(item["seed"]), abs(item["recommended"]), 1.0)
        if feature == "tempo":
            max_v = 200.0
        left_pct = max(0.0, item["seed"] / max_v) * 100
        right_pct = max(0.0, item["recommended"] / max_v) * 100
        bars_html += f"""
        <div class="feat-row">
            <div class="feat-name">{feature}</div>
            <div style="display:grid;gap:6px">
                <div class="feat-bar-track"><div class="feat-bar-fill" style="width:{left_pct:.1f}%;background:#f1684d"></div></div>
                <div class="feat-bar-track"><div class="feat-bar-fill" style="width:{right_pct:.1f}%;background:#4de3bb"></div></div>
            </div>
            <div class="feat-val">{item["delta"]:.3f}</div>
        </div>
        """

    st.markdown(
        terminal_window("FEATURE GAPS", bars_html, tone="paper"),
        unsafe_allow_html=True,
    )

    top_features = "".join(
        f'<span class="context-chip">{feature}</span>'
        for feature in detail["top_features"]
    )
    st.markdown(
        terminal_window(
            "KEY MATCH SIGNALS",
            f'<div class="context-grid">{top_features}</div>',
            tone="paper",
        ),
        unsafe_allow_html=True,
    )
