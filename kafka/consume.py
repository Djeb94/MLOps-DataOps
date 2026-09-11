from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
TOPIC = "exo1"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="latest",
    value_deserializer=lambda v: v.decode("utf-8", errors="replace"),
)

print(f"En écoute sur le topic '{TOPIC}'... (Ctrl+C pour arrêter)")

try:
    for message in consumer:
        print(f"[partition {message.partition} | offset {message.offset}] {message.value}")
except KeyboardInterrupt:
    print("Arrêt demandé.")
finally:
    consumer.close()