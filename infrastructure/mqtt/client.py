import logging
import threading
import time
from typing import Optional, Callable, Dict, Any
from enum import Enum

import paho.mqtt.client as mqtt

from application.config import get_config

logger = logging.getLogger(__name__)


class MQTTConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CONNECTION_FAILED = "connection_failed"


class MQTTClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return

        self.config = get_config()
        self._client: Optional[mqtt.Client] = None
        self._status = MQTTConnectionStatus.DISCONNECTED
        self._subscriptions: Dict[str, int] = {}
        self._message_handlers: Dict[str, Callable] = {}
        self._connection_callbacks: list = []
        self._is_running = False
        self._reconnect_thread: Optional[threading.Thread] = None
        self._initialized = True

    def initialize(self) -> bool:
        try:
            self._client = mqtt.Client(
                client_id=self.config.MQTT_CLIENT_ID,
                protocol=mqtt.MQTTv311,
                clean_session=True
            )

            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.on_message = self._on_message
            self._client.on_subscribe = self._on_subscribe
            self._client.on_unsubscribe = self._on_unsubscribe
            self._client.on_log = self._on_log

            if self.config.MQTT_USERNAME and self.config.MQTT_PASSWORD:
                self._client.username_pw_set(
                    self.config.MQTT_USERNAME,
                    self.config.MQTT_PASSWORD
                )

            logger.info(f"Cliente MQTT inicializado: {self.config.MQTT_CLIENT_ID}")
            return True

        except Exception as e:
            logger.error(f"Erro ao inicializar cliente MQTT: {e}")
            return False

    def connect(self) -> bool:
        if not self._client:
            if not self.initialize():
                return False

        try:
            self._status = MQTTConnectionStatus.CONNECTING
            logger.info(f"Conectando ao broker MQTT {self.config.MQTT_BROKER_HOST}:{self.config.MQTT_BROKER_PORT}")

            self._client.connect(
                self.config.MQTT_BROKER_HOST,
                self.config.MQTT_BROKER_PORT,
                self.config.MQTT_KEEPALIVE
            )

            self._client.loop_start()
            self._is_running = True

            return True

        except Exception as e:
            logger.error(f"Erro ao conectar no broker MQTT: {e}")
            self._status = MQTTConnectionStatus.CONNECTION_FAILED
            return False

    def disconnect(self):
        if self._client and self._is_running:
            logger.info("Desconectando do broker MQTT")
            self._is_running = False
            self._client.loop_stop()
            self._client.disconnect()
            self._status = MQTTConnectionStatus.DISCONNECTED

    def subscribe(self, topic: str, qos: int = None, handler: Callable = None) -> bool:
        if not self._client or self._status != MQTTConnectionStatus.CONNECTED:
            logger.warning(f"Cliente não conectado. Adicionando {topic} à lista de subscrições pendentes")
            self._subscriptions[topic] = qos or self.config.MQTT_QOS
            if handler:
                self._message_handlers[topic] = handler
            return False

        try:
            qos = qos or self.config.MQTT_QOS
            result = self._client.subscribe(topic, qos)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self._subscriptions[topic] = qos
                if handler:
                    self._message_handlers[topic] = handler
                logger.info(f"Subscrito no tópico: {topic} (QoS: {qos})")
                return True
            else:
                logger.error(f"Erro ao subscrever no tópico {topic}: {result}")
                return False

        except Exception as e:
            logger.error(f"Erro ao subscrever no tópico {topic}: {e}")
            return False

    def unsubscribe(self, topic: str) -> bool:
        if not self._client or self._status != MQTTConnectionStatus.CONNECTED:
            logger.warning(f"Cliente não conectado para dessubscrever de {topic}")
            return False

        try:
            result = self._client.unsubscribe(topic)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self._subscriptions.pop(topic, None)
                self._message_handlers.pop(topic, None)
                logger.info(f"Dessubscrito do tópico: {topic}")
                return True
            else:
                logger.error(f"Erro ao dessubscrever do tópico {topic}: {result}")
                return False

        except Exception as e:
            logger.error(f"Erro ao dessubscrever do tópico {topic}: {e}")
            return False

    def publish(self, topic: str, payload: str, qos: int = None, retain: bool = False) -> bool:
        if not self._client or self._status != MQTTConnectionStatus.CONNECTED:
            logger.warning(f"Cliente não conectado. Não foi possível publicar em {topic}")
            return False

        try:
            qos = qos or self.config.MQTT_QOS
            result = self._client.publish(topic, payload, qos, retain)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Mensagem publicada em {topic}: {payload[:100]}...")
                return True
            else:
                logger.error(f"Erro ao publicar em {topic}: {result}")
                return False

        except Exception as e:
            logger.error(f"Erro ao publicar em {topic}: {e}")
            return False

    def get_status(self) -> MQTTConnectionStatus:
        return self._status

    def is_connected(self) -> bool:
        return self._status == MQTTConnectionStatus.CONNECTED

    def add_connection_callback(self, callback: Callable):
        self._connection_callbacks.append(callback)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._status = MQTTConnectionStatus.CONNECTED
            logger.info("Conectado ao broker MQTT")

            self._resubscribe_pending()

            for callback in self._connection_callbacks:
                try:
                    callback(True)
                except Exception as e:
                    logger.error(f"Erro ao executar callback de conexão: {e}")
        else:
            self._status = MQTTConnectionStatus.CONNECTION_FAILED
            logger.error(f"Falha na conexão MQTT. Código: {rc}")

            for callback in self._connection_callbacks:
                try:
                    callback(False)
                except Exception as e:
                    logger.error(f"Erro ao executar callback de falha na conexão: {e}")

    def _on_disconnect(self, client, userdata, rc):
        self._status = MQTTConnectionStatus.DISCONNECTED
        if rc != 0:
            logger.warning(f"Desconectado inesperadamente do broker MQTT. Código: {rc}")
            self._start_reconnect_thread()
        else:
            logger.info("Desconectado do broker MQTT")

    def _on_message(self, client, userdata, message):
        try:
            topic = message.topic
            payload = message.payload.decode('utf-8')

            logger.debug(f"Mensagem recebida em {topic}: {payload[:100]}...")

            handler_found = False

            for handler_topic, handler in self._message_handlers.items():
                if self._topic_matches(handler_topic, topic):
                    handler(topic, payload, message.qos, message.retain)
                    handler_found = True
                    break

            if not handler_found:
                self._default_message_handler(topic, payload, message.qos, message.retain)

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    def _topic_matches(self, pattern: str, topic: str) -> bool:
        if pattern == topic:
            return True

        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')

        if len(pattern_parts) != len(topic_parts):
            return False

        for p, t in zip(pattern_parts, topic_parts):
            if p != '+' and p != '#' and p != t:
                return False
            if p == '#':
                return True

        return True

    def _on_subscribe(self, client, userdata, mid, granted_qos):
        logger.debug(f"Subscrição confirmada. QoS concedido: {granted_qos}")

    def _on_unsubscribe(self, client, userdata, mid):
        logger.debug(f"Dessubscrição confirmada. Message ID: {mid}")

    def _on_log(self, client, userdata, level, buf):
        if level == mqtt.MQTT_LOG_DEBUG:
            logger.debug(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_INFO:
            logger.info(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_WARNING:
            logger.warning(f"MQTT: {buf}")
        elif level == mqtt.MQTT_LOG_ERR:
            logger.error(f"MQTT: {buf}")

    def _resubscribe_pending(self):
        for topic, qos in self._subscriptions.copy().items():
            try:
                result = self._client.subscribe(topic, qos)
                if result[0] == mqtt.MQTT_ERR_SUCCESS:
                    logger.info(f"Resubscrito no tópico: {topic}")
                else:
                    logger.error(f"Erro ao resubscrever no tópico {topic}: {result}")
            except Exception as e:
                logger.error(f"Erro ao resubscrever no tópico {topic}: {e}")

    def _start_reconnect_thread(self):
        if self._reconnect_thread and self._reconnect_thread.is_alive():
            return

        self._reconnect_thread = threading.Thread(target=self._reconnect_loop)
        self._reconnect_thread.daemon = True
        self._reconnect_thread.start()

    def _reconnect_loop(self):
        attempts = 0
        while self._is_running and self._status != MQTTConnectionStatus.CONNECTED:
            attempts += 1
            logger.info(f"Tentativa de reconexão {attempts}")

            try:
                self._client.reconnect()
                time.sleep(5)

                if self._status == MQTTConnectionStatus.CONNECTED:
                    logger.info("Reconectado com sucesso")
                    break

            except Exception as e:
                logger.error(f"Erro na tentativa de reconexão {attempts}: {e}")

            time.sleep(min(attempts * 2, 60))

    def _default_message_handler(self, topic: str, payload: str, qos: int, retain: bool):
        logger.info(f"Mensagem recebida em {topic} (sem handler específico): {payload[:100]}...")


mqtt_client = MQTTClient()