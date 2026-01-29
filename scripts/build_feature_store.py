import pandas as pd
import pickle
import os

# -------- PATHS --------
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_DIR, "data", "processed", "fe_data.csv")
MODEL_DIR = os.path.join(PROJECT_DIR, "backend", "models")

OUT_PATH = os.path.join(MODEL_DIR, "feature_store.pkl")

# -------- LOAD DATA --------
df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

# -------- FEATURE STORE --------
feature_store = {}

GROUP_LEVELS = [
    ["state", "district", "market", "commodity", "variety", "grade"],
    ["state", "district", "market", "commodity", "variety"],
    ["state", "district", "market", "commodity"],
    ["state", "commodity"],
    ["commodity"]
]

FEATURE_COLS = [
    "price_spread",
    "price_spread_ratio",
    "modal_to_min_ratio",
    "modal_to_max_ratio",
    "commodity_price_zscore",
    "market_avg_price",
    "state_avg_price",
    "market_price_deviation",
    "lag_1",
    "lag_7",
    "pct_change_7",
    "month",
    "week",
    "month_sin",
    "month_cos",
]

for level in GROUP_LEVELS:
    grouped = df.groupby(level)

    for key, g in grouped:
        key = key if isinstance(key, tuple) else (key,)
        feature_store[(tuple(level), key)] = (
            g.sort_values("date").iloc[-1][FEATURE_COLS].to_dict()
        )

# -------- SAVE --------
with open(OUT_PATH, "wb") as f:
    pickle.dump(feature_store, f)

print("✅ feature_store.pkl created successfully")
