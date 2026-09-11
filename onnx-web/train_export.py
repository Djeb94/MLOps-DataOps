from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import pandas as pd
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.linear_model import LinearRegression

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "houses.csv"
MODEL_PATH = BASE_DIR / "model.onnx"
FEATURES = ["size", "nb_rooms", "garden"]
TARGET = "price"

# 1. Entraînement
df = pd.read_csv(DATA_PATH)
X = df[FEATURES].to_numpy(dtype=np.float32)
y = df[TARGET].to_numpy()

model = LinearRegression()
model.fit(X, y)

print("Coefficients :", {f: round(float(c), 2) for f, c in zip(FEATURES, model.coef_)})
print(f"Intercept : {model.intercept_:,.2f}")
print(f"R² sur les données d'entraînement : {model.score(X, y):.3f}")

# 2. Export ONNX
onnx_model = convert_sklearn(
    model,
    initial_types=[("input", FloatTensorType([None, len(FEATURES)]))],
    target_opset={"": 17, "ai.onnx.ml": 3},
)
onnx.checker.check_model(onnx_model)
MODEL_PATH.write_bytes(onnx_model.SerializeToString())
print(f"Modèle exporté dans {MODEL_PATH.name} ({MODEL_PATH.stat().st_size} octets)")

# Vérification : scikit-learn et ONNX Runtime doivent donner la même prédiction
session = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
input_meta = session.get_inputs()[0]
output_meta = session.get_outputs()[0]
print(f"Entrée ONNX : '{input_meta.name}' {input_meta.shape} {input_meta.type}")
print(f"Sortie ONNX : '{output_meta.name}' {output_meta.shape} {output_meta.type}")

house = np.array([[100, 3, 1]], dtype=np.float32)
sklearn_pred = float(model.predict(house)[0])
onnx_pred = float(session.run(None, {input_meta.name: house})[0][0][0])
print(f"Prédiction scikit-learn : {sklearn_pred:,.2f}")
print(f"Prédiction ONNX Runtime : {onnx_pred:,.2f}")
print("Écart relatif :", f"{abs(sklearn_pred - onnx_pred) / abs(sklearn_pred):.2e}")