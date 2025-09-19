import logging
from .handlers import mqtt_handlers
from .client import mqtt_client

logger = logging.getLogger(__name__)


def setup_mqtt_integration(device_service, temperature_service):
    logger.info("Configurando integração MQTT com services")

    mqtt_handlers.register_services(device_service, temperature_service)

    def on_mqtt_connected(connected: bool):
        if connected:
            logger.info("MQTT conectado, configurando subscriptions")
            mqtt_handlers.setup_subscriptions()
        else:
            logger.warning("MQTT desconectado")

    mqtt_client.add_connection_callback(on_mqtt_connected)

    if mqtt_client.is_connected():
        mqtt_handlers.setup_subscriptions()

    logger.info("Integração MQTT configurada com sucesso")


def send_device_command(device_id: str, command_type: str, **kwargs) -> bool:
    if command_type == "withdraw":
        slot = kwargs.get('slot')
        if slot is None:
            logger.error("Comando withdraw requer parâmetro 'slot'")
            return False
        return mqtt_handlers.send_withdraw_command(device_id, slot)
    else:
        logger.error(f"Tipo de comando não suportado: {command_type}")
        return False