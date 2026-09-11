import sys

from kafka import KafkaConsumer, TopicPartition

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"
TOPIC = "djebar"
PARTITION = int(sys.argv[1]) if len(sys.argv) > 1 else 0

consumer = KafkaConsumer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id="grp1",
    auto_offset_reset="latest",
    value_deserializer=lambda v: v.decode("utf-8", errors="replace"),
)

available = consumer.partitions_for_topic(TOPIC) or set()
if PARTITION not in available:
    print(f"La partition {PARTITION} n'existe pas pour '{TOPIC}' (partitions : {sorted(available)})")
    consumer.close()
    sys.exit(1)

topic_partition = TopicPartition(TOPIC, PARTITION)
consumer.assign([topic_partition])

print(f"Consumer assigné à '{TOPIC}', partition {PARTITION} (group_id=grp1). Ctrl+C pour arrêter.")

try:
    for message in consumer:
        print(f"[partition {message.partition} | offset {message.offset}] {message.value}")
except KeyboardInterrupt:
    print("Arrêt demandé.")
finally:
    consumer.close()