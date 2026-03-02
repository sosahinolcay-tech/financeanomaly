"""Historical similarity retrieval for anomaly context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np


@dataclass
class SimilarCase:
    timestamp: datetime
    symbol: str
    features: Dict[str, float]
    metadata: Dict[str, str]
    similarity: float = 0.0


class SimilaritySearch:
    """In-memory cosine-similarity search over historical alerts."""

    def __init__(self, max_cases: int = 5000):
        self.max_cases = max_cases
        self._cases: List[SimilarCase] = []

    def add_case(
        self,
        timestamp: datetime,
        symbol: str,
        features: Dict[str, float],
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        self._cases.append(
            SimilarCase(
                timestamp=timestamp,
                symbol=symbol,
                features=dict(features),
                metadata=dict(metadata or {}),
            )
        )
        if len(self._cases) > self.max_cases:
            self._cases.pop(0)

    def query(self, features: Dict[str, float], top_k: int = 3) -> List[SimilarCase]:
        if not self._cases:
            return []

        keys = sorted(features.keys())
        q = np.asarray([features.get(k, 0.0) for k in keys], dtype=float)
        q_norm = float(np.linalg.norm(q)) + 1e-9

        scored: List[SimilarCase] = []
        for case in self._cases:
            v = np.asarray([case.features.get(k, 0.0) for k in keys], dtype=float)
            sim = float(np.dot(q, v) / (q_norm * (float(np.linalg.norm(v)) + 1e-9)))
            scored.append(
                SimilarCase(
                    timestamp=case.timestamp,
                    symbol=case.symbol,
                    features=case.features,
                    metadata=case.metadata,
                    similarity=sim,
                )
            )

        scored.sort(key=lambda c: c.similarity, reverse=True)
        return scored[:top_k]
