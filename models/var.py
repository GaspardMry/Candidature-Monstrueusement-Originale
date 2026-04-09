"""
var.py — Calcul de la Value at Risk (VaR) par 3 méthodes.

Méthodes implémentées :
- VaR historique
- VaR paramétrique (gaussienne)
- VaR Monte Carlo (1000 simulations)
"""

import numpy as np
import pandas as pd
from scipy import stats


def var_historique(returns: pd.Series, confidence: float = 0.95, horizon: int = 30) -> float:
    """
    VaR historique : percentile empirique des rendements.

    Args:
        returns: Série des rendements quotidiens.
        confidence: Niveau de confiance (ex: 0.95).
        horizon: Horizon en jours.

    Returns:
        VaR sur l'horizon donné (valeur négative = perte).
    """
    alpha = 1 - confidence
    var_1d = np.percentile(returns.dropna(), alpha * 100)
    return var_1d * np.sqrt(horizon)


def var_parametrique(returns: pd.Series, confidence: float = 0.95, horizon: int = 30) -> float:
    """
    VaR paramétrique : hypothèse de normalité des rendements.

    Args:
        returns: Série des rendements quotidiens.
        confidence: Niveau de confiance.
        horizon: Horizon en jours.

    Returns:
        VaR paramétrique sur l'horizon donné.
    """
    mu = returns.mean()
    sigma = returns.std()
    z_score = stats.norm.ppf(1 - confidence)
    var_1d = mu + z_score * sigma
    return var_1d * np.sqrt(horizon)


def var_monte_carlo(
    returns: pd.Series,
    confidence: float = 0.95,
    horizon: int = 30,
    n_simulations: int = 1000,
    seed: int = 42,
) -> tuple[float, np.ndarray]:
    """
    VaR Monte Carlo : simulation de trajectoires futures.

    Args:
        returns: Série des rendements quotidiens.
        confidence: Niveau de confiance.
        horizon: Horizon en jours.
        n_simulations: Nombre de simulations.
        seed: Graine aléatoire.

    Returns:
        Tuple (VaR Monte Carlo, matrice des simulations [n_simulations x horizon]).
    """
    rng = np.random.default_rng(seed)
    mu = returns.mean()
    sigma = returns.std()

    # Simuler les rendements cumulés sur l'horizon
    simulated_returns = rng.normal(mu, sigma, size=(n_simulations, horizon))
    cumulative_returns = simulated_returns.cumsum(axis=1)

    # VaR = percentile des rendements cumulés finaux
    final_returns = cumulative_returns[:, -1]
    alpha = 1 - confidence
    var_mc = np.percentile(final_returns, alpha * 100)

    return var_mc, cumulative_returns


def compute_var_all_methods(
    returns: pd.Series,
    confidence: float = 0.95,
    horizon: int = 30,
) -> dict:
    """
    Calcule la VaR par les 3 méthodes pour une série donnée.

    Returns:
        Dictionnaire avec les résultats des 3 méthodes + simulations MC.
    """
    var_hist = var_historique(returns, confidence, horizon)
    var_param = var_parametrique(returns, confidence, horizon)
    var_mc, simulations = var_monte_carlo(returns, confidence, horizon)

    return {
        "historique": var_hist,
        "parametrique": var_param,
        "monte_carlo": var_mc,
        "simulations": simulations,
        "confidence": confidence,
        "horizon": horizon,
    }


def compute_confidence_cone(
    last_value: float,
    returns: pd.Series,
    horizon: int = 60,
    n_simulations: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Calcule un cône de confiance pour la projection future.

    Returns:
        Dict avec percentiles 5%, 25%, 50%, 75%, 95% des trajectoires.
    """
    rng = np.random.default_rng(seed)
    mu = returns.mean()
    sigma = returns.std()

    sims = rng.normal(mu, sigma, size=(n_simulations, horizon))
    # Convertir en trajectoires de prix
    price_paths = last_value * np.exp(sims.cumsum(axis=1))

    return {
        "p5": np.percentile(price_paths, 5, axis=0),
        "p25": np.percentile(price_paths, 25, axis=0),
        "p50": np.percentile(price_paths, 50, axis=0),
        "p75": np.percentile(price_paths, 75, axis=0),
        "p95": np.percentile(price_paths, 95, axis=0),
    }
