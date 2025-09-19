from dataclasses import dataclass
from typing import List

from application.config import get_config


@dataclass
class TopicDefinition:
    topic: str
    qos: int = 1
    description: str = ""


class MQTTTopics:

    def __init__(self):
        self.config = get_config()

    @property
    def device_connection_request(self) -> TopicDefinition:
        return TopicDefinition(
            "devices/connection/request",
            qos=1,
            description="Solicitação de conexão de dispositivos"
        )

    def device_connection_response(self, device_id: str) -> TopicDefinition:
        return TopicDefinition(
            f"devices/connection/response/{device_id}",
            qos=1,
            description=f"Resposta de autorização para {device_id}"
        )

    def device_ping(self, device_id: str) -> TopicDefinition:
        return TopicDefinition(
            f"devices/ping/{device_id}",
            qos=0,
            description=f"Ping do dispositivo {device_id}"
        )

    def device_withdraw(self, device_id: str, slot: str = "+") -> TopicDefinition:
        return TopicDefinition(
            f"devices/withdraw/{device_id}/{slot}",
            qos=1,
            description=f"Comandos de dispensação para {device_id}"
        )

    def device_temperature(self, device_id: str) -> TopicDefinition:
        return TopicDefinition(
            f"devices/temperature/{device_id}",
            qos=1,
            description=f"Dados de temperatura do {device_id}"
        )

    def get_device_wildcard_topics(self) -> List[TopicDefinition]:
        return [
            TopicDefinition(
                "devices/connection/request",
                qos=1,
                description="Todas as solicitações de conexão"
            ),
            TopicDefinition(
                "devices/ping/+",
                qos=0,
                description="Ping de todos os dispositivos"
            ),
            TopicDefinition(
                "devices/temperature/+",
                qos=1,
                description="Temperatura de todos os dispositivos"
            )
        ]

    def is_connection_request(self, topic: str) -> bool:
        return topic == "devices/connection/request"

    def is_ping_topic(self, topic: str) -> bool:
        return topic.startswith("devices/ping/")

    def is_temperature_topic(self, topic: str) -> bool:
        return topic.startswith("devices/temperature/")

    def extract_device_id_from_ping(self, topic: str) -> str | None:
        if not self.is_ping_topic(topic):
            return None
        parts = topic.split('/')
        return parts[2] if len(parts) >= 3 else None

    def extract_device_id_from_temperature(self, topic: str) -> str | None:
        if not self.is_temperature_topic(topic):
            return None
        parts = topic.split('/')
        return parts[2] if len(parts) >= 3 else None

    def extract_device_and_slot_from_withdraw(self, topic: str) -> tuple[str, str] | None:
        if not topic.startswith("devices/withdraw/"):
            return None
        parts = topic.split('/')
        if len(parts) >= 4:
            return parts[2], parts[3]
        return None


mqtt_topics = MQTTTopics()