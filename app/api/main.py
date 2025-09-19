import asyncio
import logging
from quart import Quart
from quart_schema import QuartSchema, Info

from application.config import get_config
from app.api.error_handlers import register_error_handlers
from app.api.routes import register_blueprints
from application.middleware.context import ContextMiddleware
from infrastructure.mqtt import initialize_mqtt, shutdown_mqtt

logger = logging.getLogger(__name__)

config = get_config()
app = Quart(__name__)
app.config.from_object(config)

QuartSchema(
    app,
    info=Info(
        title="SmartLab API",
        version="1.0.0",
        description="API for managing SmartLab",
    ),
)

context_middleware = ContextMiddleware(app)

register_error_handlers(app)
register_blueprints(app)


@app.before_serving
async def startup():
    logger.info("Iniciando aplicação SmartLab")

    try:
        logger.info("Inicializando conexão MQTT...")
        mqtt_client_instance = initialize_mqtt()
        logger.info(f"MQTT inicializado. Status: {mqtt_client_instance.get_status().value}")

        if mqtt_client_instance.is_connected():
            logger.info("MQTT conectado com sucesso!")
        else:
            logger.error("MQTT não conseguiu conectar. Aplicação não pode continuar.")
            raise RuntimeError("MQTT connection failed")

    except Exception as e:
        logger.error(f"Erro crítico ao inicializar MQTT: {e}")
        raise RuntimeError(f"Startup failed: {e}") from e


@app.after_serving
async def shutdown():
    logger.info("Finalizando aplicação SmartLab")

    try:
        logger.info("Desconectando MQTT...")
        shutdown_mqtt()
        logger.info("MQTT desconectado")
    except Exception as e:
        logger.error(f"Erro ao desconectar MQTT: {e}")


if __name__ == "__main__":
    app.run(debug=config.DEBUG)