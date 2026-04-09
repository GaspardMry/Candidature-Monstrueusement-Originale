"""
styling.py — Thème visuel et configuration Plotly/Streamlit.

Palette inspirée Bloomberg : fond sombre, accents électriques.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# ── Palette de couleurs ──────────────────────────────────────────────
COLORS = {
    "bg": "#0D1117",
    "bg_card": "#161B22",
    "bg_lighter": "#1C2333",
    "text": "#E6EDF3",
    "text_muted": "#8B949E",
    "cyan": "#00D4FF",
    "orange": "#FF6B35",
    "green": "#39FF14",
    "red": "#FF4757",
    "purple": "#A855F7",
    "yellow": "#FBBF24",
    "white": "#FFFFFF",
}

# Couleurs associées à chaque métrique
METRIC_COLORS = {
    "Probabilité_Village": COLORS["cyan"],
    "Probabilité_BAC_1025": COLORS["orange"],
    "Probabilité_TDAH_TSA_HPI": COLORS["purple"],
    "Probabilité_Ecole_NonTarget": COLORS["green"],
}

METRIC_LABELS = {
    "Probabilité_Village": "Village → Risk Analyst",
    "Probabilité_BAC_1025": "BAC 10.25 → Finance",
    "Probabilité_TDAH_TSA_HPI": "Neurodivergent → Performance",
    "Probabilité_Ecole_NonTarget": "Non-Target → Stage Risk",
}


def apply_streamlit_theme():
    """Applique le thème sombre personnalisé via CSS."""
    st.markdown(f"""
    <style>
        /* Fond principal */
        .stApp {{
            background-color: {COLORS["bg"]};
            color: {COLORS["text"]};
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: {COLORS["bg_card"]};
            border-right: 1px solid #30363D;
        }}

        /* Titres */
        h1, h2, h3 {{
            color: {COLORS["cyan"]} !important;
            font-family: 'Courier New', monospace;
        }}

        /* Métriques */
        [data-testid="stMetric"] {{
            background-color: {COLORS["bg_card"]};
            border: 1px solid #30363D;
            border-radius: 8px;
            padding: 12px;
        }}
        [data-testid="stMetricValue"] {{
            font-family: 'Courier New', monospace;
            color: {COLORS["cyan"]};
        }}
        [data-testid="stMetricLabel"] {{
            color: {COLORS["text_muted"]};
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background-color: {COLORS["bg_card"]};
            border-radius: 8px;
            padding: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {COLORS["text_muted"]};
            border-radius: 6px;
            font-family: 'Courier New', monospace;
        }}
        .stTabs [aria-selected="true"] {{
            color: {COLORS["cyan"]} !important;
            background-color: {COLORS["bg_lighter"]} !important;
        }}

        /* Boîtes d'info personnalisées */
        .risk-box {{
            background-color: {COLORS["bg_card"]};
            border-left: 4px solid {COLORS["cyan"]};
            padding: 16px;
            border-radius: 0 8px 8px 0;
            margin: 12px 0;
            font-size: 0.95em;
        }}
        .risk-box-orange {{
            background-color: {COLORS["bg_card"]};
            border-left: 4px solid {COLORS["orange"]};
            padding: 16px;
            border-radius: 0 8px 8px 0;
            margin: 12px 0;
            font-size: 0.95em;
        }}
        .risk-box-green {{
            background-color: {COLORS["bg_card"]};
            border-left: 4px solid {COLORS["green"]};
            padding: 16px;
            border-radius: 0 8px 8px 0;
            margin: 12px 0;
            font-size: 0.95em;
        }}
        .risk-box-red {{
            background-color: {COLORS["bg_card"]};
            border-left: 4px solid {COLORS["red"]};
            padding: 16px;
            border-radius: 0 8px 8px 0;
            margin: 12px 0;
            font-size: 0.95em;
        }}

        /* Titres de section style terminal */
        .terminal-header {{
            font-family: 'Courier New', monospace;
            color: {COLORS["cyan"]};
            font-size: 1.4em;
            border-bottom: 1px solid #30363D;
            padding-bottom: 8px;
            margin-bottom: 16px;
        }}
    </style>
    """, unsafe_allow_html=True)


def get_plotly_layout(title="", height=450):
    """Retourne un layout Plotly cohérent avec le thème."""
    return go.Layout(
        title=dict(
            text=title,
            font=dict(color=COLORS["cyan"], size=16, family="Courier New"),
            x=0.01,
        ),
        paper_bgcolor=COLORS["bg_card"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], family="Courier New", size=12),
        height=height,
        margin=dict(l=60, r=30, t=50, b=50),
        xaxis=dict(
            gridcolor="#21262D",
            zerolinecolor="#30363D",
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor="#21262D",
            zerolinecolor="#30363D",
            showgrid=True,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_muted"], size=11),
        ),
        hovermode="x unified",
    )


def info_box(title, content, style="cyan"):
    """Affiche une boîte d'information stylisée."""
    css_class = {
        "cyan": "risk-box",
        "orange": "risk-box-orange",
        "green": "risk-box-green",
        "red": "risk-box-red",
    }.get(style, "risk-box")

    st.markdown(
        f'<div class="{css_class}"><strong>{title}</strong><br>{content}</div>',
        unsafe_allow_html=True,
    )
