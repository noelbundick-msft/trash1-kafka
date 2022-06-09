from confluent_kafka import Producer

p = Producer({
    "bootstrap.servers": "localhost:9092"
})
