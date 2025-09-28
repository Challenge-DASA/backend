import json
import logging
from typing import Dict, Any

from .client import mqtt_client
from .topics import mqtt_topics

logger = logging.getLogger(__name__)


class MQTTHandlers:

    def __init__(self):
        self.device_service = None
        self.temperature_service = None

    def register_services(self, device_service, temperature_service):
        self.device_service = device_service
        self.temperature_service = temperature_service

    def setup_subscriptions(self):
        mqtt_client.subscribe(
            mqtt_topics.device_connection_request.topic,
            handler=self.handle_connection_request
        )

        mqtt_client.subscribe(
            "devices/ping/+",
            handler=self.handle_device_ping
        )

        mqtt_client.subscribe(
            "devices/temperature/+",
            handler=self.handle_temperature_data
        )

        logger.info("MQTT subscriptions configuradas")

    def handle_connection_request(self, topic: str, payload: str, qos: int, retain: bool):
        try:
            device_id = payload.strip()
            logger.info(f"Solicitação de conexão recebida do dispositivo: {device_id}")

            if self.device_service:
                success = self.device_service.authorize_device(device_id)
                if success:
                    response_topic = mqtt_topics.device_connection_response(device_id).topic
                    mqtt_client.publish(response_topic, "authorized")
                    logger.info(f"Dispositivo {device_id} autorizado")
                else:
                    logger.warning(f"Dispositivo {device_id} não autorizado")

                self.send_authorize_command()
            else:
                response_topic = mqtt_topics.device_connection_response(device_id).topic
                mqtt_client.publish(response_topic, "authorized")
                logger.info(f"Dispositivo {device_id} autorizado (sem validação)")

        except Exception as e:
            logger.error(f"Erro ao processar solicitação de conexão: {e}")

    def handle_device_ping(self, topic: str, payload: str, qos: int, retain: bool):
        try:
            device_id = mqtt_topics.extract_device_id_from_ping(topic)
            if device_id:
                logger.info(f"Ping recebido do dispositivo: {device_id}")

                if self.device_service:
                    self.device_service.update_device_heartbeat(device_id)
            else:
                logger.warning(f"Não foi possível extrair device_id do ping: {topic}")

        except Exception as e:
            logger.error(f"Erro ao processar ping: {e}")

    def handle_temperature_data(self, topic: str, payload: str, qos: int, retain: bool):
        try:
            device_id = mqtt_topics.extract_device_id_from_temperature(topic)
            if not device_id:
                logger.warning(f"Não foi possível extrair device_id da temperatura: {topic}")
                return

            temperature_data = json.loads(payload)
            logger.info(
                f"Dados de temperatura recebidos do dispositivo {device_id}: {len(temperature_data.get('readings', []))} leituras")

            if self.temperature_service:
                self.temperature_service.process_temperature_data(device_id, temperature_data)
            else:
                logger.warning("Temperature service não configurado, dados não processados")

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON de temperatura: {e}")
        except Exception as e:
            logger.error(f"Erro ao processar dados de temperatura: {e}")

    def send_withdraw_command(self, device_id: str, slot: int) -> bool:
        try:
            topic = mqtt_topics.device_withdraw(device_id, str(slot)).topic
            success = mqtt_client.publish(topic, str(slot))

            if success:
                logger.info(f"Comando de withdraw enviado para {device_id}, slot {slot}")
            else:
                logger.error(f"Falha ao enviar comando de withdraw para {device_id}")

            return success

        except Exception as e:
            logger.error(f"Erro ao enviar comando de withdraw: {e}")
            return False

    def send_authorize_command(self):
        mqtt_client.publish(topic="devices/connection/response/smartlab_001", payload=json.dumps({
            "status": "approved",
            "device_id": "smartlab_001"
        }))

mqtt_handlers = MQTTHandlers()