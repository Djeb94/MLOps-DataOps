import os
import random
import threading
import time
from contextlib import asynccontextmanager
from typing import Literal

import mlflow
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from pydantic import BaseModel, Field

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "house-price-model")
MODEL_VERSION = os.getenv("MODEL_VERSION", "latest")
CANARY_P = float(os.getenv("CANARY_P", "0.9"))
FEATURES = ["size", "nb_rooms", "garden"]
STARTUP_ATTEMPTS = 10

if not 0 <= CANARY_P <= 1:
    raise ValueError(f"CANARY_P doit être compris entre 0 et 1 (reçu : {CANARY_P})")

mlflow.set_tracking_uri(TRACKING_URI)
client = MlflowClient()

state = {"current": None, "next": None}
lock = threading.Lock()


def resolve_version(version) -> str:
    """Transforme 'latest' en numéro de version et vérifie que la version existe."""
    if str(version).lower() == "latest":
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        if not versions:
            raise ValueError(f"Aucune version enregistrée pour le modèle '{MODEL_NAME}'")
        return str(max(int(v.version) for v in versions))
    client.get_model_version(MODEL_NAME, str(version))
    return str(version)


def fetch_model(version) -> dict:
    """Télécharge une version depuis le registry MLflow, sans toucher aux modèles en service."""
    resolved = resolve_version(version)
    model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{resolved}")
    return {"model": model, "version": resolved}


def versions_snapshot() -> dict:
    with lock:
        return {
            "current_version": state["current"]["version"] if state["current"] else None,
            "next_version": state["next"]["version"] if state["next"] else None,
        }


@asynccontextmanager
async def lifespan(app: FastAPI):
    last_error = None
    for attempt in range(1, STARTUP_ATTEMPTS + 1):
        try:
            loaded = fetch_model(MODEL_VERSION)
            with lock:
                state["current"] = loaded
                state["next"] = loaded
            print(
                f"Modèle '{MODEL_NAME}' version {loaded['version']} chargé depuis {TRACKING_URI} "
                f"(current = next, p = {CANARY_P})",
                flush=True,
            )
            break
        except Exception as e:
            last_error = e
            print(f"Chargement du modèle, tentative {attempt}/{STARTUP_ATTEMPTS} échouée : {e}", flush=True)
            time.sleep(3)
    else:
        raise RuntimeError(f"Impossible de charger le modèle au démarrage : {last_error}")
    yield


app = FastAPI(title="House price API (MLflow, canary)", lifespan=lifespan)


class House(BaseModel):
    size: float = Field(gt=0)
    nb_rooms: int = Field(ge=0)
    garden: int = Field(ge=0, le=1)


class UpdateModelRequest(BaseModel):
    version: int | Literal["latest"]


@app.get("/health")
def health():
    return {"status": "ok", "model_name": MODEL_NAME, "canary_p": CANARY_P, **versions_snapshot()}


@app.post("/predict")
def predict(house: House):
    role = "current" if random.random() < CANARY_P else "next"
    with lock:
        slot = state[role]
    df = pd.DataFrame([house.model_dump()], columns=FEATURES).astype("float64")
    prediction = np.asarray(slot["model"].predict(df)).ravel()[0]
    return {
        "y_pred": float(prediction),
        "model_name": MODEL_NAME,
        "model_version": slot["version"],
        "model_role": role,
    }


@app.post("/update-model")
def update_model(request: UpdateModelRequest):
    previous_next = versions_snapshot()["next_version"]
    try:
        loaded = fetch_model(request.version)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MlflowException as e:
        if e.error_code == "RESOURCE_DOES_NOT_EXIST":
            raise HTTPException(status_code=404, detail=f"Version '{request.version}' introuvable pour '{MODEL_NAME}'")
        raise HTTPException(status_code=502, detail=f"Erreur MLflow : {e.message}")

    with lock:
        state["next"] = loaded
    return {
        "message": "Modèle next mis à jour",
        "model_name": MODEL_NAME,
        "previous_next_version": previous_next,
        **versions_snapshot(),
    }


@app.post("/accept-next-model")
def accept_next_model():
    with lock:
        previous_current = state["current"]["version"]
        state["current"] = state["next"]
    return {
        "message": "Le modèle next est maintenant le modèle current",
        "model_name": MODEL_NAME,
        "previous_current_version": previous_current,
        **versions_snapshot(),
    }