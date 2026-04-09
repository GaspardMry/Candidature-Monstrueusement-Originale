"""
greeks_tab.py — Onglet Greeks (Sensibilités du profil).

Affiche les graphiques de sensibilité Delta, Gamma, Vega et Theta
avec interprétation narrative pour chaque Greek.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from models.greeks import compute_all_greeks
from utils.styling import (
    COLORS, METRIC_COLORS, METRIC_LABELS, get_plotly_layout, info_box,
)


def render(df: pd.DataFrame):
    """Rendu de l'onglet Greeks."""

    st.markdown(
        '<div class="terminal-header">Δ GREEKS — Sensibilités du profil</div>',
        unsafe_allow_html=True,
    )

    info_box(
        "💡 Traduction Risk",
        "Les <b>Greeks</b> mesurent la sensibilité du prix d'une option à différents facteurs. "
        "Ici, ils mesurent comment ma probabilité de succès réagit à : "
        "<b>l'effort</b> (Delta), <b>l'accélération de l'effort</b> (Gamma), "
        "<b>la volatilité du marché</b> (Vega), et <b>le temps sans action</b> (Theta).",
        style="cyan",
    )

    # Calcul de tous les Greeks
    greeks = compute_all_greeks(df)

    # Sélecteur de métrique
    selected = st.selectbox(
        "Métrique analysée",
        options=df.columns.tolist(),
        format_func=lambda x: METRIC_LABELS[x],
        key="greeks_select",
    )
    color = METRIC_COLORS[selected]
    g = greeks[selected]
    current_prob = g["current_prob"]

    st.markdown(f"**Probabilité actuelle : {current_prob:.1%}**")

    # ── DELTA ─────────────────────────────────────────────────────────
    st.markdown('<div class="terminal-header">Δ DELTA — Sensibilité à l\'effort</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        d = g["delta"]
        fig_delta = go.Figure(layout=get_plotly_layout(title="DELTA — dP/dHeures", height=350))

        fig_delta.add_trace(go.Scatter(
            x=d["hours"], y=d["probability"],
            name="Probabilité",
            line=dict(color=color, width=2),
            yaxis="y",
        ))
        fig_delta.add_trace(go.Scatter(
            x=d["hours"], y=d["delta"],
            name="Delta (∂P/∂H)",
            line=dict(color=COLORS["orange"], width=2, dash="dash"),
            yaxis="y2",
        ))

        fig_delta.update_layout(
            yaxis=dict(title="Probabilité", tickformat=".0%", side="left"),
            yaxis2=dict(
                title="Delta", overlaying="y", side="right",
                showgrid=False, tickformat=".4f",
            ),
        )
        fig_delta.update_xaxis(title="Heures de travail / semaine")
        st.plotly_chart(fig_delta, use_container_width=True)

    with col2:
        # Trouver le point de delta maximal
        max_delta_idx = np.argmax(d["delta"])
        optimal_hours = d["hours"][max_delta_idx]

        info_box(
            "📊 Interprétation",
            f"Le <b>Delta maximal</b> est atteint à <b>{optimal_hours:.0f}h/semaine</b>. "
            f"C'est le point d'effort optimal — chaque heure supplémentaire a le plus d'impact. "
            f"Au-delà, les rendements diminuent (fatigue, burnout). "
            f"En deçà, l'effort est insuffisant pour franchir les seuils critiques.",
            style="cyan",
        )

    # ── GAMMA ─────────────────────────────────────────────────────────
    st.markdown('<div class="terminal-header">Γ GAMMA — Accélération (Effet HPI)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        gm = g["gamma"]
        fig_gamma = go.Figure(layout=get_plotly_layout(title="GAMMA — d²P/dH²", height=350))

        fig_gamma.add_trace(go.Scatter(
            x=gm["hours"], y=gm["gamma"],
            name="Gamma",
            line=dict(color=COLORS["purple"], width=2),
            fill="tozeroy",
            fillcolor="rgba(168, 85, 247, 0.15)",
        ))

        fig_gamma.add_hline(y=0, line_color=COLORS["text_muted"], line_dash="dot")
        fig_gamma.update_xaxis(title="Heures de travail / semaine")
        fig_gamma.update_yaxis(title="Gamma (accélération)")
        st.plotly_chart(fig_gamma, use_container_width=True)

    with col2:
        # Zone de gamma positif = accélération
        gamma_pos = gm["gamma"] > 0
        zone_start = gm["hours"][gamma_pos][0] if gamma_pos.any() else 0
        zone_end = gm["hours"][gamma_pos][-1] if gamma_pos.any() else 0

        info_box(
            "📊 Interprétation",
            f"Le Gamma est positif entre <b>{zone_start:.0f}h</b> et <b>{zone_end:.0f}h</b> : "
            f"c'est la <b>zone d'accélération HPI</b>. "
            f"Dans cette plage, chaque heure supplémentaire a un impact croissant — "
            f"c'est l'effet hyperfocus. Quand le Gamma devient négatif, "
            f"les rendements décélèrent (saturation).",
            style="purple",
        )

    # ── VEGA ──────────────────────────────────────────────────────────
    st.markdown('<div class="terminal-header">ν VEGA — Sensibilité à la volatilité du marché</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        v = g["vega"]
        fig_vega = go.Figure(layout=get_plotly_layout(title="VEGA — dP/dσ(marché)", height=350))

        fig_vega.add_trace(go.Scatter(
            x=v["volatility"], y=v["probability"],
            name="Probabilité",
            line=dict(color=color, width=2),
            yaxis="y",
        ))
        fig_vega.add_trace(go.Scatter(
            x=v["volatility"], y=v["vega"],
            name="Vega (∂P/∂σ)",
            line=dict(color=COLORS["green"], width=2, dash="dash"),
            yaxis="y2",
        ))

        fig_vega.update_layout(
            yaxis=dict(title="Probabilité", tickformat=".0%", side="left"),
            yaxis2=dict(
                title="Vega", overlaying="y", side="right",
                showgrid=False, tickformat=".4f",
            ),
        )
        fig_vega.update_xaxis(title="Volatilité du marché (offres de stage)")
        st.plotly_chart(fig_vega, use_container_width=True)

    with col2:
        info_box(
            "📊 Interprétation",
            "Le <b>Vega positif</b> est la signature d'un profil atypique : "
            "quand le marché devient chaotique (restructurations, nouvelles régulations), "
            "les profils conventionnels se figent, mais un profil agile et neurodivergent "
            "<b>prospère dans l'incertitude</b>. "
            "C'est un avantage compétitif asymétrique — l'antifragilité de Taleb appliquée.",
            style="green",
        )

    # ── THETA ─────────────────────────────────────────────────────────
    st.markdown('<div class="terminal-header">Θ THETA — Le coût de l\'inaction</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        th = g["theta"]
        fig_theta = go.Figure(layout=get_plotly_layout(title="THETA — Décroissance temporelle", height=350))

        fig_theta.add_trace(go.Scatter(
            x=th["days"], y=th["probability"],
            name="Probabilité résiduelle",
            line=dict(color=COLORS["red"], width=2),
            fill="tozeroy",
            fillcolor="rgba(255, 71, 87, 0.15)",
        ))

        # Ligne de la demi-vie
        fig_theta.add_vline(
            x=60, line_dash="dash", line_color=COLORS["yellow"],
            annotation_text="Demi-vie (60j)",
            annotation_font_color=COLORS["yellow"],
        )

        fig_theta.update_xaxis(title="Jours d'inaction")
        fig_theta.update_yaxis(tickformat=".0%", title="Probabilité résiduelle")
        st.plotly_chart(fig_theta, use_container_width=True)

    with col2:
        half_prob = current_prob * 0.5
        info_box(
            "📊 Interprétation",
            f"Sans action pendant <b>60 jours</b>, ma probabilité de succès chute de moitié "
            f"(de {current_prob:.1%} à {half_prob:.1%}). "
            f"Après 180 jours d'inaction, il ne reste que <b>{current_prob * np.exp(-np.log(2) / 60 * 180):.1%}</b>. "
            f"C'est le <b>Theta négatif</b> — comme une option qui perd de la valeur chaque jour. "
            f"Le message est clair : <b>chaque jour compte</b>.",
            style="red",
        )

    # ── Résumé des Greeks ─────────────────────────────────────────────
    st.markdown("---")
    info_box(
        "📊 Ce que les Greeks disent de mon profil",
        "<b>Delta élevé</b> → l'effort paie, et je le sais. "
        "<b>Gamma positif (zone HPI)</b> → l'accélération est intégrée, pas linéaire. "
        "<b>Vega positif</b> → je suis antifragile face à l'incertitude du marché. "
        "<b>Theta négatif</b> → je ne peux pas me permettre l'inaction. "
        "Ce profil de sensibilités est celui d'un <b>call option deep out-of-the-money</b> "
        "avec un potentiel de hausse asymétrique — exactement ce qu'un risk manager cherche à identifier.",
        style="orange",
    )
