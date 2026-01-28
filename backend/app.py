# from fastapi import FastAPI, HTTPException, Query
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import RootModel
# from typing import Dict, Any, List
# import numpy as np
# import pandas as pd
# import pickle
# import json
# import os

# from preprocess import build_features

# # -------------------------------------------------
# # FASTAPI APP
# # -------------------------------------------------
# app = FastAPI(
#     title="Agri Market Price Prediction API",
#     version="1.0.0"
# )


# app = FastAPI(
#     title="Agri Market Price Prediction API",
#     version="1.0.0"
# )

# # ✅ CORS CONFIGURATION (REQUIRED FOR FRONTEND)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#         "http://localhost:3000",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # -------------------------------------------------
# # PATHS
# # -------------------------------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # backend/
# PROJECT_DIR = os.path.dirname(BASE_DIR)                    # project root

# MODEL_DIR = os.path.join(BASE_DIR, "models")
# DATA_DIR = os.path.join(PROJECT_DIR, "data", "processed")

# FE_DATA_PATH = os.path.join(DATA_DIR, "fe_data.csv")

# # -------------------------------------------------
# # LOAD MODEL ARTIFACTS
# # -------------------------------------------------
# try:
#     with open(os.path.join(MODEL_DIR, "trained_model.pkl"), "rb") as f:
#         model = pickle.load(f)

#     with open(os.path.join(MODEL_DIR, "feature_columns.pkl"), "rb") as f:
#         feature_columns = pickle.load(f)

#     with open(os.path.join(MODEL_DIR, "model_metadata.json"), "r") as f:
#         model_metadata = json.load(f)

# except Exception as e:
#     raise RuntimeError(f"❌ Failed to load model artifacts: {str(e)}")

# # -------------------------------------------------
# # LOAD fe_data.csv ONCE (FOR DROPDOWNS)
# # -------------------------------------------------
# try:
#     fe_df = pd.read_csv(FE_DATA_PATH)
# except Exception as e:
#     raise RuntimeError(f"❌ Failed to load fe_data.csv: {str(e)}")

# # -------------------------------------------------
# # REQUEST SCHEMA
# # -------------------------------------------------
# class PredictionRequest(RootModel[Dict[str, Any]]):
#     """
#     RAW user input:
#     state, district, market, commodity, variety, grade, date
#     """
#     pass

# # -------------------------------------------------
# # HEALTH CHECK
# # -------------------------------------------------

# @app.get("/metadata")
# def get_metadata():
#     return model_metadata


# @app.get("/")
# def health():
#     return {
#         "status": "running",
#         "model_info": model_metadata
#     }

# # =================================================
# # 📍 LOCATION / CASCADING DROPDOWN APIs
# # =================================================

# @app.get("/states", response_model=List[str])
# def get_states():
#     """
#     Return all unique states
#     """
#     states = (
#         fe_df["state"]
#         .dropna()
#         .unique()
#         .tolist()
#     )
#     return sorted(states)


# @app.get("/districts", response_model=List[str])
# def get_districts(state: str = Query(..., description="State name")):
#     """
#     Return districts for a given state
#     """
#     districts = (
#         fe_df[fe_df["state"] == state]["district"]
#         .dropna()
#         .unique()
#         .tolist()
#     )

#     if not districts:
#         raise HTTPException(
#             status_code=404,
#             detail=f"No districts found for state '{state}'"
#         )

#     return sorted(districts)


# @app.get("/markets", response_model=List[str])
# def get_markets(
#     state: str = Query(..., description="State name"),
#     district: str = Query(..., description="District name")
# ):
#     """
#     Return markets for a given state + district
#     """
#     markets = (
#         fe_df[
#             (fe_df["state"] == state) &
#             (fe_df["district"] == district)
#         ]["market"]
#         .dropna()
#         .unique()
#         .tolist()
#     )

#     if not markets:
#         raise HTTPException(
#             status_code=404,
#             detail=f"No markets found for district '{district}' in state '{state}'"
#         )

#     return sorted(markets)


# @app.get("/commodities", response_model=List[str])
# def get_commodities(
#     state: str = Query(...),
#     district: str = Query(...),
#     market: str = Query(...)
# ):
#     """
#     (Optional but useful)
#     Return commodities for a given market
#     """
#     commodities = (
#         fe_df[
#             (fe_df["state"] == state) &
#             (fe_df["district"] == district) &
#             (fe_df["market"] == market)
#         ]["commodity"]
#         .dropna()
#         .unique()
#         .tolist()
#     )

#     return sorted(commodities)


# @app.get("/varieties")
# def get_varieties(
#     state: str,
#     district: str,
#     market: str,
#     commodity: str
# ):
#     varieties = (
#         fe_df[
#             (fe_df["state"] == state) &
#             (fe_df["district"] == district) &
#             (fe_df["market"] == market) &
#             (fe_df["commodity"] == commodity)
#         ]["variety"]
#         .dropna()
#         .unique()
#         .tolist()
#     )
#     return sorted(varieties)


# @app.get("/grades")
# def get_grades(
#     state: str,
#     district: str,
#     market: str,
#     commodity: str,
#     variety: str
# ):
#     grades = (
#         fe_df[
#             (fe_df["state"] == state) &
#             (fe_df["district"] == district) &
#             (fe_df["market"] == market) &
#             (fe_df["commodity"] == commodity) &
#             (fe_df["variety"] == variety)
#         ]["grade"]
#         .dropna()
#         .unique()
#         .tolist()
#     )
#     return sorted(grades)



# # =================================================
# # 🔮 PREDICTION API
# # =================================================

# @app.post("/predict")
# def predict(request: PredictionRequest):
#     try:
#         # 1️⃣ Raw user input
#         raw_input = request.root

#         # 2️⃣ Feature engineering
#         engineered = build_features(raw_input)

#         # 3️⃣ Validate feature completeness
#         missing = [f for f in feature_columns if f not in engineered]
#         if missing:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Missing features: {missing}"
#             )

#         # 4️⃣ Create DataFrame WITH feature names
#         X = pd.DataFrame([engineered], columns=feature_columns)

#         # 5️⃣ Model prediction (log-scale)
#         pred_log = model.predict(X)

#         # 6️⃣ Convert log → actual price
#         prediction_value = float(np.exp(pred_log[0]))

#         return {
#             "prediction": round(prediction_value, 2)
#         }

#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import RootModel
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import pickle
import json
import os

from preprocess import build_features

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
