"""
stress_tests.py — Scénarios de stress appliqués au profil atypique.

3 scénarios :
1. Fermeture simultanée des programmes de stage
2. 10 refus consécutifs en une semaine
3. Crise de confiance sévère (-40% sur toutes les probabilités)
"""

import numpy as np
import pandas as pd


SCENARIOS = {
    "Fermeture des programmes": {
        "description": "Tous les grands groupes ferment leur programme de stage simultanément",
        "chocs": {
            "Probabilité_Village": -0.25,
            "Probabilité_BAC_1025": -0.15,
            "Probabilité_TDAH_TSA_HPI": -0.10,
            "Probabilité_Ecole_NonTarget": -0.30,
        },
        "recovery_days": {
            "Probabilité_Village": 45,
            "Probabilité_BAC_1025": 60,
            "Probabilité_TDAH_TSA_HPI": 25,
            "Probabilité_Ecole_NonTarget": 50,
        },
        "emoji": "🏢",
    },
    "10 refus consécutifs": {
        "description": "10 refus consécutifs reçus en une seule semaine",
        "chocs": {
            "Probabilité_Village": -0.10,
            "Probabilité_BAC_1025": -0.12,
            "Probabilité_TDAH_TSA_HPI": -0.20,
            "Probabilité_Ecole_NonTarget": -0.18,
        },
        "recovery_days": {
            "Probabilité_Village": 20,
            "Probabilité_BAC_1025": 35,
            "Probabilité_TDAH_TSA_HPI": 15,
            "Probabilité_Ecole_NonTarget": 30,
        },
        "emoji": "📨",
    },
    "Crise de confiance": {
        "description": "Crise de confiance sévère — choc de -40% sur toutes les probabilités",
        "chocs": {
            "Probabilité_Village": -0.40,
            "Probabilité_BAC_1025": -0.40,
            "Probabilité_TDAH_TSA_HPI": -0.40,
            "Probabilité_Ecole_NonTarget": -0.40,
        },
        "recovery_days": {
            "Probabilité_Village": 55,
            "Probabilité_BAC_1025": 70,
            "Probabilité_TDAH_TSA_HPI": 30,
            "Probabilité_Ecole_NonTarget": 60,
        },
        "emoji": "💔",
    },
}


def apply_stress(
    df: pd.DataFrame, scenario_name: str, apply_at_index: int = -1
) -> dict:
    """
    Applique un scénario de stress aux données.

    Args:
        df: DataFrame des probabilités.
        scenario_name: Nom du scénario (clé de SCENARIOS).
        apply_at_index: Index temporel d'application du choc (-1 = dernier point).

    Returns:
        Dict avec valeurs avant/après choc, impact absolu et relatif,
        et trajectoire de recovery simulée.
    """
    scenario = SCENARIOS[scenario_name]
    chocs = scenario["chocs"]
    recovery_days = scenario["recovery_days"]

    if apply_at_index == -1:
        apply_at_index = len(df) - 1

    current_values = df.iloc[apply_at_index]
    results = {}

    for col in df.columns:
        before = current_values[col]
        choc_relatif = chocs[col]
        after = max(before * (1 + choc_relatif), 0.005)
        impact_abs = after - before
        impact_rel = choc_relatif * 100

        # Simuler la trajectoire de recovery
        rec_days = recovery_days[col]
        recovery_path = _simulate_recovery(after, before, rec_days)

        results[col] = {
            "avant": before,
            "après": after,
            "impact_absolu": impact_abs,
            "impact_relatif": impact_rel,
            "recovery_days": rec_days,
            "recovery_path": recovery_path,
        }

    return results


def _simulate_recovery(stressed_value: float, target_value: float, days: int) -> np.ndarray:
    """
    Simule une trajectoire de recovery exponentielle avec bruit.

    La recovery suit une courbe exponentielle amortie avec du bruit
    pour simuler les hauts et bas du processus de récupération.
    """
    rng = np.random.default_rng(123)
    t = np.linspace(0, 1, days)
    # Recovery exponentielle
    recovery_base = stressed_value + (target_value - stressed_value) * (1 - np.exp(-3 * t))
    # Ajout de bruit
    noise = rng.normal(0, abs(target_value - stressed_value) * 0.05, days)
    recovery = np.clip(recovery_base + noise, 0.005, 1.0)
    return recovery


def get_scenario_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère un tableau récapitulatif de tous les scénarios de stress.

    Returns:
        DataFrame avec colonnes : Scénario, Métrique, Avant, Après, Impact, Recovery (jours).
    """
    rows = []
    for scenario_name in SCENARIOS:
        results = apply_stress(df, scenario_name)
        for col, vals in results.items():
            rows.append({
                "Scénario": scenario_name,
                "Métrique": col,
                "Avant": f"{vals['avant']:.1%}",
                "Après": f"{vals['après']:.1%}",
                "Impact": f"{vals['impact_relatif']:+.0f}%",
                "Recovery (jours)": vals["recovery_days"],
            })
    return pd.DataFrame(rows)
