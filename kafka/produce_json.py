import json

from kafka import KafkaProducer

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
TOPIC = "djebar"

producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)

data = {"data": [[1, 2], [3, 4]]}

json_text = json.dumps(data)
message = json_text.encode("utf-8")

future = producer.send(TOPIC, message)
metadata = future.get(timeout=10)

print(f"Envoyé : {json_text}")
print(f"Topic '{metadata.topic}', partition {metadata.partition}, offset {metadata.offset}")
print(f"Nombre de partitions du topic : {len(producer.partitions_for(TOPIC))}")

producer.flush()
producer.close()