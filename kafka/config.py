from pathlib import Path

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
AUTHOR = "gd"
NOM = "djebar"

TOPIC_HOUSES = f"houses_{NOM}"
TOPIC_PREDICTIONS = f"prediction_{NOM}"

MODEL_PATH = Path(__file__).parent / "house_model.joblib"
FEATURES = ["size", "nb_rooms", "garden"]