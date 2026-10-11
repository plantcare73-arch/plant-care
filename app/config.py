"""
Centralized application configuration.

All configuration is driven by environment variables with sensible defaults.
No secrets should ever be committed to source control.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # --- App ---
    APP_ENV = os.getenv('APP_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-to-a-strong-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # --- MongoDB ---
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'plant_disease_db')

    # --- ML Model ---
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/plant_disease_model.h5')
    MODEL_NAME = 'plant_disease_cnn'
    MODEL_VERSION = '1.0.0'
    PREPROCESSING_VERSION = '1.0'
    IMG_SIZE = 224

    # --- Uploads ---
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg'}

    # --- Session ---
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # --- External APIs (optional, behind adapters) ---
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
    WEATHER_API_URL = os.getenv('WEATHER_API_URL', 'https://api.openweathermap.org/data/2.5')
    MAPS_API_KEY = os.getenv('MAPS_API_KEY', '')

    # --- Rate Limiting ---
    RATELIMIT_LOGIN_MAX = int(os.getenv('RATELIMIT_LOGIN_MAX', 10))
    RATELIMIT_LOGIN_WINDOW = int(os.getenv('RATELIMIT_LOGIN_WINDOW', 300))  # 5 min
    RATELIMIT_PREDICT_MAX = int(os.getenv('RATELIMIT_PREDICT_MAX', 30))
    RATELIMIT_PREDICT_WINDOW = int(os.getenv('RATELIMIT_PREDICT_WINDOW', 3600))  # 1 hour

    # --- Logging ---
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')  # 'json' or 'text'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    DATABASE_NAME = 'plant_disease_test_db'
    WTF_CSRF_ENABLED = False


# Config mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}


def get_config():
    """Return config class based on APP_ENV."""
    env = os.getenv('APP_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)
