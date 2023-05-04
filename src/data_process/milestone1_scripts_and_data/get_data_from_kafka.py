from os import path
import sys, os
from datetime import datetime
from json import dumps, loads
from time import sleep
from random import randint
import numpy as np
# ssh -o ServerAliveInterval=60 -L 9092:localhost:9092 tunnel@128.2.24.106 -NTf
from kafka import KafkaConsumer, KafkaProducer

# Update this for your demo otherwise you'll see my data :)
# topic = 'recitation-d'
topic = 'movielog20'
#topic = 'recitation-d'
"""
# Create a producer to write data to kafka
# Ref: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                        value_serializer=lambda x: dumps(x).encode('utf-8'),
                        )
cities = ['Pittsburgh','New York','London','Bangalore','Shanghai','Tokyo','Munich']
# Write data via the producer
print("Writing to Kafka Broker")
for i in range(10):
    data = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")},{cities[randint(0,len(cities)-1)]},{randint(18, 32)}ºC'
    print(f"Writing: {data}")
    producer.send(topic=topic, value=data)
    sleep(1)
"""
# Create a consumer to read data from kafka
# Ref: https://kafka-python.readthedocs.io/en/master/apidoc/KafkaConsumer.html
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=['localhost:9092'],
    # Read from the start of the topic; Default is latest
    #auto_offset_reset='earliest',
    #auto_offset_reset='latest',
    group_id='team20',
    # Commit that an offset has been read
    enable_auto_commit=True,
    # How often to tell Kafka, an offset has been read
    auto_commit_interval_ms=1000
)

print('Reading Kafka Broker')

data_count = 0
rate_count = 0
total_count = 0 

max_for_each_type = 10000
#max_total_count = 50000



for message in consumer:
    #total_count += 1

    if (data_count >= max_for_each_type) and (rate_count >= max_for_each_type):
        break
    #elif total_count > max_total_count:
    #    break

    else:
        message = message.value.decode()
        # Default message.value type is bytes!
        # print(loads(message))
        print(message)
        if ("/data/" in message) and (data_count <= max_for_each_type):
            os.system(f"echo {message} >> kafka_movielog.csv")
            data_count += 1
        elif ("/rate/" in message) and (rate_count <= max_for_each_type):
            os.system(f"echo {message} >> kafka_movielog_rate.csv")
            rate_count += 1

