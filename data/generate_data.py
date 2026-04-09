"""
generate_data.py — Génération des 4 séries temporelles personnelles.

Chaque série simule sur 24 mois (journalier, ~504 points) la probabilité
qu'un profil atypique atteigne un objectif en finance de marché.
Seed fixe pour reproductibilité.
"""

import numpy as np
import pandas as pd


def generate_all_series(seed: int = 42) -> pd.DataFrame:
    """
    Génère les 4 séries temporelles personnelles.

    Returns:
        DataFrame indexé par date avec les 4 colonnes de probabilité.
    """
    rng = np.random.default_rng(seed)
    n_days = 504  # ~24 mois de jours ouvrés
    dates = pd.bdate_range(start="2024-01-02", periods=n_days, freq="B")

    t = np.linspace(0, 1, n_days)

    # ── 1. Probabilité_Village ───────────────────────────────────────
    # Départ très bas (~2%), progression sigmoïde avec paliers
    base_village = 0.02 + 0.38 * (1 / (1 + np.exp(-12 * (t - 0.5))))
    # Ajout de chocs positifs (certifications, projets)
    chocs_village = np.zeros(n_days)
    for idx in [100, 200, 300, 380, 430]:
        chocs_village[idx:] += rng.uniform(0.02, 0.05)
    noise_village = rng.normal(0, 0.006, n_days)
    village = np.clip(base_village + chocs_village + noise_village, 0.01, 0.60)

    # ── 2. Probabilité_BAC_1025 ──────────────────────────────────────
    # Plateau long puis accélération soudaine (résilience)
    plateau = np.full(n_days, 0.03)
    acceleration_start = int(n_days * 0.55)
    plateau[acceleration_start:] = 0.03 + 0.32 * (
        (t[acceleration_start:] - t[acceleration_start])
        / (1 - t[acceleration_start])
    ) ** 1.8
    noise_bac = rng.normal(0, 0.005, n_days)
    bac = np.clip(plateau + noise_bac, 0.01, 0.50)

    # ── 3. Probabilité_TDAH_TSA_HPI ─────────────────────────────────
    # Haute volatilité, pics de surperformance, tendance haussière
    trend_neuro = 0.05 + 0.30 * t**0.8
    volatility = 0.04 + 0.06 * np.sin(2 * np.pi * t * 3)  # vol cyclique
    noise_neuro = rng.normal(0, 1, n_days) * volatility
    # Pics de surperformance (hyperfocus)
    spikes = np.zeros(n_days)
    spike_indices = rng.choice(range(50, n_days), size=8, replace=False)
    for idx in spike_indices:
        width = rng.integers(5, 15)
        spike_end = min(idx + width, n_days)
        spikes[idx:spike_end] += rng.uniform(0.05, 0.12)
    neuro = np.clip(trend_neuro + noise_neuro + spikes, 0.01, 0.65)

    # ── 4. Probabilité_Ecole_NonTarget ───────────────────────────────
    # Chocs négatifs (refus) + rebonds (résilience)
    trend_ecole = 0.04 + 0.26 * (1 / (1 + np.exp(-8 * (t - 0.45))))
    # Chocs négatifs (refus de stage)
    chocs_negatifs = np.zeros(n_days)
    refus_indices = [80, 150, 210, 270, 340]
    for idx in refus_indices:
        drop = rng.uniform(0.04, 0.08)
        recovery = rng.integers(15, 30)
        end = min(idx + recovery, n_days)
        chocs_negatifs[idx:end] -= drop * np.exp(
            -np.linspace(0, 3, end - idx)
        )
        # Rebond post-refus (résilience)
        rebond_start = min(idx + recovery, n_days - 1)
        rebond_end = min(rebond_start + 20, n_days)
        chocs_negatifs[rebond_start:rebond_end] += drop * 0.3

    noise_ecole = rng.normal(0, 0.005, n_days)
    ecole = np.clip(trend_ecole + chocs_negatifs + noise_ecole, 0.01, 0.50)

    df = pd.DataFrame(
        {
            "Probabilité_Village": village,
            "Probabilité_BAC_1025": bac,
            "Probabilité_TDAH_TSA_HPI": neuro,
            "Probabilité_Ecole_NonTarget": ecole,
        },
        index=dates,
    )
    df.index.name = "Date"
    return df


def compute_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les rendements quotidiens (variations relatives)."""
    returns = df.pct_change().dropna()
    # Remplacer les inf par NaN puis forward-fill
    returns = returns.replace([np.inf, -np.inf], np.nan).ffill().fillna(0)
    return returns
