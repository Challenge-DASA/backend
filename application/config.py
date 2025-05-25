import os
from domain.context import UserId


class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TEMP_USER_ID = UserId(os.getenv('TEMP_USER_ID', '12345678-1234-5678-1234-123456789012'))
    ENABLE_REQUEST_LOGGING = os.getenv('ENABLE_REQUEST_LOGGING', 'True').lower() == 'true'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')


class DevelopmentConfig(Config):
    DEBUG = True
    ENABLE_REQUEST_LOGGING = True


class ProductionConfig(Config):
    DEBUG = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Sobrescreve com valor real


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    config_class = config_by_name.get(env, DevelopmentConfig)

    if env == 'production' and not config_class.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY must be set in production")

    return config_class