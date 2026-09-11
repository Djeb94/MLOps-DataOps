import time

from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from config import BOOTSTRAP_SERVERS, TOPIC_HOUSES, TOPIC_PREDICTIONS

NUM_PARTITIONS = 3
TOPICS = [TOPIC_HOUSES, TOPIC_PREDICTIONS]

admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)
for name in TOPICS:
    try:
        admin.create_topics([NewTopic(name=name, num_partitions=NUM_PARTITIONS, replication_factor=1)])
        print(f"Topic '{name}' créé avec {NUM_PARTITIONS} partitions")
    except TopicAlreadyExistsError:
        print(f"Topic '{name}' existe déjà")
admin.close()

time.sleep(2)
consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS)
consumer.topics()
for name in TOPICS:
    print(f"{name} -> partitions {sorted(consumer.partitions_for_topic(name) or [])}")
consumer.close()