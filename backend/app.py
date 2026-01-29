from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import RootModel
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import pickle
import json
import os

from .preprocess import build_features

# =================================================
# FASTAPI APP
# =================================================
app = FastAPI(
    title="Agri Market Price Prediction API",
    version="1.0.0"
)

# =================================================
# CORS
# =================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =================================================
# PATHS
# =================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# =================================================
# LOAD MODEL & ARTIFACTS
# =================================================
try:
    with open(os.path.join(MODEL_DIR, "trained_model.pkl"), "rb") as f:
        model = pickle.load(f)

    with open(os.path.join(MODEL_DIR, "feature_columns.pkl"), "rb") as f:
        feature_columns = pickle.load(f)

    with open(os.path.join(MODEL_DIR, "model_metadata.json"), "r") as f:
        model_metadata = json.load(f)

    with open(os.path.join(MODEL_DIR, "input_schema.json"), "r") as f:
        INPUT_SCHEMA = json.load(f)

except Exception as e:
    raise RuntimeError(f"Failed to load model artifacts: {e}")

# =================================================
# REQUEST SCHEMA
# =================================================
class PredictionRequest(RootModel[Dict[str, Any]]):
    pass

# =================================================
# HEALTH
# =================================================
@app.get("/")
def health():
    return {
        "status": "running",
        "model_info": model_metadata
    }

# =================================================
# DROPDOWN ROUTES
# =================================================
@app.get("/states", response_model=List[str])
def get_states():
    return INPUT_SCHEMA.get("states", [])

@app.get("/districts", response_model=List[str])
def get_districts(state: str = Query(...)):
    return INPUT_SCHEMA.get("districts", {}).get(state, [])

@app.get("/markets", response_model=List[str])
def get_markets(
    state: str = Query(...),
    district: str = Query(...)
):
    return INPUT_SCHEMA.get("markets", {}).get(f"{state}|{district}", [])

@app.get("/commodities", response_model=List[str])
def get_commodities(
    state: str = Query(...),
    district: str = Query(...),
    market: str = Query(...)
):
    return INPUT_SCHEMA.get("commodities", {}).get(
        f"{state}|{district}|{market}", []
    )

@app.get("/varieties", response_model=List[str])
def get_varieties(commodity: str = Query(...)):
    return INPUT_SCHEMA.get("varieties", {}).get(commodity, [])

@app.get("/grades", response_model=List[str])
def get_grades(
    commodity: str = Query(...),
    variety: str = Query(...)
):
    return INPUT_SCHEMA.get("grades", {}).get(
        f"{commodity}|{variety}", []
    )

# =================================================
# PREDICTION
# =================================================
@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        raw_input = request.root

        # Feature engineering (date accepted but not required)
        engineered = build_features(raw_input)

        # Align feature order
        X = pd.DataFrame([engineered], columns=feature_columns)

        # Predict (log → normal)
        pred_log = model.predict(X)
        prediction_value = float(np.exp(pred_log[0]))

        return {
            "prediction": round(prediction_value, 2),
            "fallback_used": engineered.get("_fallback_level")
        }

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required field: {str(e)}"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
