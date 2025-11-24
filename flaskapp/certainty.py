"""
certainty.py — Certainty and confidence-interval computation for SPACE scoring.

This module implements the “certainty” (C) component described in the
SPACE Score (v1.3) methodology. Certainty quantifies how reliable the
individual submetric evaluations are, based on both the COVERAGE of
observed data and the QUALITY of the underlying evidence.

The functions here compute:

    * Coverage_G    — weighted proportion of observed inputs for group G ∈ {I, T, V}
    * Quality_G     — weighted average quality score for group G
    * C (certainty) — geometric mean √(Coverage x Quality)
    * certainty band classification
    * I-beam confidence interval used for visualization and reporting

These outputs integrate directly into the main SPACE scoring pipeline.
"""

from __future__ import annotations
import math
from typing import Dict, Tuple


# --------------------[ COVERAGE + QUALITY CALCULATION ]-------------------- #
def compute_coverage_quality(
    observed: Dict[str, Dict[str, float]],
    quality: Dict[str, Dict[str, float]],
    weights: Dict[str, Dict[str, float]]
) -> Tuple[float, float]:
    """
    Compute the coverage and quality components described in SPACE v1.3.

    Parameters
    ----------
    observed : dict
        Nested structure of boolean/0-1 indicators:
            {
              "I": {"i1": 1, "i2": 0, ...},
              "T": {"t1": 1, ...},
              "V": {"v1": 1, ...}
            }
        o_j = 1 → submetric j based on real observed data
        o_j = 0 → inferred / missing / placeholder evidence

    quality : dict
        Nested structure of quality scores q_j ∈ [0.30, 1.00], e.g.:
            {
              "I": {"i1": 0.90, "i2": 0.60, ...},
              ...
            }

    weights : dict
        Weight assignments w_j for each submetric j, e.g.:
            {
              "I": {"i1": 0.30, "i2": 0.25, ...},
              ...
            }

    Returns
    -------
    (coverage, quality) : (float, float)
        Group-averaged Coverage ∈ [0, 1] and Quality ∈ [0, 1].

    Notes
    -----
    Follows SPACE v1.3:
        Coverage_G = Σ_j (w_j * o_j)
        Quality_G  = Σ_j (w_j * q_j)

        Coverage = (Coverage_I + Coverage_T + Coverage_V) / 3
        Quality  = (Quality_I  + Quality_T  + Quality_V)  / 3
    """
    group_cov = []
    group_qual = []

    for group in ["I", "T", "V"]:
        cov = sum(weights[group][k] * observed[group][k] for k in weights[group])
        qual = sum(weights[group][k] * quality[group][k] for k in weights[group])

        group_cov.append(cov)
        group_qual.append(qual)

    coverage = sum(group_cov) / 3.0
    quality_val = sum(group_qual) / 3.0

    return coverage, quality_val


# --------------------[ CERTAINTY SCORE + CLASSIFICATION ]-------------------- #
def compute_certainty(coverage: float, quality: float) -> float:
    """
    Compute the certainty score C.

    Parameters
    ----------
    coverage : float
        Weighted proportion of observed submetrics (0.0-1.0).
    quality : float
        Weighted evidence quality average (0.0-1.0).

    Returns
    -------
    float
        Certainty C = √(coverage x quality)

    Explanation
    -----------
    SPACE v1.3 defines certainty as the geometric mean of coverage and quality,
    ensuring that a deficiency in either dimension reduces analytic confidence.
    """
    return math.sqrt(max(0.0, coverage * quality))

def classify_certainty(C: float) -> str:
    """
    Classify certainty score C into categorical bands.

    Parameters
    ----------
    C : float
        Certainty score ∈ [0.0, 1.0].

    Returns
    -------
    str
        One of:
            - "Low"
            - "Moderate"
            - "High"
            - "Very High"

    Thresholds follow SPACE v1.3:
        C < 0.40     → Low
        0.40-0.70    → Moderate
        0.70-0.85    → High
        ≥ 0.85       → Very High
    """
    if C < 0.40:
        return "Low"
    if C < 0.70:
        return "Moderate"
    if C < 0.85:
        return "High"
    return "Very High"


# --------------------[ I-BEAM CONFIDENCE INTERVAL ]-------------------- #
def compute_ibeam(space_score: float, C: float, u: float = 0.3) -> dict:
    """
    Compute the I-beam (mean-with-confidence-interval) around a SPACE score.

    Parameters
    ----------
    space_score : float
        The computed SPACE severity score (0.0-10.0).
    C : float
        Certainty score (0.0-1.0).
    u : float, optional
        Visual scaling parameter ∈ [0.2, 0.4], default 0.3.
        Controls how wide the I-beam becomes for low-certainty cases.

    Returns
    -------
    dict
        {
            "center": float,
            "half_width": float,
            "lower": float,
            "upper": float
        }

    Notes
    -----
    SPACE v1.3 defines the I-beam half-width as:
        Δ = (1 - C) · u · SPACE

    This encodes how uncertainty expands the confidence interval.
    """
    delta = (1.0 - C) * u * space_score

    center = space_score
    lower = max(0.0, center - delta)
    upper = min(10.0, center + delta)

    return {
        "center": center,
        "half_width": delta,
        "lower": lower,
        "upper": upper,
    }
