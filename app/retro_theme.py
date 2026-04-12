"""
SonicSense theme system
=======================
Premium product styling helpers for the Streamlit UI.
"""

from __future__ import annotations


RETRO_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap');

:root {
    --bg: #ffffff;
    --fg: #000000;
    --accent: #2962ff; /* Strong professional blue */
    --accent-light: #448aff;
    --accent-cyan: #00e5ff;
    --accent-pink: #d500f9;
    --gray: #f5f5f5;
    
    --border: 4px solid var(--fg);
    --shadow: 6px 6px 0px var(--fg);
    
    --font-body: 'Space Mono', monospace;
    --font-display: 'Press Start 2P', cursive;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--fg) !important;
    font-family: var(--font-body) !important;
    background-image: 
        linear-gradient(rgba(41, 98, 255, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(41, 98, 255, 0.1) 1px, transparent 1px) !important;
    background-size: 30px 30px !important;
    background-position: center top !important;
}

[data-testid="stHeader"] { background: transparent !important; border-bottom: none !important; }
[data-testid="stSidebar"] { display: none !important; }

.main .block-container {
    max-width: 1200px;
    margin: auto;
    padding: 24px !important;
}

h1, h2, h3, h4, div, span, p, label {
    font-family: var(--font-body) !important;
}

a { color: var(--accent) !important; }

/* Boot screen */
.boot-screen {
    min-height: 60vh;
    display: grid;
    place-items: center;
}
.boot-screen__panel {
    background-color: var(--accent);
    color: var(--bg);
    border: var(--border);
    box-shadow: var(--shadow);
    padding: 30px;
    width: min(800px, 100%);
    text-align: center;
}
.boot-screen__title {
    font-family: var(--font-display) !important;
    font-size: 20px;
    margin-bottom: 20px;
}
.boot-screen__sub {
    font-family: var(--font-display) !important;
    font-size: 32px;
    line-height: 1.5;
    margin-bottom: 20px;
}
.boot-screen__meta {
    font-size: 16px;
    font-family: var(--font-body) !important;
}
.cursor-blink { animation: blink-cursor 1s step-end infinite; }
@keyframes blink-cursor { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

/* Shell Frame */
.shell-frame {
    background-color: var(--bg);
    border: var(--border);
    box-shadow: var(--shadow);
    padding: 20px;
    margin-bottom: 30px;
}
.shell-frame__top {
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 20px;
    border-bottom: 4px solid var(--fg);
    padding-bottom: 10px;
}
.shell-frame__eyebrow {
    font-family: var(--font-body) !important;
    font-weight: 700;
    text-transform: uppercase;
}
.shell-frame__brand {
    font-family: var(--font-display) !important;
    font-size: 32px;
    margin-top: 10px;
    color: var(--accent) !important;
}
.shell-frame__meta {
    display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end;
}
.shell-frame__chip, .route-hud__chip, .desktop-intro__badge, .context-chip {
    background: var(--bg);
    border: 2px solid var(--fg);
    padding: 8px 12px;
    font-family: var(--font-display) !important;
    font-size: 10px;
    text-transform: uppercase;
    box-shadow: 2px 2px 0px var(--fg);
}
.shell-frame__marquee {
    background-color: var(--accent);
    color: var(--bg) !important;
    border: var(--border);
    padding: 10px;
    font-family: var(--font-display) !important;
    font-size: 12px;
    margin-bottom: 20px;
    text-transform: uppercase;
    white-space: nowrap;
    overflow: hidden;
}

.shell-frame__grid {
    display: grid;
    grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.75fr);
    gap: 20px;
}

/* Specific component tweaks... */
.hud-card, .desktop-window, .pixel-screen, .route-hud, .section-banner, .note-card, .stat-card, .mood-card, .stPlotlyChart {
    background-color: var(--bg) !important;
    border: var(--border) !important;
    box-shadow: var(--shadow) !important;
    border-radius: 0px !important;
}

.hud-card { padding: 20px; }
.hud-card--warm { background-color: var(--gray) !important; }

