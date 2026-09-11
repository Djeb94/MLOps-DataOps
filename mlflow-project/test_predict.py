import sys

import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
TIMEOUT = 30
failures = 0


def check(name, condition, detail=""):
    global failures
    if not condition:
        failures += 1
    status = "OK   " if condition else "ÉCHEC"
    print(f"[{status}] {name}" + (f" -> {detail}" if detail else ""))


def json_or_empty(response):
    try:
        return response.json()
    except ValueError:
        return {}


# 1. Le service répond et les deux modèles sont chargés
r = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
health = json_or_empty(r)
check("GET /health répond 200", r.status_code == 200, str(health))
check("les modèles current et next sont chargés",
      health.get("current_version") is not None and health.get("next_version") is not None)

# 2. Prédiction valide
house = {"size": 100, "nb_rooms": 3, "garden": 1}
r = requests.post(f"{BASE_URL}/predict", json=house, timeout=TIMEOUT)
body = json_or_empty(r)
check("POST /predict valide répond 200", r.status_code == 200, str(body))
check("y_pred est un nombre positif", isinstance(body.get("y_pred"), (int, float)) and body["y_pred"] > 0)
check("model_role vaut current ou next", body.get("model_role") in ("current", "next"))
expected_version = health.get(f"{body.get('model_role')}_version")
check("model_version correspond au rôle indiqué", body.get("model_version") == expected_version,
      f"{body.get('model_role')} -> version {body.get('model_version')}")

# 3. Déterminisme : vérifiable seulement si current et next sont le même modèle
if health.get("current_version") == health.get("next_version"):
    r = requests.post(f"{BASE_URL}/predict", json=house, timeout=TIMEOUT)
    check("la prédiction est déterministe", json_or_empty(r).get("y_pred") == body.get("y_pred"))
else:
    print("[INFO ] déterminisme non vérifié : current et next sont des versions différentes")

# 4. Les entrées invalides sont refusées
invalid_cases = {
    "garden hors de [0, 1]": {**house, "garden": 5},
    "size négative": {**house, "size": -10},
    "champ manquant": {"size": 100, "nb_rooms": 3},
    "texte au lieu d'un nombre": {**house, "size": "grand"},
}
for label, payload in invalid_cases.items():
    r = requests.post(f"{BASE_URL}/predict", json=payload, timeout=TIMEOUT)
    check(f"POST /predict avec {label} répond 422", r.status_code == 422, f"code {r.status_code}")

print()
print("Tous les tests sont passés" if failures == 0 else f"{failures} test(s) en échec")
sys.exit(1 if failures else 0)