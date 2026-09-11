import argparse
import json
import os
import socket

from kafka import KafkaConsumer, KafkaProducer

from config import AUTHOR, BOOTSTRAP_SERVERS, FEATURES, TOPIC_HOUSES, TOPIC_PREDICTIONS
from model_utils import load_model, predict_price

parser = argparse.ArgumentParser()
parser.add_argument("--send", action="store_true", help="envoyer les prédictions sur le topic de sortie")
args = parser.parse_args()

WORKER = f"{socket.gethostname()}-{os.getpid()}"

model = load_model()

consumer = KafkaConsumer(
    TOPIC_HOUSES,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id=f"predict-{AUTHOR}",
    auto_offset_reset="latest",
    value_deserializer=lambda v: v.decode("utf-8", errors="replace"),
)

producer = None
if args.send:
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

destination = f"affichage + envoi sur '{TOPIC_PREDICTIONS}'" if producer else "affichage seulement"
print(f"[{WORKER}] En écoute sur '{TOPIC_HOUSES}' ({destination}). Ctrl+C pour arrêter.")

try:
    for message in consumer:
        try:
            house = json.loads(message.value)
            prediction = predict_price(model, house)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            print(f"Message ignoré (partition {message.partition}, offset {message.offset}) : {e}")
            continue

        print(f"[{WORKER}] partition {message.partition} | {house} -> {prediction:,.0f}")

        if producer:
            result = {
                "id": house.get("id"),
                "input": {f: house[f] for f in FEATURES},
                "prediction": prediction,
                "author": AUTHOR,
                "worker": WORKER,
            }
            key = str(house["id"]).encode("utf-8") if "id" in house else None
            producer.send(TOPIC_PREDICTIONS, key=key, value=result).get(timeout=10)
except KeyboardInterrupt:
    print("Arrêt demandé.")
finally:
    if producer:
        producer.flush()
        producer.close()
    consumer.close()