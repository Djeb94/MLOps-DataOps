from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from config import FEATURES, MODEL_PATH

DATA_PATH = Path(__file__).resolve().parent.parent / "houses.csv"

df = pd.read_csv(DATA_PATH)
X = df[FEATURES]
y = df["price"]

model = LinearRegression()
model.fit(X, y)

joblib.dump(model, MODEL_PATH)

print(f"Modèle entraîné sur {len(df)} maisons, sauvegardé dans {MODEL_PATH.name}")
print("Coefficients :", {f: round(float(c), 2) for f, c in zip(FEATURES, model.coef_)})