"""Regime indicator feature utilities."""

from __future__ import annotations

import numpy as np


def _safe_kurtosis(values: np.ndarray) -> float:
    if values.size < 4:
        return 0.0
    mean = float(np.mean(values))
    std = float(np.std(values))
    if std <= 1e-12:
        return 0.0
    centered = (values - mean) / std
    return float(np.mean(centered ** 4) - 3.0)


def classify_volatility_regime(realized_vol: float) -> int:
    """Map volatility to a simple regime code.

    - 0: low vol
    - 1: medium vol
    - 2: high vol
    """
    if realized_vol < 0.01:
        return 0
    if realized_vol < 0.03:
        return 1
    return 2


def compute_regime_features(prices: np.ndarray, lookback: int = 100) -> dict[str, float]:
    """Compute simple regime features from recent prices.

    This is intentionally lightweight and deterministic for streaming use.
    """
    arr = np.asarray(prices, dtype=float)
    if arr.size < 5:
        return {}

    window = arr[-lookback:] if arr.size > lookback else arr
    log_returns = np.diff(np.log(np.clip(window, 1e-12, None)))
    if log_returns.size == 0:
        return {}

    realized_vol = float(np.std(log_returns) * np.sqrt(log_returns.size))
    trend_strength = float(np.mean(log_returns))
    max_drawdown = float(np.min(window / np.maximum.accumulate(window) - 1.0))
    kurt = _safe_kurtosis(log_returns)
    regime = classify_volatility_regime(realized_vol)

    return {
        "realized_volatility": realized_vol,
        "trend_strength": trend_strength,
        "max_drawdown": max_drawdown,
        "returns_kurtosis": kurt,
        "vol_regime_code": float(regime),
    }
