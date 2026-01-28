import pandas as pd
import numpy as np
import pickle
import os

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # backend/
PROJECT_DIR = os.path.dirname(BASE_DIR)                    # project root

MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

ENCODER_PATH = os.path.join(MODEL_DIR, "target_encoder.pkl")
FE_DATA_PATH = os.path.join(DATA_DIR, "fe_data.csv")

# -------------------------------------------------
# LOAD RESOURCES
# -------------------------------------------------
with open(ENCODER_PATH, "rb") as f:
    cat_encoder = pickle.load(f)

fe_df = pd.read_csv(FE_DATA_PATH)
fe_df["date"] = pd.to_datetime(fe_df["date"])

CAT_COLS = ["state", "district", "market", "commodity", "variety", "grade"]

# Encode historical categorical columns ONCE
fe_df[CAT_COLS] = cat_encoder.transform(fe_df[CAT_COLS])

# -------------------------------------------------
# UTIL
# -------------------------------------------------
def to_python(d: dict) -> dict:
    return {k: float(v) if isinstance(v, (np.floating, np.integer)) else v for k, v in d.items()}

# -------------------------------------------------
# HIERARCHICAL FALLBACK FILTER
# -------------------------------------------------
FALLBACK_LEVELS = [
    ["state", "district", "market", "commodity", "variety", "grade"],
    ["state", "district", "market", "commodity", "variety"],
    ["state", "district", "market", "commodity"],
    ["state", "commodity"],
    ["commodity"]
]

# -------------------------------------------------
# MAIN FEATURE BUILDER
# -------------------------------------------------
def build_features(raw_input: dict) -> dict:
    # Encode user categorical input
    raw_cat_df = pd.DataFrame([{
        "state": raw_input["state"],
        "district": raw_input["district"],
        "market": raw_input["market"],
        "commodity": raw_input["commodity"],
        "variety": raw_input["variety"],
        "grade": raw_input["grade"],
    }])

    encoded_user = cat_encoder.transform(raw_cat_df).iloc[0]
    user_date = pd.to_datetime(raw_input["date"])

    df = fe_df.copy()

    # --------- APPLY FALLBACK LOGIC ----------
    matched_df = None
    used_level = None

    for level in FALLBACK_LEVELS:
        temp = df.copy()
        for col in level:
            temp = temp[temp[col] == encoded_user[col]]

        if not temp.empty:
            matched_df = temp
            used_level = "+".join(level)
            break

    # Absolute fallback (should almost never happen)
    if matched_df is None or matched_df.empty:
        matched_df = df[df["commodity"] == encoded_user["commodity"]]
        used_level = "commodity_only"

    # --------- NEAREST DATE LOGIC ----------
    matched_df["date_diff"] = (matched_df["date"] - user_date).abs()
    row = matched_df.sort_values("date_diff").iloc[0]

    # --------- FINAL FEATURES ----------
    features = {
        "district": row["district"],
        "market": row["market"],
        "commodity": row["commodity"],
        "variety": row["variety"],
        "grade": row["grade"],
        "state": row["state"],

        "price_spread": row["price_spread"],
        "price_spread_ratio": row["price_spread_ratio"],
        "modal_to_min_ratio": row["modal_to_min_ratio"],
        "modal_to_max_ratio": row["modal_to_max_ratio"],

        "month": int(row["month"]),
        "week": int(row["week"]),
        "month_sin": row["month_sin"],
        "month_cos": row["month_cos"],

        "commodity_price_zscore": row["commodity_price_zscore"],
        "market_avg_price": row["market_avg_price"],
        "state_avg_price": row["state_avg_price"],
        "market_price_deviation": row["market_price_deviation"],

        "lag_1": row["lag_1"],
        "lag_7": row["lag_7"],
        "pct_change_7": row["pct_change_7"],
    }

    # Optional metadata (you can remove if not needed)
    features["_fallback_level"] = used_level

    return to_python(features)
