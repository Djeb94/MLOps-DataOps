import argparse
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "house-price"
MODEL_NAME = "house-price-model"
DATA_PATH = Path(__file__).parent / "houses.csv"
FEATURES = ["size", "nb_rooms", "garden"]
TARGET = "price"
TEST_SIZE = 0.25

parser = argparse.ArgumentParser(description="Entraînement d'un modèle de prix avec suivi MLflow")
parser.add_argument("--n-estimators", type=int, default=100, help="nombre d'arbres")
parser.add_argument("--max-depth", type=int, default=None, help="profondeur maximale des arbres")
parser.add_argument("--log-model", action="store_true", help="sauvegarder le modèle dans le run")
parser.add_argument("--register", action="store_true", help=f"sauvegarder ET enregistrer le modèle sous '{MODEL_NAME}'")
args = parser.parse_args()

log_model = args.log_model or args.register

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

df = pd.read_csv(DATA_PATH)
df[FEATURES] = df[FEATURES].astype("float64")
X = df[FEATURES]
y = df[TARGET]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=42)

params = {
    "n_estimators": args.n_estimators,
    "max_depth": args.max_depth,
    "random_state": 42,
}
run_name = f"rf_n{args.n_estimators}_d{args.max_depth}" + ("_model" if log_model else "")

with mlflow.start_run(run_name=run_name) as run:
    dataset = mlflow.data.from_pandas(df, source=str(DATA_PATH), name="houses", targets=TARGET)
    mlflow.log_input(dataset, context="training")

    mlflow.log_params(params)
    mlflow.log_param("test_size", TEST_SIZE)

    model = RandomForestRegressor(**params)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    metrics = {
        "mse": mse,
        "rmse": mse ** 0.5,
        "mae": mean_absolute_error(y_test, y_pred),
        "r2": r2_score(y_test, y_pred),
    }
    mlflow.log_metrics(metrics)

    model_info = None
    if log_model:
        model_info = mlflow.sklearn.log_model(
            model,
            name="model",
            input_example=X_train.head(3),
            registered_model_name=MODEL_NAME if args.register else None,
        )

    print(f"Run '{run_name}' terminé (run_id = {run.info.run_id})")
    for key, value in metrics.items():
        print(f"  {key} = {value:,.2f}")
    print(f"  modèle sauvegardé : {'oui' if log_model else 'non'}")
    if args.register:
        print(f"  enregistré dans le registry : {MODEL_NAME}, version {model_info.registered_model_version}")