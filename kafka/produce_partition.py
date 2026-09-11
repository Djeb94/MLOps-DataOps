import random
import sys
import time

from kafka import KafkaProducer

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
TOPIC = "djebar"
NOM = "Gaël"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 10

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: v.encode("utf-8"),
)

for i in range(N):
    partition = random.randint(0, 1)
    text = f"coucou {NOM} n°{i}"
    metadata = producer.send(TOPIC, value=text, partition=partition).get(timeout=10)
    print(f"Envoyé '{text}' -> partition {metadata.partition} (offset {metadata.offset})")
    time.sleep(0.5)

producer.flush()
producer.close()