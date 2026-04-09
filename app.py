"""
app.py — Point d'entrée du dashboard Human Risk Analytics.

Pourquoi Moi ? — Modélisation quantitative de mon profil quelque peu "atypique".
Application des concepts de Market Risk (VaR, Stress Tests, Greeks, Capture Ratios)
à des métriques personnelles modélisées comme des actifs financiers.

Lancement : streamlit run app.py
"""

import streamlit as st
import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.generate_data import generate_all_series, compute_returns
from utils.styling import apply_streamlit_theme, COLORS
from components import overview, var_tab, stress_tab, greeks_tab, market_tab, risk_dashboard

# ── Configuration de la page ──────────────────────────────────────────
st.set_page_config(
    page_title="Pourquoi Moi ?",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Appliquer le thème ────────────────────────────────────────────────
apply_streamlit_theme()

# ── Génération des données (cache Streamlit) ──────────────────────────
@st.cache_data
def load_data():
    df = generate_all_series(seed=42)
    returns = compute_returns(df)
    return df, returns

df, returns = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: {COLORS['cyan']}; font-family: 'Courier New'; font-size: 1.6em; margin-bottom: 0;">
            HUMAN RISK<br>ANALYTICS
        </h1>
        <p style="color: {COLORS['text_muted']}; font-family: 'Courier New'; font-size: 0.8em;">
            Modélisation quantitative<br>d'un profil atypique
        </p>
        <hr style="border-color: #30363D; margin: 15px 0;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: {COLORS['bg_lighter']}; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
        <p style="color: {COLORS['cyan']}; font-family: 'Courier New'; font-size: 0.75em; margin: 0;">
            > PROFIL : Gaspard Méray<br>
            > STATUT : Candidat plus qu'original #FR<br>
            > OBJECTIF : Stage de 3 mois en tant que Market Risk Analyst<br>
            > ORIGINE : Lasson, Normandie (autrement dit from Scratch)<br>
            > BAC : 10.25/20 grâce à mon beau sourire<br>
            > NEURO : #Confidentiel on en parlera pendant l'entretien...<br>
            > ÉCOLE : Non-target
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: {COLORS['bg_card']}; padding: 12px; border-radius: 8px; border: 1px solid #30363D;">
        <p style="color: {COLORS['orange']}; font-family: 'Courier New'; font-size: 0.75em; margin: 0 0 8px 0;">
            ⚡ THÈSE
        </p>
        <p style="color: {COLORS['text']}; font-size: 0.82em; margin: 0; line-height: 1.5;">
            Un profil atypique est un actif à <b style="color: {COLORS['cyan']};">haute convexité</b> :
            les pertes sont bornées (on ne peut pas descendre plus bas qu'un village normand),
            mais le potentiel de hausse est <b style="color: {COLORS['green']};">asymétrique</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f"""
    <div style="text-align: center;">
        <p style="color: {COLORS['text_muted']}; font-size: 0.7em; font-family: 'Courier New';">
            Données synthétiques · Seed 42<br>
            504 observations · 24 mois<br>
            Built with Python & Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Navigation par onglets ────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📡 Vue d'ensemble",
    "🎯 VaR & Monte Carlo",
    "⚡ Stress Tests",
    "Δ Greeks",
    "📊 Up/Down Market",
    "🚨 Risk Dashboard",
])

with tab1:
    overview.render(df)

with tab2:
    var_tab.render(df, returns)

with tab3:
    stress_tab.render(df)

with tab4:
    greeks_tab.render(df)

with tab5:
    market_tab.render(df, returns)

with tab6:
    risk_dashboard.render(df)
