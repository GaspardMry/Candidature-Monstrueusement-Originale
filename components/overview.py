"""
overview.py — Onglet Vue d'ensemble.

Affiche les 4 séries temporelles sur un même graphique avec légende narrative,
métriques clés et interprétation du profil.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils.styling import (
    COLORS, METRIC_COLORS, METRIC_LABELS, get_plotly_layout, info_box,
)


def render(df: pd.DataFrame):
    """Rendu de l'onglet Vue d'ensemble."""

    st.markdown('<div class="terminal-header">📡 VUE D\'ENSEMBLE — Trajectoires de probabilité</div>', unsafe_allow_html=True)

    # ── Métriques résumées ────────────────────────────────────────────
    cols = st.columns(4)
    for i, col_name in enumerate(df.columns):
        with cols[i]:
            current = df[col_name].iloc[-1]
            initial = df[col_name].iloc[0]
            delta = current - initial
            st.metric(
                label=METRIC_LABELS[col_name],
                value=f"{current:.1%}",
                delta=f"{delta:+.1%} depuis le début",
            )

    st.markdown("---")

    # ── Graphique principal : 4 séries ────────────────────────────────
    fig = go.Figure(layout=get_plotly_layout(
        title="TRAJECTOIRES DE PROBABILITÉ — 24 MOIS",
        height=500,
    ))

    for col_name in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[col_name],
            name=METRIC_LABELS[col_name],
            line=dict(color=METRIC_COLORS[col_name], width=2),
            hovertemplate="%{y:.1%}<extra>" + METRIC_LABELS[col_name] + "</extra>",
        ))

    fig.update_yaxis(tickformat=".0%", title="Probabilité de succès")
    fig.update_xaxis(title="Date")

    st.plotly_chart(fig, use_container_width=True)

    # ── Encadrés narratifs ────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        info_box(
            "💡 Traduction Risk",
            "Chaque courbe représente une <b>probabilité de succès</b> modélisée comme "
            "le prix d'un actif financier. Les variations quotidiennes simulent les "
            "événements réels (certifications obtenues, refus essuyés, pics d'énergie HPI). "
            "L'ensemble forme un <b>portefeuille de risques personnels</b> analysable avec "
            "les outils classiques du Market Risk.",
            style="cyan",
        )

    with col2:
        info_box(
            "📊 Ce que ça dit de mon profil",
            f"En 24 mois, ma probabilité globale est passée de "
            f"<b>{df.iloc[0].mean():.1%}</b> à <b>{df.iloc[-1].mean():.1%}</b>. "
            f"La métrique la plus volatile est <b>TDAH/TSA/HPI</b> "
            f"(σ = {df['Probabilité_TDAH_TSA_HPI'].std():.1%}) — "
            "typique d'un profil neurodivergent avec des pics d'hyperfocus. "
            "La courbe <b>Village → Risk Analyst</b> montre la progression la plus régulière : "
            "chaque action concrète (projet, certification) crée un palier irréversible.",
            style="orange",
        )

    # ── Graphique des rendements quotidiens ───────────────────────────
    st.markdown('<div class="terminal-header">📈 RENDEMENTS QUOTIDIENS — Volatilité des trajectoires</div>', unsafe_allow_html=True)

    returns = df.pct_change().dropna().replace([np.inf, -np.inf], np.nan).ffill().fillna(0)

    fig_ret = go.Figure(layout=get_plotly_layout(
        title="RENDEMENTS QUOTIDIENS (%)",
        height=350,
    ))

    for col_name in df.columns:
        fig_ret.add_trace(go.Scatter(
            x=returns.index,
            y=returns[col_name],
            name=METRIC_LABELS[col_name],
            line=dict(color=METRIC_COLORS[col_name], width=1),
            opacity=0.7,
            hovertemplate="%{y:.2%}<extra>" + METRIC_LABELS[col_name] + "</extra>",
        ))

    fig_ret.update_yaxis(tickformat=".0%", title="Rendement quotidien")
    fig_ret.update_xaxis(title="Date")

    st.plotly_chart(fig_ret, use_container_width=True)

    # ── Tableau statistique ───────────────────────────────────────────
    st.markdown('<div class="terminal-header">📋 STATISTIQUES DESCRIPTIVES</div>', unsafe_allow_html=True)

    stats_data = []
    for col_name in df.columns:
        stats_data.append({
            "Métrique": METRIC_LABELS[col_name],
            "Valeur initiale": f"{df[col_name].iloc[0]:.1%}",
            "Valeur finale": f"{df[col_name].iloc[-1]:.1%}",
            "Min": f"{df[col_name].min():.1%}",
            "Max": f"{df[col_name].max():.1%}",
            "Moyenne": f"{df[col_name].mean():.1%}",
            "Volatilité (σ)": f"{df[col_name].std():.1%}",
            "Progression": f"{(df[col_name].iloc[-1] / df[col_name].iloc[0] - 1) * 100:+.0f}%",
        })

    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
