"""Idealised compression response built from surrogate predictions (not FEA output)."""
import math

DENSIFICATION_STRAIN = 0.55


def stress_at(strain: float, modulus: float, peak: float) -> float:
    """Linear elastic to the peak, gentle softening plateau, then exponential densification."""
    e_peak = min(peak / modulus, 0.2)
    if strain <= e_peak:
        return modulus * strain
    plateau_end = peak * 0.85
    if strain <= DENSIFICATION_STRAIN:
        return peak * (1 - 0.15 * (strain - e_peak) / (DENSIFICATION_STRAIN - e_peak))
    return plateau_end * math.exp(10 * (strain - DENSIFICATION_STRAIN))


def curve(modulus: float, peak: float, max_strain_pct: float = 60, step_pct: float = 0.5):
    n = int(max_strain_pct / step_pct)
    return [[round(i * step_pct, 2), round(stress_at(i * step_pct / 100, modulus, peak), 4)] for i in range(n + 1)]
