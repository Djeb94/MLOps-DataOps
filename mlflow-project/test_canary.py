import math
import sys

import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
HOUSE = {"size": 100, "nb_rooms": 3, "garden": 1}
N_REQUESTS = 500
TIMEOUT = 120

session = requests.Session()
failures = 0


def check(name, condition, detail=""):
    global failures
    if not condition:
        failures += 1
    status = "OK   " if condition else "ÉCHEC"
    print(f"[{status}] {name}" + (f" -> {detail}" if detail else ""))


def health():
    r = session.get(f"{BASE_URL}/health", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def update(version):
    r = session.post(f"{BASE_URL}/update-model", json={"version": version}, timeout=TIMEOUT)
    return r.status_code, r.json()


def accept():
    r = session.post(f"{BASE_URL}/accept-next-model", timeout=TIMEOUT)
    return r.status_code, r.json()


def predict():
    r = session.post(f"{BASE_URL}/predict", json=HOUSE, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


# 0. Point de départ connu : current = next = version 1
print("--- Préparation : current = next = version 1")
code, body = update(1)
check("POST /update-model version 1 répond 200", code == 200, str(body))
code, body = accept()
check("POST /accept-next-model répond 200", code == 200, str(body))
h = health()
p = h["canary_p"]
check("current et next valent tous les deux 1", h["current_version"] == "1" and h["next_version"] == "1", str(h))

# 1. Tant que current = next, toutes les prédictions sont identiques
print("--- Étape 1 : current = next")
results = [predict() for _ in range(20)]
check("20 prédictions faites avec la version 1", all(r["model_version"] == "1" for r in results))
check("les 20 prédictions sont identiques", len({r["y_pred"] for r in results}) == 1)

# 2. /update-model ne modifie que next
print("--- Étape 2 : chargement du candidat dans next")
code, body = update(2)
check("POST /update-model version 2 répond 200", code == 200, str(body))
h = health()
check("current reste en version 1", h["current_version"] == "1", str(h))
check("next passe en version 2", h["next_version"] == "2")

# 3. Répartition du trafic entre current et next
print(f"--- Étape 3 : envoi de {N_REQUESTS} requêtes (p = {p})")
results = [predict() for _ in range(N_REQUESTS)]
current_hits = [r for r in results if r["model_role"] == "current"]
next_hits = [r for r in results if r["model_role"] == "next"]

check("les requêtes current utilisent la version 1", all(r["model_version"] == "1" for r in current_hits))
check("les requêtes next utilisent la version 2", all(r["model_version"] == "2" for r in next_hits))

expected_next = N_REQUESTS * (1 - p)
margin = 3 * math.sqrt(N_REQUESTS * p * (1 - p))
check(
    f"environ {1 - p:.0%} du trafic part vers next",
    abs(len(next_hits) - expected_next) <= margin,
    f"{len(next_hits)}/{N_REQUESTS} requêtes vers next (attendu {expected_next:.0f} ± {margin:.0f})",
)

if current_hits and next_hits:
    v1_pred, v2_pred = current_hits[0]["y_pred"], next_hits[0]["y_pred"]
    check("current et next donnent des prédictions différentes", v1_pred != v2_pred,
          f"v1 = {v1_pred:,.0f} / v2 = {v2_pred:,.0f}")

# 4. Une version inexistante ne casse pas next
print("--- Étape 4 : version inexistante")
code, body = update(9999)
check("POST /update-model version 9999 répond 404", code == 404, str(body))
check("next reste en version 2", health()["next_version"] == "2")

# 5. Promotion du candidat
print("--- Étape 5 : promotion de next en current")
code, body = accept()
check("POST /accept-next-model répond 200", code == 200, str(body))
h = health()
check("current et next valent tous les deux 2", h["current_version"] == "2" and h["next_version"] == "2", str(h))
results = [predict() for _ in range(20)]
check("20 prédictions faites avec la version 2", all(r["model_version"] == "2" for r in results))

print()
print("Tous les tests sont passés" if failures == 0 else f"{failures} test(s) en échec")
sys.exit(1 if failures else 0)