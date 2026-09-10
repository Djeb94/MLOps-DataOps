from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).parent / "regression.joblib"
model = joblib.load(MODEL_PATH)

app = FastAPI(title="House price API")


class House(BaseModel):
    size: float = Field(gt=0)
    nb_rooms: int = Field(ge=0)
    garden: int = Field(ge=0, le=1)


def run_prediction(house: House) -> float:
    df = pd.DataFrame([house.model_dump()])
    if hasattr(model, "feature_names_in_"):
        df = df[list(model.feature_names_in_)]
    return float(model.predict(df)[0])


@app.get("/predict")
def predict_get(house: Annotated[House, Query()]):
    return {"y_pred": run_prediction(house)}


@app.post("/predict")
def predict_post(house: House):
    return {"y_pred": run_prediction(house)}