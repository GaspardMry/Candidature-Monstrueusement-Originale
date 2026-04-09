"""
risk_dashboard.py — Onglet Risk Dashboard.

Tableau de bord des contraintes, exceedances, alertes visuelles
et historique des breaches avec temps de retour au-dessus du seuil.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from utils.styling import (
    COLORS, METRIC_COLORS, METRIC_LABELS, get_plotly_layout, info_box,
)


# Seuils minimaux par métrique
DEFAULT_THRESHOLDS = {
    "Probabilité_Village": 0.05,
    "Probabilité_BAC_1025": 0.04,
    "Probabilité_TDAH_TSA_HPI": 0.08,
    "Probabilité_Ecole_NonTarget": 0.05,
}


def compute_exceedances(df: pd.DataFrame, thresholds: dict) -> dict:
    """
    Calcule les exceedances (passages sous le seuil) pour chaque métrique.

    Returns:
        Dict par métrique avec nombre de breaches, durée moyenne, durée max,
        et dates des breaches.
    """
    results = {}

    for col_name in df.columns:
        threshold = thresholds.get(col_name, 0.05)
        series = df[col_name]
        below = series < threshold

        # Identifier les périodes de breach
        breaches = []
        in_breach = False
        breach_start = None

        for i, (date, is_below) in enumerate(below.items()):
            if is_below and not in_breach:
                in_breach = True
                breach_start = date
            elif not is_below and in_breach:
                in_breach = False
                breach_end = date
                duration = (breach_end - breach_start).days
                min_val = series.loc[breach_start:breach_end].min()
                breaches.append({
                    "start": breach_start,
                    "end": breach_end,
                    "duration_days": duration,
                    "min_value": min_val,
                    "depth": threshold - min_val,
                })

        # Si toujours en breach à la fin
        if in_breach:
            breach_end = series.index[-1]
            duration = (breach_end - breach_start).days
            min_val = series.loc[breach_start:].min()
            breaches.append({
                "start": breach_start,
                "end": breach_end,
                "duration_days": duration,
                "min_value": min_val,
                "depth": threshold - min_val,
                "ongoing": True,
            })

        n_breach_days = below.sum()
        results[col_name] = {
            "threshold": threshold,
            "n_breaches": len(breaches),
            "n_breach_days": n_breach_days,
            "pct_breach": n_breach_days / len(series) * 100,
            "avg_duration": np.mean([b["duration_days"] for b in breaches]) if breaches else 0,
            "max_duration": max([b["duration_days"] for b in breaches]) if breaches else 0,
            "current_value": series.iloc[-1],
            "is_currently_breached": below.iloc[-1],
            "breaches": breaches,
        }

    return results


def render(df: pd.DataFrame):
    """Rendu de l'onglet Risk Dashboard."""

    st.markdown(
        '<div class="terminal-header">🚨 RISK DASHBOARD — Contraintes & Exceedances</div>',
        unsafe_allow_html=True,
    )

    info_box(
        "💡 Traduction Risk",
        "Un <b>Risk Dashboard</b> définit des seuils minimaux (limites de risque) "
        "et surveille les <b>exceedances</b> — les moments où une métrique passe sous son seuil. "
        "C'est l'équivalent des limites VaR d'un desk de trading : "
        "quand le seuil est franchi, une <b>alerte</b> se déclenche et un plan d'action est requis.",
        style="cyan",
    )

    # ── Seuils personnalisables ───────────────────────────────────────
    st.markdown('<div class="terminal-header">⚙️ CONFIGURATION DES SEUILS</div>', unsafe_allow_html=True)

    thresholds = {}
    cols = st.columns(4)
    for i, col_name in enumerate(df.columns):
        with cols[i]:
            thresholds[col_name] = st.slider(
                f"Seuil {METRIC_LABELS[col_name].split('→')[0].strip()}",
                min_value=0.01,
                max_value=0.20,
                value=DEFAULT_THRESHOLDS[col_name],
                step=0.01,
                format="%.0f%%",
                key=f"threshold_{col_name}",
            )

    # ── Calcul des exceedances ────────────────────────────────────────
    exceedances = compute_exceedances(df, thresholds)

    # ── Panneau d'alertes ─────────────────────────────────────────────
    st.markdown('<div class="terminal-header">🔴 STATUT DES ALERTES</div>', unsafe_allow_html=True)

    alert_cols = st.columns(4)
    for i, col_name in enumerate(df.columns):
        exc = exceedances[col_name]
        with alert_cols[i]:
            if exc["is_currently_breached"]:
                st.error(f"⚠️ **BREACH ACTIVE**")
                st.metric(
                    label=METRIC_LABELS[col_name],
                    value=f"{exc['current_value']:.1%}",
                    delta=f"Seuil: {exc['threshold']:.0%}",
                    delta_color="inverse",
                )
            else:
                margin = exc["current_value"] - exc["threshold"]
                st.success(f"✅ **OK**")
                st.metric(
                    label=METRIC_LABELS[col_name],
                    value=f"{exc['current_value']:.1%}",
                    delta=f"+{margin:.1%} au-dessus du seuil",
                )

    st.markdown("---")

    # ── Graphiques avec seuils et zones de breach ─────────────────────
    st.markdown('<div class="terminal-header">📉 HISTORIQUE DES EXCEEDANCES</div>', unsafe_allow_html=True)

    for col_name in df.columns:
        exc = exceedances[col_name]
        threshold = exc["threshold"]
        color = METRIC_COLORS[col_name]

        fig = go.Figure(layout=get_plotly_layout(
            title=f"{METRIC_LABELS[col_name]} — Seuil à {threshold:.0%}",
            height=300,
        ))

        # Série temporelle
        fig.add_trace(go.Scatter(
            x=df.index, y=df[col_name],
            line=dict(color=color, width=2),
            name=METRIC_LABELS[col_name],
            hovertemplate="%{y:.1%}<extra></extra>",
        ))

        # Seuil
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color=COLORS["red"],
            annotation_text=f"Seuil ({threshold:.0%})",
            annotation_font_color=COLORS["red"],
        )

        # Zones de breach
        for breach in exc["breaches"]:
            fig.add_vrect(
                x0=breach["start"],
                x1=breach["end"],
                fillcolor="rgba(255, 71, 87, 0.15)",
                line_width=0,
            )

        fig.update_yaxis(tickformat=".0%", title="Probabilité")
        fig.update_xaxis(title="Date")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown(f"**{METRIC_LABELS[col_name]}**")
            st.markdown(f"- Breaches : **{exc['n_breaches']}**")
            st.markdown(f"- Jours sous seuil : **{exc['n_breach_days']}** ({exc['pct_breach']:.1f}%)")
            st.markdown(f"- Durée moy. : **{exc['avg_duration']:.0f}j**")
            st.markdown(f"- Durée max : **{exc['max_duration']}j**")

    st.markdown("---")

    # ── Tableau récapitulatif des breaches ─────────────────────────────
    st.markdown('<div class="terminal-header">📋 REGISTRE DES BREACHES</div>', unsafe_allow_html=True)

    all_breaches = []
    for col_name in df.columns:
        exc = exceedances[col_name]
        for breach in exc["breaches"]:
            all_breaches.append({
                "Métrique": METRIC_LABELS[col_name],
                "Début": breach["start"].strftime("%Y-%m-%d"),
                "Fin": breach["end"].strftime("%Y-%m-%d"),
                "Durée (jours)": breach["duration_days"],
                "Valeur min": f"{breach['min_value']:.1%}",
                "Profondeur": f"{breach['depth']:.1%}",
                "Statut": "🔴 En cours" if breach.get("ongoing") else "✅ Résolu",
            })

    if all_breaches:
        breach_df = pd.DataFrame(all_breaches)
        st.dataframe(breach_df, use_container_width=True, hide_index=True)
    else:
        st.success("Aucune breach enregistrée — toutes les métriques sont au-dessus de leur seuil.")

    # ── Interprétation ────────────────────────────────────────────────
    info_box(
        "📊 Ce que ça dit de mon profil",
        "Les breaches sont concentrées en <b>début de période</b>, "
        "quand les probabilités étaient naturellement basses. "
        "Le fait que les breaches récentes soient <b>rares et courtes</b> "
        "confirme la progression structurelle du profil. "
        "Un Risk Manager noterait que le <b>temps moyen de recovery diminue</b> avec le temps — "
        "signe que les mécanismes de résilience se renforcent.",
        style="green",
    )
