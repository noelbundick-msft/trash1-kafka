import time
from confluent_kafka import Producer
from azure.identity import DefaultAzureCredential

# AAD
cred = DefaultAzureCredential()


def _get_token(config):
    """Note here value of config comes from sasl.oauthbearer.config below.
    It is not used in this example but you can put arbitrary values to
    configure how you can get the token (e.g. which token URL to use)
    """
    access_token = cred.get_token(
        "https://kafka-6tp98k.servicebus.windows.net/.default")
    return access_token.token, time.time() + access_token.expires_on


producer = Producer({
    "bootstrap.servers": "kafka-6tp98k.servicebus.windows.net:9093",
    "sasl.mechanism": "OAUTHBEARER",
    "security.protocol": "SASL_SSL",
    "oauth_cb": _get_token,
    "enable.idempotence": True,
    "acks": "all",
    # "debug": "broker,topic,msg"
})


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush()."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


some_data_source = [str(i) for i in range(1000)]
for data in some_data_source:
    # Trigger any available delivery report callbacks from previous produce() calls
    producer.poll(0)

    # Asynchronously produce a message, the delivery report callback
    # will be triggered from poll() above, or flush() below, when the message has
    # been successfully delivered or failed permanently.
    producer.produce("topic1", data.encode("utf-8"), callback=delivery_report)

# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
producer.flush()
