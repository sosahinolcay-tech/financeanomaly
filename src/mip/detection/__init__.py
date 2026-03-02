"""Anomaly and regime detection models."""

from .base import Detector
from .autoencoder import AutoencoderDetector
from .ensemble import WeightedEnsembleDetector
from .isolation_forest import IsolationForestDetector
from .river_detector import RiverDetector
from .thresholding import (
    ThresholdStrategy,
    StaticThreshold,
    RollingQuantileThreshold,
    EWMAAdaptiveThreshold,
)
