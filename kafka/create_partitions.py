import time

from kafka import KafkaAdminClient, KafkaConsumer
from kafka.admin import NewPartitions
from kafka.errors import InvalidPartitionsError, UnknownTopicOrPartitionError

BOOTSTRAP_SERVERS = "nowledgeable.com:9092"


def list_partitions(topic_name):
    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVERS)
    partitions = consumer.partitions_for_topic(topic_name)
    consumer.close()
    return sorted(partitions) if partitions else []


admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)

topic_partitions = {}

topic = "djebar"

new_partitions = NewPartitions(total_count=2)

topic_partitions[topic] = new_partitions

print(f"Avant : topic '{topic}' -> partitions {list_partitions(topic)}")

try:
    admin_client.create_partitions(topic_partitions)
    print(f"Demande envoyée : '{topic}' passe à {new_partitions.total_count} partitions")
except InvalidPartitionsError as e:
    print(f"Refusé : total_count doit être strictement supérieur au nombre actuel de partitions ({e})")
except UnknownTopicOrPartitionError:
    print(f"Le topic '{topic}' n'existe pas. Envoie d'abord un message dessus avec produce_json.py.")
finally:
    admin_client.close()

time.sleep(2)
print(f"Après : topic '{topic}' -> partitions {list_partitions(topic)}")