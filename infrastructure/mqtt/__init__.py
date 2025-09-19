from .client import mqtt_client, MQTTConnectionStatus
from .topics import mqtt_topics, TopicDefinition

__all__ = [
    'mqtt_client',
    'mqtt_topics',
    'MQTTConnectionStatus',
    'TopicDefinition'
]


def initialize_mqtt():
    if not mqtt_client.initialize():
        raise RuntimeError("Falha ao inicializar cliente MQTT")

    if not mqtt_client.connect():
        raise RuntimeError("Falha ao conectar no broker MQTT")

    return mqtt_client


def shutdown_mqtt():
    mqtt_client.disconnect()