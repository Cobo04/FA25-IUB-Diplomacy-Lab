"""
vector.py — Generation of standardized SPACE vector-string representations.

This module implements the vector encoding layer for the SPACE Score (v1.3)
framework. Whereas the SPACE numerical score provides a single aggregated
severity value in the range [0, 10], the 'vector string' preserves the
interpretability of the underlying subdimensions:

    * I — Impact
    * T — Threat
    * V — Vulnerability
    * E — Environmental Modifiers
    * S — Supplemental Context (Confidence)

Each dimension is converted from normalized quantitative values into
qualitative categorical bands, following the SPACE framework's
standardization guidelines. The resulting vector string is designed to
mirror CVSS-style encodings while retaining SPACE-specific semantics.

These vector strings:
    * are stored alongside each company's SPACE score,
    * support UI presentation,
    * allow quick analyst interpretation,
    * and can be parsed programmatically for downstream analytic workflows.

Example:
    SPACE:6.0/I:C(0.82)/T:H(0.70)/V:H(0.68)/E:Up(1.08)/S:LowConf(0.95)
"""


# --------------------[ NORMED SUBMETRIC → QUALITATIVE BAND MAPPER ]-------------------- #
def band_from_numeric(x: float) -> str:
    """
    Convert a normalized quantitative score (0.0-1.0) into a qualitative band.

    This is used for the I/T/V dimensions of the SPACE score, where normalized
    component weights are mapped onto categorical levels:

        C = Critical
        H = High
        M = Medium
        L = Low
        N = None

    These breakpoints follow the SPACE framework's standardization guidelines.
    """
    if x >= 0.875:
        return "C"   # Critical
    if x >= 0.625:
        return "H"   # High
    if x >= 0.375:
        return "M"   # Medium
    if x >= 0.125:
        return "L"   # Low
    return "N"       # None


# --------------------[ ENVIRONMENTAL MODIFIER CLASSIFICATION (E) ]-------------------- #
def classify_E(E: float) -> str:
    """
    Classify the environmental modifier (E) into an adjustment category.

    E > 1.0  → "Up"      (system conditions increase risk)
    E = 1.0  → "Neutral" (no net adjustment)
    E < 1.0  → "Down"    (mitigations reduce risk)

    This provides a human-readable interpretation of the multiplicative
    environmental factor used in SPACE scoring.
    """
    if E > 1.0:
        return "Up"
    if E < 1.0:
        return "Down"
    return "Neutral"


# --------------------[ SUPPLEMENTAL MODIFIER CLASSIFICATION (S) ]-------------------- #
def classify_S(S: float) -> str:
    """
    Classify the supplemental context (S) confidence modifier.

    S >= 1.05 → "HighConf" (high-confidence supporting data)
    S >= 1.00 → "ModConf"  (moderate-confidence)
    S >= 0.95 → "LowConf"  (low-confidence)
    else      → "DispData" (disputed or inconsistent data)

    These reflect how reliable or stable the underlying intelligence inputs are.
    """
    if S >= 1.05:
        return "HighConf"
    if S >= 1.00:
        return "ModConf"
    if S >= 0.95:
        return "LowConf"
    return "DispData"


# --------------------[ VECTOR STRING CONSTRUCTION (CVSS-STYLE FORMAT) ]-------------------- #
def vector_stringify(space_score: float, ITVES_data: dict) -> str:
    """
    Generate a CVSS-style vector string representation of a SPACE score.

    Parameters
    ----------
    space_score : float
        The final computed SPACE score (0.0-10.0).
    ITVES_data : dict
        A dictionary containing normalized component values:
            - I_value : Impact dimension
            - T_value : Threat dimension
            - V_value : Vulnerability dimension
            - E_value : Environmental modifier
            - S_value : Supplemental confidence modifier

    Returns
    -------
    str
        A standardized vector string encoding the full risk profile.
        Example:
            SPACE:6.0/I:C(0.82)/T:H(0.70)/V:H(0.68)/E:Up(1.08)/S:LowConf(0.95)

    This string is stored in the CSV and can be displayed in UI components or
    parsed for analytic workflows.
    """
    
    I = ITVES_data["I_value"]
    T = ITVES_data["T_value"]
    V = ITVES_data["V_value"]
    E = ITVES_data["E_value"]
    S = ITVES_data["S_value"]

    I_band = band_from_numeric(I)
    T_band = band_from_numeric(T)
    V_band = band_from_numeric(V)
    E_band = classify_E(E)
    S_band = classify_S(S)

    return (
        f"SPACE:{space_score}/"
        f"I:{I_band}({I:.2f})/"
        f"T:{T_band}({T:.2f})/"
        f"V:{V_band}({V:.2f})/"
        f"E:{E_band}({E:.2f})/"
        f"S:{S_band}({S:.2f})"
    )
