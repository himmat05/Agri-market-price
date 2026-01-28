import pandas as pd
import json
from collections import defaultdict
import os

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # backend/
PROJECT_DIR = os.path.dirname(BASE_DIR)                    # project root
DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

FE_DATA_PATH = os.path.join(DATA_DIR, "fe_data.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "models", "input_schema.json")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(FE_DATA_PATH)

schema = {
    "states": sorted(df["state"].dropna().unique().tolist()),
    "districts": defaultdict(set),
    "markets": defaultdict(set),
    "commodities": defaultdict(set),
    "varieties": defaultdict(set),
    "grades": defaultdict(set),
}

# -----------------------------
# EXTRACT ALL VALUES
# -----------------------------
for _, r in df.iterrows():
    schema["districts"][r["state"]].add(r["district"])
    schema["markets"][f"{r['state']}|{r['district']}"].add(r["market"])
    schema["commodities"][f"{r['state']}|{r['district']}|{r['market']}"].add(r["commodity"])
    schema["varieties"][r["commodity"]].add(r["variety"])
    schema["grades"][f"{r['commodity']}|{r['variety']}"].add(r["grade"])

# -----------------------------
# CONVERT SETS → LISTS
# -----------------------------
final_schema = {}
for key, value in schema.items():
    if isinstance(value, dict):
        final_schema[key] = {k: sorted(list(v)) for k, v in value.items()}
    else:
        final_schema[key] = value

# -----------------------------
# SAVE JSON
# -----------------------------
with open(OUTPUT_PATH, "w") as f:
    json.dump(final_schema, f, indent=2)

print("✅ input_schema.json generated successfully")
