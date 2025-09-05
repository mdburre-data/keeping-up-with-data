import numpy as np
from scipy.stats import zscore

def momentum_score(ts):
    """
    ts = pandas Series of weekly values
    Returns last score + label
    """
    if len(ts) < 6:
        return 50, "Stable"

    recent = ts[-1]
    prev = ts[-5]
    growth = (recent - prev) / (prev + 1e-6)

    accel = (ts.pct_change().tail(3).mean())

    parts = [
        0.4 * zscore([growth])[-1] if len(ts) > 1 else 0,
        0.3 * zscore([accel])[-1] if len(ts) > 1 else 0,
        0.3 * zscore(np.log1p(ts.values))[-1] if len(ts) > 1 else 0
    ]
    score = int(np.clip(50 + sum(parts) * 10, 0, 100))

    # Label
    if score >= 65 and accel > 0:
        label = "Surging"
    elif score >= 50 and accel > 0:
        label = "Emerging"
    elif accel < 0:
        label = "Cooling"
    else:
        label = "Stable"

    return score, label
