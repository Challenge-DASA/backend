import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class TemperatureService:

    def __init__(self):
        self.temperature_buffer: Dict[str, List[Dict]] = {}
        self.device_repository = None
        self.temperature_repository = None

    def set_repositories(self, device_repo, temperature_repo):
        self.device_repository = device_repo
        self.temperature_repository = temperature_repo

    def process_temperature_data(self, device_id: str, temperature_data: Dict[str, Any]):
        try:
            readings = temperature_data.get('readings', [])
            device_timestamp = temperature_data.get('timestamp')

            if not readings:
                logger.warning(f"Dados de temperatura vazios do dispositivo {device_id}")
                return

            logger.info(f"Processando {len(readings)} leituras de temperatura do dispositivo {device_id}")

            processed_readings = []
            for reading in readings:
                temperature = reading.get('temperature')
                reading_timestamp = reading.get('timestamp')

                if temperature is None:
                    logger.warning(f"Leitura sem temperatura do dispositivo {device_id}")
                    continue

                processed_reading = {
                    'device_id': device_id,
                    'temperature': float(temperature),
                    'reading_timestamp': reading_timestamp,
                    'device_batch_timestamp': device_timestamp,
                    'received_at': datetime.now().isoformat()
                }

                processed_readings.append(processed_reading)

            if processed_readings:
                self._store_temperature_readings(device_id, processed_readings)
                self._check_temperature_alerts(device_id, processed_readings)

        except Exception as e:
            logger.error(f"Erro ao processar dados de temperatura do dispositivo {device_id}: {e}")

    def _store_temperature_readings(self, device_id: str, readings: List[Dict]):
        if device_id not in self.temperature_buffer:
            self.temperature_buffer[device_id] = []

        self.temperature_buffer[device_id].extend(readings)
        logger.debug(f"Buffer de temperatura para {device_id}: {len(self.temperature_buffer[device_id])} leituras")

        if self.temperature_repository:
            try:
                self.temperature_repository.save_temperature_batch(readings)
                logger.debug(f"Leituras de temperatura salvas no banco: {len(readings)}")
            except Exception as e:
                logger.error(f"Erro ao salvar temperaturas no banco: {e}")

    def _check_temperature_alerts(self, device_id: str, readings: List[Dict]):
        for reading in readings:
            temperature = reading['temperature']

            if temperature > 30.0:
                logger.warning(f"ALERTA: Temperatura alta no dispositivo {device_id}: {temperature}°C")
                self._trigger_temperature_alert(device_id, temperature, "high")
            elif temperature < 5.0:
                logger.warning(f"ALERTA: Temperatura baixa no dispositivo {device_id}: {temperature}°C")
                self._trigger_temperature_alert(device_id, temperature, "low")

    def _trigger_temperature_alert(self, device_id: str, temperature: float, alert_type: str):
        alert_data = {
            'device_id': device_id,
            'temperature': temperature,
            'alert_type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'message': f"Temperatura {alert_type}: {temperature}°C"
        }

        logger.info(f"Alerta de temperatura disparado: {alert_data}")

    def get_latest_temperatures(self, device_id: str, limit: int = 10) -> List[Dict]:
        if device_id not in self.temperature_buffer:
            return []

        return self.temperature_buffer[device_id][-limit:]

    def get_temperature_stats(self, device_id: str) -> Dict:
        if device_id not in self.temperature_buffer:
            return {
                "device_id": device_id,
                "total_readings": 0,
                "avg_temperature": None,
                "min_temperature": None,
                "max_temperature": None
            }

        readings = self.temperature_buffer[device_id]
        temperatures = [r['temperature'] for r in readings]

        return {
            "device_id": device_id,
            "total_readings": len(temperatures),
            "avg_temperature": sum(temperatures) / len(temperatures) if temperatures else None,
            "min_temperature": min(temperatures) if temperatures else None,
            "max_temperature": max(temperatures) if temperatures else None,
            "latest_temperature": temperatures[-1] if temperatures else None,
            "latest_reading_time": readings[-1]['received_at'] if readings else None
        }

    def get_all_devices_temperature_stats(self) -> List[Dict]:
        return [self.get_temperature_stats(device_id) for device_id in self.temperature_buffer.keys()]

    def clear_temperature_buffer(self, device_id: str = None):
        if device_id:
            if device_id in self.temperature_buffer:
                del self.temperature_buffer[device_id]
                logger.info(f"Buffer de temperatura limpo para dispositivo {device_id}")
        else:
            self.temperature_buffer.clear()
            logger.info("Todos os buffers de temperatura limpos")