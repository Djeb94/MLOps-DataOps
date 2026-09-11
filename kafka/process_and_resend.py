import json

import numpy as np
from kafka import KafkaConsumer, KafkaProducer

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
TOPIC_IN = "djebar"
TOPIC_OUT = "processed"
AUTHOR = "gd"

consumer = KafkaConsumer(
    TOPIC_IN,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id=f"process-{AUTHOR}",
    auto_offset_reset="latest",
)

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

print(f"Traitement : '{TOPIC_IN}' -> '{TOPIC_OUT}' (Ctrl+C pour arrêter)")

try:
    for message in consumer:
        try:
            payload = json.loads(message.value.decode("utf-8"))
            array = np.array(payload["data"])
            total = array.sum().item()
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            print(f"Message ignoré (offset {message.offset}) : {e}")
            continue

        result = {
            "author": AUTHOR,
            "source_topic": message.topic,
            "source_offset": message.offset,
            "sum": total,
        }

        metadata = producer.send(TOPIC_OUT, result).get(timeout=10)
        print(f"Reçu {payload['data']} -> somme {total} -> envoyé sur '{metadata.topic}' (offset {metadata.offset})")
except KeyboardInterrupt:
    print("Arrêt demandé.")
finally:
    producer.flush()
    producer.close()
    consumer.close()