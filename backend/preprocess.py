import pickle
import os
import numpy as np

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

STORE_PATH = os.path.join(MODEL_DIR, "feature_store.pkl")

# -------------------------------------------------
# LOAD FEATURE STORE
# -------------------------------------------------
with open(STORE_PATH, "rb") as f:
    FEATURE_STORE = pickle.load(f)

# -------------------------------------------------
# FALLBACK LEVELS (MOST → LEAST SPECIFIC)
# -------------------------------------------------
FALLBACK_LEVELS = [
    ["state", "district", "market", "commodity", "variety", "grade"],
    ["state", "district", "market", "commodity", "variety"],
    ["state", "district", "market", "commodity"],
    ["state", "commodity"],
    ["commodity"]
]

# -------------------------------------------------
# UTIL
# -------------------------------------------------
def to_python(d: dict) -> dict:
    return {
        k: float(v) if isinstance(v, (np.integer, np.floating)) else v
        for k, v in d.items()
    }

# -------------------------------------------------
# MAIN FEATURE BUILDER
# -------------------------------------------------
def build_features(raw_input: dict) -> dict:
    """
    raw_input includes:
    state, district, market, commodity, variety, grade, date
    (date is accepted but not required for lookup)
    """

    # Validate required categorical fields
    required = ["state", "district", "market", "commodity", "variety", "grade"]
    for field in required:
        if field not in raw_input:
            raise KeyError(field)

    # Try fallback levels
    for level in FALLBACK_LEVELS:
        key_vals = tuple(raw_input[col] for col in level)
        lookup_key = (tuple(level), key_vals)

        if lookup_key in FEATURE_STORE:
            features = FEATURE_STORE[lookup_key].copy()
            features["_fallback_level"] = "+".join(level)
            return to_python(features)

    raise ValueError("No matching feature group found")
