from model_utils import load_model, predict_price

model = load_model()
house = {"size": 100, "nb_rooms": 3, "garden": 1}

print("Type de modèle :", type(model).__name__)
print("Prédiction :", predict_price(model, house))