.hud-card__title, .route-hud__title, .desktop-window__title, .note-card__title, .section-banner__title, .pixel-screen__label {
    font-family: var(--font-display) !important;
    text-transform: uppercase;
}
.hud-card__title { font-size: 16px; margin-bottom: 10px; }
.hud-card__copy { font-size: 14px; margin-bottom: 20px; }
.hud-card__routes { display: flex; flex-wrap: wrap; gap: 10px; }
.hud-card__routes span {
    font-family: var(--font-display) !important;
    font-size: 10px;
    padding: 8px 12px;
    border: 2px solid var(--fg);
    background: var(--bg);
}

.hud-meter-grid { display: grid; gap: 15px; }
.hud-meter { border: 2px solid var(--fg); padding: 10px; background: var(--bg); }
.hud-meter__top { display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: 700; font-size: 14px; }
.hud-meter__track, .gauge-track, .feat-bar-track, .stat-card__accent {
    height: 16px; border: 2px solid var(--fg); background: var(--bg);
}
.hud-meter__fill, .gauge-fill, .feat-bar-fill, .stat-card__accent-fill {
    height: 100%; background: var(--accent);
}

.desktop-window__bar {
    border-bottom: var(--border);
    background: var(--accent);
    color: var(--bg);
    padding: 10px;
    display: flex; gap: 10px; align-items: center;
}
.desktop-window--navy .desktop-window__bar { background: var(--fg); }
.desktop-window--crt .desktop-window__bar { background: var(--accent-pink); }
.desktop-window__lights { display: flex; gap: 6px; }
.desktop-window__light { width: 12px; height: 12px; border: 2px solid var(--fg); background: var(--bg); }
.desktop-window__light--red { background: var(--accent-pink); }
.desktop-window__title { color: var(--bg) !important; font-size: 12px; }
.desktop-window__body { padding: 20px; font-size: 14px; color: var(--fg) !important; }

.desktop-intro__headline { font-family: var(--font-display) !important; font-size: 32px; line-height: 1.3; }
.desktop-intro__copy { margin-top: 20px; font-size: 16px; }
.desktop-intro__badges { display: flex; gap: 10px; margin-top: 20px; }

.pixel-screen { min-height: 250px; padding: 20px; background: var(--accent); border: var(--border); color: var(--bg); display: flex; flex-direction: column; justify-content: space-between; }
.pixel-screen__label { font-family: var(--font-display) !important; font-size: 12px; color: var(--bg) !important; }
.pixel-screen__headline { font-family: var(--font-display) !important; font-size: 28px; line-height: 1.3; margin-top: 15px; color: var(--bg) !important; }
.pixel-screen__list { margin-top: 20px; display: grid; gap: 10px; }
.pixel-screen__item { display: flex; justify-content: space-between; border-bottom: 2px dashed var(--fg); padding-bottom: 5px; font-weight: 700; color: var(--bg) !important;}

.section-banner { padding: 20px; background: var(--accent-cyan) !important; }
.section-banner__eyebrow { font-weight: 700; font-size: 14px; margin-bottom: 10px; }
.section-banner__title { font-size: 24px; line-height: 1.2; }
.section-banner__subtitle { font-size: 14px; margin-top: 10px; }

.route-hud { padding: 20px; }
.route-hud__top { display: flex; justify-content: space-between; margin-bottom: 20px; }
.route-hud__eyebrow { font-weight: 700; font-size: 14px; margin-bottom: 10px; }
.route-hud__title { font-size: 28px; }
.route-hud__copy { font-size: 14px; margin-top: 10px; max-width: 600px; }
.route-hud__chips { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; }
.route-hud__grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.route-hud__cell { border: 2px solid var(--fg); padding: 15px; box-shadow: 4px 4px 0 var(--fg); }
.route-hud__cell-title { font-family: var(--font-display) !important; font-size: 12px; margin-bottom: 10px; }
.route-hud__cell-copy { font-size: 14px; }

.note-card { padding: 20px; background: var(--gray) !important; }
.note-card__title { font-size: 16px; margin-bottom: 10px; }
.note-card__body { font-size: 14px; }

.stat-card { padding: 20px; }
.stat-card__value { font-family: var(--font-display) !important; font-size: 24px; line-height: 1.2; word-break: break-word;}
.stat-card__label { font-size: 14px; margin-top: 10px; font-weight: 700; }
.stat-card__accent { margin-top: 10px; }

