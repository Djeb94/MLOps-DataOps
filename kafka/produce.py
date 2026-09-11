from kafka import KafkaProducer

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
TOPIC = "exo1"
NOM = "Gaël"

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: v.encode("utf-8"),
)

future = producer.send(TOPIC, f"coucou {NOM}")
metadata = future.get(timeout=10)
print(f"Message envoyé sur '{metadata.topic}', partition {metadata.partition}, offset {metadata.offset}")

producer.flush()
producer.close()