import sys

from kafka import KafkaConsumer

from config import BOOTSTRAP_SERVERS, TOPIC_PREDICTIONS

topic = sys.argv[1] if len(sys.argv) > 1 else TOPIC_PREDICTIONS

consumer = KafkaConsumer(
    topic,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="latest",
    value_deserializer=lambda v: v.decode("utf-8", errors="replace"),
)

print(f"En écoute sur '{topic}'... (Ctrl+C pour arrêter)")

try:
    for message in consumer:
        print(f"[partition {message.partition} | offset {message.offset}] {message.value}")
except KeyboardInterrupt:
    print("Arrêt demandé.")
finally:
    consumer.close()