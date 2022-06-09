import signal
import sys
import time
from confluent_kafka import Consumer
from azure.identity import DefaultAzureCredential


# AAD
cred = DefaultAzureCredential()


def _get_token(config):
    """Note here value of config comes from sasl.oauthbearer.config below.
    It is not used in this example but you can put arbitrary values to
    configure how you can get the token (e.g. which token URL to use)
    """
    access_token = cred.get_token(
        "https://kafka-6tp98k.servicebus.windows.net")
    return access_token.token, time.time() + access_token.expires_on


consumer = Consumer({
    "bootstrap.servers": "kafka-6tp98k.servicebus.windows.net:9093",
    "sasl.mechanism": "OAUTHBEARER",
    "security.protocol": "SASL_SSL",
    "oauth_cb": _get_token,
    "group.id": "consumer",
    # "debug": "broker,topic,msg"
})


def signal_handler(sig, frame):
    print("exiting")
    consumer.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

print("consuming topic1")
consumer.subscribe(["topic1"])

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print(f"Consumer error: {msg.error()}")
        continue

    print(
        f"Received message [{msg.partition()}]: {msg.value().decode('utf-8')}")
