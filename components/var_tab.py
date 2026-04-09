"""
var_tab.py — Onglet VaR & Monte Carlo.

Affiche les distributions de rendements, les VaR par 3 méthodes,
les cônes de confiance et les simulations Monte Carlo.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from models.var import compute_var_all_methods, compute_confidence_cone
from utils.styling import (
    COLORS, METRIC_COLORS, METRIC_LABELS, get_plotly_layout, info_box,
)


def render(df: pd.DataFrame, returns: pd.DataFrame):
    """Rendu de l'onglet VaR & Monte Carlo."""

    st.markdown(
        '<div class="terminal-header">🎯 VALUE AT RISK — "Risk of Giving Up"</div>',
        unsafe_allow_html=True,
    )

    info_box(
        "💡 Traduction Risk",
        "La <b>Value at Risk (VaR)</b> mesure la perte maximale attendue sur un horizon donné "
        "à un niveau de confiance. Ici, elle répond à la question : "
        "<i>\"À 95% de confiance, de combien ma probabilité de succès peut-elle chuter "
        "sur les 30 prochains jours ?\"</i> — C'est le <b>risque d'abandon</b> quantifié.",
        style="cyan",
    )

    # ── Paramètres ────────────────────────────────────────────────────
    col_param1, col_param2 = st.columns(2)
    with col_param1:
        confidence = st.slider("Niveau de confiance", 0.90, 0.99, 0.95, 0.01)
    with col_param2:
        horizon = st.slider("Horizon (jours)", 5, 60, 30, 5)

    # ── Calcul VaR pour chaque métrique ───────────────────────────────
    var_results = {}
    for col_name in df.columns:
        var_results[col_name] = compute_var_all_methods(
            returns[col_name], confidence, horizon
        )

    # ── Tableau comparatif VaR ────────────────────────────────────────
    st.markdown('<div class="terminal-header">📊 COMPARAISON DES 3 MÉTHODES</div>', unsafe_allow_html=True)

    var_table = []
    for col_name in df.columns:
        vr = var_results[col_name]
        current = df[col_name].iloc[-1]
        var_table.append({
            "Métrique": METRIC_LABELS[col_name],
            "Prob. actuelle": f"{current:.1%}",
            "VaR Historique": f"{vr['historique']:.2%}",
            "VaR Paramétrique": f"{vr['parametrique']:.2%}",
            "VaR Monte Carlo": f"{vr['monte_carlo']:.2%}",
            f"Plancher ({confidence:.0%})": f"{max(current + vr['monte_carlo'], 0):.1%}",
        })

    st.dataframe(pd.DataFrame(var_table), use_container_width=True, hide_index=True)

    info_box(
        "📊 Ce que ça dit de mon profil",
        f"À <b>{confidence:.0%}</b> de confiance sur <b>{horizon} jours</b>, "
        "même dans le pire des cas raisonnable, aucune de mes probabilités ne tombe à zéro. "
        "La métrique la plus risquée est <b>TDAH/TSA/HPI</b> (VaR la plus large), "
        "ce qui reflète la volatilité naturelle d'un profil neurodivergent — "
        "mais cette même volatilité génère les plus hauts pics de performance.",
        style="orange",
    )

    st.markdown("---")

    # ── Sélecteur de métrique pour détail ─────────────────────────────
    selected = st.selectbox(
        "Détail par métrique",
        options=df.columns.tolist(),
        format_func=lambda x: METRIC_LABELS[x],
    )
    color = METRIC_COLORS[selected]
    vr = var_results[selected]

    col1, col2 = st.columns(2)

    # ── Distribution des rendements + VaR ─────────────────────────────
    with col1:
        ret_data = returns[selected].dropna()

        fig_hist = go.Figure(layout=get_plotly_layout(
            title=f"DISTRIBUTION DES RENDEMENTS — {METRIC_LABELS[selected]}",
            height=400,
        ))

        fig_hist.add_trace(go.Histogram(
            x=ret_data,
            nbinsx=50,
            marker_color=color,
            opacity=0.7,
            name="Rendements",
        ))

        # Lignes VaR
        for method, val, dash in [
            ("Historique", vr["historique"] / np.sqrt(horizon), "solid"),
            ("Paramétrique", vr["parametrique"] / np.sqrt(horizon), "dash"),
            ("Monte Carlo", vr["monte_carlo"] / np.sqrt(horizon), "dot"),
        ]:
            fig_hist.add_vline(
                x=val,
                line_dash=dash,
                line_color=COLORS["red"],
                annotation_text=f"VaR {method}",
                annotation_font_color=COLORS["red"],
            )

        fig_hist.update_xaxis(tickformat=".1%", title="Rendement quotidien")
        fig_hist.update_yaxis(title="Fréquence")
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── Simulations Monte Carlo ───────────────────────────────────────
    with col2:
        sims = vr["simulations"]

        fig_mc = go.Figure(layout=get_plotly_layout(
            title=f"SIMULATIONS MONTE CARLO (1000 trajectoires)",
            height=400,
        ))

        # Afficher un échantillon de trajectoires
        for i in range(min(100, sims.shape[0])):
            fig_mc.add_trace(go.Scatter(
                x=list(range(horizon)),
                y=sims[i],
                mode="lines",
                line=dict(color=color, width=0.3),
                opacity=0.15,
                showlegend=False,
                hoverinfo="skip",
            ))

        # Percentiles
        p5 = np.percentile(sims, 5, axis=0)
        p50 = np.percentile(sims, 50, axis=0)
        p95 = np.percentile(sims, 95, axis=0)

        fig_mc.add_trace(go.Scatter(
            x=list(range(horizon)), y=p5,
            line=dict(color=COLORS["red"], dash="dash"),
            name="5e percentile",
        ))
        fig_mc.add_trace(go.Scatter(
            x=list(range(horizon)), y=p50,
            line=dict(color=COLORS["white"], width=2),
            name="Médiane",
        ))
        fig_mc.add_trace(go.Scatter(
            x=list(range(horizon)), y=p95,
            line=dict(color=COLORS["green"], dash="dash"),
            name="95e percentile",
        ))

        fig_mc.update_xaxis(title="Jours")
        fig_mc.update_yaxis(tickformat=".2%", title="Rendement cumulé")
        st.plotly_chart(fig_mc, use_container_width=True)

    # ── Cône de confiance ─────────────────────────────────────────────
    st.markdown('<div class="terminal-header">🔮 CÔNE DE CONFIANCE — Projection à 60 jours</div>', unsafe_allow_html=True)

    cone = compute_confidence_cone(
        df[selected].iloc[-1], returns[selected], horizon=60
    )

    future_dates = pd.bdate_range(
        start=df.index[-1] + pd.Timedelta(days=1), periods=60, freq="B"
    )

    fig_cone = go.Figure(layout=get_plotly_layout(
        title=f"PROJECTION — {METRIC_LABELS[selected]}",
        height=420,
    ))

    # Historique
    fig_cone.add_trace(go.Scatter(
        x=df.index[-60:], y=df[selected].iloc[-60:],
        line=dict(color=color, width=2),
        name="Historique",
    ))

    # Cône
    fig_cone.add_trace(go.Scatter(
        x=future_dates, y=cone["p95"],
        line=dict(color=COLORS["green"], width=0),
        showlegend=False,
        hoverinfo="skip",
    ))
    fig_cone.add_trace(go.Scatter(
        x=future_dates, y=cone["p5"],
        fill="tonexty",
        fillcolor="rgba(0, 212, 255, 0.1)",
        line=dict(color=COLORS["red"], width=0),
        name="Intervalle 90%",
    ))
    fig_cone.add_trace(go.Scatter(
        x=future_dates, y=cone["p75"],
        line=dict(color=color, width=0),
        showlegend=False,
        hoverinfo="skip",
    ))
    fig_cone.add_trace(go.Scatter(
        x=future_dates, y=cone["p25"],
        fill="tonexty",
        fillcolor="rgba(0, 212, 255, 0.2)",
        line=dict(color=color, width=0),
        name="Intervalle 50%",
    ))
    fig_cone.add_trace(go.Scatter(
        x=future_dates, y=cone["p50"],
        line=dict(color=COLORS["white"], width=2, dash="dash"),
        name="Médiane projetée",
    ))

    fig_cone.update_yaxis(tickformat=".0%", title="Probabilité")
    fig_cone.update_xaxis(title="Date")
    st.plotly_chart(fig_cone, use_container_width=True)
