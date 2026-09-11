import json
import random
import sys
import time

from kafka import KafkaProducer

from config import BOOTSTRAP_SERVERS, TOPIC_HOUSES

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

for i in range(N):
    house = {
        "id": f"{int(time.time() * 1000)}-{i}",
        "size": round(random.uniform(30, 250), 1),
        "nb_rooms": random.randint(1, 6),
        "garden": random.randint(0, 1),
    }
    metadata = producer.send(TOPIC_HOUSES, key=house["id"].encode("utf-8"), value=house).get(timeout=10)
    print(f"Envoyé {house} -> partition {metadata.partition}")
    time.sleep(0.3)

producer.flush()
producer.close()