.mood-card { text-align: center; padding: 20px; transition: transform 0.1s; cursor: default; }
.mood-card:hover { transform: translate(-2px, -2px); box-shadow: 8px 8px 0 var(--fg) !important; }
.mood-card__icon { font-family: var(--font-display) !important; font-size: 24px; margin-bottom: 15px; }
.mood-card__name { font-family: var(--font-display) !important; font-size: 16px; margin-bottom: 10px; }
.mood-card__desc { font-size: 14px; }

.equalizer { display: flex; align-items: flex-end; gap: 4px; height: 40px; }
.equalizer__bar { width: 12px; background: var(--fg); border: 2px solid var(--fg); animation: bounce 1s infinite alternate steps(4); animation-delay: calc(var(--i) * 0.1s); }
@keyframes bounce { 0% { height: 20%; } 100% { height: 100%; } }

.ticker-bar { width: 100%; overflow: hidden; border: var(--border); background: var(--accent); color: var(--bg); margin-bottom: 30px; box-shadow: var(--shadow); border-radius: 0; }
.ticker-content { display: inline-block; white-space: nowrap; padding: 10px 0; font-family: var(--font-display) !important; font-size: 14px; animation: ticker 20s linear infinite; }
@keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

.bullet-stack, .status-grid { display: grid; gap: 15px; }
.bullet-line { font-size: 14px; }
.status-line { display: flex; justify-content: space-between; border-bottom: 2px dashed var(--fg); padding-bottom: 10px; font-size: 14px; font-weight: 700;}
.status-pill { border: 2px solid var(--fg); padding: 5px 10px; font-family: var(--font-display) !important; font-size: 10px; text-transform: uppercase; box-shadow: 2px 2px 0 var(--fg); }
.status-pill--good { background: var(--accent); color: var(--bg) !important; }
.status-pill--warn { background: var(--accent-pink); color: var(--bg) !important; }

.mood-split-row { display: grid; grid-template-columns: 180px 1fr auto; gap: 20px; border: var(--border); padding: 15px; margin-bottom: 15px; background: var(--gray); box-shadow: var(--shadow);}
.mood-split-row__meta { display: grid; gap: 6px; }
.mood-split-row__title { font-family: var(--font-display) !important; font-size: 14px; }
.mood-split-row__desc { font-size: 14px; margin-top: 5px; }
.mood-split-row__value { font-family: var(--font-display) !important; font-size: 16px; align-self: center; }

