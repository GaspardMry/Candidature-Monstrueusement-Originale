"""
stress_tab.py — Onglet Stress Tests.

Affiche les scénarios de stress avec graphiques avant/après,
trajectoires de recovery et tableaux d'impact.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from models.stress_tests import SCENARIOS, apply_stress, get_scenario_summary
from utils.styling import (
    COLORS, METRIC_COLORS, METRIC_LABELS, get_plotly_layout, info_box,
)


def render(df: pd.DataFrame):
    """Rendu de l'onglet Stress Tests."""

    st.markdown(
        '<div class="terminal-header">⚡ STRESS TESTS — "Worst Case Scenarios"</div>',
        unsafe_allow_html=True,
    )

    info_box(
        "💡 Traduction Risk",
        "Les <b>Stress Tests</b> simulent des chocs extrêmes pour évaluer la résistance "
        "d'un portefeuille. Ici, ils répondent à la question : "
        "<i>\"Que se passe-t-il si tout va mal en même temps ?\"</i> — "
        "et surtout : <b>combien de temps faut-il pour se relever ?</b> "
        "C'est le temps de recovery qui révèle la vraie résilience.",
        style="cyan",
    )

    # ── Tableau récapitulatif ─────────────────────────────────────────
    st.markdown('<div class="terminal-header">📋 RÉCAPITULATIF DES SCÉNARIOS</div>', unsafe_allow_html=True)

    summary = get_scenario_summary(df)
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Détail par scénario ───────────────────────────────────────────
    for scenario_name, scenario_info in SCENARIOS.items():
        st.markdown(
            f'<div class="terminal-header">{scenario_info["emoji"]} SCÉNARIO : {scenario_name.upper()}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"*{scenario_info['description']}*")

        results = apply_stress(df, scenario_name)

        # ── Graphique d'impact ────────────────────────────────────────
        fig_impact = go.Figure(layout=get_plotly_layout(
            title=f"IMPACT — {scenario_name}",
            height=350,
        ))

        metrics = list(results.keys())
        before_vals = [results[m]["avant"] * 100 for m in metrics]
        after_vals = [results[m]["après"] * 100 for m in metrics]
        labels = [METRIC_LABELS[m] for m in metrics]

        fig_impact.add_trace(go.Bar(
            x=labels, y=before_vals,
            name="Avant stress",
            marker_color=COLORS["cyan"],
            text=[f"{v:.1f}%" for v in before_vals],
            textposition="outside",
        ))
        fig_impact.add_trace(go.Bar(
            x=labels, y=after_vals,
            name="Après stress",
            marker_color=COLORS["red"],
            text=[f"{v:.1f}%" for v in after_vals],
            textposition="outside",
        ))

        fig_impact.update_layout(barmode="group")
        fig_impact.update_yaxis(title="Probabilité (%)", range=[0, max(before_vals) * 1.3])

        st.plotly_chart(fig_impact, use_container_width=True)

        # ── Trajectoires de recovery ──────────────────────────────────
        fig_recovery = go.Figure(layout=get_plotly_layout(
            title=f"TRAJECTOIRE DE RECOVERY — {scenario_name}",
            height=350,
        ))

        for col_name in metrics:
            r = results[col_name]
            path = r["recovery_path"]
            days = np.arange(len(path))

            fig_recovery.add_trace(go.Scatter(
                x=days, y=path,
                name=METRIC_LABELS[col_name],
                line=dict(color=METRIC_COLORS[col_name], width=2),
                hovertemplate="%{y:.1%}<extra>" + METRIC_LABELS[col_name] + "</extra>",
            ))

            # Ligne du niveau pré-stress
            fig_recovery.add_hline(
                y=r["avant"],
                line_dash="dot",
                line_color=METRIC_COLORS[col_name],
                opacity=0.3,
            )

        fig_recovery.update_yaxis(tickformat=".0%", title="Probabilité")
        fig_recovery.update_xaxis(title="Jours après le choc")

        st.plotly_chart(fig_recovery, use_container_width=True)

        # ── Métriques de recovery ─────────────────────────────────────
        rec_cols = st.columns(4)
        for i, col_name in enumerate(metrics):
            r = results[col_name]
            with rec_cols[i]:
                st.metric(
                    label=f"Recovery {METRIC_LABELS[col_name].split('→')[0].strip()}",
                    value=f"{r['recovery_days']} jours",
                    delta=f"{r['impact_relatif']:+.0f}% choc",
                    delta_color="inverse",
                )

        st.markdown("---")

    # ── Interprétation globale ────────────────────────────────────────
    info_box(
        "📊 Ce que ça dit de mon profil",
        "Même sous le pire scénario (crise de confiance à -40%), "
        "la métrique <b>TDAH/TSA/HPI</b> se rétablit la plus vite (30 jours). "
        "C'est l'avantage du profil neurodivergent : <b>la capacité de rebond est intégrée</b>. "
        "La volatilité n'est pas un bug, c'est une feature. "
        "Un Risk Manager reconnaîtra ici le profil d'un actif à <b>haute convexité</b> — "
        "les pertes sont bornées, mais le potentiel de hausse est asymétrique.",
        style="green",
    )
