from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import RootModel
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import pickle
import json
import os

# from preprocess import build_features
from .preprocess import build_features


# -------------------------------------------------
# FASTAPI APP
# -------------------------------------------------
app = FastAPI(
    title="Agri Market Price Prediction API",
    version="1.0.0"
)

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

MODEL_DIR = os.path.join(BASE_DIR, "models")

# -------------------------------------------------
# LOAD MODEL ARTIFACTS
# -------------------------------------------------
try:
    with open(os.path.join(MODEL_DIR, "trained_model.pkl"), "rb") as f:
        model = pickle.load(f)

    with open(os.path.join(MODEL_DIR, "feature_columns.pkl"), "rb") as f:
        feature_columns = pickle.load(f)

    with open(os.path.join(MODEL_DIR, "model_metadata.json"), "r") as f:
        model_metadata = json.load(f)

except Exception as e:
    raise RuntimeError(f"❌ Failed to load model artifacts: {e}")

# -------------------------------------------------
# LOAD INPUT SCHEMA (NO CSV)
# -------------------------------------------------
try:
    with open(os.path.join(MODEL_DIR, "input_schema.json")) as f:
        INPUT_SCHEMA = json.load(f)
except Exception as e:
    raise RuntimeError(f"❌ Failed to load input_schema.json: {e}")

# -------------------------------------------------
# REQUEST SCHEMA
# -------------------------------------------------
class PredictionRequest(RootModel[Dict[str, Any]]):
    pass

# -------------------------------------------------
# HEALTH & METADATA
# -------------------------------------------------
@app.get("/")
def health():
    return {
        "status": "running",
        "model_info": model_metadata
    }

@app.get("/metadata")
def get_metadata():
    return model_metadata

# =================================================
# 📍 DROPDOWN APIs (JSON-BASED)
# =================================================

@app.get("/states", response_model=List[str])
def get_states():
    return INPUT_SCHEMA["states"]

@app.get("/districts", response_model=List[str])
def get_districts(state: str = Query(...)):
    return INPUT_SCHEMA["districts"].get(state, [])

@app.get("/markets", response_model=List[str])
def get_markets(
    state: str = Query(...),
    district: str = Query(...)
):
    return INPUT_SCHEMA["markets"].get(f"{state}|{district}", [])

@app.get("/commodities", response_model=List[str])
def get_commodities(
    state: str = Query(...),
    district: str = Query(...),
    market: str = Query(...)
):
    return INPUT_SCHEMA["commodities"].get(f"{state}|{district}|{market}", [])

@app.get("/varieties", response_model=List[str])
def get_varieties(
    state: str,
    district: str,
    market: str,
    commodity: str
):
    return INPUT_SCHEMA["varieties"].get(commodity, [])

@app.get("/grades", response_model=List[str])
def get_grades(
    state: str,
    district: str,
    market: str,
    commodity: str,
    variety: str
):
    return INPUT_SCHEMA["grades"].get(f"{commodity}|{variety}", [])

# =================================================
# 🔮 PREDICTION API
# =================================================

@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        # 1️⃣ Raw user input
        raw_input = request.root

        # 2️⃣ Feature engineering (uses fe_data.csv internally)
        engineered = build_features(raw_input)

        # 3️⃣ Validate features
        missing = [f for f in feature_columns if f not in engineered]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing features: {missing}"
            )

        # 4️⃣ Create DataFrame
        X = pd.DataFrame([engineered], columns=feature_columns)

        # 5️⃣ Predict (log scale)
        pred_log = model.predict(X)

        # 6️⃣ Convert back
        prediction_value = float(np.exp(pred_log[0]))

        return {
            "prediction": round(prediction_value, 2),
            "fallback_used": engineered.get("_fallback_level", "exact")
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