.keyword-board { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.keyword-board__group { border: var(--border); padding: 15px; box-shadow: 4px 4px 0 var(--fg); background: var(--bg); }
.keyword-board__title { font-family: var(--font-display) !important; font-size: 12px; margin-bottom: 15px; }
.keyword-board__chips, .context-grid { display: flex; flex-wrap: wrap; gap: 10px; }
.expl-chip { border: 2px solid var(--fg); padding: 8px 12px; font-size: 12px; font-weight: 700; box-shadow: 2px 2px 0 var(--fg); background: var(--gray); display: block; margin: 8px 0;}

.gauge-row { margin: 15px 0; }
.gauge-label { font-family: var(--font-display) !important; font-size: 10px; margin-bottom: 5px; }
.gauge-num, .feat-val { font-family: var(--font-body) !important; font-size: 14px; font-weight: 700; text-align: right; margin-top: 5px; }

.sonic-table-wrap { overflow-x: auto; border: var(--border); box-shadow: var(--shadow); background: var(--bg); }
.sonic-table { width: 100%; border-collapse: collapse; font-family: var(--font-body) !important; font-size: 13px; }
.sonic-table th { border-bottom: 4px solid var(--fg); padding: 15px; text-align: left; font-family: var(--font-display) !important; font-size: 10px; text-transform: uppercase; background: var(--gray); }
.sonic-table td { border-bottom: 2px solid var(--fg); padding: 15px; }

.feat-row { display: grid; grid-template-columns: 140px 1fr auto; gap: 15px; align-items: center; margin: 15px 0; }
.feat-name { font-weight: 700; font-size: 14px; }
.feat-val { font-weight: 700; font-size: 14px; }

.status-dot { display: inline-block; width: 12px; height: 12px; background: var(--accent); border: 2px solid var(--fg); box-shadow: 2px 2px 0 var(--fg); border-radius: 0; }

/* Inputs and Buttons */
.stButton > button {
    border: var(--border) !important; box-shadow: var(--shadow) !important; border-radius: 0 !important; background: var(--accent) !important; color: var(--bg) !important; font-family: var(--font-display) !important; font-size: 12px !important; text-transform: uppercase; padding: 15px !important; transition: transform 0.1s; width: auto; min-width: 176px;
}
.stButton > button:hover { transform: translate(-2px, -2px); box-shadow: 8px 8px 0 var(--fg) !important; border: var(--border) !important;}
.stButton > button:active { transform: translate(2px, 2px); box-shadow: 2px 2px 0 var(--fg) !important; border: var(--border) !important;}

.stTextInput input, .stNumberInput input, [data-baseweb="select"] > div, .stSelectbox > div > div {
    border: var(--border) !important; border-radius: 0 !important; box-shadow: 4px 4px 0 var(--fg) !important; background: var(--bg) !important; color: var(--fg) !important; font-weight: 700; font-size: 14px !important; padding: 10px !important; min-height: 50px !important;
}
[data-baseweb="menu"] { border: var(--border) !important; border-radius: 0 !important; box-shadow: 6px 6px 0 var(--fg) !important; background: var(--bg) !important; }
[data-baseweb="menu"] li { color: var(--fg) !important; font-weight: 700; }

.stSlider label, .stTextInput label, .stSelectbox label, .stNumberInput label, .stRadio label { font-family: var(--font-display) !important; font-size: 10px !important; text-transform: uppercase; color: var(--fg) !important; letter-spacing: 0.06em; margin-bottom: 8px; }
.stSlider [role="slider"] { width: 20px !important; height: 20px !important; border: var(--border) !important; border-radius: 0 !important; background: var(--accent) !important; box-shadow: 4px 4px 0 var(--fg) !important;}
.stSlider [data-baseweb="slider"] > div > div { background: var(--fg) !important; height: 8px !important; }
.stSlider [data-baseweb="slider"] > div > div > div { background: var(--accent) !important; }

.stRadio > div { gap: 15px !important; }
.stRadio [role="radiogroup"] { gap: 15px !important; flex-wrap: wrap !important; }
.stRadio [role="radiogroup"] > label { border: 2px solid var(--fg) !important; box-shadow: 4px 4px 0 var(--fg) !important; border-radius: 0 !important; background: var(--bg) !important; padding: 10px 15px !important; min-height: 52px; flex: 1 1 auto !important; justify-content: center !important;}
.stRadio [role="radiogroup"] > label div, .stRadio [role="radiogroup"] > label span { font-weight: 700; color: var(--fg) !important; font-size: 14px !important; }
.stRadio [role="radiogroup"] > label[data-checked="true"], .stRadio [role="radiogroup"] > label:has(input:checked) { background: var(--accent) !important; border-color: var(--fg) !important;}
.stRadio [role="radiogroup"] > label[data-checked="true"] p, .stRadio [role="radiogroup"] > label:has(input:checked) p { color: var(--bg) !important; }

.streamlit-expanderHeader, details summary { border: var(--border) !important; border-radius: 0 !important; box-shadow: 4px 4px 0 var(--fg) !important; background: var(--gray) !important; color: var(--fg) !important; font-weight: 700; font-size: 14px !important; margin-bottom: 20px;}
.streamlit-expanderContent { border: var(--border) !important; border-top: none !important; padding: 20px !important; background: var(--bg) !important; }

.stAlert, [data-testid="stAlert"] { border: var(--border) !important; border-radius: 0 !important; box-shadow: var(--shadow) !important; background: var(--accent-cyan) !important; color: var(--fg) !important; font-weight: 700; }
[data-testid="stMetricValue"] { font-family: var(--font-display) !important; color: var(--fg) !important; font-size: 24px !important; }
[data-testid="stMetricLabel"] { font-weight: 700; color: var(--fg) !important; }

.stPlotlyChart { padding: 10px; background: rgba(0,0,0,0.02); }

.footer-note { border: var(--border); padding: 20px; text-align: center; font-weight: 700; text-transform: uppercase; font-family: var(--font-display) !important; font-size: 10px; background: var(--bg); box-shadow: var(--shadow); margin-top: 40px; color: var(--fg) !important;}

@media (max-width: 980px) {
    .shell-frame__top, .shell-frame__grid, .route-hud__top, .route-hud__grid, .mood-split-row { grid-template-columns: 1fr; display: grid; }
    .shell-frame__meta, .route-hud__chips { justify-content: flex-start; }
    .main .block-container { padding: 14px; margin: 10px; }
}
@media (max-width: 720px) {
    .desktop-intro__headline { font-size: 24px; }
    .pixel-screen__headline { font-size: 24px; }
    .section-banner__title { font-size: 20px; }
}
</style>
"""


PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Mono, monospace", color="#000000", size=12),
    xaxis=dict(
        gridcolor="#000000",
        zerolinecolor="#000000",
        color="#000000",
        tickfont=dict(family="Space Mono", size=10, color="#000000", weight="bold"),
    ),
    yaxis=dict(
        gridcolor="#000000",
        zerolinecolor="#000000",
        color="#000000",
        tickfont=dict(family="Space Mono", size=10, color="#000000", weight="bold"),
    ),
    colorway=["#2962ff", "#00e5ff", "#d500f9", "#000000", "#448aff", "#e0e0e0"],
    margin=dict(l=38, r=20, t=54, b=40),
)


MOOD_HEX = {
    "Chill": "#00e5ff",
    "Energetic": "#2962ff",
    "Romantic": "#d500f9",
    "Melancholic": "#000000",
    "Focus": "#448aff",
}

MOOD_ICONS = {
    "Chill": "Chill",
    "Energetic": "Boost",
    "Romantic": "Glow",
    "Melancholic": "Haze",
    "Focus": "Deep",
}

MOOD_DESCS = {
    "Chill": "Warm, easy, low-friction listening",
    "Energetic": "Fast, bright, high-momentum tracks",
    "Romantic": "Soft edges, warmth, and intimacy",
    "Melancholic": "Late-night emotion and introspection",
    "Focus": "Steady flow with minimal distraction",
}


def equalizer_html(n_bars: int = 20, size: str = "normal") -> str:
    """Decorative waveform bars."""
    cls = "equalizer"
    if size == "small":
        cls += " equalizer--small"
    bars = "".join(
        f'<span class="equalizer__bar" style="--i:{i};height:{10 + (i % 8) * 4}px"></span>'
        for i in range(n_bars)
    )
    return f'<div class="{cls}">{bars}</div>'


def desktop_shell(hero_html: str, monitor_html: str) -> str:
    """Top hero split shell."""
    return f"""
    <section class="shell-frame">
        <div class="shell-frame__grid">
            {hero_html}
            {monitor_html}
        </div>
    </section>
    """


def desktop_intro(title: str, subtitle: str, badges: list[str] | None = None) -> str:
    """Hero intro panel."""
    badges_html = ""
    if badges:
        badges_html = '<div class="desktop-intro__badges">' + "".join(
            f'<span class="desktop-intro__badge">{badge}</span>' for badge in badges
        ) + "</div>"
    body = f"""
    <div class="desktop-intro__headline">{title}</div>
    <div class="desktop-intro__copy">{subtitle}</div>
    {badges_html}
    """
    return terminal_window("SonicSense", body, tone="crt")


def crt_monitor(title: str, headline: str, items: list[tuple[str, str]]) -> str:
    """Highlight panel."""
    rows = "".join(
        f'<div class="pixel-screen__item"><span>{left}</span><span>{right}</span></div>'
        for left, right in items
    )
    body = f"""
    <div class="pixel-screen">
        <div class="pixel-screen__label">{title}</div>
        <div class="pixel-screen__headline">{headline}</div>
    </div>
    <div class="pixel-screen__list">{rows}</div>
    """
    return terminal_window("Live Discovery", body, tone="navy")


def section_banner(icon: str, title: str, subtitle: str = "", eyebrow: str = "") -> str:
    """Section heading."""
    eyebrow_html = f'<div class="section-banner__eyebrow">{eyebrow}</div>' if eyebrow else ""
    subtitle_html = f'<div class="section-banner__subtitle">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="section-banner">
        {eyebrow_html}
        <div class="section-banner__title">{icon} {title}</div>
        {subtitle_html}
    </div>
    """


def terminal_window(title: str, body_html: str, tone: str = "paper") -> str:
    """Panel wrapper."""
    tone_map = {
        "paper": "desktop-window desktop-window--paper",
        "navy": "desktop-window desktop-window--navy",
        "crt": "desktop-window desktop-window--crt",
    }
    cls = tone_map.get(tone, "desktop-window desktop-window--paper")
    return f"""
    <section class="{cls}">
        <div class="desktop-window__bar">
            <div class="desktop-window__lights">
                <span class="desktop-window__light desktop-window__light--red"></span>
                <span class="desktop-window__light desktop-window__light--gold"></span>
                <span class="desktop-window__light desktop-window__light--teal"></span>
            </div>
            <div class="desktop-window__title">{title}</div>
        </div>
        <div class="desktop-window__body">{body_html}</div>
    </section>
    """


def route_hud(title: str, eyebrow: str, copy: str, chips: list[str], cells: list[tuple[str, str]]) -> str:
    """Page-specific product HUD."""
    chips_html = "".join(f'<span class="route-hud__chip">{chip}</span>' for chip in chips)
    cells_html = "".join(
        f"""
        <div class="route-hud__cell">
            <div class="route-hud__cell-title">{cell_title}</div>
            <div class="route-hud__cell-copy">{cell_copy}</div>
        </div>
        """
        for cell_title, cell_copy in cells
    )
    return f"""
    <section class="route-hud">
        <div class="route-hud__top">
            <div>
                <div class="route-hud__eyebrow">{eyebrow}</div>
                <div class="route-hud__title">{title}</div>
                <div class="route-hud__copy">{copy}</div>
            </div>
            <div class="route-hud__chips">{chips_html}</div>
        </div>
        <div class="route-hud__grid">{cells_html}</div>
    </section>
    """


def paper_note(title: str, body_html: str) -> str:
    """Light note card."""
    return f"""
    <section class="note-card">
        <div class="note-card__title">{title}</div>
        <div class="note-card__body">{body_html}</div>
    </section>
    """


def stat_box(label: str, value: str, accent: str = "#2962ff") -> str:
    """Small metric card."""
    return f"""
    <div class="stat-card">
        <div class="stat-card__value">{value}</div>
        <div class="stat-card__label">{label}</div>
        <div class="stat-card__accent">
            <div class="stat-card__accent-fill" style="width:72%;background:{accent}"></div>
        </div>
    </div>
    """


def gauge_bar(label: str, value: float, max_val: float = 1.0) -> str:
    """Metric gauge."""
    pct = min(100.0, max(0.0, (value / max_val) * 100 if max_val else 0.0))
    return f"""
    <div class="gauge-row">
        <div class="gauge-label">{label}</div>
        <div class="gauge-track"><div class="gauge-fill" style="width:{pct:.1f}%"></div></div>
        <div class="gauge-num">{value:.4f}</div>
    </div>
    """


def retro_table_html(df, max_rows: int = 20) -> str:
    """Render a dataframe as a styled table."""
    cols = list(df.columns)
    hdr = "".join(f"<th>{col}</th>" for col in cols)
    rows = []
    for _, row in df.head(max_rows).iterrows():
        cells = []
        for col in cols:
            value = row[col]
            if isinstance(value, float):
                value = f"{value:.4f}" if abs(value) < 100 else f"{value:.1f}"
            cells.append(f"<td>{value}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return (
        '<div class="sonic-table-wrap"><table class="sonic-table">'
        f"<thead><tr>{hdr}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def feature_bar_html(name: str, value: float, max_val: float = 1.0) -> str:
    """Feature bar helper."""
    pct = min(100.0, max(0.0, (value / max_val) * 100 if max_val else 0.0))
    return f"""
    <div class="feat-row">
        <div class="feat-name">{name}</div>
        <div class="feat-bar-track"><div class="feat-bar-fill" style="width:{pct:.1f}%"></div></div>
        <div class="feat-val">{value:.3f}</div>
    </div>
    """
