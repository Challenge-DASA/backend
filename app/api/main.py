import asyncio
import logging
from quart import Quart
from sqlalchemy import text

from application.config import get_config
from app.api.error_handlers import register_error_handlers
from app.api.routes import register_blueprints
from application.middleware.context import ContextMiddleware
from infrastructure.mqtt import initialize_mqtt, shutdown_mqtt
from infrastructure.mqtt.integration import setup_mqtt_integration
from application.services.device_service import DeviceService
from application.services.temperature_service import TemperatureService
from infrastructure.storage.postgres.database import engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

config = get_config()
app = Quart(__name__)
app.config.from_object(config)
app.json.ensure_ascii = False

device_service = DeviceService()
temperature_service = TemperatureService()

app.device_service = device_service
app.temperature_service = temperature_service

context_middleware = ContextMiddleware(app)

register_error_handlers(app)
register_blueprints(app)


@app.before_serving
async def startup():
    logger.info("Iniciando aplicação SmartLab")

    try:
        logger.info("Testando conexão com PostgreSQL...")
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("✓ PostgreSQL conectado com sucesso!")
        except Exception as db_error:
            logger.error(f"✗ Erro ao conectar no PostgreSQL: {db_error}")
            raise RuntimeError("Database connection failed") from db_error

        logger.info("Inicializando conexão MQTT...")
        mqtt_client_instance = initialize_mqtt()
        logger.info(f"MQTT inicializado. Status: {mqtt_client_instance.get_status().value}")

        await asyncio.sleep(2)

        if mqtt_client_instance.is_connected():
            logger.info("✓ MQTT conectado com sucesso!")
            setup_mqtt_integration(device_service, temperature_service)
            logger.info("Integração MQTT configurada")
        else:
            logger.error("✗ MQTT não conseguiu conectar. Aplicação não pode continuar.")
            raise RuntimeError("MQTT connection failed")

    except Exception as e:
        logger.error(f"Erro crítico ao inicializar aplicação: {e}")
        raise RuntimeError(f"Startup failed: {e}") from e


@app.after_serving
async def shutdown():
    logger.info("Finalizando aplicação SmartLab")

    try:
        logger.info("Desconectando MQTT...")
        shutdown_mqtt()
        logger.info("✓ MQTT desconectado")
    except Exception as e:
        logger.error(f"Erro ao desconectar MQTT: {e}")

    try:
        logger.info("Fechando conexões do PostgreSQL...")
        await engine.dispose()
        logger.info("✓ PostgreSQL desconectado")
    except Exception as e:
        logger.error(f"Erro ao desconectar PostgreSQL: {e}")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)