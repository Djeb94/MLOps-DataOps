import json
import sys

import numpy as np
from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
TOPIC = "djebar"
GROUP_ID = sys.argv[1] if len(sys.argv) > 1 else None

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id=GROUP_ID,
    auto_offset_reset="latest",
)

print(f"En écoute sur '{TOPIC}' | group_id = {GROUP_ID} (Ctrl+C pour arrêter)")

try:
    for message in consumer:
        try:
            payload = json.loads(message.value.decode("utf-8"))
            array = np.array(payload["data"])
            total = array.sum()
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Message ignoré (format invalide) : {e}")
            continue

        print(f"[partition {message.partition} | offset {message.offset}]")
        print(f"  Dictionnaire reçu : {payload}")
        print(f"  Tableau numpy :\n{array}")
        print(f"  Somme : {total}")
except KeyboardInterrupt:
    print("Arrêt demandé.")
finally:
    consumer.close()