import joblib
import pandas as pd

from config import FEATURES, MODEL_PATH


def load_model(path=MODEL_PATH):
    """Charge le modèle sauvegardé avec joblib et le retourne."""
    return joblib.load(path)


def predict_price(model, house: dict) -> float:
    """Prédit le prix d'une maison décrite par un dictionnaire."""
    missing = [f for f in FEATURES if f not in house]
    if missing:
        raise KeyError(f"champs manquants : {missing}")
    df = pd.DataFrame([{f: house[f] for f in FEATURES}], columns=FEATURES)
    return float(model.predict(df)[0])