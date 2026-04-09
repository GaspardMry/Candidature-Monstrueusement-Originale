"""
market_tab.py — Onglet UpMarket / DownMarket.

Analyse comparative de la performance du profil atypique
dans des contextes favorables vs défavorables.
Calcule les Capture Ratios et démontre l'avantage asymétrique.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from models.updown_market import (
    generate_market_regime,
    classify_regimes,
    compute_capture_ratios,
    compute_regime_performance,
)
from data.generate_data import compute_returns
from utils.styling import (
    COLORS, METRIC_COLORS, METRIC_LABELS, get_plotly_layout, info_box,
)


def render(df: pd.DataFrame, returns: pd.DataFrame):
    """Rendu de l'onglet UpMarket / DownMarket."""

    st.markdown(
        '<div class="terminal-header">📊 UPMARKET / DOWNMARKET — Analyse asymétrique</div>',
        unsafe_allow_html=True,
    )

    info_box(
        "💡 Traduction Risk",
        "L'analyse <b>UpMarket/DownMarket</b> évalue comment un actif se comporte "
        "dans les phases haussières vs baissières du marché. "
        "Le <b>Capture Ratio</b> mesure la participation relative : "
        "un Up Capture > 100% et un Down Capture < 100% signifient un <b>avantage asymétrique</b>. "
        "Thèse : un profil résilient surperforme quand les conditions sont difficiles.",
        style="cyan",
    )

    # ── Génération du régime de marché ────────────────────────────────
    market = generate_market_regime(n_days=len(df))
    market.index = df.index
    regimes = classify_regimes(market)

    # ── Graphique du régime de marché ─────────────────────────────────
    st.markdown('<div class="terminal-header">🌡️ RÉGIME DU MARCHÉ DU RECRUTEMENT</div>', unsafe_allow_html=True)

    fig_market = go.Figure(layout=get_plotly_layout(
        title="INDICE DU MARCHÉ DU RECRUTEMENT QUANT",
        height=300,
    ))

    # Colorier UpMarket en vert, DownMarket en rouge
    up_vals = market.where(market > 0)
    down_vals = market.where(market <= 0)

    fig_market.add_trace(go.Scatter(
        x=market.index, y=up_vals,
        fill="tozeroy",
        fillcolor="rgba(57, 255, 20, 0.2)",
        line=dict(color=COLORS["green"], width=1),
        name=f"UpMarket ({regimes['pct_up']:.0f}% des jours)",
    ))
    fig_market.add_trace(go.Scatter(
        x=market.index, y=down_vals,
        fill="tozeroy",
        fillcolor="rgba(255, 71, 87, 0.2)",
        line=dict(color=COLORS["red"], width=1),
        name=f"DownMarket ({regimes['pct_down']:.0f}% des jours)",
    ))

    fig_market.add_hline(y=0, line_color=COLORS["text_muted"], line_width=1)
    fig_market.update_yaxis(title="Indice de marché")
    fig_market.update_xaxis(title="Date")

    st.plotly_chart(fig_market, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Jours UpMarket", f"{regimes['n_up_days']} ({regimes['pct_up']:.0f}%)")
    with col2:
        st.metric("Jours DownMarket", f"{regimes['n_down_days']} ({regimes['pct_down']:.0f}%)")

    st.markdown("---")

    # ── Capture Ratios ────────────────────────────────────────────────
    st.markdown('<div class="terminal-header">🎯 CAPTURE RATIOS</div>', unsafe_allow_html=True)

    capture_df = compute_capture_ratios(returns, market)

    # Graphique des capture ratios
    fig_capture = go.Figure(layout=get_plotly_layout(
        title="CAPTURE RATIOS PAR MÉTRIQUE",
        height=400,
    ))

    labels = [METRIC_LABELS[m] for m in capture_df["Métrique"]]

    fig_capture.add_trace(go.Bar(
        x=labels,
        y=capture_df["Up Capture"] * 100,
        name="Up Capture (%)",
        marker_color=COLORS["green"],
        text=[f"{v:.0f}%" for v in capture_df["Up Capture"] * 100],
        textposition="outside",
    ))
    fig_capture.add_trace(go.Bar(
        x=labels,
        y=capture_df["Down Capture"] * 100,
        name="Down Capture (%)",
        marker_color=COLORS["red"],
        text=[f"{v:.0f}%" for v in capture_df["Down Capture"] * 100],
        textposition="outside",
    ))

    fig_capture.add_hline(y=100, line_dash="dash", line_color=COLORS["text_muted"],
                          annotation_text="100% (neutre)")
    fig_capture.update_layout(barmode="group")
    fig_capture.update_yaxis(title="Capture Ratio (%)")

    st.plotly_chart(fig_capture, use_container_width=True)

    # Tableau détaillé
    display_df = capture_df.copy()
    display_df["Métrique"] = [METRIC_LABELS[m] for m in display_df["Métrique"]]
    display_df["Up Capture"] = display_df["Up Capture"].apply(lambda x: f"{x:.1%}")
    display_df["Down Capture"] = display_df["Down Capture"].apply(lambda x: f"{x:.1%}")
    display_df["Asymmetry Ratio"] = display_df["Asymmetry Ratio"].apply(
        lambda x: f"{x:.2f}" if x != float("inf") else "∞"
    )
    display_df["Rendement moyen (Up)"] = display_df["Rendement moyen (Up)"].apply(lambda x: f"{x:.4%}")
    display_df["Rendement moyen (Down)"] = display_df["Rendement moyen (Down)"].apply(lambda x: f"{x:.4%}")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    info_box(
        "📊 Ce que ça dit de mon profil",
        "Un <b>Asymmetry Ratio > 1</b> signifie que le profil capte davantage "
        "de hausse qu'il ne subit de baisse — c'est la <b>convexité positive</b>. "
        "La métrique <b>TDAH/TSA/HPI</b> devrait afficher le ratio le plus élevé : "
        "en période de crise, un profil neurodivergent <b>ne se fige pas</b>, il adapte. "
        "C'est l'avantage asymétrique de la résilience — le même mécanisme "
        "qui fait qu'un hedge fund antifragile prospère en période de volatilité.",
        style="orange",
    )

    st.markdown("---")

    # ── Performance par régime ────────────────────────────────────────
    st.markdown('<div class="terminal-header">📈 PERFORMANCE PAR RÉGIME</div>', unsafe_allow_html=True)

    perf = compute_regime_performance(df, market)

    for col_name in df.columns:
        p = perf[col_name]
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{METRIC_LABELS[col_name]}**")

            fig_box = go.Figure(layout=get_plotly_layout(height=250))

            up_data = df.loc[regimes["up_mask"].loc[df.index], col_name]
            down_data = df.loc[regimes["down_mask"].loc[df.index], col_name]

            fig_box.add_trace(go.Box(
                y=up_data, name="UpMarket",
                marker_color=COLORS["green"],
                boxmean=True,
            ))
            fig_box.add_trace(go.Box(
                y=down_data, name="DownMarket",
                marker_color=COLORS["red"],
                boxmean=True,
            ))

            fig_box.update_yaxis(tickformat=".0%", title="Probabilité")
            st.plotly_chart(fig_box, use_container_width=True)

        with col2:
            st.markdown("&nbsp;")
            st.markdown("&nbsp;")
            stats_table = pd.DataFrame({
                "": ["Moyenne", "Volatilité", "Max / Min"],
                "UpMarket 🟢": [
                    f"{p['up_mean']:.1%}", f"{p['up_std']:.1%}", f"{p['up_max']:.1%}",
                ],
                "DownMarket 🔴": [
                    f"{p['down_mean']:.1%}", f"{p['down_std']:.1%}", f"{p['down_min']:.1%}",
                ],
            })
            st.dataframe(stats_table, use_container_width=True, hide_index=True)
