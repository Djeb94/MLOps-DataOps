import json

from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
TOPIC = "processed"
AUTHOR = "gd"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="latest",
)

print(f"En écoute sur '{TOPIC}'... (Ctrl+C pour arrêter)")

try:
    for message in consumer:
        try:
            result = json.loads(message.value.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            print(f"[offset {message.offset}] message non JSON : {message.value!r}")
            continue

        is_mine = isinstance(result, dict) and result.get("author") == AUTHOR
        tag = "MOI " if is_mine else "autre"
        print(f"[{tag}] offset {message.offset} : {result}")
except KeyboardInterrupt:
    print("Arrêt demandé.")
finally:
    consumer.close()