"""
updown_market.py — Analyse UpMarket / DownMarket.

Évalue la performance du profil atypique dans des contextes
favorables (boom recrutement) vs défavorables (gel recrutement).
Calcule les Capture Ratios pour démontrer l'avantage asymétrique
de la résilience.
"""

import numpy as np
import pandas as pd


def generate_market_regime(n_days: int = 504, seed: int = 42) -> pd.Series:
    """
    Génère un indice de marché synthétique représentant les conditions
    de recrutement en finance quantitative.

    Returns:
        Series avec valeurs positives (marché favorable) et négatives (défavorable).
    """
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, n_days)

    # Tendance cyclique avec bruit
    trend = 0.3 * np.sin(2 * np.pi * t * 2.5) + 0.1 * np.sin(2 * np.pi * t * 5)
    noise = rng.normal(0, 0.02, n_days)
    market = trend + noise

    dates = pd.bdate_range(start="2024-01-02", periods=n_days, freq="B")
    return pd.Series(market, index=dates, name="Market_Regime")


def classify_regimes(market: pd.Series) -> dict:
    """
    Classifie les jours en UpMarket et DownMarket.

    Returns:
        Dict avec masques booléens et statistiques par régime.
    """
    up_mask = market > 0
    down_mask = market <= 0

    return {
        "up_mask": up_mask,
        "down_mask": down_mask,
        "n_up_days": up_mask.sum(),
        "n_down_days": down_mask.sum(),
        "pct_up": up_mask.mean() * 100,
        "pct_down": down_mask.mean() * 100,
    }


def compute_capture_ratios(
    returns: pd.DataFrame, market: pd.Series
) -> pd.DataFrame:
    """
    Calcule les Capture Ratios pour chaque métrique.

    - Up Capture Ratio = rendement moyen en UpMarket / rendement moyen du marché en UpMarket
    - Down Capture Ratio = rendement moyen en DownMarket / rendement moyen du marché en DownMarket

    Un profil résilient a un Up Capture > 1 et un Down Capture < 1
    (surperforme en hausse, résiste mieux en baisse).

    Returns:
        DataFrame avec Up Capture, Down Capture et Asymmetry Ratio par métrique.
    """
    market_returns = market.pct_change().dropna()

    # Aligner les indices
    common_idx = returns.index.intersection(market_returns.index)
    ret = returns.loc[common_idx]
    mkt = market_returns.loc[common_idx]

    up_days = mkt > 0
    down_days = mkt <= 0

    rows = []
    for col in ret.columns:
        # Rendements moyens en UpMarket
        up_ret_profile = ret.loc[up_days, col].mean()
        up_ret_market = mkt[up_days].mean()
        up_capture = up_ret_profile / up_ret_market if up_ret_market != 0 else 0

        # Rendements moyens en DownMarket
        down_ret_profile = ret.loc[down_days, col].mean()
        down_ret_market = mkt[down_days].mean()
        down_capture = down_ret_profile / down_ret_market if down_ret_market != 0 else 0

        # Ratio d'asymétrie : > 1 signifie avantage asymétrique
        asymmetry = up_capture / down_capture if down_capture != 0 else float("inf")

        rows.append({
            "Métrique": col,
            "Up Capture": up_capture,
            "Down Capture": down_capture,
            "Asymmetry Ratio": asymmetry,
            "Rendement moyen (Up)": up_ret_profile,
            "Rendement moyen (Down)": down_ret_profile,
        })

    return pd.DataFrame(rows)


def compute_regime_performance(
    df: pd.DataFrame, market: pd.Series
) -> dict:
    """
    Calcule les statistiques de performance par régime de marché.

    Returns:
        Dict avec stats UpMarket et DownMarket pour chaque métrique.
    """
    regimes = classify_regimes(market)
    up_mask = regimes["up_mask"]
    down_mask = regimes["down_mask"]

    # Aligner
    common_idx = df.index.intersection(market.index)
    data = df.loc[common_idx]
    up = up_mask.loc[common_idx]
    down = down_mask.loc[common_idx]

    results = {}
    for col in data.columns:
        results[col] = {
            "up_mean": data.loc[up, col].mean(),
            "up_std": data.loc[up, col].std(),
            "up_max": data.loc[up, col].max(),
            "down_mean": data.loc[down, col].mean(),
            "down_std": data.loc[down, col].std(),
            "down_min": data.loc[down, col].min(),
        }

    return results
