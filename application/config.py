import os
import uuid
from datetime import datetime

from domain.value_objects.ids import UserId


class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TEMP_USER_ID = UserId(uuid.UUID(os.getenv('TEMP_USER_ID', '12345678-1234-5678-1234-123456789012')))
    ENABLE_REQUEST_LOGGING = os.getenv('ENABLE_REQUEST_LOGGING', 'True').lower() == 'true'

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')

    API_NAME = os.getenv('API_NAME', 'SmartLab API')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    BUILD_DATE = os.getenv('BUILD_DATE', datetime.utcnow().isoformat())
    GIT_COMMIT = os.getenv('GIT_COMMIT', 'unknown')

    # PostgreSQL Database Configuration
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'smartlab')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

    # MQTT Configuration
    MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
    MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    MQTT_USERNAME = os.getenv('MQTT_USERNAME', '')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')
    MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', f'smartlab-{uuid.uuid4().hex[:8]}')
    MQTT_QOS = int(os.getenv('MQTT_QOS', '1'))
    MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', '60'))

    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class DevelopmentConfig(Config):
    DEBUG = True
    ENABLE_REQUEST_LOGGING = True
    ENVIRONMENT = 'development'

    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'smartlab')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
    MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')


class ProductionConfig(Config):
    DEBUG = False
    ENVIRONMENT = 'production'

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    VERSION = os.getenv('APP_VERSION', '1.0.0')
    API_NAME = os.getenv('API_NAME', 'SmartLab API')
    BUILD_DATE = os.getenv('BUILD_DATE')
    GIT_COMMIT = os.getenv('GIT_COMMIT')

    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'smartlab')

    MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST')
    MQTT_USERNAME = os.getenv('MQTT_USERNAME')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
config_by_name = {
    'development': DevelopmentConfig(),
    'production': ProductionConfig()
}


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    config_class = config_by_name.get(env, DevelopmentConfig)

    if env == 'production':
        if not config_class.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in production")

        if not all([config_class.POSTGRES_HOST, config_class.POSTGRES_USER,
                   config_class.POSTGRES_PASSWORD, config_class.POSTGRES_DB]):
            raise ValueError("PostgreSQL configuration must be set in production")

        if not config_class.BUILD_DATE:
            raise ValueError("BUILD_DATE should be set in production")

        if not config_class.GIT_COMMIT or config_class.GIT_COMMIT == 'unknown':
            raise ValueError("GIT_COMMIT should be set in production")

        if not config_class.MQTT_BROKER_HOST:
            raise ValueError("MQTT_BROKER_HOST must be set in production")

    return config_class