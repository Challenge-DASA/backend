import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DeviceService:

    def __init__(self):
        self.connected_devices: Dict[str, datetime] = {}
        self.device_whitelist: List[str] = []
        self.heartbeat_timeout = timedelta(minutes=2)

    def set_device_whitelist(self, whitelist: List[str]):
        self.device_whitelist = whitelist
        logger.info(f"Whitelist de dispositivos configurada: {whitelist}")

    def authorize_device(self, device_id: str) -> bool:
        if not self.device_whitelist:
            logger.debug(f"Sem whitelist configurada, autorizando {device_id}")
            self.connected_devices[device_id] = datetime.now()
            return True

        if device_id in self.device_whitelist:
            self.connected_devices[device_id] = datetime.now()
            logger.info(f"Dispositivo {device_id} autorizado (whitelist)")
            return True
        else:
            logger.warning(f"Dispositivo {device_id} não está na whitelist")
            return False

    def update_device_heartbeat(self, device_id: str):
        if device_id in self.connected_devices:
            self.connected_devices[device_id] = datetime.now()
            logger.debug(f"Heartbeat atualizado para {device_id}")
        else:
            logger.warning(f"Heartbeat recebido de dispositivo não autorizado: {device_id}")

    def get_connected_devices(self) -> List[str]:
        now = datetime.now()
        active_devices = []

        for device_id, last_seen in self.connected_devices.items():
            if now - last_seen <= self.heartbeat_timeout:
                active_devices.append(device_id)

        return active_devices

    def get_disconnected_devices(self) -> List[str]:
        now = datetime.now()
        disconnected_devices = []

        for device_id, last_seen in self.connected_devices.items():
            if now - last_seen > self.heartbeat_timeout:
                disconnected_devices.append(device_id)

        return disconnected_devices

    def is_device_connected(self, device_id: str) -> bool:
        if device_id not in self.connected_devices:
            return False

        last_seen = self.connected_devices[device_id]
        return datetime.now() - last_seen <= self.heartbeat_timeout

    def get_device_status(self, device_id: str) -> Dict:
        if device_id not in self.connected_devices:
            return {
                "device_id": device_id,
                "status": "never_connected",
                "last_seen": None
            }

        last_seen = self.connected_devices[device_id]
        is_connected = self.is_device_connected(device_id)

        return {
            "device_id": device_id,
            "status": "connected" if is_connected else "disconnected",
            "last_seen": last_seen.isoformat(),
            "last_seen_seconds_ago": int((datetime.now() - last_seen).total_seconds())
        }

    def get_all_devices_status(self) -> List[Dict]:
        return [self.get_device_status(device_id) for device_id in self.connected_devices.keys()]

    def cleanup_old_devices(self, max_age_days: int = 7):
        now = datetime.now()
        cutoff = now - timedelta(days=max_age_days)

        to_remove = []
        for device_id, last_seen in self.connected_devices.items():
            if last_seen < cutoff:
                to_remove.append(device_id)

        for device_id in to_remove:
            del self.connected_devices[device_id]
            logger.info(f"Dispositivo {device_id} removido (inativo há {max_age_days} dias)")

        return len(to_remove)