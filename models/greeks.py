"""
greeks.py — Calcul des sensibilités (Greeks) du profil.

- Delta : sensibilité aux heures de travail
- Gamma : accélération de la sensibilité (effet HPI)
- Vega : sensibilité à la volatilité des opportunités
- Theta : décroissance temporelle sans action
"""

import numpy as np
import pandas as pd


def compute_delta(base_prob: float, hours_range: np.ndarray = None) -> dict:
    """
    Delta — Sensibilité de la probabilité de succès aux heures de travail hebdo.

    La relation suit une sigmoïde : rendements faibles au début,
    accélération, puis plateau (on ne peut pas travailler 24h/24).

    Args:
        base_prob: Probabilité de base actuelle.
        hours_range: Plage d'heures à évaluer.

    Returns:
        Dict avec heures, probabilités, et delta instantané.
    """
    if hours_range is None:
        hours_range = np.linspace(0, 80, 200)

    # Sigmoïde centrée sur 35h, amplitude basée sur la prob de base
    max_boost = min(base_prob * 2.5, 0.95)
    probs = base_prob + (max_boost - base_prob) * (
        1 / (1 + np.exp(-0.15 * (hours_range - 35)))
    )

    # Delta = dérivée dP/dH
    delta = np.gradient(probs, hours_range)

    return {
        "hours": hours_range,
        "probability": probs,
        "delta": delta,
    }


def compute_gamma(base_prob: float, hours_range: np.ndarray = None) -> dict:
    """
    Gamma — Accélération de la sensibilité (d²P/dH²).

    Capte l'effet HPI : après un certain seuil d'heures,
    les rendements s'accélèrent (hyperfocus).

    Args:
        base_prob: Probabilité de base actuelle.
        hours_range: Plage d'heures à évaluer.

    Returns:
        Dict avec heures et gamma.
    """
    delta_data = compute_delta(base_prob, hours_range)
    hours = delta_data["hours"]
    delta = delta_data["delta"]

    # Gamma = dérivée du delta
    gamma = np.gradient(delta, hours)

    return {
        "hours": hours,
        "gamma": gamma,
        "delta": delta,
        "probability": delta_data["probability"],
    }


def compute_vega(
    base_prob: float, vol_range: np.ndarray = None, seed: int = 42
) -> dict:
    """
    Vega — Sensibilité à la volatilité des opportunités de marché.

    Plus le marché est volatile (beaucoup d'offres qui apparaissent/disparaissent),
    plus un profil atypique peut saisir des opportunités que d'autres ignorent.

    Args:
        base_prob: Probabilité de base actuelle.
        vol_range: Plage de volatilité à évaluer (0 = aucune, 1 = extrême).

    Returns:
        Dict avec volatilité, probabilité résultante, et vega.
    """
    if vol_range is None:
        vol_range = np.linspace(0, 1, 200)

    # Un profil atypique bénéficie de la volatilité (asymétrie positive)
    # Car il est plus agile et prêt à saisir les opportunités non conventionnelles
    probs = base_prob * (1 + 0.4 * vol_range - 0.15 * vol_range**2)
    probs = np.clip(probs, 0.01, 0.95)

    vega = np.gradient(probs, vol_range)

    return {
        "volatility": vol_range,
        "probability": probs,
        "vega": vega,
    }


def compute_theta(base_prob: float, days_range: np.ndarray = None) -> dict:
    """
    Theta — Décroissance temporelle si aucune action n'est entreprise.

    Comme une option, la probabilité de succès se déprécie avec le temps
    si on ne fait rien. C'est le coût de l'inaction.

    Args:
        base_prob: Probabilité de base actuelle.
        days_range: Nombre de jours d'inaction à évaluer.

    Returns:
        Dict avec jours, probabilité résiduelle, et theta.
    """
    if days_range is None:
        days_range = np.linspace(0, 180, 200)

    # Décroissance exponentielle : demi-vie de ~60 jours
    half_life = 60
    decay_rate = np.log(2) / half_life
    prob_decay = base_prob * np.exp(-decay_rate * days_range)
    # Plancher minimal
    prob_decay = np.maximum(prob_decay, 0.01)

    theta = np.gradient(prob_decay, days_range)

    return {
        "days": days_range,
        "probability": prob_decay,
        "theta": theta,
    }


def compute_all_greeks(df: pd.DataFrame) -> dict:
    """
    Calcule tous les Greeks pour chaque métrique.

    Returns:
        Dict imbriqué : {métrique: {delta: ..., gamma: ..., vega: ..., theta: ...}}
    """
    results = {}
    for col in df.columns:
        current_prob = df[col].iloc[-1]
        results[col] = {
            "delta": compute_delta(current_prob),
            "gamma": compute_gamma(current_prob),
            "vega": compute_vega(current_prob),
            "theta": compute_theta(current_prob),
            "current_prob": current_prob,
        }
    return results
