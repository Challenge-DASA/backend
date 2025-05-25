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

    VERSION = os.getenv('APP_VERSION', '1.0.0')
    API_NAME = os.getenv('API_NAME', 'SmartLab API')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    BUILD_DATE = os.getenv('BUILD_DATE', datetime.utcnow().isoformat())
    GIT_COMMIT = os.getenv('GIT_COMMIT', 'unknown')

    ORACLE_HOST = os.getenv('ORACLE_HOST', 'localhost')
    ORACLE_PORT = int(os.getenv('ORACLE_PORT', '1521'))
    ORACLE_SERVICE_NAME = os.getenv('ORACLE_SERVICE_NAME', 'FREEPDB1')
    ORACLE_USERNAME = os.getenv('ORACLE_USERNAME', 'smartlab')
    ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD', 'password')

    def DATABASE_URL(self) -> str:
        return f"oracle+oracledb://{self.ORACLE_USERNAME}:{self.ORACLE_PASSWORD}@{self.ORACLE_HOST}:{self.ORACLE_PORT}/?service_name={self.ORACLE_SERVICE_NAME}"


class DevelopmentConfig(Config):
    DEBUG = True
    ENABLE_REQUEST_LOGGING = True
    ENVIRONMENT = 'development'

    ORACLE_HOST = os.getenv('ORACLE_HOST', 'localhost')
    ORACLE_SERVICE_NAME = os.getenv('ORACLE_SERVICE_NAME', 'FREEPDB1')


class ProductionConfig(Config):
    DEBUG = False
    ENVIRONMENT = 'production'

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    VERSION = os.getenv('APP_VERSION', '1.0.0')
    API_NAME = os.getenv('API_NAME', 'SmartLab API')
    BUILD_DATE = os.getenv('BUILD_DATE')
    GIT_COMMIT = os.getenv('GIT_COMMIT')

    ORACLE_HOST = os.getenv('ORACLE_HOST')
    ORACLE_USERNAME = os.getenv('ORACLE_USERNAME')
    ORACLE_PASSWORD = os.getenv('ORACLE_PASSWORD')
    ORACLE_SERVICE_NAME = os.getenv('ORACLE_SERVICE_NAME', 'FREEPDB1')


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

        if not all([config_class.ORACLE_HOST, config_class.ORACLE_USERNAME,
                    config_class.ORACLE_PASSWORD, config_class.ORACLE_SERVICE_NAME]):
            raise ValueError("Oracle configuration must be set in production")

        if not config_class.BUILD_DATE:
            raise ValueError("BUILD_DATE should be set in production")

        if not config_class.GIT_COMMIT or config_class.GIT_COMMIT == 'unknown':
            raise ValueError("GIT_COMMIT should be set in production")

    return config_class